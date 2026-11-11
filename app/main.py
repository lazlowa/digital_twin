from fastapi import FastAPI

app = FastAPI(title="Digital Twin")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
