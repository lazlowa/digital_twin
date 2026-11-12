# State

## Current task

None. TID-6 (Hardening) was closed by the developer on 2026-11-12, merged into `main` and pushed.

## TID-6 (completed, merged)

- `app/config.py`, `.env.example`: `MAX_MESSAGE_CHARS` (2000), `MAX_HISTORY_MESSAGES` (40), `MAX_RESPONSE_TOKENS` (1000), `RATE_LIMIT_PER_MINUTE` (10), `RATE_LIMIT_PER_DAY` (100).
- `app/chat.py`: request validation returns 422 for empty or over-long histories and empty messages. Visitor messages are limited to `MAX_MESSAGE_CHARS`. Earlier twin replies in the history may be up to 8 x `MAX_RESPONSE_TOKENS` characters, because replies can be longer than visitor messages. Every model call sends `max_tokens=MAX_RESPONSE_TOKENS`. The `rate_limit` dependency runs on `/api/chat`.
- `app/ratelimit.py`: in-memory sliding-window limiter per client IP (`request.client.host`), with per-minute and per-day windows. Requests over a limit get 429 with `Retry-After`. Rejected requests are not counted; requests that fail validation are.
- `templates/index.html`, `app/main.py`: the textarea has `maxlength` set to the message limit, and the form carries the history limit.
- `static/chat.js`: sends at most the last 39 messages (odd, so the window starts with a visitor message), and shows specific messages for 429 and 422.
- `README.md`: limits section and the recommendation to set an OpenRouter spending limit.
- `tests/conftest.py` (resets the limiter), `tests/test_limits.py`.
- Decision recorded in `plan/DECISIONS.md` (2026-11-12, TID-6).

## Verification (TID-6, 2026-11-12)

- `uv run pytest`: 33 passed. `uv run ruff check .` and `uv run ruff format --check .`: pass. `node --check static/chat.js`: OK.
- Tests cover over-long message and history (422), a long earlier twin reply (200), malformed bodies and invalid JSON (422), 429 after `RATE_LIMIT_PER_MINUTE` requests with `Retry-After`, the `max_tokens` cap, and the minute and day windows with a fake clock.
- Live server: 10 invalid requests got 422, then 429 with `Retry-After: 59`, and a valid request was also blocked. The page renders `maxlength="2000"` and `data-max-history="40"`.
- The chat UI's 429/422 messages and the history trimming were checked with Node (syntax, trimming parity) but not in a browser.

## TID-5 (completed, merged)

- `static/chat.js` (vanilla JS, loaded with `defer`): keeps the history in memory and sends it to `/api/chat`. It reads the reply stream with `TextDecoderStream` and re-renders the reply with a minimal Markdown renderer on every chunk (paragraphs, lists, headings as bold, bold, italic, inline code, http(s)/mailto links; all other content is escaped). A typing indicator shows while waiting. Send is disabled while a reply is in progress or the input is empty. Enter sends, Shift+Enter adds a new line. On error it shows "Sorry, something went wrong. Please try again in a moment.", removes the failed question from the history, and puts it back into the input. The input is focused when the panel opens. Starter chips are removed after the first question.
- `templates/index.html`: client-side greeting, three starter questions, a textarea input, and the script tag.
- `static/style.css`: message bubbles, error style, typing dots, starter chips, an auto-growing textarea (`field-sizing: content`), and a larger panel (26rem x 40rem max).
- `app/chat.py`: the stream response sends `X-Content-Type-Options: nosniff`, because Chromium otherwise buffers the start of `text/plain` responses for MIME sniffing. Test added in `tests/test_chat.py`. Its effect could not be observed here (see the blocker).
- `tests/test_resume.py`: the page includes `/static/chat.js` and the file is served.
- Decision recorded in `plan/DECISIONS.md` (2026-11-12, TID-5).
- `app/chat.py` `TOOL_GUIDANCE` (TID-4 behaviour, found by the developer while testing TID-5): record each question and contact only once per conversation. The model cannot see earlier tool calls because the client history contains only visible text, so the rule states that its earlier replies are accurate evidence of recording. Developer chose a prompt rule over a code guard (2026-11-12).
- Mobile: the panel covers almost the whole screen at phone width. The developer accepted this as the standard mobile chat pattern (closable via the x button, Esc/back, or the launcher).

## Verification (TID-5, 2026-11-12)

- `uv run pytest`: 20 passed. `uv run ruff check .` and `uv run ruff format --check .`: pass. `node --check static/chat.js`: OK.
- Markdown renderer exercised in Node: lists, headings, bold, italic, code, links render; `<script>`, quotes, and `javascript:` links are escaped or left as text; `2*3*4` is not italicised.
- Headless Edge driven over CDP against the local server with the real OpenRouter API (scratch script, not in the repo):
  - The panel opens, the input is focused, and Send is disabled for empty input.
  - Starter chip -> reply rendered, chips removed. Send stayed disabled while the reply was pending, even with text in the input, and was enabled afterwards.
  - Follow-up sent with Enter: the 2nd request carried roles `user, assistant, user`, so earlier turns are sent as context. A reply rendered list/bold Markdown.
  - Whitespace-only input: Send disabled, no message added.
  - Simulated 502: the error message is shown, the question is restored to the input, and nothing extra is added to the history.
  - 390px mobile emulation: `scrollWidth` 390 = `innerWidth` 390; the panel fits (16-374 px).
- Developer check (Chrome and Edge, 2026-11-12): earlier context is used in follow-ups; phone emulation works (panel nearly full-screen, accepted); the reply appeared at once (see Later to-do).
- Duplicate recording, checked with the real model and email sending replaced by a log line (scratch harness): before the rule, "Did you record my email already?" sent a second contact email and the twin falsely said it had not saved the details. With the final rule: contact scenario 3/3 runs sent one email and answered truthfully; asking the same unanswerable question twice sent one email in 2/3 runs and two in 1/3.
- Streaming in the browser: the server streams (a Python client received 52 chunks over about 1.8 s), but headless Edge received each reply as a single network chunk. A minimal standalone Python server streaming 10 chunks 300 ms apart showed the same behaviour in Edge (one chunk after 3 s), so something on this machine buffers browser HTTP traffic. ESET Security (web access protection) is installed and is the likely cause, though this is not proven. `--no-proxy-server` did not help, and no system proxy is set.

## Completed

- TID-1: project scaffold.
- TID-2: the page renders `data/PROFILE.md` (short profile, bento grid, floating chat placeholder using the HTML `popover` attribute). `data/ME.md` is the LLM knowledge base and is not shown on the page. Self-hosted Geist and Geist Mono fonts.
- TID-3: `POST /api/chat` (`app/chat.py`) takes `{"messages": [{"role", "content"}, ...]}`, accepts only `user` and `assistant` roles, and streams the reply as plain text from OpenRouter (default model `anthropic/claude-haiku-5.5`). The system prompt is the quoted instruction block parsed from `plan/PLAN.md` at runtime, then `TOOL_GUIDANCE`, then the full `data/ME.md`. An OpenRouter error before streaming returns 502.
- TID-4:
  - `app/tools.py`: `record_unknown_question(question)` and `record_visitor_contact(email, name?, note?)`. Each emails `NOTIFY_TO` through `smtplib.SMTP_SSL` (port 465, `EMAIL_SMTP_SERVER`, `EMAIL_ADDRESS`, `EMAIL_APP_PASSWORD`) with the conversation transcript. Nothing is stored. SMTP errors and invalid calls are logged and return "Recording failed." to the model.
  - `app/chat.py`: both tools are offered on every request. The tool-call loop (at most 3 tool rounds) streams text, runs requested tools, returns the results to the model, and keeps streaming.
  - Chat panel privacy note (approved): "If the twin can't answer a question or you share your contact details, this conversation is forwarded to Laszlo by email."
- Settings: `.env.example` documents `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `EMAIL_SMTP_SERVER`, `EMAIL_ADDRESS`, `EMAIL_APP_PASSWORD`, `NOTIFY_TO`, and the optional, unused `PUSHOVER_USER` and `PUSHOVER_TOKEN`. The local `.env` (git-ignored) holds the developer's values.
- Decisions for TID-2 to TID-4 are recorded in `plan/DECISIONS.md`.

## Verification (TID-4, 2026-11-12)

- `uv run pytest`: 20 passed. `uv run ruff check .` and `uv run ruff format --check .`: pass.
- Manual checks (local server, real OpenRouter and Gmail SMTP):
  - "What is Laszlo's favourite dish?" -> "I don't know Laszlo's favourite dish, as that isn't something covered in his professional profile..." with a redirect to professional topics and no mention of recording. The developer received the "Digital twin: unanswered question" email.
  - "We are hiring a data platform architect. Would Laszlo be interested?" -> a profile summary, "I can't speak for Laszlo's interest...", and one offer to pass on an email address. "Great, I'm Jane Doe, you can reach me at jane.doe@example.com about the architect role." -> "Thank you, Jane. I've recorded your details..." The developer received the "Digital twin: new visitor contact" email.
- TID-3 manual check (earlier): replies stream incrementally (64 chunks over about 2.3 s). One answer misdated a role ("to present" instead of 07/2026); a second run was correct.

## Open points for the developer

- PLAN.md wording fixed by the agent with one-time developer permission (2026-11-12): TID-1 lists the `EMAIL_*` settings, TID-2 describes `data/PROFILE.md` and the bento page, and TID-4 says SMTP (Gmail) and "both tools". The quoted instruction block was not changed.
- Deferred: page style fine-tuning (font alternatives offered: Plus Jakarta Sans, Manrope, Space Grotesk, Sora) and review of the agent-written `data/PROFILE.md` copy.

## Blockers

None.

## Later to-do

- TID-7: behind Vercel the client IP must come from the proxy's forwarding header (`X-Forwarded-For` / `X-Real-IP`). Otherwise all visitors share one rate limit. Locally the direct connection address is used.
- Browser streaming: on the developer's machine, replies appear at once in Chrome and Edge, although the server streams (Python client: 52 chunks over about 1.8 s). A minimal standalone streaming server was also delivered as one chunk to headless Edge, so local buffering (likely ESET web access protection, not proven) is suspected. The developer deferred this. Re-check on the deployed app (TID-7) and in a browser without ESET filtering.
- Duplicate recording is reduced but not eliminated for repeated unanswerable questions (see verification). If it matters, consider a code guard.

## Next action

Wait for the developer to assign the next task (TID-7 starts only on explicit instruction).
