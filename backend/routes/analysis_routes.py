from fastapi import APIRouter
from services.sentiment_service import run_sentiment_analysis

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])

@router.post("/sentiment")
async def run_sentiment():
    """
    Endpoint untuk menjalankan analisis sentimen pada data yang sudah
    melalui pipeline preprocessing (hasil stemming).
    """
    result = await run_sentiment_analysis()
    return result
