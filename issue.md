# Issue: Ganti `get_comments()` ke TikTok Web API

## Latar Belakang

Fungsi crawling komentar TikTok saat ini menggunakan **RapidAPI** (`tiktok-api23.p.rapidapi.com/api/post/comments`).  
RapidAPI key yang dipakai sudah **403 Forbidden** (expired/tidak valid), sehingga tidak ada komentar yang berhasil diambil.

## Solusi

Ganti method `get_comments()` di class `TikTokCommentScraper` untuk mengakses **TikTok Web API** langsung:
```
GET https://www.tiktok.com/api/comment/list/?aid=1988&aweme_id={video_id}&count=50&cursor={cursor}
```

**Keuntungan:**
- Gratis, tanpa quota
- Tidak perlu API key
- Tidak perlu cookie (cukup User-Agent browser)

## File yang Diubah

Hanya **satu file**:

| File | Perubahan |
|------|-----------|
| `backend/services/crawl_tiktok_service.py` | class `TikTokCommentScraper` — ganti method `get_comments()` dan `__init__()` |

## Tidak Berubah

- `extract_tiktok_data()` — tetap pakai RapidAPI untuk search video (jika key sudah valid)
- `get_tiktok_video_details()` — tetap pakai RapidAPI untuk detail video
- `crawl_service.py`
- Pipeline, routes, frontend

## Detail Implementasi

### Method `__init__()`

```python
def __init__(self):
    self.session = requests.Session()
    self.session.headers.update({
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.tiktok.com/',
    })
```

### Method `get_comments()`

```python
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
                print(f"[TikTok Web] Gagal: {resp.status_code}")
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
            time.sleep(2.5)

        except Exception as e:
            print(f"[TikTok Web] Error get_comments {video_id}: {e}")
            break

    return comments
```

### Perbedaan dengan kode lama (RapidAPI)

| Aspek | Sebelum (RapidAPI) | Sesudah (TikTok Web) |
|-------|-------------------|---------------------|
| Endpoint | `tiktok-api23.p.rapidapi.com/api/post/comments` | `www.tiktok.com/api/comment/list/` |
| Auth | API key + Host header | User-Agent browser |
| Biaya | Berbayar (quota 100/jam) | Gratis |
| Rate limit | 1 req/4 detik | 1 req/2.5 detik |
| Return format | `list[dict]` | `list[dict]` (sama) |
| Parameter | `videoId`, `count: "20"`, `cursor` | `aweme_id`, `count: 50`, `cursor` |

### Response format TikTok Web API

```json
{
  "comments": [
    {
      "cid": "12345",
      "text": "Komentar...",
      "user": {
        "nickname": "User1",
        "unique_id": "user1"
      },
      "digg_count": 5,
      "create_time": 1234567890
    }
  ],
  "has_more": true,
  "cursor": "50"
}
```

## Cara Test

Jalankan script berikut dari `backend/` directory:

```python
from services.crawl_tiktok_service import TikTokCommentScraper

scraper = TikTokCommentScraper()
comments = scraper.get_comments("VIDEO_ID_AND", max_comments=100)
print(f"Mendapat {len(comments)} komentar")
if comments:
    print(comments[0])
```

## Catatan

1. **TikTok Web API bisa berubah kapan saja** — TikTok tidak menyediakan dokumentasi resmi untuk endpoint ini
2. **Rate limiting TikTok** — jika terlalu cepat, TikTok bisa return 403 atau empty response. Delay 2.5 detik sudah cukup aman
3. **Fungsi search & detail video masih via RapidAPI** — jika RapidAPI masih 403, pencarian video tetap tidak akan berfungsi, hanya ambil komentar yang berubah
