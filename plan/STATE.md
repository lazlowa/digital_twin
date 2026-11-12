# State

## Current task

None. TID-3 (Chat backend) was closed by the developer on 2026-11-12, merged into `main` and pushed.

## Completed

- TID-1: merged into `main` and pushed.
- TID-2: merged into `main` and pushed. The page renders `data/PROFILE.md` (short profile, bento grid, floating chat placeholder using the HTML `popover` attribute). `data/ME.md` is the LLM knowledge base and is not shown on the page. Self-hosted Geist and Geist Mono fonts.
- TID-3: merged into `main` and pushed.
  - `app/chat.py`: `POST /api/chat` with body `{"messages": [{"role", "content"}, ...]}`. Only `user` and `assistant` roles are accepted (422 otherwise). The system prompt is the quoted instruction block parsed from `plan/PLAN.md` at runtime plus the full `data/ME.md`, both read per request. The reply streams as plain text from OpenRouter (`AsyncOpenAI`, `stream=True`). An OpenRouter error before streaming returns 502. The client comes from the `get_client` dependency, which tests override.
  - `app/config.py`, `.env.example`: default model `anthropic/claude-haiku-5.5`. Notification settings `EMAIL_SMTP_SERVER` (default `smtp.gmail.com`), `EMAIL_ADDRESS`, `EMAIL_APP_PASSWORD`, `NOTIFY_TO`; `PUSHOVER_USER` and `PUSHOVER_TOKEN` are documented as optional and unused.
  - `tests/test_chat.py`. Dependency: openai 3.49.0.
- Local `.env` (git-ignored) holds the developer's values, including `NOTIFY_TO` (set to the sender address).
- Decisions for TID-2 and TID-3 are recorded in `plan/DECISIONS.md`.

## Verification (TID-3, 2026-11-12)

- `uv run pytest`: 12 passed. `uv run ruff check .` and `uv run ruff format --check .`: pass.
- Manual OpenRouter check (`anthropic/claude-haiku-5.5`, local server): HTTP 200 `text/plain`, 64 chunks between 2.05 s and 4.39 s, so the reply streams incrementally.
  - Question: "What experience do you have with Kafka and event-driven systems?"
  - Answer (summary): a first-person reply covering the event-driven data labeling pipeline (Python/FastAPI, Kafka, MongoDB on Kubernetes, 10,000+ requests per day), the data-asset discovery platform (Kafka, Neo4j, Java/Spring Boot on AKS), pypz with its `kafka_io` plugin, and RabbitMQ/AMQP and Azure Service Bus, ending with a follow-up question.
  - Finding: that answer dated the labeling pipeline "02/2024 to present" instead of 02/2024 - 07/2026 (`data/ME.md` line 103). A second run ("What did you build with Kafka?", 47 chunks, via the PowerShell streaming request) gave the correct dates.
- `plan/PLAN.md`: unchanged.

## Open points for the developer

- PLAN.md TID-2 still says the page renders `data/ME.md`; TID-1 and TID-4 still name `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD`. The developer may update the wording.
- Deferred: page style fine-tuning (font alternatives offered: Plus Jakarta Sans, Manrope, Space Grotesk, Sora) and review of the agent-written `data/PROFILE.md` copy.
- Until TID-4, the instructions mention a tool that does not exist yet, so the twin may claim to record a question without doing so.

## Blockers

None.

## Next action

Wait for the developer to assign the next task (TID-4 starts only on explicit instruction).
