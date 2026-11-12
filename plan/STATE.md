# State

## Current task

None. TID-7 (Deployment to Vercel) was closed by the developer on 2026-11-12, merged into `main` and pushed. All planned tasks (TID-1 to TID-7) are complete. The site is live at https://lazlowa.space.

## TID-7 (completed, merged)

- Vercel project `digital-twin` (scope `lazlowas`) created and linked (`.vercel/` and `.env.local` are git-ignored). Production URL: https://digital-twin-sigma-beige.vercel.app
- `vercel.json`: `framework: fastapi` (required: without it the CLI-created project used the "Other" preset and served only static files, so `/` returned 404), `regions: ["fra1"]`, and a permanent redirect from `www.lazlowa.space` to `https://lazlowa.space`.
- `app/ratelimit.py`, `app/config.py`, `.env.example`: with `TRUST_PROXY_HEADERS=true` the client IP comes from `X-Real-IP`, then the first `X-Forwarded-For` entry; otherwise the direct connection address. Test in `tests/test_limits.py`.
- Production environment variables added from `.env` without printing values: `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `EMAIL_SMTP_SERVER`, `EMAIL_ADDRESS`, `EMAIL_APP_PASSWORD`, `NOTIFY_TO`, `TRUST_PROXY_HEADERS=true`. Pushover values skipped.
- GitHub repository connected to the project (`vercel git connect`, after the developer added the GitHub Login Connection and installed the Vercel app on the repo). Pushes to `main` deploy to production.
- Domains `lazlowa.space` and `www.lazlowa.space`: Namecheap DNS set by the developer (`A @ 216.198.79.1`, `A @ 64.29.17.1`, `CNAME www 4e2a39c3b465bb55.vercel-dns-017.com.`). Vercel reports both configured correctly and issued certificates for both automatically (90 days, auto-renew).
- `README.md`: deployment section. Decision recorded in `plan/DECISIONS.md` (2026-11-12, TID-7).

## Verification (TID-7, 2026-11-12)

- `uv run pytest`: 34 passed. `uv run ruff check .` and `uv run ruff format --check .`: pass.
- Build: Python 3.12 (`.python-version`), dependencies from `uv.lock`, one function `fastapi` (15.5 MB) in `fra1`.
- `GET /` renders the profile page; `/health` and static files return 200.
- Streaming on Vercel (Python client): 200 `text/plain` with `nosniff`, 28 chunks between 1.45 s and 3.62 s.
- Gmail SMTP from Vercel: "What is Laszlo's favourite dish? (deployment test)" -> "I'm sorry, I don't know Laszlo's favourite dish...". Logs show two OpenRouter calls (tool round) and no email error. The developer confirmed the email arrived.
- Developer check (2026-11-12): after a router restart, https://lazlowa.space works over home Wi-Fi, and chat replies stream properly in the browser. The earlier all-at-once rendering was local to the developer's machine and network, not the app.
- Custom domain (requests pinned to 216.198.79.1 because the local router still cached the old parking IP 192.64.119.46): `https://lazlowa.space/health` 200 with a valid certificate, `/` renders the page, `https://www.lazlowa.space/about` returns 308 to `https://lazlowa.space/about`, and chat streams (12 chunks between 1.61 s and 2.42 s).

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

## On hold

- TID-9 (Fix Email Notification): put on hold by the developer (2026-11-12) after the agent's review. Open concerns: a per-visitor hard cap and periodic batching of unanswered questions need state that survives between requests, which in-memory storage on Vercel serverless cannot guarantee (several instances, freezing, no background timers, Hobby cron at most daily, no reliable shutdown hook for sending email). Proposed: a small external store (for example Upstash Redis) with a per-IP contact counter, a shared question list, a lazy flush on requests and a daily cron backstop. This would reverse the "nothing is stored" decisions. Also open: how a visitor is identified (IP or conversation), the cap period, and whether batch emails include transcripts.

## Later to-do

- Preview deployments have no environment variables (production only), so chat fails on previews. Add them to the preview environment if needed.
- Optional: GitHub Actions CI (pytest, ruff) before deploys; not part of the plan.
- Duplicate recording is reduced but not eliminated for repeated unanswerable questions (see verification). If it matters, consider a code guard.

## Next action

New tasks TID-8 (preview deployments), TID-9 (on hold) and TID-10 (style polishing) were added to `plan/PLAN.md` by the developer. Wait for the developer to assign the next task.
