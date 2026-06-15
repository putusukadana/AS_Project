# Issue: Upload File Excel/CSV/JSON pada Extraction Parameters (DataEngine)

## Deskripsi Singkat

Saat ini, halaman **DataEngine** hanya mendukung 2 mode input di `ExtractionPanel.vue`:
1. **Keyword** — mengetik kata kunci untuk crawling TikTok
2. **URL** — menempel URL video TikTok

**Fitur baru ini** menambahkan mode ke-3: **Upload File**, yang memungkinkan user mengunggah file berformat **Excel (.xlsx)**, **CSV (.csv)**, atau **JSON (.json)** yang berisi data komentar/teks. Data dari file tersebut akan di-inject langsung ke pipeline NLP (Obsidian) **tanpa perlu crawling**, sehingga user bisa langsung menjalankan preprocessing + analisis sentimen terhadap data mereka sendiri.

---

## Alur Kerja Fitur (User Flow)

```
1. User membuka halaman DataEngine
2. User klik tab "upload" di Mode Switcher (sebelah keyword & url)
3. Area input berubah menjadi drag-and-drop zone + tombol browse file
4. User memilih file .xlsx / .csv / .json
5. Frontend menampilkan preview: nama file, ukuran, jumlah baris
6. User klik "🚀 Mulai Proses" (bukan "Mulai Crawling")
7. Frontend mengirim file ke backend via multipart/form-data
8. Backend mem-parse file, mengekstrak kolom teks, mengubah ke format _current_data
9. Backend mengembalikan data dalam format yang sama dengan hasil crawl
10. Frontend menerima response dan langsung menjalankan pipeline NLP otomatis
11. User melihat hasil di ResultPanel (sama persis seperti flow crawling biasa)
```

---

## Kondisi Kode Saat Ini

| Komponen | File | Kondisi |
|---|---|---|
| Mode Switcher | `ExtractionPanel.vue` line 8-18 | ✅ Sudah ada, tapi hanya `keyword` dan `url` |
| Backend Upload Route | `backend/routes/` | ❌ Tidak ada endpoint upload file |
| Backend Upload Service | `backend/services/` | ❌ Tidak ada service parsing file |
| Frontend Upload UI | `ExtractionPanel.vue` | ❌ Tidak ada UI upload |
| Frontend Store | `crawlStore.js` | ❌ Tidak ada method upload |
| Pipeline Integration | `pipeline_service.py` → `set_current_data()` | ✅ Sudah ada, tinggal pakai |

---

## Struktur Data yang Diharapkan

### Format File yang Diterima

User harus menyiapkan file dengan **minimal 1 kolom teks**. Sistem akan mencoba mendeteksi kolom teks secara otomatis.

**Contoh CSV:**
```csv
text,username,date
"Produk ini bagus sekali","user1","2025-06-01"
"Pelayanan kurang memuaskan","user2","2025-06-02"
```

**Contoh JSON:**
```json
[
  {"text": "Produk ini bagus sekali", "username": "user1"},
  {"text": "Pelayanan kurang memuaskan", "username": "user2"}
]
```

**Contoh Excel:** Sama seperti CSV tapi dalam format .xlsx

### Format Output Backend (Harus Sama dengan Hasil Crawl)

Backend harus mengubah data file menjadi format berikut agar kompatibel dengan pipeline yang sudah ada:

```json
[
  {
    "video_id": "upload_1718434463",
    "platform": "upload",
    "description": "Data upload dari file: dataset.csv",
    "comment_sample": [
      {
        "text": "Produk ini bagus sekali",
        "raw_text": "Produk ini bagus sekali",
        "user_unique_id": "user1"
      },
      {
        "text": "Pelayanan kurang memuaskan",
        "raw_text": "Pelayanan kurang memuaskan",
        "user_unique_id": "user2"
      }
    ]
  }
]
```

> ⚠️ **PENTING**: Format ini **harus persis** mengikuti struktur `_current_data` di `pipeline_service.py` agar semua step pipeline (emoji_conversion, cleansing, normalization, stopwords, stemming) bisa berjalan tanpa modifikasi.

---

## Tahapan Implementasi

---

### Tahap 1: Install Dependency Backend — `openpyxl`

**Tujuan:** Menambahkan library untuk membaca file Excel (.xlsx).

**Langkah:**
1. Buka terminal di folder `backend/`
2. Jalankan:
   ```bash
   pip install openpyxl python-multipart
   ```
   - `openpyxl` → untuk membaca file Excel
   - `python-multipart` → **WAJIB** agar FastAPI bisa menerima `UploadFile` (form/multipart)

**Catatan:** Library `pandas`, `json`, dan `csv` sudah built-in Python, tidak perlu install.

---

### Tahap 2: Buat Backend Service — `upload_service.py`

**Buat file baru:** `backend/services/upload_service.py`

File ini bertanggung jawab untuk:
- Menerima file yang di-upload (bytes)
- Mendeteksi tipe file berdasarkan ekstensi
- Mem-parse file menjadi list of dict
- Mendeteksi kolom teks secara otomatis (cari kolom bernama `text`, `comment`, `komentar`, `content`, `review`, dll.)
- Mengubah data ke format `_current_data` yang kompatibel dengan pipeline

**Kode lengkap:**

```python
# backend/services/upload_service.py

import csv
import json
import io
import time
from typing import List, Dict, Any, Optional

import pandas as pd


# Daftar nama kolom yang mungkin berisi teks utama
TEXT_COLUMN_CANDIDATES = [
    "text", "comment", "komentar", "content", "review",
    "message", "pesan", "caption", "isi", "teks",
    "comment_text", "review_text", "body"
]

# Daftar nama kolom yang mungkin berisi username/author
AUTHOR_COLUMN_CANDIDATES = [
    "username", "user", "author", "nama", "name",
    "user_unique_id", "commenter", "reviewer", "pengguna"
]


def _detect_column(columns: List[str], candidates: List[str]) -> Optional[str]:
    """Mendeteksi kolom berdasarkan daftar kandidat (case-insensitive)."""
    col_lower_map = {c.lower().strip(): c for c in columns}
    for candidate in candidates:
        if candidate in col_lower_map:
            return col_lower_map[candidate]
    return None


def _parse_csv(file_bytes: bytes) -> List[Dict[str, Any]]:
    """Parse file CSV menjadi list of dict."""
    text = file_bytes.decode("utf-8-sig")  # utf-8-sig handles BOM
    reader = csv.DictReader(io.StringIO(text))
    return [row for row in reader]


def _parse_json(file_bytes: bytes) -> List[Dict[str, Any]]:
    """Parse file JSON menjadi list of dict."""
    text = file_bytes.decode("utf-8-sig")
    data = json.loads(text)
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        # Coba cari key yang berisi list (misalnya {"data": [...], "comments": [...]})
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                return value
        # Jika tidak ada list, wrap dict sebagai single item
        return [data]
    return []


def _parse_excel(file_bytes: bytes) -> List[Dict[str, Any]]:
    """Parse file Excel (.xlsx) menjadi list of dict."""
    df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
    # Hapus baris yang semua kolomnya NaN
    df = df.dropna(how="all")
    # Convert NaN ke empty string
    df = df.fillna("")
    return df.to_dict(orient="records")


def parse_uploaded_file(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Parse file yang di-upload dan konversi ke format _current_data.

    Returns:
        {
            "status": "success" | "error",
            "message": str,
            "total": int,
            "signal_quality": int,
            "data": list   # format sama dengan hasil crawl
        }
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    # 1. Parse file sesuai ekstensi
    try:
        if ext == "csv":
            rows = _parse_csv(file_bytes)
        elif ext == "json":
            rows = _parse_json(file_bytes)
        elif ext in ("xlsx", "xls"):
            rows = _parse_excel(file_bytes)
        else:
            return {
                "status": "error",
                "message": f"Format file '.{ext}' tidak didukung. Gunakan .csv, .json, atau .xlsx",
                "total": 0,
                "signal_quality": 0,
                "data": []
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Gagal membaca file: {str(e)}",
            "total": 0,
            "signal_quality": 0,
            "data": []
        }

    if not rows:
        return {
            "status": "error",
            "message": "File kosong atau tidak berisi data yang valid.",
            "total": 0,
            "signal_quality": 0,
            "data": []
        }

    # 2. Deteksi kolom teks dan author
    columns = list(rows[0].keys())
    text_col = _detect_column(columns, TEXT_COLUMN_CANDIDATES)
    author_col = _detect_column(columns, AUTHOR_COLUMN_CANDIDATES)

    # Jika tidak ditemukan kolom teks, gunakan kolom pertama
    if not text_col:
        text_col = columns[0]

    # 3. Bangun comment_sample dari rows
    comment_sample = []
    for row in rows:
        teks = str(row.get(text_col, "")).strip()
        if not teks:
            continue
        comment = {
            "text": teks,
            "raw_text": teks,
            "user_unique_id": str(row.get(author_col, "Unknown")).strip() if author_col else "Unknown"
        }
        comment_sample.append(comment)

    if not comment_sample:
        return {
            "status": "error",
            "message": f"Tidak ditemukan data teks yang valid di kolom '{text_col}'.",
            "total": 0,
            "signal_quality": 0,
            "data": []
        }

    # 4. Bungkus dalam format _current_data (1 "video" virtual berisi semua komentar)
    virtual_video = {
        "video_id": f"upload_{int(time.time())}",
        "platform": "upload",
        "description": f"Data upload dari file: {filename}",
        "comment_sample": comment_sample
    }

    return {
        "status": "success",
        "message": f"Berhasil memproses {len(comment_sample)} baris data dari '{filename}' (kolom teks: '{text_col}')",
        "total": len(comment_sample),
        "signal_quality": 95,
        "data": [virtual_video]
    }
```

---

### Tahap 3: Buat Backend Route — `upload_routes.py`

**Buat file baru:** `backend/routes/upload_routes.py`

```python
# backend/routes/upload_routes.py

from fastapi import APIRouter, UploadFile, File
from services.upload_service import parse_uploaded_file
from services.pipeline_service import set_current_data

router = APIRouter(prefix="/api/v1/upload", tags=["upload"])

# Batas ukuran file: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint untuk upload file Excel/CSV/JSON.
    File akan di-parse dan dikonversi ke format pipeline.
    """
    # Validasi tipe file
    allowed_extensions = ["csv", "json", "xlsx", "xls"]
    filename = file.filename or "unknown"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in allowed_extensions:
        return {
            "status": "error",
            "message": f"Tipe file '.{ext}' tidak didukung. Gunakan: {', '.join(allowed_extensions)}",
            "total": 0,
            "signal_quality": 0,
            "data": []
        }

    # Baca file content
    file_bytes = await file.read()

    # Validasi ukuran file
    if len(file_bytes) > MAX_FILE_SIZE:
        return {
            "status": "error",
            "message": f"Ukuran file terlalu besar ({len(file_bytes) // 1024 // 1024}MB). Maksimal 10MB.",
            "total": 0,
            "signal_quality": 0,
            "data": []
        }

    # Parse file
    result = parse_uploaded_file(file_bytes, filename)

    # Jika berhasil, set data ke pipeline
    if result["status"] == "success":
        set_current_data(result["data"])

    return result
```

---

### Tahap 4: Daftarkan Route Upload di `main.py`

**File:** `backend/main.py`

Tambahkan 2 baris berikut di bagian import dan include router:

```python
# Tambahkan SETELAH baris: from routes.analysis_routes import router as analysis_router
from routes.upload_routes import router as upload_router

# Tambahkan SETELAH baris: app.include_router(analysis_router)
app.include_router(upload_router)
```

**Lokasi tepat di file (referensi baris):**

```diff
 from routes.crawl_routes import router as crawl_router
 from routes.pipeline_routes import router as pipeline_router
 from routes.analysis_routes import router as analysis_router
+from routes.upload_routes import router as upload_router

 app.include_router(crawl_router)
 app.include_router(pipeline_router)
 app.include_router(analysis_router)
+app.include_router(upload_router)
```

---

### Tahap 5: Tambahkan Method Upload di Frontend Store — `crawlStore.js`

**File:** `frontend/src/stores/crawlStore.js`

**a. Tambahkan method `uploadFile()` setelah method `startCrawl`:**

```javascript
const uploadFile = async ({ file, onStatus }) => {
  onStatus({ type: "info", message: `📁 Mengupload file: ${file.name} (${(file.size / 1024).toFixed(1)} KB)` });
  try {
    const formData = new FormData();
    formData.append("file", file);

    const res = await api.post("/upload/file", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    if (res.data.status === "error") {
      onStatus({ type: "error", message: `❌ ${res.data.message}` });
      return;
    }

    rawData.value = res.data.data;
    stats.value = { total: res.data.total, quality: res.data.signal_quality };
    pipelineMeta.value = {};
    keywords.value = { overall: [], by_label: {} };

    // Reset pipeline status
    pipelineStatus.value = {
      emoji_conversion: "idle",
      cleansing: "idle",
      normalization: "idle",
      stopwords: "idle",
      stemming: "idle",
    };

    onStatus({ type: "success", message: `✅ ${res.data.total} baris data berhasil dimuat — ${res.data.message}` });

    // Otomatis jalankan pipeline
    await runPipeline(onStatus);
  } catch (err) {
    onStatus({ type: "error", message: `❌ Upload gagal: ${err.message}` });
  }
};
```

**b. Expose `uploadFile` di return statement:**

```diff
 return {
   rawData,
   stats,
   pipelineStatus,
   isAnalyzing,
   sentimentSummary,
   analyzedData,
   pipelineMeta,
   keywords,
   startCrawl,
+  uploadFile,
   runSentimentAnalysis,
   fetchKeywords,
 };
```

---

### Tahap 6: Update UI `ExtractionPanel.vue` — Tambahkan Mode Upload

**File:** `frontend/src/components/dataengine/ExtractionPanel.vue`

Ini adalah perubahan terbesar. Berikut tahapan detailnya:

#### 6a. Tambahkan "upload" ke Mode Switcher

**Cari baris 10 (mode switcher loop):**

```diff
-          v-for="mode in ['keyword', 'url']"
+          v-for="mode in ['keyword', 'url', 'upload']"
```

#### 6b. Tambahkan state baru di `<script setup>`

Tambahkan setelah `const crawlStatus = ref([]);` (sekitar baris 172):

```javascript
const uploadedFile = ref(null);
const isDragOver = ref(false);
```

#### 6c. Tambahkan UI Upload Zone

Tambahkan **SETELAH** penutup `</div>` dari blok "Input Area" (setelah baris 80) dan **SEBELUM** blok "Jumlah Video" (baris 82):

```html
    <!-- Upload File Area -->
    <div v-if="extractionMode === 'upload'" class="mt-8 space-y-3">
      <label class="block text-sm font-bold text-slate-500 uppercase tracking-wider">Upload Dataset</label>
      
      <!-- Drag & Drop Zone -->
      <div
        class="relative border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer"
        :class="isDragOver 
          ? 'border-indigo-400 bg-indigo-50' 
          : 'border-slate-200 bg-slate-50 hover:border-slate-300 hover:bg-slate-100'"
        @dragover.prevent="isDragOver = true"
        @dragleave.prevent="isDragOver = false"
        @drop.prevent="handleFileDrop"
        @click="$refs.fileInput.click()"
      >
        <input
          ref="fileInput"
          type="file"
          accept=".csv,.json,.xlsx,.xls"
          class="hidden"
          @change="handleFileSelect"
        />

        <!-- Empty State -->
        <div v-if="!uploadedFile">
          <span class="text-4xl block mb-3">📂</span>
          <p class="text-sm font-bold text-slate-600">
            Drag & drop file di sini, atau <span class="text-indigo-600 underline">browse</span>
          </p>
          <p class="text-[11px] text-slate-400 mt-2 font-medium">
            Format: .xlsx, .csv, .json — Maks 10MB
          </p>
        </div>

        <!-- File Selected State -->
        <div v-else class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <span class="text-2xl">
              {{ uploadedFile.name.endsWith('.csv') ? '📊' : uploadedFile.name.endsWith('.json') ? '📋' : '📗' }}
            </span>
            <div class="text-left">
              <p class="text-sm font-bold text-slate-800 truncate max-w-[200px]">{{ uploadedFile.name }}</p>
              <p class="text-[11px] text-slate-400 font-medium">{{ (uploadedFile.size / 1024).toFixed(1) }} KB</p>
            </div>
          </div>
          <button
            class="text-xs font-bold text-rose-500 hover:text-rose-700 bg-rose-50 hover:bg-rose-100 px-3 py-1.5 rounded-lg transition-all"
            @click.stop="uploadedFile = null"
          >
            ✕ Hapus
          </button>
        </div>
      </div>

      <p class="text-[11px] text-slate-400 pl-1 font-medium italic">
        * File harus memiliki kolom teks (misal: "text", "comment", "review", "content"). Kolom pertama akan digunakan jika tidak terdeteksi.
      </p>
    </div>
```

#### 6d. Sembunyikan Input Area biasa saat mode upload

**Cari blok "Input Area" (baris 41):**

Tambahkan `v-if="extractionMode !== 'upload'"` pada div wrapper:

```diff
-    <div class="mt-8 space-y-3">
+    <div class="mt-8 space-y-3" v-if="extractionMode !== 'upload'">
```

#### 6e. Sembunyikan "Jumlah Video" dan "Rentang Waktu" saat mode upload

**Jumlah Video — cari baris 83:**

```diff
-    <div class="mt-6 space-y-3" :class="{ 'opacity-30 pointer-events-none': extractionMode === 'url' }">
+    <div class="mt-6 space-y-3" v-if="extractionMode !== 'upload'" :class="{ 'opacity-30 pointer-events-none': extractionMode === 'url' }">
```

**Rentang Waktu — cari baris 101:**

```diff
-    <div class="mt-8 space-y-3" :class="{ 'opacity-30 pointer-events-none': extractionMode === 'url' }">
+    <div class="mt-8 space-y-3" v-if="extractionMode !== 'upload'" :class="{ 'opacity-30 pointer-events-none': extractionMode === 'url' }">
```

#### 6f. Update tombol aksi (label dan disabled logic)

**Cari baris 124-131 (tombol aksi):**

```diff
     <button
       class="w-full p-4 bg-indigo-600 text-white rounded-xl font-bold mt-8 shadow-lg shadow-indigo-100 hover:bg-indigo-700 hover:-translate-y-0.5 transition-all active:scale-95 disabled:opacity-50 disabled:translate-y-0 disabled:shadow-none"
-      :disabled="!canCrawl || isCrawling"
+      :disabled="!canCrawl || isCrawling || isUploading"
       @click="startCrawl"
     >
-      <span v-if="isCrawling" class="animate-spin mr-2 inline-block">⏳</span>
-      {{ isCrawling ? "Crawling Data..." : "🚀 Mulai Crawling" }}
+      <span v-if="isCrawling || isUploading" class="animate-spin mr-2 inline-block">⏳</span>
+      {{ isUploading ? "Memproses File..." : isCrawling ? "Crawling Data..." : extractionMode === 'upload' ? "📁 Mulai Proses File" : "🚀 Mulai Crawling" }}
     </button>
```

#### 6g. Tambahkan method handler dan update logic di `<script setup>`

Tambahkan setelah `const videoLimit = ref(0);` (baris 208):

```javascript
const isUploading = ref(false);

// Handler drag & drop
const handleFileDrop = (event) => {
  isDragOver.value = false;
  const files = event.dataTransfer.files;
  if (files.length > 0) {
    validateAndSetFile(files[0]);
  }
};

// Handler input file biasa
const handleFileSelect = (event) => {
  const files = event.target.files;
  if (files.length > 0) {
    validateAndSetFile(files[0]);
  }
};

// Validasi file
const validateAndSetFile = (file) => {
  const allowedExts = [".csv", ".json", ".xlsx", ".xls"];
  const ext = "." + file.name.split(".").pop().toLowerCase();
  
  if (!allowedExts.includes(ext)) {
    alert("Format file tidak didukung. Gunakan .csv, .json, atau .xlsx");
    return;
  }
  
  if (file.size > 10 * 1024 * 1024) {
    alert("Ukuran file melebihi 10MB");
    return;
  }
  
  uploadedFile.value = file;
};
```

#### 6h. Update `canCrawl` computed untuk mendukung mode upload

**Cari baris 174-177 (computed canCrawl):**

```diff
 const canCrawl = computed(() => {
+  if (extractionMode.value === "upload") return uploadedFile.value !== null;
   if (extractionMode.value === "url") return keyword.value.trim().includes("tiktok.com");
   return selectedPlatforms.value.length > 0 && keyword.value.trim().length > 0;
 });
```

#### 6i. Update `startCrawl` method untuk menangani mode upload

**Cari baris 187 (const startCrawl):**

Tambahkan pengecekan mode upload di awal fungsi:

```diff
 const startCrawl = async () => {
   if (!canCrawl.value || isCrawling.value) return;
+
+  // Mode Upload
+  if (extractionMode.value === "upload") {
+    isUploading.value = true;
+    crawlStatus.value = [];
+    try {
+      await crawlStore.uploadFile({
+        file: uploadedFile.value,
+        onStatus: (log) => {
+          crawlStatus.value.push(log);
+        },
+      });
+    } finally {
+      isUploading.value = false;
+    }
+    return;
+  }
+
   isCrawling.value = true;
   // ... sisa kode tetap sama
```

---

### Tahap 7: (Opsional) Tambahkan Platform Icon di Komponen Lain

Jika di komponen lain (misalnya `RawSnapshotTable.vue`) ada pengecekan platform berdasarkan icon, tambahkan case untuk platform `"upload"`:

```javascript
// Contoh mapping yang mungkin ada:
case "upload": return "📁";
```

> Cek di `RawSnapshotTable.vue` apakah ada mapping platform → icon. Jika ya, tambahkan case "upload".

---

## Ringkasan File yang Harus Diubah

| Aksi | File | Tingkat Kesulitan |
|---|---|---|
| 🆕 **BUAT BARU** | `backend/services/upload_service.py` | 🟡 Sedang |
| 🆕 **BUAT BARU** | `backend/routes/upload_routes.py` | 🟢 Mudah |
| ✏️ **MODIFIKASI** (2 baris) | `backend/main.py` | 🟢 Mudah |
| ✏️ **MODIFIKASI** (tambah method) | `frontend/src/stores/crawlStore.js` | 🟡 Sedang |
| ✏️ **MODIFIKASI** (terbesar) | `frontend/src/components/dataengine/ExtractionPanel.vue` | 🟠 Kompleks |
| ⚙️ **INSTALL** | `pip install openpyxl python-multipart` | 🟢 Mudah |

---

## Checklist Implementasi

- [ ] `pip install openpyxl python-multipart` di folder backend
- [ ] Buat `backend/services/upload_service.py` (copy kode di Tahap 2)
- [ ] Buat `backend/routes/upload_routes.py` (copy kode di Tahap 3)
- [ ] Tambahkan 2 baris di `backend/main.py` (Tahap 4)
- [ ] Tambahkan method `uploadFile` di `crawlStore.js` (Tahap 5)
- [ ] Update `ExtractionPanel.vue` — mode switcher (Tahap 6a)
- [ ] Update `ExtractionPanel.vue` — state baru (Tahap 6b)
- [ ] Update `ExtractionPanel.vue` — upload UI zone (Tahap 6c)
- [ ] Update `ExtractionPanel.vue` — sembunyikan input biasa (Tahap 6d)
- [ ] Update `ExtractionPanel.vue` — sembunyikan video/waktu (Tahap 6e)
- [ ] Update `ExtractionPanel.vue` — label tombol (Tahap 6f)
- [ ] Update `ExtractionPanel.vue` — handler methods (Tahap 6g)
- [ ] Update `ExtractionPanel.vue` — canCrawl logic (Tahap 6h)
- [ ] Update `ExtractionPanel.vue` — startCrawl upload mode (Tahap 6i)
- [ ] (Opsional) Update platform icon di komponen lain (Tahap 7)

---

## Cara Menguji (Testing)

### Test 1: Upload CSV
1. Buat file `test.csv` dengan isi:
   ```csv
   text,username
   "Saya suka produk ini","testuser1"
   "Pelayanan sangat buruk","testuser2"
   "Biasa saja tidak ada yang spesial","testuser3"
   ```
2. Buka halaman DataEngine → pilih mode **Upload**
3. Drag & drop atau browse file `test.csv`
4. Klik "📁 Mulai Proses File"
5. **Expected:** Data muncul di ResultPanel, pipeline otomatis berjalan

### Test 2: Upload JSON
1. Buat file `test.json`:
   ```json
   [
     {"comment": "Bagus sekali!", "user": "alice"},
     {"comment": "Jelek banget", "user": "bob"}
   ]
   ```
2. Upload via mode Upload
3. **Expected:** Kolom `comment` terdeteksi otomatis sebagai kolom teks

### Test 3: Upload Excel
1. Buat file `test.xlsx` dengan kolom `review` dan `nama`
2. Upload via mode Upload
3. **Expected:** Kolom `review` terdeteksi otomatis

### Test 4: Error Handling
1. Upload file `.txt` → **Expected:** Error "format tidak didukung"
2. Upload file kosong → **Expected:** Error "file kosong"
3. Upload file >10MB → **Expected:** Error "terlalu besar"

### Test 5: Full Pipeline
1. Upload CSV yang valid
2. Tunggu pipeline selesai (emoji → cleansing → normalization → stopwords → stemming)
3. Klik "Analisis Sentimen" di ObsidianPipeline
4. **Expected:** Sentimen berhasil dianalisis, dashboard menampilkan hasil

---

## Catatan Penting untuk Implementor

1. **JANGAN ubah `pipeline_service.py`** — Fungsi `set_current_data()` sudah cukup untuk menerima data dari upload. Kunci keberhasilannya adalah memastikan format output `upload_service.py` **identik** dengan format output crawling.

2. **Content-Type**: Saat mengirim file dari frontend, HARUS menggunakan `multipart/form-data`, BUKAN `application/json`. Axios akan otomatis set header jika menggunakan `FormData`.

3. **Pastikan `python-multipart` terinstall** — Tanpa library ini, FastAPI akan error saat menerima `UploadFile`. Error-nya: `"Form data requires 'python-multipart' to be installed"`.

4. **Encoding file**: Service menggunakan `utf-8-sig` untuk handle BOM (Byte Order Mark) yang sering muncul di file CSV dari Excel.

5. **Kolom teks tidak ditemukan**: Jika tidak ada kolom yang cocok dengan `TEXT_COLUMN_CANDIDATES`, sistem otomatis menggunakan kolom pertama. User tetap akan diberitahu kolom mana yang digunakan via response message.
