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

## 2026-11-12 | TID-5 | Chat UI behaviour

Decision: Replies are rendered by a small built-in Markdown renderer in vanilla JavaScript (paragraphs, bold, italic, lists, links, inline code), escaping all other content. On first open the panel shows a client-side greeting and three clickable starter questions; the greeting is not sent to the model. The conversation is kept in memory only, so a reload starts a new conversation.

Rationale: Model replies use Markdown, and a small renderer avoids new dependencies while staying safe. Starter questions lower the barrier to start. Memory-only history follows PLAN.md and stores nothing in the browser.

Approved by developer: yes

## 2026-11-12 | TID-6 | Limits and rate limiting

Decision: Default limits are 2,000 characters per message, 40 messages of history, 1,000 response tokens, and 10 requests per minute and 100 per day per IP, all configurable through settings. The rate limit is an in-memory sliding-window counter without a new dependency. Notification emails have no extra cap beyond the per-IP request limit. Locally the client IP is the direct connection address; trusting a proxy's forwarding header is decided in TID-7.

Rationale: Moderate limits keep normal conversations unaffected while bounding cost per visitor. In-memory counting is simple and sufficient as abuse protection together with an OpenRouter spending limit, although it is only approximate on serverless hosting.

Approved by developer: yes

## 2026-11-12 | TID-7 | Vercel deployment setup

Decision: Vercel project `digital-twin`, linked to the GitHub repository through the Git integration (pushes to `main` deploy to production, other branches get previews). Secrets are copied by the agent from the local `.env` into Vercel environment variables with the CLI, without printing them; the unused Pushover values are skipped. The function runs in Frankfurt (`fra1`). The site is served at the custom domain `lazlowa.space` (DNS at Namecheap), with `www.lazlowa.space` redirecting to it.

Rationale: Automatic deploys keep `main` and production in sync. Frankfurt is close to the expected European visitors.

Approved by developer: yes

## 2026-11-12 | TID-7 | Hosting on Vercel confirmed

Decision: Confirms "Hosting: Vercel (tentative)" (2026-11-11). The app is hosted on Vercel and served at https://lazlowa.space.

Rationale: Both open risks were validated on the deployed app: responses stream incrementally (12 to 28 chunks per reply, measured with a Python client via the Vercel URL and the custom domain), and outbound Gmail SMTP works from the Vercel function (the notification email arrived).

Approved by developer: yes (by instructing to conclude TID-7)

## 2026-11-12 | TID-8 | Preview deployments use the production configuration

Decision: Preview deployments get the same environment variables as production in the Vercel Preview environment, including the same model and the same OpenRouter API key, with the default rate limits. Notification emails sent from previews have a `[Preview]` subject prefix, based on `VERCEL_ENV`.

Rationale: Previews then test exactly what production runs. Previews are behind Vercel Authentication, so only the developer uses them, and a separate key or spending limit is not needed. The prefix keeps preview test emails apart from real ones.

Approved by developer: yes

## 2026-11-12 | TID-8 | Build and preview badges

Decision: Every Vercel deployment shows a small build badge with the short commit hash (`VERCEL_GIT_COMMIT_SHA`) in the top-left corner, including production. Preview deployments additionally show an amber "Preview" badge. No badges are shown locally.

Rationale: The developer can see at a glance which commit a deployment runs and whether it is a preview.

Approved by developer: yes

## 2026-11-12 | TID-11 | Visitor contact tool removed

Decision: Supersedes "Visitor contact tool and privacy note" (2026-11-12, TID-4). The `record_visitor_contact` tool is removed. When a visitor wants to get in touch or offers contact details, the twin shares the email address from `data/ME.md` and mentions the contact panel, which lists the email address and LinkedIn profile. The twin does not speak for Laszlo about his interest, availability or reaction. The unknown-question tool stays.

Rationale: Developer choice after testing. The email address is already on the page, so collecting visitor contacts adds no value, and Laszlo answers for himself.

Approved by developer: yes

## 2026-11-12 | TID-11 | Cap on unanswered-question emails

Decision: Unanswered-question emails are capped per client IP per 24 hours by `MAX_QUESTION_EMAILS_PER_DAY` (default 10), counted in memory with the existing rate limiter. Over the cap the email is skipped silently; the twin still says it does not know and the visitor is not told. A limit of 0 blocks all emails.

Rationale: Prevents abuse of the notification email. In-memory counting is approximate on serverless hosting, which the developer accepted.

Approved by developer: yes

## 2026-11-12 | TID-10 | Page content: Highlights instead of In Numbers and Open Source

Decision: The "In Numbers" and "Open Source" panels are removed from the page. A full-width "Highlights" panel follows the profile, hand-written in `data/PROFILE.md` (not parsed from `data/ME.md`): first person, bold titles, key figures emphasised, and a link to pypz. The business unit where pypz became the standard is deliberately not named.

Rationale: The developer found both panels thin with a single open-source project. Keeping the page copy in `PROFILE.md` follows "Page content comes from data/PROFILE.md" (2026-11-12, TID-2): the page needs short text, while `ME.md` stays detailed for the LLM.

Approved by developer: yes

## 2026-11-12 | TID-10 | Public repository and project section in ME.md

Decision: The repository https://github.com/lazlowa/digital_twin is public, and the page links to it in the contact panel. `data/ME.md` describes this website as a project: what it is, its purpose (showing how Laszlo builds products with AI-assisted development), the roles ("Laszlo wrote the plan, made every decision and reviewed every change; an AI coding agent (Claude Code) wrote the code"), the technology, the workflow and the skills it demonstrates, without a timeline.

Rationale: The project's purpose is to show recruiters the AI-assisted way of working, and the public plan, state and decision files make that visible. No secrets were found in the history, and Vercel Git Fork Protection is enabled.

Approved by developer: yes

## 2026-11-12 | TID-11 | Chat privacy note states the purpose

Decision: The chat panel note reads "If the twin can't answer a question, this conversation is emailed to Laszlo so he can improve its answers." It replaces the TID-4 wording, which also mentioned shared contact details. The full privacy notice is part of TID-12.

Rationale: Visitors should learn why their conversation is forwarded, not only that it is.

Approved by developer: yes

## 2026-11-13 | TID-12 | Legal notice (Impressum) without postal address for now

Decision: The site gets a legal notice (Impressum) in English with name and email. The postal address is left out for now for privacy reasons and will be added later; a c/o address or a mail-box service are the options considered instead of the home address.

Rationale: The research in TID-12 step 3 found that § 18 Abs. 1 MStV very likely applies, because the site is not exclusively personal, and it requires a serviceable postal address. The developer accepts that the notice is incomplete until the address is added. English is acceptable because the whole site is in English.

Approved by developer: yes

## 2026-11-13 | TID-12 | Full privacy notice in English

Decision: The site gets a full GDPR privacy notice in English covering the controller, hosting and server logs, in-memory abuse limits, chat processing through OpenRouter and the model provider, email forwarding of unanswered questions, transfers outside the EU, retention and visitor rights. The chat panel note stays as the short first layer. Placement of both texts is decided in step 4.

Rationale: The research in TID-12 step 3 found that the GDPR household exemption does not cover a public professional website, and the chat note alone does not contain the information Art. 13 GDPR requires.

Approved by developer: yes

## 2026-11-13 | TID-13 | Postal address via address service

Decision: Supersedes "Legal notice (Impressum) without postal address for now" (2026-11-13, TID-12). The legal notice and the privacy notice ("Who is responsible") give the postal address "Laszlo Anka, c/o Autorenglück #56130, Albert-Einstein-Straße 47, 02977 Hoyerswerda, Germany", an address service with a signed power of post and service (Post- und Zustellungsvollmacht).

Rationale: Completes the legal notice with a serviceable address, as § 18 Abs. 1 MStV requires, while keeping the home address private. The provider's terms grant the power of service and state that court and lawyer mail is forwarded without delay.

Approved by developer: yes
