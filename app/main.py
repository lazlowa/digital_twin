from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.chat import router as chat_router
from app.config import settings
from app.resume import DATA_DIR, find_cv, load_page, load_resume

ROOT = Path(__file__).resolve().parent.parent
CV_DOWNLOAD_NAME = "ANKA_Laszlo_CV.pdf"

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


@app.get("/cv")
def cv() -> FileResponse:
    # Served by the app, not as a static file, so the saved file name comes from
    # this header (Vercel names static files after their path) and the flag
    # also hides the file itself.
    name = find_cv() if settings.cv_download_enabled else None
    if name is None:
        raise HTTPException(status_code=404)
    return FileResponse(
        DATA_DIR / name,
        filename=CV_DOWNLOAD_NAME,
        headers={"Cache-Control": "no-cache"},
    )


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
