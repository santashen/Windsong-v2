import logging
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Query

from config import settings
from services.base_llm import OpenAICompatibleService
from services.finance_data import FinanceDataService
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
finance_service = FinanceDataService()


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


@app.get("/api/finance/search")
async def finance_search(keyword: str = Query(..., min_length=1)):
    """Search stocks and funds by keyword."""
    try:
        results = finance_service.search(keyword)
        return {"results": results}
    except Exception as e:
        logger.error(f"Finance search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/finance/history")
async def finance_history(
    codes: str = Query(..., description="Comma-separated codes"),
    type: str = Query("stock", description="stock or fund"),
    start: str = Query(None, description="Start date YYYY-MM-DD"),
    end: str = Query(None, description="End date YYYY-MM-DD"),
):
    """Fetch historical data for one or more codes."""
    if not end:
        end = datetime.now().strftime("%Y-%m-%d")
    if not start:
        start = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

    code_list = [c.strip() for c in codes.split(",") if c.strip()]
    if not code_list:
        raise HTTPException(status_code=400, detail="No codes provided")

    results = []
    for code in code_list:
        try:
            data = finance_service.get_history(code, type, start, end)
            results.append(data)
        except Exception as e:
            logger.error(f"Failed to fetch history for {code}: {e}")
            results.append({"code": code, "type": type, "error": str(e)})

    return {"results": results}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
