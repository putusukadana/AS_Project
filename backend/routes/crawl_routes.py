from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from services.crawl_service import run_crawl
from services.pipeline_service import set_current_data
from services.crawl_tiktok_service import get_last_quota
from auth import get_current_user

router = APIRouter(prefix="/api/v1/crawl", tags=["crawl"])

class CrawlRequest(BaseModel):
    platforms: List[str]
    keyword: str
    video_limit: Optional[int] = 0 
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

@router.post("/start")
async def start_crawl(body: CrawlRequest, user = Depends(get_current_user)):
    result = await run_crawl(
        body.platforms, 
        body.keyword, 
        body.video_limit, 
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

@router.get("/quota")
async def get_quota(user = Depends(get_current_user)):
    quota = get_last_quota()
    return {
        "status": "success",
        "data": quota
    }
