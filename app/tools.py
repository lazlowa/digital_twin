"""The tool offered to the LLM: emails unanswered questions to NOTIFY_TO."""

import asyncio
import json
import logging
import smtplib
from email.message import EmailMessage

from app.config import settings
from app.ratelimit import RateLimiter

SMTP_PORT = 465
RECORDED = "Recorded."
FAILED = "Recording failed."
DAY = 86400

logger = logging.getLogger(__name__)
# Caps notification emails per client IP; approximate on serverless hosting.
email_limiter = RateLimiter([(settings.max_question_emails_per_day, DAY)])

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


def record_unknown_question(question: str, transcript: str, client_ip: str) -> str:
    if email_limiter.hit(client_ip) is not None:
        # Over the daily cap the email is skipped silently: the twin still says
        # it doesn't know, and the visitor is not told.
        logger.warning("Daily question email cap reached; email not sent")
        return RECORDED
    return _notify(
        "Digital twin: unanswered question",
        f"Question:\n{question}\n\nConversation:\n\n{transcript}\n",
    )


async def run_tool(name: str, arguments: str, transcript: str, client_ip: str) -> str:
    """Executes a tool call from the model and returns the result for the model."""
    try:
        if name != "record_unknown_question":
            raise ValueError("unknown tool")
        return await asyncio.to_thread(
            record_unknown_question,
            transcript=transcript,
            client_ip=client_ip,
            **json.loads(arguments),
        )
    except (TypeError, ValueError) as error:
        logger.error("Invalid tool call %s(%s): %s", name, arguments, error)
        return FAILED


def _notify(subject: str, body: str) -> str:
    try:
        send_email(subject, body)
    except (smtplib.SMTPException, OSError) as error:
        logger.error("Sending notification email failed: %s", error)
        return FAILED
    return RECORDED
