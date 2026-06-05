# Issue: Integrasi TopKeywords/Wordcloud dari Data Real Pipeline

## Deskripsi Singkat

Komponen `TopKeywords.vue` di halaman Dashboard saat ini menampilkan **data dummy hardcoded** (14 keyword palsu). 
Sistem sudah memiliki data real dari hasil pipeline + analisis sentimen, yaitu setiap komentar memiliki 
`stemmed_text` (hasil stemming) dan `sentiment_label` (Positif/Netral/Negatif).

Tujuan issue ini adalah:
1. Membuat backend service untuk menghitung frekuensi kata dari `stemmed_text` seluruh komentar
2. Membuat endpoint API untuk mengembalikan top keywords (overall dan per sentiment label)
3. Update `TopKeywords.vue` untuk menampilkan data real

---

## Kondisi Kode Saat Ini

| Komponen | File | Kondisi |
|---|---|---|
| Backend Service Keywords | `backend/services/` | ❌ Tidak ada `keyword_service.py` |
| Backend Route Keywords | `backend/routes/analysis_routes.py` | ❌ Tidak ada endpoint `/keywords` |
| Frontend Store | `frontend/src/stores/crawlStore.js` | ❌ Tidak ada state `keywords` |
| Dashboard TopKeywords | `frontend/src/components/dashboard/TopKeywords.vue` | ❌ Data dummy hardcoded |
| Data Tersedia | `analyzedData` → `comment.stemmed_text` + `sentiment_label` | ✅ Lengkap |

---

## Tahapan Implementasi

### Tahap 1: Buat Backend Service — `keyword_service.py`

**Buat file baru:** `backend/services/keyword_service.py`

File ini bertanggung jawab untuk:
- Membaca `_current_data` (data global hasil pipeline)
- Mengumpulkan `stemmed_text` dari setiap komentar
- Mengelompokkan kata per label sentimen
- Menghitung frekuensi kata menggunakan `collections.Counter`
- Mengembalikan top keywords (overall dan per label)

Kode lengkap:

```python
# backend/services/keyword_service.py

from collections import Counter

async def compute_keywords(top_n: int = 20) -> dict:
    from services.pipeline_service import _current_data

    if not _current_data:
        return {
            "status": "error",
            "message": "Tidak ada data. Jalankan pipeline preprocessing terlebih dahulu.",
            "overall": [],
            "by_label": {}
        }

    # Kumpulkan teks per label sentimen
    texts_by_label = {
        "Positif": [],
        "Netral": [],
        "Negatif": []
    }
    all_texts = []

    for video in _current_data:
        if "comment_sample" not in video or not isinstance(video["comment_sample"], list):
            continue
        for comment in video["comment_sample"]:
            stemmed = comment.get("stemmed_text") or ""
            if not stemmed.strip():
                continue
            all_texts.append(stemmed)
            label = comment.get("sentiment_label", "Netral")
            if label in texts_by_label:
                texts_by_label[label].append(stemmed)

    def count_keywords(texts: list) -> list:
        counter = Counter()
        for t in texts:
            words = t.split()
            counter.update(words)
        return [{"text": word, "count": count} for word, count in counter.most_common(top_n)]

    return {
        "status": "done",
        "overall": count_keywords(all_texts),
        "by_label": {
            label: count_keywords(texts)
            for label, texts in texts_by_label.items()
        }
    }
```

### Tahap 2: Update Backend Route — `analysis_routes.py`

**File:** `backend/routes/analysis_routes.py`

Tambahkan import dan endpoint baru:

```python
from services.keyword_service import compute_keywords

@router.post("/keywords")
async def get_keywords():
    result = await compute_keywords()
    return result
```

### Tahap 3: Update Frontend Store — `crawlStore.js`

**File:** `frontend/src/stores/crawlStore.js`

**a.** Tambahkan state `keywords` baru

**b.** Tambahkan method `fetchKeywords()`

**c.** Panggil `fetchKeywords()` setelah sentiment analysis sukses

**d.** Reset keywords saat crawl baru

**e.** Expose `keywords` dan `fetchKeywords` di return

### Tahap 4: Update `TopKeywords.vue` — Data Real

**File:** `frontend/src/components/dashboard/TopKeywords.vue`

Ganti seluruh konten dengan:
- Import `useCrawlStore`
- Tampilkan keywords dari store
- Filter tabs (All / Positif / Netral / Negatif)
- Badge warna sesuai sentimen dominan
- Total unique count dinamis

---

## Ringkasan File yang Harus Diubah

| Aksi | File |
|---|---|
| 🆕 **BUAT BARU** | `backend/services/keyword_service.py` |
| ✏️ **MODIFIKASI** | `backend/routes/analysis_routes.py` |
| ✏️ **MODIFIKASI** | `frontend/src/stores/crawlStore.js` |
| ✏️ **MODIFIKASI** | `frontend/src/components/dashboard/TopKeywords.vue` |
