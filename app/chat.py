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

ROOT = Path(__file__).resolve().parent.parent
PLAN_PATH = ROOT / "plan" / "PLAN.md"
ME_PATH = ROOT / "data" / "ME.md"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

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


def build_system_prompt() -> str:
    knowledge = ME_PATH.read_text(encoding="utf-8")
    return (
        f"{load_instructions()}\n\n"
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
    messages = [{"role": "system", "content": build_system_prompt()}]
    messages += [message.model_dump() for message in request.messages]
    try:
        stream = await client.chat.completions.create(
            model=settings.openrouter_model, messages=messages, stream=True
        )
    except openai.APIError as error:
        logger.error("OpenRouter request failed: %s", error)
        raise HTTPException(
            status_code=502, detail="The assistant is currently unavailable."
        ) from error

    return StreamingResponse(_text(stream), media_type="text/plain; charset=utf-8")


async def _text(stream: AsyncIterator) -> AsyncIterator[str]:
    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
