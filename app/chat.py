"""POST /api/chat: streams the digital twin's reply from OpenRouter."""

import logging
import re
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Annotated, Literal

import openai
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel

from app.config import settings
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
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


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
- After you could not answer a question, or when the visitor shows clear interest
  (for example hiring or a collaboration), you may offer once that the visitor can
  leave an email address so the person you represent can follow up. Do not push.
- When the visitor shares an email address, record it with record_visitor_contact,
  together with their name and topic if they gave them.
- Record each question and each contact only once per conversation. You cannot
  see tool calls from earlier turns, only your earlier replies, and those replies
  are accurate: if you earlier confirmed recording contact details, or said you
  don't know something, it was already recorded. Do not call the tool again for
  it; just answer in the chat."""


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


@router.post("/api/chat")
async def chat(
    request: ChatRequest, client: Annotated[AsyncOpenAI, Depends(get_client)]
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

    reply = _reply(client, messages, stream, format_transcript(history))
    # nosniff: browsers otherwise buffer the start of a text/plain response to
    # sniff its type, so short replies would arrive all at once.
    return StreamingResponse(
        reply,
        media_type="text/plain; charset=utf-8",
        headers={"X-Content-Type-Options": "nosniff"},
    )


async def _complete(client: AsyncOpenAI, messages: list[dict]) -> AsyncIterator:
    return await client.chat.completions.create(
        model=settings.openrouter_model, messages=messages, tools=TOOLS, stream=True
    )


async def _reply(
    client: AsyncOpenAI, messages: list[dict], stream: AsyncIterator, transcript: str
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
            result = await run_tool(call["name"], call["args"], transcript)
            messages.append(
                {"role": "tool", "tool_call_id": call["id"], "content": result}
            )
    logger.error("Stopped after %d tool rounds", MAX_TOOL_ROUNDS)
