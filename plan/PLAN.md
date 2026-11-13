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
- `.env` is git-ignored, and `.env.example` documents `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `EMAIL_SMTP_SERVER`, `EMAIL_ADDRESS`, `EMAIL_APP_PASSWORD`, and `NOTIFY_TO`.
- `plan/STATE.md` is updated.

## TID-2 Resume page

### Description

Serve the single page at `GET /`. A Jinja2 template renders `data/PROFILE.md`, a short, hand-curated profile (Markdown to HTML), as a bento grid with the profile prominent at the top. `data/ME.md` remains the full knowledge base for the LLM and is not shown on the page. Add a modern, responsive layout using plain CSS, and a floating chat widget placeholder.

### Acceptance Criteria

- `GET /` returns HTML containing the rendered content of `data/PROFILE.md`, including the profile.
- The page is readable on desktop and mobile widths without horizontal scrolling.
- Changing `data/PROFILE.md` changes the page with no code changes.
- A test asserts that `GET /` returns `200` and contains the profile text.
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

Expose a `record_unknown_question(question: str)` tool to the LLM. Implement the tool-call loop: when the model calls the tool, execute it, return the result to the model, and continue streaming the final reply. The tool emails the question to `NOTIFY_TO` over SMTP (Gmail, using an App Password). If sending fails, the error is logged and the visitor still gets a reply. Additionally expose `record_visitor_contact(email: str, name: str | None, note: str | None)`. The twin offers it after it could not answer a question or when the visitor shows clear interest, without pushing. The contact details are emailed to `NOTIFY_TO`; nothing is stored. All notification emails include the conversation transcript. The chat panel shows a short privacy note about this.

### Acceptance Criteria

- The model is offered both tools on every chat request.
- A test with a mocked LLM that emits a tool call verifies that the tool runs with the question, the result goes back to the model, and the final reply is streamed.
- A test with mocked SMTP verifies the email recipient, subject, and body.
- A test verifies that an SMTP failure does not break the chat response.
- A manual check confirms that a question not covered by `ME.md` (for example, "What is Laszlo's favourite dish?") delivers an email and that the twin says it does not know. The result is recorded in `plan/STATE.md`.
- Lint and tests pass, and `plan/STATE.md` is updated.
- A test with mocked SMTP verifies the contact email: recipient, subject, and a body containing the email, name, note and transcript.
- A manual check confirms that sharing an email address in the chat delivers a contact email. The result is recorded in `plan/STATE.md`.

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

## TID-8 Fix Preview Deployments

### Description

Preview deployments shall be fully functioning. Decision has to be made, whether it works with the same model or a free model with higher restrictions.

### Acceptance Criteria

- Preview deployments have a working chatbot

## TID-9 Fix Email Notification

### Remarks from Agent

#### Issues

   - Several function instances can run at once, and each has its own memory.
   - Instances are frozen between requests and shut down after idling.
   - There are no background timers between requests, so nothing can "send every 30 minutes" from memory.
   - Vercel Cron could trigger a flush, but on the Hobby plan a cron job runs at most once a day, and it can land on a different instance than the one holding the questions.
   - Sending on shutdown isn't reliable either. Vercel documents a 500 ms shutdown window for Node.js functions; I don't know whether Python functions get one at all, and an email can't reliably be sent in that time. A crash loses everything regardless.

#### Proposed

Proposed solution: a small external store, for example Upstash Redis through the Vercel Marketplace, which has a free tier:
   - The contact cap becomes a per-IP counter with an expiry, for example 3 per day.
   - Unanswered questions are appended to a shared list.
   - The flush runs whenever a chat request finds the oldest stored question older than 30 minutes, plus a daily Vercel Cron as a backstop.
   - Nothing is lost on rollout or crash, so no shutdown hook is needed.

#### Decision

This task is now on-hold for further evaluation and rework.

### Description

Contact registration shall have only one notification per email. This means that one visitor might want to register multiple emails, should the visitor register them in one message, then
it one notification shall be created. However, if the visitor wants to register more contact in separate messages, then for each message, there shall be a notification. As of now,
I don't believe that a guard needs to be in place to detect, if a notification is already sent for a specific email i.e., if visitor sends in message 1 "a@b.com" and in message 2
"a@b.com, c@b.com", then it is ok to include "a@b.com" again in the notification. However, there should be a hard cap of 3 contact notification per visitor. I dont see any reason to have more.
If the cap reached, the agent shall respond with a gentle message.

On the other hand, unanswerable questions shall be collected across all visitors. Then one notification email per 30 minutes (configurable) shall be emitted (flush). Notification
shall as well be sent before shutting down to avoid losing questions in case of a crash or rollout.

### Acceptance Criteria

- Contact notification hard cap of 3 is introduced (number shall be configurable, but default is 3)
- Upon reaching the cap, the agent formulates a gentle response about not being able to send more message
- Unanswerable questions are collected and notification sent on regular base not on event based

## TID-10 Style Polishing

### Description

Based on directly prompted instructions, multiple style variants shall be evaluated. Some aspects of the shown contents shall be refactored as well.

### Acceptance Criteria

- developer accepts the changes

## TID-11 Remove contact notification

### Description

After some testing, I realized that allowing the visitor to register an email and then sending a notification is not necessary. If the visitor wants
to contact, the email address is right away on the side. Hence this task is about removing the entire email registration and notification functionality.
The notification on unanswerable questions shall remain intact.

### Acceptance Criteria

- Visitor prompting for contact with email address shall be gently pointed to the contact panel, so they can contact me via email
- No email registration and tool usage on email provision shall take place
- Unanswerable questions shall still emit notification email each time with a cap of 10

## TID-12 Impressum

### Description

Appearently, there is a regulation in EU to provide an impressum and privacy note. 
We already provide a privacy note on the chat interface, however it shall be checked, whether that fulfills all regulation
This task contains the following steps:

1) Create a footer on the side
2) Move the build id from the badge into the footer.
3) Research on the internet, whether and how it is required to have a privacy note and an impressum, prompt the developer with your response before moving to the next step.
4) If it is regulatory requirement, give proposals for both impressum and privacy note.
5) Check, if the legal text can be in English and the side can rely on browser's translate functionality

If impressum is required, the address will be left out for now for privacy reasons.

Since this is a SPA, how the impressum text will blend in is subject of discussion. Give the developer proposals and an option to choose.

Footer shall contain copyright information.

Build id notice shall link back to the specific commit.

### Acceptance Criteria

- Footer implemented
- No more build badge, the build id moved to the footer (displayed discretely)
- Eventually, privacy note and impressum text is on the page in English
- Amber preview badge shall remain intact
- Privacy note and impressum texts shall be maintained in their own file in `data` folder
- The side shall load the note texts at startup


## TID-13 Fixing Impressum

### Description

Impressum and privacy notice did not have any address. This task is about fixing it. The address is:

Laszlo Anka
c/o Autorenglück #56130
Albert-Einstein-Straße 47
02977 Hoyerswerda

### Acceptance Criteria

- Address is now in impressum and in privacy notice


## TID-14 Content Fine-Tuning

### Description

Some more content optimization is necessary.

Findings:
- § 18 (1) MStV is still on the Legal notice. It’s harmless, but probably unnecessary unless you publish editorial content.
- No Open Graph tags, so a link shared on LinkedIn still gets no proper preview. This is the most useful remaining fix before your announcement post.
- No favicon declared (new finding). Browser tabs and bookmarks show a generic icon. A simple “LA” icon in your accent colors would fit.
- Meta description is still just the tagline.
- Privacy details: the model provider is still unnamed, and you could name the relevant data protection authority.

Additionally:
- Add CV download
- open to work with date and details (relocation etc.)

Tasks for the developer
- Extend profile with concrete projects and topics/tasks
- Add home projects, hobbies
- Adapt profile texts


### Acceptance Criteria

- Findings fixed.
