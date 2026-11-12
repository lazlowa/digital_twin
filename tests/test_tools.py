import asyncio
from email.message import EmailMessage

import pytest

from app import tools
from app.config import settings

TRANSCRIPT = tools.format_transcript(
    [
        {"role": "user", "content": "Are you open to new roles?"},
        {"role": "assistant", "content": "Happy to talk. Want to leave your email?"},
    ]
)


class FakeSMTP:
    """Stands in for smtplib.SMTP_SSL and keeps the sent messages."""

    sent: list[EmailMessage] = []

    def __init__(self, host: str, port: int) -> None:
        self.address = (host, port)

    def __enter__(self) -> "FakeSMTP":
        return self

    def __exit__(self, *exc) -> None:
        pass

    def login(self, user: str, password: str) -> None:
        self.login_as = (user, password)

    def send_message(self, message: EmailMessage) -> None:
        assert self.login_as == ("twin@example.com", "app-password")
        assert self.address == ("smtp.example.com", 465)
        FakeSMTP.sent.append(message)


@pytest.fixture(autouse=True)
def smtp(monkeypatch: pytest.MonkeyPatch) -> list[EmailMessage]:
    FakeSMTP.sent = []
    monkeypatch.setattr(tools.smtplib, "SMTP_SSL", FakeSMTP)
    monkeypatch.setattr(settings, "email_smtp_server", "smtp.example.com")
    monkeypatch.setattr(settings, "email_address", "twin@example.com")
    monkeypatch.setattr(settings, "email_app_password", "app-password")
    monkeypatch.setattr(settings, "notify_to", "owner@example.com")
    return FakeSMTP.sent


def test_transcript_names_speakers() -> None:
    assert TRANSCRIPT == (
        "Visitor: Are you open to new roles?\n\n"
        "Twin: Happy to talk. Want to leave your email?"
    )


def test_unknown_question_email(smtp: list[EmailMessage]) -> None:
    result = tools.record_unknown_question("Favourite dish?", TRANSCRIPT)

    [message] = smtp
    assert result == tools.RECORDED
    assert message["To"] == "owner@example.com"
    assert message["From"] == "twin@example.com"
    assert message["Subject"] == "Digital twin: unanswered question"
    body = message.get_content()
    assert "Question:\nFavourite dish?" in body
    assert TRANSCRIPT in body


def test_visitor_contact_email(smtp: list[EmailMessage]) -> None:
    result = tools.record_visitor_contact(
        "jane@example.com", TRANSCRIPT, name="Jane Doe", note="A platform role"
    )

    [message] = smtp
    assert result == tools.RECORDED
    assert message["To"] == "owner@example.com"
    assert message["Subject"] == "Digital twin: new visitor contact"
    body = message.get_content()
    assert "Email: jane@example.com" in body
    assert "Name: Jane Doe" in body
    assert "Note: A platform role" in body
    assert TRANSCRIPT in body


def test_run_tool_dispatches_json_arguments(smtp: list[EmailMessage]) -> None:
    args = '{"email": "jane@example.com"}'

    result = asyncio.run(tools.run_tool("record_visitor_contact", args, TRANSCRIPT))

    assert result == tools.RECORDED
    assert "Name: -" in smtp[0].get_content()


def test_run_tool_rejects_invalid_calls(smtp: list[EmailMessage]) -> None:
    assert asyncio.run(tools.run_tool("unknown_tool", "{}", "")) == tools.FAILED
    assert (
        asyncio.run(tools.run_tool("record_unknown_question", "{", "")) == tools.FAILED
    )
    assert smtp == []
