import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.resume import parse_resume

client = TestClient(app)

SAMPLE = """## Identity

- Name: Jane Doe
- Role: Engineer
- Tagline: I build things.
- Email: jane@example.com
- GitHub: github.com/jane
- Location: Berlin

## Profile

Jane builds **systems**.

## Experience

- **2020 - now** Engineer *Acme*
"""


def test_index_renders_profile_md() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Laszlo Anka" in response.text
    assert "I build the data platforms other teams build on." in response.text
    assert "Twenty years ago" in response.text
    assert "<h2>Experience</h2>" in response.text


def test_index_does_not_show_me_md() -> None:
    response = client.get("/")

    assert "Source-of-truth knowledge base" not in response.text
    assert "Scope and Boundaries for the Twin" not in response.text


def test_index_has_chat_widget() -> None:
    response = client.get("/")

    assert 'id="chat" popover' in response.text
    assert 'popovertarget="chat"' in response.text
    assert '<script src="/static/chat.js" defer></script>' in response.text
    assert client.get("/static/chat.js").status_code == 200


def test_static_files_are_served() -> None:
    assert client.get("/static/style.css").status_code == 200


def test_parse_resume_identity() -> None:
    resume = parse_resume(SAMPLE)

    assert resume.name == "Jane Doe"
    assert resume.role == "Engineer"
    assert resume.tagline == "I build things."
    assert [(link.label, link.href) for link in resume.links] == [
        ("Email", "mailto:jane@example.com"),
        ("GitHub", "https://github.com/jane"),
        ("Location", None),
    ]


def test_parse_resume_sections() -> None:
    resume = parse_resume(SAMPLE)

    assert resume.profile_html == "<p>Jane builds <strong>systems</strong>.</p>\n"
    assert [(section.title, section.slug) for section in resume.sections] == [
        ("Experience", "experience"),
    ]
    assert "<strong>2020 - now</strong>" in resume.sections[0].html


def test_preview_badge_only_on_preview(monkeypatch: pytest.MonkeyPatch) -> None:
    assert "env-badge" not in client.get("/").text

    monkeypatch.setattr(settings, "vercel_env", "preview")

    assert '<div class="env-badge">Preview</div>' in client.get("/").text
