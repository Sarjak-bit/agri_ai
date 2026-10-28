from fastapi import FastAPI

from app.routers import analysis, vegetation

app = FastAPI(title="Agri AI Service", version="0.2.0")

app.include_router(analysis.router)
app.include_router(vegetation.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
