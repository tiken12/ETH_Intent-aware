from fastapi import FastAPI
from app.api import bridge
from app.api.routes import router as api_router
from app.core.logging import configure_logging
from app.api.bridge import router as bridge_router
from app.api import sim_4337

app = FastAPI(title="Intent Guard", version="0.1.0")
configure_logging()
app.include_router(bridge.router)
app.include_router(sim_4337.router, tags=["simulate"]) # Include sim_4337 router

@app.get("/health")
def health():
    return {"ok": True}