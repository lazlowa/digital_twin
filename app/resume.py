"""Turns data/PROFILE.md into the visitor-facing page.

PROFILE.md is a short, hand-curated profile for the page. data/ME.md remains the
full knowledge base for the LLM and is not shown on the page.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from markdown_it import MarkdownIt

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PROFILE_PATH = DATA_DIR / "PROFILE.md"

IDENTITY_SECTION = "Identity"
PROFILE_SECTION = "Profile"

_markdown = MarkdownIt("commonmark")


def _render_link_open(self, tokens, idx, options, env) -> str:
    # Links to other sites open in a new tab, so visitors keep this page.
    token = tokens[idx]
    if str(token.attrGet("href")).startswith(("http://", "https://")):
        token.attrSet("target", "_blank")
        token.attrSet("rel", "noopener")
    return self.renderToken(tokens, idx, options, env)


_markdown.add_render_rule("link_open", _render_link_open)


@dataclass
class Link:
    label: str
    text: str
    href: str | None


@dataclass
class Section:
    title: str
    slug: str
    html: str


@dataclass
class Resume:
    name: str
    role: str
    tagline: str
    description: str
    availability: str
    profile_html: str
    links: list[Link]
    sections: list[Section]


def load_resume(path: Path = PROFILE_PATH) -> Resume:
    return parse_resume(path.read_text(encoding="utf-8"))


def load_page(filename: str) -> str:
    """Renders a Markdown file from data/ (legal notice, privacy) to HTML."""
    return _markdown.render((DATA_DIR / filename).read_text(encoding="utf-8"))


def parse_resume(text: str) -> Resume:
    parts = re.split(r"^## +(.+?)[ \t]*$", text, flags=re.MULTILINE)
    identity: dict[str, str] = {}
    profile_html = ""
    sections: list[Section] = []
    for title, body in zip(parts[1::2], parts[2::2], strict=True):
        if title == IDENTITY_SECTION:
            identity = dict(re.findall(r"^- ([^:\n]+):[ \t]*(.+)$", body, re.MULTILINE))
        elif title == PROFILE_SECTION:
            profile_html = _markdown.render(body)
        else:
            sections.append(Section(title, _slugify(title), _markdown.render(body)))

    return Resume(
        name=identity.pop("Name", ""),
        role=identity.pop("Role", ""),
        tagline=identity.pop("Tagline", ""),
        description=identity.pop("Description", ""),
        availability=identity.pop("Availability", ""),
        profile_html=profile_html,
        links=[Link(label, value, _href(value)) for label, value in identity.items()],
        sections=sections,
    )


def _href(value: str) -> str | None:
    if re.fullmatch(r"[\w.+-]+@[\w-]+\.[\w.-]+", value):
        return f"mailto:{value}"
    if re.fullmatch(r"[\w-]+(\.[\w-]+)+/\S*", value):
        return f"https://{value}"
    return None


def _slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
