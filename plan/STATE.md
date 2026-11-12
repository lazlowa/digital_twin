# State

## Current task

None. TID-4 was closed by the developer on 2026-11-12, merged into `main` and pushed, together with the developer's PLAN.md edit that extends TID-4.

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

- PLAN.md TID-2 still says the page renders `data/ME.md`; TID-1 and TID-4 still name `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD`. The developer may update the wording.
- Deferred: page style fine-tuning (font alternatives offered: Plus Jakarta Sans, Manrope, Space Grotesk, Sora) and review of the agent-written `data/PROFILE.md` copy.

## Blockers

None.

## Next action

Wait for the developer to assign the next task (TID-5 starts only on explicit instruction).
