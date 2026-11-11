# Decisions

## 2026-11-11 | Planning (pre-TID-1) | Tech stack: Python, FastAPI, vanilla JS

Decision: Build a single FastAPI application that serves both the resume page (Jinja2 template, `data/ME.md` rendered as Markdown) and the chat API. The frontend is plain HTML/CSS with a small vanilla JavaScript chat client; there is no separate frontend framework or build step. Dependencies are managed with `uv`.

Rationale: The developer is experienced in Python and prefers to avoid technologies with uncertainty. The scope (one page, one chat endpoint, one tool) does not justify a second service or language.

Approved by developer: yes

## 2026-11-11 | Planning (pre-TID-1) | LLM provider: OpenRouter

Decision: Use OpenRouter for LLM access through its OpenAI-compatible API (`openai` Python SDK with a custom `base_url`). The model is configurable and must support tool calling.

Rationale: Developer choice. OpenRouter allows switching models without code changes.

Approved by developer: yes

## 2026-11-11 | Planning (pre-TID-1) | Unknown-question notification: Gmail

Decision: When the twin cannot answer, the `record_unknown_question` tool emails the question to the developer through Gmail SMTP, authenticated with a Gmail App Password stored as a secret.

Rationale: Developer choice. No persistent storage is required, which also suits serverless hosting.

Approved by developer: yes

## 2026-11-11 | Planning (pre-TID-1) | Contact email may be disclosed

Decision: The twin may share the developer's email address with visitors.

Rationale: The address is already public on the CV.

Approved by developer: yes

## 2026-11-11 | Planning (pre-TID-1) | Hosting: Vercel (tentative)

Decision: Vercel is the preferred hosting target, using its Python runtime for FastAPI. This choice is tentative until the deployment task confirms that streaming responses and outbound Gmail SMTP work there. If they do not, the developer chooses an alternative host.

Rationale: The developer prefers Vercel but is unsure about it. The app is stateless, so it fits serverless hosting in principle.

Approved by developer: tentative, pending validation
