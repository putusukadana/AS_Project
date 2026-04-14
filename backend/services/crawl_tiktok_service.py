import requests
import datetime
import time
import re
from typing import List, Dict, Any, Optional, Union

# --- TikTok Video Extraction ---

def extract_tiktok_data(
    keywords: Union[str, List[str]],
    cursor: str = "0",
    limit: int = 0,
    sort_by: str = "relevance",
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None
) -> Dict[str, Any]:
    if not keywords:
        return {"status": "error", "message": "Harus memasukkan keyword"}

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
    comment_scraper = TikTokCommentScraper()
    sample_comments_fetched = False

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
                            # "description": description,
                            # "text": description, # for generic text field
                            "post_url": post_url,
                            "video_id": video_id,
                            "author_unique_id": author_unique_id,
                            "comment_count": int(comment_count),
                            "estimated_size_kb": round(float(comment_count) * 0.15, 2), # Estimasi 0.15KB per komentar
                            # "created_at": create_time_str,
                            # "source_keyword": keyword
                        }

                        # Ambil sample 10 komentar jika belum ada
                        if not sample_comments_fetched and int(comment_count) >= 5:
                            try:
                                video_info["comment_sample"] = comment_scraper.get_comments(video_id, max_comments=10)
                                if video_info["comment_sample"]:
                                    sample_comments_fetched = True
                            except:
                                video_info["comment_sample"] = []
                        
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
    """Mengambil metadata video TikTok berdasarkan ID."""
    url = "https://tiktok-api23.p.rapidapi.com/api/post/info"
    headers = {
        "x-rapidapi-key": "d501fae7bfmsh3f1de8ef5dc24d3p1d9ebejsnabaf8a976a3e",
        "x-rapidapi-host": "tiktok-api23.p.rapidapi.com"
    }
    querystring = {"videoId": video_id}
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        
        # Mapping response ke format yang seragam
        item = data.get("base") or data.get("itemInfo", {}).get("itemStruct", {})
        if not item:
            item = data
            
        author = item.get("author") or {}
        author_unique_id = author.get("uniqueId") or author.get("unique_id", "")
        
        video_id_actual = item.get("id") or video_id
        
        # Ambil sample komentar untuk video tunggal ini
        comment_scraper = TikTokCommentScraper()
        comment_sample = []
        try:
            comment_sample = comment_scraper.get_comments(video_id_actual, max_comments=10)
        except:
            pass

        return {
            "status": "success",
            "results": [{
                "platform": "tiktok",
                "post_url": f"https://www.tiktok.com/@{author_unique_id}/video/{video_id_actual}",
                "video_id": video_id_actual,
                "author_unique_id": author_unique_id,
                "comment_count": int(item.get("stats", {}).get("commentCount") or 0),
                "comment_sample": comment_sample
            }]
        }
    except Exception as e:
        print(f"Error fetching video details: {e}")
        return {"status": "error", "results": []}

class TikTokCommentScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.tiktok.com/',
        }
        self.session.headers.update(self.headers)

    def get_comments(self, video_id, max_comments=None):
        comments = []
        cursor = 0
        has_more = True
        url = "https://tiktok-api23.p.rapidapi.com/api/post/comments"
        headers = {
            "x-rapidapi-key": "d501fae7bfmsh3f1de8ef5dc24d3p1d9ebejsnabaf8a976a3e",
            "x-rapidapi-host": "tiktok-api23.p.rapidapi.com"
        }
        
        while has_more:
            if max_comments and len(comments) >= max_comments:
                break
            try:
                params = {"videoId": video_id, "count": "20", "cursor": str(cursor)}
                response = requests.get(url, headers=headers, params=params, timeout=15)
                if response.status_code != 200: break
                res_data = response.json()
                
                # Cek beberapa kemungkinan key hasil (tergantung versi API)
                data_list = res_data.get("data") or res_data.get("comments")
                if not data_list or not isinstance(data_list, list):
                    break
                
                for item in data_list:
                    # Mapping response ke format aplikasi
                    user = item.get('user', {})
                    comments.append({
                        'cid': item.get('cid') or item.get('id'),
                        'text': item.get('text') or item.get('comment_text') or item.get('desc'),
                        'user_nickname': user.get('nickname', 'Tiktok User'),
                        'user_unique_id': user.get('unique_id') or user.get('uniqueId'),
                        'digg_count': item.get('digg_count', 0),
                        'replies': [] # Skip recursive replies for summary preview
                    })
                
                has_more = res_data.get("hasMore", False) or res_data.get("has_more", False)
                next_cursor = res_data.get("cursor")
                if next_cursor is not None and str(next_cursor) != str(cursor):
                    cursor = next_cursor
                else:
                    has_more = False
                
                if has_more:
                    time.sleep(0.5)
            except Exception as e:
                print(f"Error fetching comments for {video_id}: {e}")
                break
        return comments

    def get_replies(self, video_id, comment_id):
        replies = []
        cursor = 0
        has_more = True
        url = "https://tiktok-api23.p.rapidapi.com/api/post/comment/replies"
        headers = {
            "x-rapidapi-key": "d501fae7bfmsh3f1de8ef5dc24d3p1d9ebejsnabaf8a976a3e",
            "x-rapidapi-host": "tiktok-api23.p.rapidapi.com"
        }
        
        while has_more:
            params = {"videoId": video_id, "commentId": comment_id, "count": "50", "cursor": str(cursor)}
            try:
                res = requests.get(url, headers=headers, params=params, timeout=15)
                res.raise_for_status()
                res_data = res.json()
                
                data_list = res_data.get("data") or res_data.get("comments") or res_data.get("replies")
                if not data_list or not isinstance(data_list, list):
                    break
                    
                replies.extend(data_list)
                
                has_more = res_data.get("hasMore", False) or res_data.get("has_more", False)
                next_cursor = res_data.get("cursor")
                if next_cursor is not None and str(next_cursor) != str(cursor):
                    cursor = next_cursor
                else:
                    has_more = False
                
                if has_more:
                    time.sleep(0.5)
            except Exception as e:
                print(f"Error fetching replies for {comment_id}: {e}")
                break
                
        return replies
