from fastapi import APIRouter
from services.pipeline_service import (
    run_case_folding, run_url_removal, run_stopwords, run_emotion_detection
)

router = APIRouter(prefix="/api/v1/pipeline", tags=["pipeline"])

@router.post("/case_folding")
async def case_folding():
    return await run_case_folding()

@router.post("/url_removal")
async def url_removal():
    return await run_url_removal()

@router.post("/stopwords")
async def stopwords():
    return await run_stopwords()

@router.post("/emotion")
async def emotion():
    return await run_emotion_detection()
