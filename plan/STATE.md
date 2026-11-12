# State

## Current task

None. TID-2 (Resume page) was closed by the developer on 2026-11-12, merged into `main` and pushed. Style and content fine-tuning is deferred to later.

## Completed

- TID-1: merged into `main` and pushed.
- TID-2 first version (renders all of `data/ME.md`) was rejected by the developer on 2026-11-12: too verbose, dated style, too dry.
- TID-2 rework (2026-11-12):
  - `data/PROFILE.md` (new): short, hand-curated page content. `## Identity` (`- Key: Value`; `Name`, `Role`, `Tagline` feed the hero, other keys become contact items), `## Profile` (hero text), and further `##` sections, each rendered as a bento tile. All facts are taken from `data/ME.md`.
  - `app/resume.py`: parses `data/PROFILE.md`. `data/ME.md` is no longer shown on the page; it stays the LLM knowledge base.
  - `templates/index.html`: bento grid (hero, contact, one tile per section) and a floating chat widget (launcher button plus panel using the native HTML `popover` attribute, no JavaScript). Chat input is a disabled placeholder until TID-5.
  - `static/style.css`: dark ink-blue canvas with gradient glows, glassy tiles, gradient accents, staggered entrance animation, CSS-only hover/focus states, reduced-motion support. Grid: 4 columns, 2 below 64rem, 1 below 40rem. Tile spans are keyed on the section slug (`tile-in-numbers`, `tile-experience`, `tile-open-source`, `tile-toolbox`, `tile-education`); unknown sections get a default 2-column tile.
  - `static/fonts/`: self-hosted Geist (body, headings) and Geist Mono (labels, dates) variable fonts, OFL license included. Self-hosted to avoid sending visitor IPs to Google (GDPR). Replaced Archivo on developer request (2026-11-12).
  - Asset links in the template are root-relative (`/static/...`) instead of `url_for` absolute URLs, which failed in the VS Code built-in browser.
  - `tests/test_resume.py`, `README.md` (content files note).
- Dependencies: jinja2 3.1.6, markdown-it-py 4.3.0.

## Developer decisions for the rework (2026-11-12, via clarifying questions)

- Page content comes from a separate `data/PROFILE.md`; `data/ME.md` stays the full LLM knowledge base.
- Visual direction: bento grid. Tone: confident and warm, first person. Chat: floating widget.

## Verification (TID-2 rework, 2026-11-12)

- `uv run pytest`: 8 passed.
- `uv run ruff check .` and `uv run ruff format --check .`: pass.
- Geist font check: headless Edge screenshot at 1440px after the font change.
- Visual check with headless Edge: 1440px, 1000px, and a 390px iframe (measured `innerWidth` 390 = `scrollWidth` 390, no horizontal scrolling). Chat panel checked open at 1440px and 390px.
- `plan/PLAN.md`: unchanged.

## Open points for the developer

- PLAN.md TID-2 still says the page renders `data/ME.md` and the test checks the executive summary heading. This conflicts with the approved `PROFILE.md` approach. Proposed wording was given to the developer; the developer updates PLAN.md.
- Recording the `PROFILE.md` decision in `plan/DECISIONS.md` needs developer approval.
- Deferred by the developer: fine-tuning of the page style (font choice, e.g. Plus Jakarta Sans, Manrope, Space Grotesk, Sora were offered as more distinctive than Geist) and of the `data/PROFILE.md` copy, which is an agent-written draft.

## Blockers

None.

## Next action

Wait for the developer to assign the next task (TID-3 starts only on explicit instruction).
