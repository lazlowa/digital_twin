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


IP = "203.0.113.7"


def test_unknown_question_email(smtp: list[EmailMessage]) -> None:
    result = tools.record_unknown_question("Favourite dish?", TRANSCRIPT, IP)

    [message] = smtp
    assert result == tools.RECORDED
    assert message["To"] == "owner@example.com"
    assert message["From"] == "twin@example.com"
    assert message["Subject"] == "Digital twin: unanswered question"
    body = message.get_content()
    assert "Question:\nFavourite dish?" in body
    assert TRANSCRIPT in body


def test_preview_subject_prefix(
    smtp: list[EmailMessage], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "vercel_env", "preview")

    tools.record_unknown_question("Favourite dish?", TRANSCRIPT, IP)

    assert smtp[0]["Subject"] == "[Preview] Digital twin: unanswered question"


def test_daily_email_cap_per_ip(smtp: list[EmailMessage]) -> None:
    cap = settings.max_question_emails_per_day
    results = [
        tools.record_unknown_question(f"Question {n}?", TRANSCRIPT, IP)
        for n in range(cap + 2)
    ]

    assert len(smtp) == cap
    assert results == [tools.RECORDED] * (cap + 2)
    tools.record_unknown_question("Other visitor?", TRANSCRIPT, "198.51.100.1")
    assert len(smtp) == cap + 1


def test_run_tool_dispatches_json_arguments(smtp: list[EmailMessage]) -> None:
    args = '{"question": "Favourite dish?"}'

    result = asyncio.run(
        tools.run_tool("record_unknown_question", args, TRANSCRIPT, IP)
    )

    assert result == tools.RECORDED
    assert "Question:\nFavourite dish?" in smtp[0].get_content()


def test_run_tool_rejects_invalid_calls(smtp: list[EmailMessage]) -> None:
    for name, args in [
        ("record_visitor_contact", '{"email": "jane@example.com"}'),
        ("record_unknown_question", "{"),
        ("record_unknown_question", '{"email": "jane@example.com"}'),
    ]:
        assert asyncio.run(tools.run_tool(name, args, "", IP)) == tools.FAILED
    assert smtp == []
