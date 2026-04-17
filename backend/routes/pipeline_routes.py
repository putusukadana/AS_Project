from fastapi import APIRouter
from services.pipeline_service import (
    run_emoji_conversion, 
    run_cleansing, 
    run_normalization, 
    run_stopwords, 
    run_sentiment_analysis_legacy
)

router = APIRouter(prefix="/api/v1/pipeline", tags=["pipeline"])

@router.post("/emoji_conversion")
async def emoji_conversion():
    return await run_emoji_conversion()

@router.post("/cleansing")
async def cleansing():
    return await run_cleansing()

@router.post("/normalization")
async def normalization():
    return await run_normalization()

@router.post("/stopwords")
async def stopwords():
    return await run_stopwords()

@router.post("/sentiment_analysis")
async def sentiment_analysis():
    return await run_sentiment_analysis_legacy()
