from fastapi import APIRouter
router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])

@router.post("/sentiment")
async def run_sentiment():
    # Placeholder for sentiment analysis logic
    return {"status": "ok", "message": "Analisis sentimen berhasil dijalankan"}
