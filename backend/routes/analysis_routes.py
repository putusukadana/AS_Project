from fastapi import APIRouter
from services.sentiment_service import run_sentiment_analysis
from services.keyword_service import compute_keywords

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])

@router.post("/sentiment")
async def run_sentiment():
    """
    Endpoint untuk menjalankan analisis sentimen pada data yang sudah
    melalui pipeline preprocessing (hasil stemming).
    """
    result = await run_sentiment_analysis()
    return result

@router.post("/keywords")
async def get_keywords():
    """
    Endpoint untuk mendapatkan top keywords dari seluruh komentar
    yang sudah melalui pipeline dan analisis sentimen.
    """
    result = await compute_keywords()
    return result
