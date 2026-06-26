from fastapi import APIRouter, Depends, Query
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
async def emoji_conversion(convert_emoji: bool = Query(True), user = Depends(get_current_user)):
    return await run_emoji_conversion(convert_emoji=convert_emoji)

@router.post("/cleansing")
async def cleansing(filter_lang: bool = Query(True), user = Depends(get_current_user)):
    return await run_cleansing(filter_lang=filter_lang)

@router.post("/normalization")
async def normalization(user = Depends(get_current_user)):
    return await run_normalization()

@router.post("/stopwords")
async def stopwords(user = Depends(get_current_user)):
    return await run_stopwords()

@router.post("/stemming")
async def stemming(user = Depends(get_current_user)):
    return await run_stemming()
