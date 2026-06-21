from fastapi import APIRouter, Depends
from auth import get_current_user
from services.sentiment_service import run_sentiment_analysis
from services.keyword_service import compute_keywords

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])

@router.post("/sentiment")
async def run_sentiment(user = Depends(get_current_user)):
    result = await run_sentiment_analysis()
    return result

@router.post("/keywords")
async def get_keywords(user = Depends(get_current_user)):
    result = await compute_keywords()
    return result
