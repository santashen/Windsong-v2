import logging

from fastapi import FastAPI, HTTPException

from config import settings
from services.base_llm import OpenAICompatibleService
from services.gold_analysis import GoldAnalysisService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Windsong AI Service", version="1.0.0")

# Initialize services
llm_service = OpenAICompatibleService(
    api_url=settings.LLM_API_URL,
    api_key=settings.LLM_API_KEY,
    model=settings.LLM_MODEL,
)
gold_service = GoldAnalysisService(llm_service)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai-service"}


@app.get("/api/test")
async def test_llm():
    """Simple test to verify LLM API connectivity."""
    try:
        response = await llm_service.generate("Say 'Hello, connection successful!' in one short sentence.")
        return {
            "status": "ok",
            "model": llm_service.get_model_name(),
            "response": response,
        }
    except Exception as e:
        logger.error(f"LLM test failed: {e}")
        raise HTTPException(status_code=500, detail=f"LLM connection failed: {str(e)}")


@app.get("/api/gold/analyze")
async def analyze_gold():
    try:
        result = await gold_service.analyze()
        return result
    except Exception as e:
        logger.error(f"Gold analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
