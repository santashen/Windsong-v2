import uvicorn
from fastapi import FastAPI

from windsong_python.api.photo_metadata import router as photo_metadata_router

app = FastAPI(title="Windsong Python Services", version="0.1.0")
app.include_router(photo_metadata_router, prefix="/api")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "python"}


def run() -> None:
    uvicorn.run("windsong_python.main:app", host="0.0.0.0", port=8000)
