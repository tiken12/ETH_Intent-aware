from fastapi import FastAPI
from app.api.routes import router as api_router
from app.core.logging import configure_logging

app = FastAPI(title="Intent Guard")
configure_logging()
app.include_router(api_router)

@app.get("/health")
def health():
    return {"ok": True}
