import datetime
import re
from typing import List, Dict, Any, Optional
from services.crawl_tiktok_service import (
    extract_tiktok_data, 
    resolve_and_extract_video_id, 
    get_tiktok_video_details
)

# --- Main Service Function ---

async def run_crawl(
    platforms: list, 
    keyword: str, 
    start_date: Optional[datetime.datetime] = None, 
    end_date: Optional[datetime.datetime] = None
) -> dict:
    if not keyword or not keyword.strip():
        return {"status": "error", "message": "Harus memasukkan keyword"}

    all_data = []
    
    # Split keyword by newline or comma to handle multiple inputs
    inputs = [i.strip() for i in re.split(r'[\n,]+', keyword) if i.strip()]
    
    # Limit to 10 targets for performance/safety
    targets = inputs[:10]
    
    for item in targets:
        # Deteksi jika input adalah URL TikTok
        is_tiktok_url = "tiktok.com" in item.lower()
        
        if is_tiktok_url and "tiktok" in platforms:
            video_id = resolve_and_extract_video_id(item)
            if video_id:
                tiktok_res = get_tiktok_video_details(video_id)
            else:
                tiktok_res = {"status": "error", "results": []}
        elif "tiktok" in platforms:
            # If dates are provided, we should sort by date to allow early termination
            sort_by = "date" if (start_date or end_date) else "relevance"
            
            tiktok_res = extract_tiktok_data(
                keywords=item, 
                limit=100, # Lower safety limit per keyword for multi-search
                sort_by=sort_by,
                start_date=start_date, 
                end_date=end_date
            )
        else:
            tiktok_res = {"status": "success", "results": []}

        if tiktok_res["status"] == "success":
            for video in tiktok_res["results"]:
                all_data.append(video)
                
    # Ensure signal quality logic
    signal_quality = 95 if all_data else 0
    if len(targets) > 1 and not all_data:
        signal_quality = 0
            
    return {
        "total": len(all_data),
        "signal_quality": signal_quality,
        "data": all_data
    }
