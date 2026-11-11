# Project Overview

Build a digital twin of the user as a single-page web application.
The page shall contain the resume of the user with an executive summary about the skills and competencies.
The page shall contain a chat interface, where the visitor can ask professional questions about the user.
On the other side an LLM will be configured, which shall answer those questions according to the following instructions:

"
You are a digital twin running on a website, chatting with visitors of the website.
You represent the person who's website you are on.
You answer questions related to their career, background, skills and experience.

Rules:

- Engage with the user.
- Be professional and engaging, as if talking to future employer who came across the website.
- Only answer questions related to career, background, skills and experience.
- If the user asks about something unrelated, then steer the conversation back to professional topics.
- Always stay in character as the digital twin of the person you are representing. Represent the person.

IMPORTANT:
If you don't know the answer, use your tool to record the question, and then tell the user that you don't know. Never make up an answer.
"

## Terms

- user/developer: the subject of the digital twin project
- visitor: the person visiting the digital twin side and asking questions

# Tasks

IMPORTANT - before executing a task, always ask clarifying questions, if you don't know or understand something, engage in constructive
discussion, if you see improvement potentials related to tasks.

For each task, start by creating a corresponding branch and work on the specific task in that branch.

## TID-1 Project scaffold

### Description

Set up the Python project with `uv`: `pyproject.toml`, a FastAPI app in `app/`, settings loaded with `pydantic-settings` from environment variables or a `.env` file, `ruff` for lint and format, and `pytest`. Add `.gitignore` (excluding `.env`), `.env.example` listing all required variables, and a concise README with setup and run instructions.

### Acceptance Criteria

- `uv sync` installs all dependencies.
- `uv run uvicorn app.main:app` starts the server, and `GET /health` returns `200` with `{"status": "ok"}`.
- `uv run ruff check .` and `uv run ruff format --check .` pass.
- `uv run pytest` passes, with at least one test covering `/health`.
- `.env` is git-ignored, and `.env.example` documents `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD`, and `NOTIFY_TO`.
- `plan/STATE.md` is updated.

## TID-2 Resume page

### Description

Serve the single page at `GET /`. A Jinja2 template renders `data/ME.md` (Markdown to HTML) as the resume, with the executive summary prominent at the top. Add a clean, responsive layout using plain CSS, and leave a placeholder region for the chat panel.

### Acceptance Criteria

- `GET /` returns HTML containing the rendered content of `data/ME.md`, including the executive summary.
- The page is readable on desktop and mobile widths without horizontal scrolling.
- Changing `data/ME.md` changes the page with no code changes.
- A test asserts that `GET /` returns `200` and contains the executive summary heading.
- Lint and tests pass, and `plan/STATE.md` is updated.

## TID-3 Chat backend

### Description

Implement `POST /api/chat`. It accepts the conversation history (a list of `{role, content}` messages) from the client and streams the assistant reply back. The system prompt is the instruction text from `plan/PLAN.md` combined with the full content of `data/ME.md`. Calls go to OpenRouter through the `openai` SDK, with the model taken from settings. The server stays stateless.

### Acceptance Criteria

- `POST /api/chat` streams the reply incrementally rather than as one final response.
- The system prompt contains the PLAN.md instructions and the content of `data/ME.md`. A test verifies this with a mocked LLM client.
- A test with a mocked client verifies that the streamed output is passed through to the response.
- A manual check against the real OpenRouter API returns a sensible answer to a career question. The question and the answer are recorded in `plan/STATE.md`.
- Lint and tests pass, and `plan/STATE.md` is updated.

## TID-4 Unknown-question tool with Gmail notification

### Description

Expose a `record_unknown_question(question: str)` tool to the LLM. Implement the tool-call loop: when the model calls the tool, execute it, return the result to the model, and continue streaming the final reply. The tool emails the question to `NOTIFY_TO` through Gmail SMTP using an App Password. If sending fails, the error is logged and the visitor still gets a reply.

### Acceptance Criteria

- The model is offered the tool on every chat request.
- A test with a mocked LLM that emits a tool call verifies that the tool runs with the question, the result goes back to the model, and the final reply is streamed.
- A test with mocked SMTP verifies the email recipient, subject, and body.
- A test verifies that an SMTP failure does not break the chat response.
- A manual check confirms that a question not covered by `ME.md` (for example, "What is Laszlo's favourite dish?") delivers an email and that the twin says it does not know. The result is recorded in `plan/STATE.md`.
- Lint and tests pass, and `plan/STATE.md` is updated.

## TID-5 Chat UI

### Description

Add the chat panel to the page with vanilla JavaScript: a message list, an input, and a send button. The client keeps the conversation history in memory, sends it to `/api/chat`, and renders the streamed reply as it arrives. It shows a pending state while waiting and a readable error message on failure.

### Acceptance Criteria

- A visitor can hold a multi-turn conversation, and earlier turns are sent as context.
- Reply text appears incrementally while streaming.
- The send button is disabled while a reply is in progress, and empty messages cannot be sent.
- A backend error shows a user-facing error message instead of failing silently.
- The panel works at mobile width.
- A manual browser check is done and recorded in `plan/STATE.md`, and `plan/STATE.md` is updated.

## TID-6 Hardening

### Description

Protect the public endpoint against abuse and cost. Add limits on message length, number of messages in the history, and response tokens. Add simple per-IP rate limiting, and reject malformed input with clear errors.

### Acceptance Criteria

- Over-long messages and over-long histories are rejected with `4xx`. Tests cover both.
- Requests above the rate limit receive `429`. A test covers this.
- Malformed request bodies return `422`.
- The limits are configurable through settings and documented in `.env.example`.
- The README recommends setting a spending limit in OpenRouter.
- Lint and tests pass, and `plan/STATE.md` is updated.

## TID-7 Deployment to Vercel

### Description

Deploy the FastAPI app to Vercel using its Python runtime. Configure secrets as Vercel environment variables. Validate the two open risks: streaming responses, and outbound Gmail SMTP from Vercel functions. If either one does not work, stop and report findings and alternatives to the developer before changing hosts.

### Acceptance Criteria

- The app is reachable at a Vercel URL, and `GET /` renders the resume.
- Chat replies stream incrementally in the deployed app.
- An unknown question asked on the deployed app delivers an email.
- No secrets are committed. All secrets are configured in Vercel.
- The README documents deployment steps.
- The Vercel hosting decision in `plan/DECISIONS.md` is confirmed or superseded, with developer approval.
- `plan/STATE.md` is updated.

