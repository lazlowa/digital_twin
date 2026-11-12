"""Tools offered to the LLM. Each one emails a notification to NOTIFY_TO."""

import asyncio
import json
import logging
import smtplib
from email.message import EmailMessage

from app.config import settings

SMTP_PORT = 465
RECORDED = "Recorded."
FAILED = "Recording failed."

logger = logging.getLogger(__name__)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "record_unknown_question",
            "description": (
                "Record a question you cannot answer from the provided document, "
                "including unrelated questions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The question."}
                },
                "required": ["question"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_visitor_contact",
            "description": (
                "Record the contact details a visitor has shared so the person you "
                "represent can follow up."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "Visitor's email."},
                    "name": {"type": "string", "description": "Visitor's name."},
                    "note": {
                        "type": "string",
                        "description": "What the visitor wants to discuss.",
                    },
                },
                "required": ["email"],
            },
        },
    },
]


def format_transcript(messages: list[dict]) -> str:
    speakers = {"user": "Visitor", "assistant": "Twin"}
    return "\n\n".join(f"{speakers[m['role']]}: {m['content']}" for m in messages)


def send_email(subject: str, body: str) -> None:
    if settings.vercel_env == "preview":
        subject = f"[Preview] {subject}"
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.email_address
    message["To"] = settings.notify_to
    message.set_content(body)
    with smtplib.SMTP_SSL(settings.email_smtp_server, SMTP_PORT) as smtp:
        smtp.login(settings.email_address, settings.email_app_password)
        smtp.send_message(message)


def record_unknown_question(question: str, transcript: str) -> str:
    return _notify(
        "Digital twin: unanswered question",
        f"Question:\n{question}\n\nConversation:\n\n{transcript}\n",
    )


def record_visitor_contact(
    email: str, transcript: str, name: str | None = None, note: str | None = None
) -> str:
    return _notify(
        "Digital twin: new visitor contact",
        f"Email: {email}\nName: {name or '-'}\nNote: {note or '-'}\n\n"
        f"Conversation:\n\n{transcript}\n",
    )


async def run_tool(name: str, arguments: str, transcript: str) -> str:
    """Executes a tool call from the model and returns the result for the model."""
    handlers = {
        "record_unknown_question": record_unknown_question,
        "record_visitor_contact": record_visitor_contact,
    }
    try:
        handler = handlers[name]
        return await asyncio.to_thread(
            handler, transcript=transcript, **json.loads(arguments)
        )
    except (KeyError, TypeError, ValueError) as error:
        logger.error("Invalid tool call %s(%s): %s", name, arguments, error)
        return FAILED


def _notify(subject: str, body: str) -> str:
    try:
        send_email(subject, body)
    except (smtplib.SMTPException, OSError) as error:
        logger.error("Sending notification email failed: %s", error)
        return FAILED
    return RECORDED
