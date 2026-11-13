"""POST /api/chat: streams the digital twin's reply from OpenRouter."""

import logging
import re
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Annotated, Literal

import openai
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, model_validator

from app.config import settings
from app.ratelimit import client_ip, rate_limit
from app.tools import TOOLS, format_transcript, run_tool

ROOT = Path(__file__).resolve().parent.parent
PLAN_PATH = ROOT / "plan" / "PLAN.md"
ME_PATH = ROOT / "data" / "ME.md"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MAX_TOOL_ROUNDS = 3

logger = logging.getLogger(__name__)
router = APIRouter()


class Message(BaseModel):
    # No "system" role from clients: visitors must not override the instructions.
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)

    @model_validator(mode="after")
    def check_length(self) -> "Message":
        # Earlier twin replies come back as history and may be longer than a
        # visitor message, so they get a bound derived from the token limit.
        if self.role == "user":
            limit = settings.max_message_chars
        else:
            limit = 8 * settings.max_response_tokens
        if len(self.content) > limit:
            raise ValueError(f"Message is too long (max {limit} characters)")
        return self


class ChatRequest(BaseModel):
    messages: list[Message] = Field(
        min_length=1, max_length=settings.max_history_messages
    )


def load_instructions(path: Path = PLAN_PATH) -> str:
    """Returns the quoted LLM instruction block from PLAN.md."""
    match = re.search(
        r'^"\n(.+?)\n"$', path.read_text(encoding="utf-8"), re.MULTILINE | re.DOTALL
    )
    if match is None:
        raise RuntimeError(f"No quoted instruction block found in {path}")
    return match.group(1).strip()


TOOL_GUIDANCE = """\
Tool use:
- Record every question you cannot answer from the document below with
  record_unknown_question, including unrelated questions. Afterwards tell the
  visitor only that you don't know; do not mention that the question was recorded.
- You cannot record or pass on contact details. When the visitor wants to get in
  touch or offers their own contact details, kindly share the email address from
  the document below and mention that the contact panel on this page lists the
  email address and LinkedIn profile. Apart from the availability stated in the
  document, do not speak for the person you represent about their interest in a
  role or their reaction; they will answer themselves.
- Record each question only once per conversation. You cannot see tool calls
  from earlier turns, only your earlier replies, and those replies are accurate:
  if you earlier said you don't know something, it was already recorded. Do not
  call the tool again for it; just answer in the chat."""


def build_system_prompt() -> str:
    knowledge = ME_PATH.read_text(encoding="utf-8")
    return (
        f"{load_instructions()}\n\n{TOOL_GUIDANCE}\n\n"
        "Everything you know about the person you represent is in the following "
        f"document.\n\n{knowledge}"
    )


def get_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        base_url=OPENROUTER_BASE_URL, api_key=settings.openrouter_api_key
    )


@router.post("/api/chat", dependencies=[Depends(rate_limit)])
async def chat(
    request: ChatRequest,
    http_request: Request,
    client: Annotated[AsyncOpenAI, Depends(get_client)],
) -> StreamingResponse:
    history = [message.model_dump() for message in request.messages]
    messages = [{"role": "system", "content": build_system_prompt()}, *history]
    try:
        # The first request is made here so that failures can return 502.
        stream = await _complete(client, messages)
    except openai.APIError as error:
        logger.error("OpenRouter request failed: %s", error)
        raise HTTPException(
            status_code=502, detail="The assistant is currently unavailable."
        ) from error

    transcript = format_transcript(history)
    reply = _reply(client, messages, stream, transcript, client_ip(http_request))
    # nosniff: browsers otherwise buffer the start of a text/plain response to
    # sniff its type, so short replies would arrive all at once.
    return StreamingResponse(
        reply,
        media_type="text/plain; charset=utf-8",
        headers={"X-Content-Type-Options": "nosniff"},
    )


async def _complete(client: AsyncOpenAI, messages: list[dict]) -> AsyncIterator:
    extra_body = {}
    if settings.openrouter_provider:
        # OpenRouter provider routing: no fallback to other providers, so the
        # provider named in the privacy notice is the only one used.
        extra_body["provider"] = {
            "order": [settings.openrouter_provider],
            "allow_fallbacks": False,
        }
    return await client.chat.completions.create(
        model=settings.openrouter_model,
        messages=messages,
        tools=TOOLS,
        max_tokens=settings.max_response_tokens,
        stream=True,
        extra_body=extra_body,
    )


async def _reply(
    client: AsyncOpenAI,
    messages: list[dict],
    stream: AsyncIterator,
    transcript: str,
    ip: str,
) -> AsyncIterator[str]:
    """Streams text, runs requested tools, and continues until the model is done."""
    for round_ in range(MAX_TOOL_ROUNDS + 1):
        if round_:
            stream = await _complete(client, messages)
        text = ""
        calls: dict[int, dict] = {}
        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if delta.content:
                text += delta.content
                yield delta.content
            for part in delta.tool_calls or []:
                call = calls.setdefault(part.index, {"id": "", "name": "", "args": ""})
                call["id"] = part.id or call["id"]
                if part.function:
                    call["name"] += part.function.name or ""
                    call["args"] += part.function.arguments or ""
        if not calls:
            return

        messages.append(
            {
                "role": "assistant",
                "content": text or None,
                "tool_calls": [
                    {
                        "id": call["id"],
                        "type": "function",
                        "function": {"name": call["name"], "arguments": call["args"]},
                    }
                    for call in calls.values()
                ],
            }
        )
        for call in calls.values():
            result = await run_tool(call["name"], call["args"], transcript, ip)
            messages.append(
                {"role": "tool", "tool_call_id": call["id"], "content": result}
            )
    logger.error("Stopped after %d tool rounds", MAX_TOOL_ROUNDS)
