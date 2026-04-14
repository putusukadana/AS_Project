# Issue: Crawling TikTok Berdasarkan URL Video

## Overview
Pengguna memerlukan kemampuan untuk melakukan crawling pada satu video spesifik hanya dengan memasukkan **URL Video TikTok**. Sistem harus mengekstrak ID video dari URL tersebut, mengambil metadata video (deskripsi, pengunggah, waktu), dan kemudian menarik semua komentar serta balasan komentar menggunakan skrip yang sudah ada.

---

## Tahapan Implementasi

### 1. Backend: Fungsi Ekstraksi Video ID
**File:** `backend/services/crawl_service.py`

Buat fungsi pembantu (helper) untuk mengambil ID video dari berbagai format URL TikTok.
- **Tugas:** Gunakan regex untuk menangkap angka ID setelah string `/video/`.
- **Contoh Input:** `https://www.tiktok.com/@kamu/video/7311302323228167429`
- **Contoh Output:** `7311302323228167429`

### 2. Backend: Service Pengambilan Metadata Video
**File:** `backend/services/crawl_service.py`

Implementasikan fungsi untuk mendapatkan detail video berdasarkan ID.
- **API:** Gunakan `https://tiktok-api23.p.rapidapi.com/api/post/info` (referensi dari RapidAPI) atau endpoint serupa.
- **Tugas:** Kirim request dengan `videoId` dan ambil data:
  - `nickname` (Nama pengunggah)
  - `desc` / `text` (Deskripsi video)
  - `create_time` (Waktu unggah)
  - `post_url` (Link asli)

### 3. Backend: Integrasi ke `run_crawl`
**File:** `backend/services/crawl_service.py`

Modifikasi fungsi utama `run_crawl` agar bisa menangani input URL.
- **Logika:** 
  1. Jika input diawali dengan `http`, jalankan mode **URL Crawl**.
  2. Ekstrak `video_id`.
  3. Panggil fungsi metadata (Tahap 2).
  4. Jalankan `TikTokCommentScraper.get_comments(video_id)` untuk menarik komentar (Gunakan logic yang sudah ada).
  5. Masukkan metadata video dan data komentar ke dalam `all_data`.

### 4. Frontend: Penyesuaian Antarmuka (UI)
**File:** `frontend/src/components/dataengine/ExtractionPanel.vue`

Berikan opsi bagi pengguna untuk memilih jenis input.
- **Tugas:** 
  - Tambahkan tab atau checkbox: "Pencarian Kata Kunci" vs "Link Video Langsung".
  - Update placeholder input sesuai mode yang dipilih.
  - Kirim data ke backend.

### 5. Pengujian & Penanganan Error
- **Kasus Uji:** Masukkan URL video yang valid dan pastikan metadata video muncul di tabel Raw Snapshot beserta komentarnya.
- **Error Handling:** Berikan pesan error jika URL tidak valid atau `video_id` tidak ditemukan oleh API.

---

## Referensi Kode Integrasi API (Python)

```python
import requests

def get_video_by_url(video_id):
    url = "https://tiktok-api23.p.rapidapi.com/api/post/info" # Gunakan endpoint info untuk detail video
    querystring = {"videoId": video_id}
    headers = {
        "x-rapidapi-key": "YOUR_API_KEY", # Gunakan key yang ada di project
        "x-rapidapi-host": "tiktok-api23.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    return response.json()
```

---

## Catatan untuk Implementor
- Gunakan `TikTokCommentScraper` yang sudah ada untuk bagian komentar agar tidak menulis ulang kode.
- Pastikan `post_url` tetap disertakan di hasil akhir agar kolom link di tabel Snapshot tetap berfungsi.
