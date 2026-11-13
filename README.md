# Digital Twin

Single-page website with a resume and a chat, where an LLM answers visitors'
professional questions on the owner's behalf.

Stack: Python 3.12, FastAPI, uv.

Content: `data/PROFILE.md` is the short profile shown on the page (each `##`
section becomes a tile). `data/ME.md` is the full knowledge base for the LLM.
`data/LEGAL.md` and `data/PRIVACY.md` are served at `/legal` and `/privacy`.

CV: with `CV_DOWNLOAD_ENABLED=true` the "Download CV" button links the highest
`static/CV_v<N>.pdf`, and the twin mentions it. To update,
add the new file with the next number (for example `CV_v2.pdf`) and delete the
old one; the new URL avoids cached copies. Visitors save it as
`ANKA_Laszlo_CV.pdf`.

## Setup

```sh
uv sync
cp .env.example .env   # then fill in the values
```

## Limits and costs

`POST /api/chat` rejects over-long messages and histories (`422`) and limits
requests per client IP (`429`). Unanswered-question emails are capped per client
IP per 24 hours (default 10); further questions are not emailed. The limits and
the maximum response length are configurable in `.env` (see `.env.example`).
Rate limits and the email cap are counted in memory per server process, so on
serverless hosting they are approximate.

Set a spending limit for the API key in OpenRouter
(<https://openrouter.ai/keys>) so that abuse cannot cause unbounded
costs.

## Run

```sh
uv run uvicorn app.main:app --reload
```

Health check: <http://127.0.0.1:8000/health>

## Checks

```sh
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

## Deployment (Vercel)

The app runs on Vercel as a single Python function (FastAPI preset, region
`fra1`), configured in `vercel.json`. `plan/PLAN.md` must be deployed with the
app because the LLM instructions are read from it.

1. Link the project: `vercel link --project digital-twin`.
2. Add the variables from `.env.example` to the production and preview
   environments (`vercel env add NAME --environment production,preview`), with
   `TRUST_PROXY_HEADERS=true`.
3. Deploy: pushes to `main` deploy to production through the Git integration,
   pushes to other branches create preview deployments. `vercel deploy --prod`
   deploys the local working tree manually. Notification emails sent from
   previews have a `[Preview]` subject prefix.
4. Custom domain: `lazlowa.space` with an `A` record to Vercel and
   `www.lazlowa.space` as a `CNAME` (see `vercel domains verify <domain>`);
   `vercel.json` redirects `www` to the apex domain.
