from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.resume import find_cv, load_page, load_resume, parse_resume

client = TestClient(app)

SAMPLE = """## Identity

- Name: Jane Doe
- Role: Engineer
- Tagline: I build things.
- Description: Jane, an engineer.
- Availability: Open to work
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

    resume = load_resume()
    assert response.status_code == 200
    assert resume.name in response.text
    assert f'<p class="tagline">{resume.tagline}</p>' in response.text
    assert resume.profile_html in response.text
    assert f"{resume.availability}</p>" in response.text
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
    for name in ["style.css", "og.png", "favicon.svg", "favicon-32.png"]:
        assert client.get(f"/static/{name}").status_code == 200
    assert client.get("/static/apple-touch-icon.png").status_code == 200


def test_index_has_description_and_link_preview_tags() -> None:
    page = client.get("/").text
    description = parse_resume(
        (Path(__file__).parent.parent / "data" / "PROFILE.md").read_text(
            encoding="utf-8"
        )
    ).description

    assert description
    assert f'<meta name="description" content="{description}">' in page
    assert f'<meta property="og:description" content="{description}">' in page
    assert '<meta property="og:url" content="https://lazlowa.space/">' in page
    assert (
        '<meta property="og:image" content="https://lazlowa.space/static/og.png">'
        in page
    )
    assert '<meta name="twitter:card" content="summary_large_image">' in page


def test_icons_on_all_pages() -> None:
    for path in ("/", "/legal", "/privacy"):
        page = client.get(path).text
        assert '<link rel="icon" href="/static/favicon.svg"' in page
        assert (
            '<link rel="apple-touch-icon" href="/static/apple-touch-icon.png">' in page
        )


def test_parse_resume_identity() -> None:
    resume = parse_resume(SAMPLE)

    assert resume.name == "Jane Doe"
    assert resume.role == "Engineer"
    assert resume.tagline == "I build things."
    assert resume.description == "Jane, an engineer."
    assert resume.availability == "Open to work"
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


def test_find_cv_picks_highest_version(tmp_path: Path) -> None:
    assert find_cv(tmp_path) is None

    for name in ["CV_v2.pdf", "CV_v10.pdf", "CV_v9.pdf", "CV_vx.pdf", "other.pdf"]:
        (tmp_path / name).write_bytes(b"%PDF")

    assert find_cv(tmp_path) == "CV_v10.pdf"


def test_cv_download_button(monkeypatch: pytest.MonkeyPatch) -> None:
    cv = find_cv()
    assert cv is not None
    monkeypatch.setattr(settings, "cv_download_enabled", False)
    assert "Download CV" not in client.get("/").text

    monkeypatch.setattr(settings, "cv_download_enabled", True)
    page = client.get("/").text
    assert (
        f'<a class="cta-secondary" href="/static/{cv}" '
        'download="ANKA_Laszlo_CV.pdf">Download CV</a>'
    ) in page
    response = client.get(f"/static/{cv}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

    monkeypatch.setattr("app.main.find_cv", lambda: None)
    assert "Download CV" not in client.get("/").text
