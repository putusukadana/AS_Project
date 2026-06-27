import requests
import datetime
import time
import re
import os
from typing import List, Dict, Any, Optional, Union
from dotenv import load_dotenv
from database import db

load_dotenv()

# --- Configuration & Global Rate Limiting ---
RAPIDAPI_HOST = "tiktok-api23.p.rapidapi.com"

async def _get_rapidapi_key():
    collection = db["settings"]
    doc = await collection.find_one({"key": "rapidapi_key"})
    if doc and doc.get("value"):
        return doc["value"]
    return os.getenv("RAPIDAPI_KEY", "5a4e413e53msh489dc431409691cp1d2ffbjsn439845531010")
# Track last request to ensure 1 request/second (approx 1.1s safety)
_last_request_time = 0
_last_quota = {"remaining": 100, "limit": 100} # Initial estimate based on last test

def get_last_quota():
    global _last_quota
    return _last_quota

def respect_rate_limit():
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < 4.0: # 1000 req/hour ~ 1 req / 3.6s. Gunakan 4.0s agar aman.
        time.sleep(4.0 - elapsed)
    _last_request_time = time.time()

# --- Utility: Safe API Request with Retry & Backoff ---

def safe_api_request(url, headers, params=None, timeout=15, max_retries=1):
    """Wrapper untuk requests.get dengan penanganan error 429 (Rate Limit)."""
    retry_delay = 5 # Detik awal tunggu
    
    for i in range(max_retries + 1):
        try:
            respect_rate_limit() # Global RPS enforcement
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            
            # Log Rate Limit Info from Headers
            rem = response.headers.get('x-ratelimit-requests-remaining')
            lim = response.headers.get('x-ratelimit-requests-limit')
            if rem:
                try:
                    _last_quota["remaining"] = int(rem)
                    _last_quota["limit"] = int(lim)
                except:
                    pass
                print(f"[TikTok API] Quota Remaining: {_last_quota['remaining']}/{_last_quota['limit']}")
            
            if response.status_code == 200:
                return response
            
            if response.status_code == 429:
                if i < max_retries:
                    wait_time = retry_delay * (2**i) # Exponential backoff
                    print(f"Rate limit (429) hit. Menunggu {wait_time} detik sebelum mencoba lagi ({i+1}/{max_retries})...")
                    time.sleep(wait_time)
                    continue
                else:
                    print("Batas maksimal retry tercapai untuk error 429.")
                    return response
            
            # Error lainnya (500, 403, dll)
            return response
            
        except requests.exceptions.RequestException as e:
            if i < max_retries:
                time.sleep(retry_delay)
                continue
            raise e
    return None

# --- TikTok Video Extraction ---

async def extract_tiktok_data(
    keywords: Union[str, List[str]],
    cursor: str = "0",
    limit: int = 0,
    sort_by: str = "top",
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None
) -> Dict[str, Any]:
    if not keywords:
        return {"status": "error", "message": "Harus memasukkan keyword"}

    rapidapi_key = await _get_rapidapi_key()
    url = "https://tiktok-api23.p.rapidapi.com/api/search/video"
    headers = {
        "x-rapidapi-key": rapidapi_key,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    if isinstance(keywords, str):
        keywords_list = [keywords]
    else:
        keywords_list = keywords

    collected_videos = []
    unique_video_ids = set()
    comment_scraper = TikTokCommentScraper()

    for keyword in keywords_list:
        querystring = {"keyword": keyword, "cursor": cursor, "search_id": "0"}
        if sort_by.lower() == "date":
            querystring["sort_type"] = "1"

        has_more = True
        current_cursor = cursor

        try:
            while has_more:
                if limit > 0 and len(collected_videos) >= limit:
                    break

                querystring["cursor"] = current_cursor
                response = safe_api_request(url, headers=headers, params=querystring)
                if not response or response.status_code != 200:
                    if response and response.status_code == 429:
                        print(f"[Video] Kuota API habis. Menyelesaikan crawling dengan {len(collected_videos)} video yang sudah didapat.")
                    break
                
                data = response.json()

                if "item_list" in data and isinstance(data["item_list"], list):
                    videos = data["item_list"]
                    for video in videos:
                        video_id = video.get("id") or video.get("id_str") or video.get("video", {}).get("id")
                        if not video_id or video_id in unique_video_ids:
                            continue

                        if "create_time" in video:
                            try:
                                video_date = datetime.datetime.fromtimestamp(int(video["create_time"]))
                                
                                # Optimization: If sorting by date (desc), once we hit a video older than start_date, we stop.
                                if sort_by.lower() == "date" and start_date and video_date < start_date:
                                    has_more = False
                                    break
                                    
                                if start_date and video_date < start_date: continue
                                if end_date and video_date > end_date: continue
                            except:
                                pass

                        author = video.get("author", {})
                        author_unique_id = author.get("unique_id") or author.get("uniqueId") or video.get("creator", {}).get("uniqueId", "")
                        
                        description = video.get("desc") or video.get("description") or video.get("text", "")
                        post_url = f"https://www.tiktok.com/@{author_unique_id}/video/{video_id}" if video_id and author_unique_id else f"https://www.tiktok.com/video/{video_id}"

                        create_time_str = ""
                        try:
                            create_time_str = datetime.datetime.fromtimestamp(int(video["create_time"])).strftime("%Y-%m-%d %H:%M:%S")
                        except:
                            create_time_str = str(video.get("create_time", ""))

                        stats = video.get("stats") or video.get("statistics") or {}
                        comment_count = stats.get("comment_count") or stats.get("commentCount") or 0

                        video_info = {
                            "platform": "tiktok",
                            "nickname": author.get("nickname", "Tidak tersedia"),
                            "post_url": post_url,
                            "video_id": video_id,
                            "author_unique_id": author_unique_id,
                            "description": description,
                            "comment_count": int(comment_count),
                            "estimated_size_kb": round(float(comment_count) * 0.15, 2),
                        }

                        # Batasi pengambilan komentar hanya untuk 20 video teratas
                        if int(comment_count) >= 1:
                            try:
                                # Ambil semua komentar
                                video_info["comment_sample"] = comment_scraper.get_comments(video_id, max_comments=None)
                            except Exception as e:
                                print(f"Error sampling comments for {video_id}: {e}")
                                video_info["comment_sample"] = []
                        else:
                            video_info["comment_sample"] = []
                        
                        video_info["comment_count"] = len(video_info["comment_sample"])
                        video_info["estimated_size_kb"] = round(len(video_info["comment_sample"]) * 0.15, 2)
                        
                        unique_video_ids.add(video_id)
                        collected_videos.append(video_info)

                if "has_more" in data and data["has_more"] and "cursor" in data and data["cursor"] != current_cursor:
                    current_cursor = data["cursor"]
                else:
                    has_more = False
        except Exception as e:
            print(f"Error TikTok search: {e}")
            continue

    return {"status": "success", "results": collected_videos}

def resolve_and_extract_video_id(url: str) -> Optional[str]:
    """Mengambil video_id dari URL TikTok, mendukung short links."""
    try:
        # Jika itu short link (vt.tiktok.com atau tiktok.com/t/), resolusi dulu
        if "vt.tiktok.com" in url or "tiktok.com/t/" in url:
            res = requests.head(url, allow_redirects=True, timeout=10)
            url = res.url
            
        # Regex untuk mengambil ID video
        match = re.search(r'video/(\d+)', url)
        if match:
            return match.group(1)
            
        # Cek format mobile/lainnya
        match = re.search(r'v/(\d+)', url)
        if match:
            return match.group(1)
            
        return None
    except Exception as e:
        print(f"Error resolving URL: {e}")
        return None

def get_tiktok_video_details(video_id: str) -> Dict[str, Any]:
    """Mengambil komentar TikTok berdasarkan video_id (gratis, tanpa RapidAPI)."""
    try:
        comment_scraper = TikTokCommentScraper()
        comment_sample = comment_scraper.get_comments(video_id, max_comments=None)

        return {
            "status": "success",
            "results": [{
                "platform": "tiktok",
                "nickname": "TikTok User",
                "post_url": f"https://www.tiktok.com/video/{video_id}",
                "video_id": video_id,
                "author_unique_id": "",
                "comment_count": len(comment_sample),
                "estimated_size_kb": round(len(comment_sample) * 0.15, 2),
                "comment_sample": comment_sample
            }]
        }
    except Exception as e:
        print(f"[TikTok Web] Error get_tiktok_video_details: {e}")
        return {"status": "error", "results": []}

class TikTokCommentScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.tiktok.com/',
        })

    def get_comments(self, video_id, max_comments=None):
        comments = []
        cursor = 0
        has_more = True

        while has_more:
            if max_comments and len(comments) >= max_comments:
                break

            try:
                url = (
                    f"https://www.tiktok.com/api/comment/list/"
                    f"?aid=1988&aweme_id={video_id}&count=50&cursor={cursor}"
                )
                self.session.headers.update({
                    'referer': f'https://www.tiktok.com/@x/video/{video_id}'
                })

                resp = self.session.get(url, timeout=15)
                if resp.status_code != 200:
                    print(f"[TikTok Web] Gagal mengambil komentar: {resp.status_code}")
                    break

                data = resp.json()
                raw_comments = data.get("comments")
                if not raw_comments or not isinstance(raw_comments, list):
                    break

                for item in raw_comments:
                    user = item.get("user", {})
                    comments.append({
                        "cid": item.get("cid", ""),
                        "text": item.get("text", ""),
                        "user_nickname": user.get("nickname", "TikTok User"),
                        "user_unique_id": user.get("unique_id", ""),
                        "digg_count": item.get("digg_count", 0),
                        "replies": [],
                    })

                has_more = data.get("has_more", False)
                cursor = data.get("cursor", cursor)

                if has_more:
                    time.sleep(2.5)

            except Exception as e:
                print(f"[TikTok Web] Error get_comments {video_id}: {e}")
                break

        return comments

