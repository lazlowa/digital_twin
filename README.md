# Digital Twin

Single-page website with a resume and a chat, where an LLM answers visitors'
professional questions on the owner's behalf.

Stack: Python 3.12, FastAPI, uv.

## Setup

```sh
uv sync
cp .env.example .env   # then fill in the values
```

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
