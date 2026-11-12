from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.chat import router as chat_router
from app.config import settings
from app.resume import load_resume

ROOT = Path(__file__).resolve().parent.parent

app = FastAPI(title="Digital Twin")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
templates = Jinja2Templates(directory=ROOT / "templates")
app.include_router(chat_router)


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    context = {"resume": load_resume(), "settings": settings}
    return templates.TemplateResponse(request, "index.html", context)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
