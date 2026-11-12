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

## 2026-11-12 | TID-2 | Page content comes from data/PROFILE.md

Decision: The page renders a short, hand-curated `data/PROFILE.md` (identity, profile, and one bento tile per `##` section). `data/ME.md` remains the full knowledge base for the LLM and is not shown on the page.

Rationale: The first version rendered all of `ME.md` and was too verbose and dry for visitors. A separate file keeps the page short while the LLM keeps full detail.

Approved by developer: yes

## 2026-11-12 | TID-2 | Page design: bento grid, floating chat widget

Decision: Dark bento-grid layout with a confident, warm first-person tone. The chat is a floating widget (launcher button plus popover panel). Fonts are Geist and Geist Mono, self-hosted.

Rationale: Developer choices after the first design was judged dated. Self-hosting fonts avoids sending visitor IPs to Google. Style and copy fine-tuning is deferred.

Approved by developer: yes

## 2026-11-12 | TID-3 | Default model: anthropic/claude-haiku-5.5

Decision: `OPENROUTER_MODEL` defaults to `anthropic/claude-haiku-5.5` (USD 0.10 / 0.50 per million input / output tokens on OpenRouter at the time of the decision, supports tool calling).

Rationale: Low cost per reply, tool calling for TID-4, and reliable instruction following. The model can be changed through settings.

Approved by developer: yes

## 2026-11-12 | TID-3 | System prompt instructions are read from plan/PLAN.md

Decision: The chat endpoint parses the quoted instruction block from `plan/PLAN.md` at runtime and appends the full `data/ME.md`. `plan/` must therefore be deployed with the app.

Rationale: Developer choice for a single source of the instructions.

Approved by developer: yes

## 2026-11-12 | TID-3 | Chat API contract

Decision: `POST /api/chat` accepts `{"messages": [{"role", "content"}]}`, streams the reply as plain text chunks (`text/plain`), and accepts only the `user` and `assistant` roles from clients. No reply-language rule is added to the prompt.

Rationale: Plain text is the simplest stream for a vanilla JavaScript client. Rejecting client `system` messages keeps visitors from overriding the instructions.

Approved by developer: yes

## 2026-11-12 | TID-3 | Notification settings use generic email names

Decision: Refines "Unknown-question notification: Gmail" (2026-11-11). Email remains the notification channel, configured as `EMAIL_SMTP_SERVER` (default `smtp.gmail.com`), `EMAIL_ADDRESS`, `EMAIL_APP_PASSWORD`, and `NOTIFY_TO` instead of `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD`. `PUSHOVER_USER` and `PUSHOVER_TOKEN` are kept as optional, unused settings for possible later use.

Rationale: Matches the developer's existing configuration values and keeps the SMTP server configurable.

Approved by developer: yes

## 2026-11-12 | TID-4 | Unknown-question handling

Decision: The twin records every question it cannot answer from `data/ME.md`, including unrelated ones, and still steers unrelated conversations back to professional topics. It tells the visitor only that it does not know, without mentioning the notification. Notification emails include the question and the full conversation transcript.

Rationale: Developer choice. The transcript gives context for a follow-up; recording everything gives a complete picture of what visitors ask.

Approved by developer: yes

## 2026-11-12 | TID-4 | Visitor contact tool and privacy note

Decision: Add a `record_visitor_contact(email, name?, note?)` tool. The twin offers it after it could not answer a question or when the visitor shows clear interest, without pushing. The details and the transcript are emailed to `NOTIFY_TO` immediately; nothing is stored. The chat panel shows a one-line privacy note about forwarding by email, with wording approved by the developer.

Rationale: Lets the developer follow up with interested visitors while the app stays stateless. The note informs visitors that conversations may be forwarded.

Approved by developer: yes
