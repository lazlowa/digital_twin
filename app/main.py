from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.resume import load_resume

ROOT = Path(__file__).resolve().parent.parent

app = FastAPI(title="Digital Twin")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
templates = Jinja2Templates(directory=ROOT / "templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html", {"resume": load_resume()})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
