# Issue: Fitur Pembatasan Jumlah Video Crawling & Crawling Komentar Tanpa Batas

## Deskripsi Singkat
Menambahkan input baru pada halaman **Data Engine** di bawah kolom pencarian kata kunci (`keyword`) yang memungkinkan pengguna menentukan **jumlah video yang ingin di-crawling**. Jika diisi `0`, sistem akan mengambil semua video yang tersedia. Jika diisi angka `> 0`, sistem hanya mengambil sejumlah video sesuai angka yang ditentukan.

Selain itu, untuk **komentar yang di-crawling**, tidak ada batasan jumlah — sistem akan terus mengambil komentar hingga habis atau hingga kuota API RapidAPI habis. Jika kuota API habis (error 429 atau `remaining = 0`), proses crawling langsung diselesaikan secara *graceful* tanpa menampilkan error fatal.

---

## Kebutuhan Fitur (Requirements)
1. **Frontend UI**: Tambahkan input angka (*number input*) di bawah kolom kata kunci pada komponen `ExtractionPanel.vue` untuk menentukan jumlah video yang akan di-crawl.
2. **Frontend Logic**: Kirim nilai `video_limit` ke backend sebagai bagian dari *request body* saat memulai crawling.
3. **Backend API**: Terima parameter `video_limit` di endpoint `/api/v1/crawl/start` dan teruskan ke service layer.
4. **Backend Service**: Terapkan logika pembatasan jumlah video dan hapus batasan jumlah komentar per video. Jika kuota API habis saat mengambil komentar, proses selesai secara *graceful*.

---

## Tahapan Implementasi (Step-by-Step Guide)

Dokumen ini ditujukan bagi programmer junior atau asisten AI pendamping untuk mengimplementasikan fitur ini secara terstruktur.

### Tahap 1: Tambahkan Input "Jumlah Video" di Frontend UI

Buka file [ExtractionPanel.vue](file:///c:/Users/User/webAS/AS_Project/frontend/src/components/dataengine/ExtractionPanel.vue).

#### A. Tambahkan State Baru
Di dalam blok `<script setup>` (sekitar baris 150-154), tambahkan sebuah reactive variable baru untuk menyimpan jumlah video:
```javascript
const videoLimit = ref(0); // 0 = ambil semua video
```

#### B. Tambahkan Elemen Input di Template
Cari bagian penutup dari input kata kunci (sekitar baris 76-80, setelah penutup `</div>` dan `<p>` dari input area). Tambahkan blok input baru **di bawahnya**, sebelum bagian "Rentang Waktu":

```html
    <!-- Jumlah Video -->
    <div class="mt-6 space-y-3" :class="{ 'opacity-30 pointer-events-none': extractionMode === 'url' }">
      <label class="block text-sm font-bold text-slate-500 uppercase tracking-wider">Jumlah Video</label>
      <div class="relative group">
        <span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-indigo-500 transition-colors">🎬</span>
        <input
          v-model.number="videoLimit"
          type="number"
          min="0"
          placeholder="0 = Ambil semua video"
          class="w-full pl-11 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 placeholder:text-slate-400 outline-none focus:bg-white focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all font-medium"
        />
      </div>
      <p class="text-[11px] text-slate-400 pl-1 font-medium italic">
        * Isi 0 untuk mengambil semua video. Isi angka > 0 untuk membatasi jumlah video yang di-crawl.
      </p>
    </div>
```

#### C. Kirim `videoLimit` ke Store saat Crawling
Cari fungsi `startCrawl` (sekitar baris 169-187). Tambahkan `video_limit` ke dalam objek parameter yang dikirim:

**Sebelum:**
```javascript
    await crawlStore.startCrawl({
      platforms: extractionMode.value === 'url' ? ['tiktok'] : selectedPlatforms.value,
      keyword: keyword.value,
      start_date: (extractionMode.value === 'keyword' && startDate.value) ? new Date(startDate.value).toISOString() : null,
      end_date: (extractionMode.value === 'keyword' && endDate.value) ? new Date(endDate.value).toISOString() : null,
      onStatus: (log) => {
        crawlStatus.value.push(log);
      },
    });
```

**Sesudah:**
```javascript
    await crawlStore.startCrawl({
      platforms: extractionMode.value === 'url' ? ['tiktok'] : selectedPlatforms.value,
      keyword: keyword.value,
      video_limit: videoLimit.value,  // <-- Tambahkan baris ini
      start_date: (extractionMode.value === 'keyword' && startDate.value) ? new Date(startDate.value).toISOString() : null,
      end_date: (extractionMode.value === 'keyword' && endDate.value) ? new Date(endDate.value).toISOString() : null,
      onStatus: (log) => {
        crawlStatus.value.push(log);
      },
    });
```

---

### Tahap 2: Teruskan `video_limit` melalui State Store

Buka file [crawlStore.js](file:///c:/Users/User/webAS/AS_Project/frontend/src/stores/crawlStore.js).

Cari fungsi `startCrawl` (baris 17). Tambahkan `video_limit` ke dalam destructuring parameter dan kirim ke API:

**Sebelum:**
```javascript
  const startCrawl = async ({ platforms, keyword, start_date, end_date, onStatus }) => {
    onStatus({ type: "info", message: `🚀 Memulai crawl untuk: "${keyword}"` });
    try {
      const res = await api.post("/crawl/start", { 
        platforms, 
        keyword,
        start_date: start_date || null,
        end_date: end_date || null
      });
```

**Sesudah:**
```javascript
  const startCrawl = async ({ platforms, keyword, video_limit, start_date, end_date, onStatus }) => {
    onStatus({ type: "info", message: `🚀 Memulai crawl untuk: "${keyword}" (Video limit: ${video_limit || 'Semua'})` });
    try {
      const res = await api.post("/crawl/start", { 
        platforms, 
        keyword,
        video_limit: video_limit || 0,  // <-- Tambahkan baris ini
        start_date: start_date || null,
        end_date: end_date || null
      });
```

---

### Tahap 3: Terima Parameter `video_limit` di Backend API Route

Buka file [crawl_routes.py](file:///c:/Users/User/webAS/AS_Project/backend/routes/crawl_routes.py).

#### A. Tambahkan Field `video_limit` ke Pydantic Model
Cari class `CrawlRequest` (baris 11-15) dan tambahkan field baru:

**Sebelum:**
```python
class CrawlRequest(BaseModel):
    platforms: List[str]
    keyword: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
```

**Sesudah:**
```python
class CrawlRequest(BaseModel):
    platforms: List[str]
    keyword: str
    video_limit: Optional[int] = 0  # 0 = ambil semua, >0 = batasi jumlah video
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
```

#### B. Teruskan `video_limit` ke Fungsi `run_crawl`
Cari fungsi `start_crawl` (baris 17-32) dan tambahkan parameter:

**Sebelum:**
```python
@router.post("/start")
async def start_crawl(body: CrawlRequest):
    result = await run_crawl(
        body.platforms, 
        body.keyword, 
        body.start_date, 
        body.end_date
    )
```

**Sesudah:**
```python
@router.post("/start")
async def start_crawl(body: CrawlRequest):
    result = await run_crawl(
        body.platforms, 
        body.keyword,
        body.video_limit,      # <-- Tambahkan baris ini
        body.start_date, 
        body.end_date
    )
```

---

### Tahap 4: Teruskan `video_limit` di Service Orchestrator

Buka file [crawl_service.py](file:///c:/Users/User/webAS/AS_Project/backend/services/crawl_service.py).

#### A. Tambahkan Parameter `video_limit` pada Fungsi `run_crawl`

**Sebelum:**
```python
async def run_crawl(
    platforms: list, 
    keyword: str, 
    start_date: Optional[datetime.datetime] = None, 
    end_date: Optional[datetime.datetime] = None
) -> dict:
```

**Sesudah:**
```python
async def run_crawl(
    platforms: list, 
    keyword: str,
    video_limit: int = 0,  # <-- Tambahkan parameter ini
    start_date: Optional[datetime.datetime] = None, 
    end_date: Optional[datetime.datetime] = None
) -> dict:
```

#### B. Gunakan `video_limit` saat Memanggil `extract_tiktok_data`
Cari bagian pemanggilan `extract_tiktok_data` (sekitar baris 43-49):

**Sebelum:**
```python
            tiktok_res = extract_tiktok_data(
                keywords=item, 
                limit=100, # Lower safety limit per keyword for multi-search
                sort_by=sort_by,
                start_date=start_date, 
                end_date=end_date
            )
```

**Sesudah:**
```python
            tiktok_res = extract_tiktok_data(
                keywords=item, 
                limit=video_limit,  # 0 = ambil semua, >0 = sesuai user input
                sort_by=sort_by,
                start_date=start_date, 
                end_date=end_date
            )
```

---

### Tahap 5: Modifikasi Logika Crawling Komentar di TikTok Service

Buka file [crawl_tiktok_service.py](file:///c:/Users/User/webAS/AS_Project/backend/services/crawl_tiktok_service.py).

Perubahan utama ada di **dua area**: logika pengambilan komentar per video, dan penanganan kuota habis.

#### A. Hapus Batasan 20 Video untuk Komentar & Hapus Batasan `max_comments=20`
Cari blok kode pengambilan komentar (sekitar baris 170-179):

**Sebelum:**
```python
                        # Batasi pengambilan komentar hanya untuk 20 video teratas
                        if int(comment_count) >= 1 and len(collected_videos) < 20:
                            try:
                                # Ambil sampel komentar (dibatasi 20 untuk hemat kuota)
                                video_info["comment_sample"] = comment_scraper.get_comments(video_id, max_comments=20)
                            except Exception as e:
                                print(f"Error sampling comments for {video_id}: {e}")
                                video_info["comment_sample"] = []
                        else:
                            video_info["comment_sample"] = []
```

**Sesudah:**
```python
                        # Ambil SEMUA komentar tanpa batasan jumlah
                        if int(comment_count) >= 1:
                            try:
                                video_info["comment_sample"] = comment_scraper.get_comments(video_id, max_comments=None)
                            except Exception as e:
                                print(f"Error sampling comments for {video_id}: {e}")
                                video_info["comment_sample"] = []
                        else:
                            video_info["comment_sample"] = []
```

> **Penjelasan:** `max_comments=None` berarti tidak ada batas. Fungsi `get_comments` (baris 275) sudah mendukung `None` — lihat baris 286: `if max_comments and len(comments) >= max_comments: break`. Jika `max_comments` bernilai `None`, kondisi ini tidak pernah `True`, sehingga loop terus berjalan hingga semua komentar terambil.

#### B. Tangani Kuota API Habis secara Graceful di `get_comments`
Cari method `get_comments` pada class `TikTokCommentScraper` (baris 275-322). Tambahkan pengecekan kuota di dalam loop utama agar jika kuota habis, proses berhenti dengan *graceful* tanpa error:

**Sebelum (bagian dalam while loop, sekitar baris 288-321):**
```python
            try:
                params = {"videoId": video_id, "count": "20", "cursor": str(cursor)}
                response = safe_api_request(url, headers=headers, params=params, timeout=15)
                if not response or response.status_code != 200: break
                res_data = response.json()
```

**Sesudah:**
```python
            try:
                params = {"videoId": video_id, "count": "20", "cursor": str(cursor)}
                response = safe_api_request(url, headers=headers, params=params, timeout=15)
                
                # Jika API mengembalikan error (termasuk 429 quota habis), hentikan gracefully
                if not response or response.status_code != 200:
                    if response and response.status_code == 429:
                        print(f"[Komentar] Kuota API habis saat mengambil komentar video {video_id}. Menghentikan pengambilan komentar.")
                    break
                    
                # Cek sisa kuota dari header, jika 0 maka berhenti setelah proses response ini
                remaining = response.headers.get('x-ratelimit-requests-remaining')
                quota_exhausted = False
                if remaining is not None:
                    try:
                        if int(remaining) <= 0:
                            quota_exhausted = True
                    except:
                        pass
                
                res_data = response.json()
```

Kemudian, di bagian akhir loop (sebelum `except`), tambahkan pengecekan `quota_exhausted`:

**Tambahkan SEBELUM baris `except Exception as e:` (baris 319):**
```python
                # Jika kuota sudah habis, hentikan loop setelah memproses response terakhir
                if quota_exhausted:
                    print(f"[Komentar] Kuota API telah habis. Menyelesaikan crawling dengan {len(comments)} komentar yang sudah didapat.")
                    break
```

#### C. Tangani Kuota Habis Juga di `extract_tiktok_data`
Agar seluruh proses crawling video juga berhenti *graceful* saat kuota habis, tambahkan pengecekan serupa di fungsi `extract_tiktok_data` (baris 78-192).

Cari bagian dalam loop utama setelah pemanggilan `safe_api_request` (sekitar baris 118-120):

**Sebelum:**
```python
                querystring["cursor"] = current_cursor
                response = safe_api_request(url, headers=headers, params=querystring)
                if not response or response.status_code != 200:
                    break
```

**Sesudah:**
```python
                querystring["cursor"] = current_cursor
                response = safe_api_request(url, headers=headers, params=querystring)
                if not response or response.status_code != 200:
                    if response and response.status_code == 429:
                        print(f"[Video] Kuota API habis. Menyelesaikan crawling dengan {len(collected_videos)} video yang sudah didapat.")
                    break
```

---

### Tahap 6: Testing & Validasi

#### A. Pengujian Batas Video
1. Buka halaman **Data Engine** (`http://localhost:5173/data-engine`).
2. Masukkan kata kunci pencarian (misal: "kucing lucu").
3. Isi kolom **Jumlah Video** dengan angka `3`.
4. Klik **Mulai Crawling**.
5. **Ekspektasi:** Hanya 3 video yang muncul di tabel ringkasan ekstraksi.

#### B. Pengujian Tanpa Batas (Semua Video)
1. Isi kolom **Jumlah Video** dengan angka `0`.
2. Klik **Mulai Crawling**.
3. **Ekspektasi:** Sistem mengambil semua video yang tersedia dari API hingga halaman habis.

#### C. Pengujian Komentar Tanpa Batas
1. Crawl 1-2 video saja (`video_limit = 2`).
2. Setelah proses selesai, periksa jumlah komentar yang diambil pada preview.
3. **Ekspektasi:** Semua komentar dari video tersebut berhasil diambil (tidak dibatasi 20 komentar lagi).

#### D. Pengujian Kuota Habis (Graceful Stop)
1. Jika kuota API sudah mendekati habis, jalankan crawling.
2. **Ekspektasi:** Proses berhenti secara *graceful*, data yang sudah dikumpulkan tetap ditampilkan, dan tidak ada error fatal di UI. Log terminal backend menampilkan pesan informatif seperti `"Kuota API habis. Menyelesaikan crawling..."`.
