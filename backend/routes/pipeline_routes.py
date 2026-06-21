from fastapi import APIRouter, Depends
from auth import get_current_user
from services.pipeline_service import (
    run_emoji_conversion, 
    run_cleansing, 
    run_normalization, 
    run_stopwords, 
    run_stemming
)

router = APIRouter(prefix="/api/v1/pipeline", tags=["pipeline"])

@router.post("/emoji_conversion")
async def emoji_conversion(user = Depends(get_current_user)):
    return await run_emoji_conversion()

@router.post("/cleansing")
async def cleansing(user = Depends(get_current_user)):
    return await run_cleansing()

@router.post("/normalization")
async def normalization(user = Depends(get_current_user)):
    return await run_normalization()

@router.post("/stopwords")
async def stopwords(user = Depends(get_current_user)):
    return await run_stopwords()

@router.post("/stemming")
async def stemming(user = Depends(get_current_user)):
    return await run_stemming()
