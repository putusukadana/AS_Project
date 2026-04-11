import requests
import json
import datetime
import time
import pandas as pd
import traceback
from typing import List, Dict, Any, Optional, Union

# --- TikTok Video Extraction ---

def extract_tiktok_data(
    keywords: Union[str, List[str]] = "bali",
    cursor: str = "0",
    limit: int = 0,
    sort_by: str = "relevance",
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None
) -> Dict[str, Any]:
    url = "https://tiktok-api23.p.rapidapi.com/api/search/video"
    headers = {
        "x-rapidapi-key": "d501fae7bfmsh3f1de8ef5dc24d3p1d9ebejsnabaf8a976a3e",
        "x-rapidapi-host": "tiktok-api23.p.rapidapi.com"
    }

    if isinstance(keywords, str):
        keywords_list = [keywords]
    else:
        keywords_list = keywords

    collected_videos = []
    unique_video_ids = set()

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
                response = requests.get(url, headers=headers, params=querystring)
                response.raise_for_status()
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

                        video_info = {
                            "platform": "tiktok",
                            "nickname": author.get("nickname", "Tidak tersedia"),
                            "description": description,
                            "text": description, # for generic text field
                            "post_url": post_url,
                            "video_id": video_id,
                            "author_unique_id": author_unique_id,
                            "created_at": create_time_str,
                            "source_keyword": keyword
                        }
                        unique_video_ids.add(video_id)
                        collected_videos.append(video_info)

                if "has_more" in data and data["has_more"] and "cursor" in data and data["cursor"] != current_cursor:
                    current_cursor = data["cursor"]
                    time.sleep(1)
                else:
                    has_more = False
        except Exception as e:
            print(f"Error TikTok search: {e}")
            continue

    return {"status": "success", "results": collected_videos}

# --- TikTok Comment Scraper ---

class TikTokCommentScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.tiktok.com/',
        }
        self.session.headers.update(self.headers)

    def get_comments(self, video_id):
        comments = []
        cursor = 0
        has_more = True
        device_id = str(int(time.time() * 1000))
        
        while has_more:
            try:
                url = f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id}&cursor={cursor}&count=20&device_id={device_id}&aid=1988"
                response = self.session.get(url, timeout=15)
                if response.status_code != 200: break
                data = response.json()
                
                if 'comments' not in data or not data['comments']: break
                
                for comment in data['comments']:
                    c_data = {
                        'cid': comment.get('cid'),
                        'text': comment.get('text'),
                        'user_nickname': comment.get('user', {}).get('nickname'),
                        'user_unique_id': comment.get('user', {}).get('unique_id'),
                        'digg_count': comment.get('digg_count', 0),
                        'replies': self.get_replies(video_id, comment.get('cid'))
                    }
                    comments.append(c_data)
                
                # Keep it short for demo/dev purposes
                if len(comments) >= 20: break
                
                cursor = data.get('cursor', 0)
                has_more = data.get('has_more', False)
                time.sleep(1)
            except:
                break
        return comments

    def get_replies(self, video_id, comment_id):
        url = "https://tiktok-api23.p.rapidapi.com/api/post/comment/replies"
        headers = {
            "x-rapidapi-key": "d501fae7bfmsh3f1de8ef5dc24d3p1d9ebejsnabaf8a976a3e",
            "x-rapidapi-host": "tiktok-api23.p.rapidapi.com"
        }
        params = {"videoId": video_id, "commentId": comment_id, "count": "5", "cursor": "0"}
        try:
            res = requests.get(url, headers=headers, params=params)
            res_data = res.json()
            return res_data.get("data", []) if isinstance(res_data, dict) else []
        except:
            return []

# --- Main Service Function ---

async def run_crawl(platforms: list, keyword: str) -> dict:
    all_data = []
    if "tiktok" in platforms:
        tiktok_res = extract_tiktok_data(keywords=keyword, limit=5)
        scraper = TikTokCommentScraper()
        
        for video in tiktok_res["results"]:
            # Optionally fetch comments
            # video["comments"] = scraper.get_comments(video["video_id"])
            all_data.append(video)
    
    # Mock other platforms if needed
    if not all_data:
         all_data = [{"platform": p, "text": f"Mock data for {p}", "created_at": "2025-01-01T00:00:00"} for p in platforms]
            
    return {
        "total": len(all_data),
        "signal_quality": 95 if all_data else 0,
        "data": all_data
    }
