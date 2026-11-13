from datetime import date
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.chat import router as chat_router
from app.config import settings
from app.resume import find_cv, load_page, load_resume

ROOT = Path(__file__).resolve().parent.parent

app = FastAPI(title="Digital Twin")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
templates = Jinja2Templates(directory=ROOT / "templates")
app.include_router(chat_router)


def page_context(**extra) -> dict:
    return {
        "resume": load_resume(),
        "settings": settings,
        "year": date.today().year,
        **extra,
    }


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    context = page_context(cv=find_cv() if settings.cv_download_enabled else None)
    return templates.TemplateResponse(request, "index.html", context)


@app.get("/legal", response_class=HTMLResponse)
def legal(request: Request) -> HTMLResponse:
    context = page_context(title="Legal notice", html=load_page("LEGAL.md"))
    return templates.TemplateResponse(request, "page.html", context)


@app.get("/privacy", response_class=HTMLResponse)
def privacy(request: Request) -> HTMLResponse:
    context = page_context(title="Privacy", html=load_page("PRIVACY.md"))
    return templates.TemplateResponse(request, "page.html", context)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
