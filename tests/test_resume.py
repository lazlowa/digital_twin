from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.resume import load_page, parse_resume

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


def test_footer_shows_copyright_and_build_link(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    page = client.get("/").text
    assert 'class="site-footer"' in page
    assert f"&copy; {date.today().year} Laszlo Anka" in page
    assert 'class="build"' not in page

    monkeypatch.setattr(settings, "vercel_git_commit_sha", "abc1234def5678")
    page = client.get("/").text
    assert (
        'href="https://github.com/lazlowa/digital_twin/commit/abc1234def5678"' in page
    )
    assert "Build abc1234</a>" in page


def test_footer_and_chat_note_link_to_legal_pages() -> None:
    page = client.get("/").text

    # Footer links stay in the same tab; the chat note opens a new one so the
    # conversation, kept only in memory, is not lost.
    assert '<a href="/legal">Legal notice</a>' in page
    assert '<a href="/privacy">Privacy</a>' in page
    assert '<a href="/privacy" target="_blank" rel="noopener">Privacy</a>' in page


def test_external_links_open_in_new_tab() -> None:
    page = client.get("/").text

    new_tab = 'target="_blank" rel="noopener"'
    assert f'<a href="https://github.com/lazlowa" {new_tab}>' in page
    assert f'<a href="https://github.com/lazlowa/pypz-python" {new_tab}>' in page
    assert '<a href="mailto:laszlo.anka@gmail.com">' in page


@pytest.mark.parametrize(
    ("path", "filename"), [("/legal", "LEGAL.md"), ("/privacy", "PRIVACY.md")]
)
def test_legal_pages_render_data_files(path: str, filename: str) -> None:
    response = client.get(path)

    assert response.status_code == 200
    assert load_page(filename) in response.text
    assert 'class="site-footer"' in response.text


def test_preview_badge_only_on_preview(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "vercel_env", "production")
    assert "badge-preview" not in client.get("/").text

    monkeypatch.setattr(settings, "vercel_env", "preview")
    for path in ("/", "/legal"):
        assert '<div class="badge-preview">Preview</div>' in client.get(path).text
