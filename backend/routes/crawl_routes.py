from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from services.crawl_service import run_crawl
from services.pipeline_service import set_current_data

router = APIRouter(prefix="/api/v1/crawl", tags=["crawl"])

class CrawlRequest(BaseModel):
    platforms: List[str]
    keyword: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

@router.post("/start")
async def start_crawl(body: CrawlRequest):
    result = await run_crawl(
        body.platforms, 
        body.keyword, 
        body.start_date, 
        body.end_date
    )
    # Sync data for pipeline demo
    set_current_data(result["data"])
    return {
        "status": "success",
        "total": result["total"],
        "signal_quality": result["signal_quality"],
        "data": result["data"]
    }
