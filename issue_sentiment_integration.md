# Issue: Integrasi Model ML (DistilBERT) untuk Analisis Sentimen

## Deskripsi Singkat

Sistem saat ini memiliki model Machine Learning siap pakai (`backend/ml_model/`) berupa **DistilBERT fine-tuned** untuk klasifikasi sentimen 3 kelas (Positif, Netral, Negatif). Namun, endpoint `/api/v1/analysis/sentiment` masih berupa **placeholder kosong** dan dashboard masih menampilkan **data dummy hardcoded**.

Tujuan issue ini adalah menghubungkan model tersebut ke alur kerja sistem secara penuh, mulai dari backend hingga chart di dashboard.

---

## Informasi Model ML

- **Lokasi**: `backend/ml_model/`
- **File**:
  - `model.safetensors` — bobot model (~268 MB)
  - `tokenizer.json` + `tokenizer_config.json` — tokenizer DistilBERT
  - `config.json` — konfigurasi arsitektur
- **Arsitektur**: `DistilBertForSequenceClassification`
- **Jumlah Label**: 3 kelas
  - `LABEL_0` → **Negatif**
  - `LABEL_1` → **Netral**
  - `LABEL_2` → **Positif**
- **Input**: Teks bahasa Indonesia (sudah melalui pipeline preprocessing: emoji → cleansing → normalization → stopwords → stemming)
- **Max Token Length**: 512 token
- **Library yang dibutuhkan**: `transformers`, `torch`

---

## Kondisi Kode Saat Ini (Sebelum Implementasi)

| Komponen | File | Kondisi |
|---|---|---|
| Backend Route | `backend/routes/analysis_routes.py` | ⚠️ Placeholder, hanya return `{"status": "ok"}` |
| Backend Service | `backend/services/` | ❌ Tidak ada `sentiment_service.py` |
| Data Model | `backend/models.py` — `ProcessedData` | ❌ Tidak ada field `sentiment_label` dan `sentiment_score` |
| Frontend Store | `frontend/src/stores/crawlStore.js` | ⚠️ `runSentimentAnalysis()` memanggil API tapi tidak menyimpan hasil |
| Dashboard Chart | `frontend/src/components/dashboard/SentimentDistribution.vue` | ❌ Data dummy hardcoded |
| Dashboard Stats | `frontend/src/components/dashboard/StatCard.vue` | ❌ Data dummy hardcoded |
| AI Insights | `frontend/src/components/dashboard/AIInsightsEngine.vue` | ❌ Insights dummy hardcoded |

---

## Tahapan Implementasi

---

### Tahap 1: Install Dependency Python yang Dibutuhkan

Sebelum membuat service, pastikan library `transformers` dan `torch` sudah terinstall.

**Jalankan perintah berikut di terminal dari folder `backend`:**

```bash
py -m pip install transformers torch
```

> **Catatan untuk Junior Dev:** Proses instalasi `torch` bisa memakan waktu 5–15 menit karena ukurannya besar (~2 GB). Biarkan berjalan hingga selesai.

---

### Tahap 2: Buat File Service Baru — `sentiment_service.py`

Buat file baru: **`backend/services/sentiment_service.py`**

File ini bertanggung jawab memuat model dari disk dan melakukan prediksi sentimen pada satu atau banyak teks sekaligus.

```python
# backend/services/sentiment_service.py

import os
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

# =====================================================================
# KONSTANTA
# =====================================================================
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml_model")

# Mapping label index ke nama label yang mudah dibaca
LABEL_MAP = {
    0: "Negatif",
    1: "Netral",
    2: "Positif"
}

# =====================================================================
# INISIALISASI MODEL (hanya dilakukan sekali saat server pertama jalan)
# =====================================================================
print(f"[Sentiment] Memuat model dari {MODEL_DIR}...")
tokenizer = DistilBertTokenizer.from_pretrained(MODEL_DIR)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()  # Set ke mode evaluasi (tidak ada gradient update)
print("[Sentiment] Model berhasil dimuat.")


# =====================================================================
# FUNGSI UTAMA
# =====================================================================

def predict_sentiment(text: str) -> dict:
    """
    Melakukan prediksi sentimen untuk satu teks.

    Args:
        text (str): Teks yang sudah di-preprocess (stemmed_text)

    Returns:
        dict: {
            "label": "Positif" | "Netral" | "Negatif",
            "score": float (confidence 0.0 - 1.0),
            "label_index": int (0, 1, atau 2)
        }
    """
    if not text or not isinstance(text, str) or text.strip() == "":
        return {"label": "Netral", "score": 0.0, "label_index": 1}

    # Tokenisasi
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True
    )

    # Inferensi (tanpa menghitung gradient untuk hemat memori)
    with torch.no_grad():
        outputs = model(**inputs)

    # Ambil probabilitas menggunakan softmax
    probabilities = torch.softmax(outputs.logits, dim=-1)
    predicted_index = torch.argmax(probabilities, dim=-1).item()
    confidence_score = probabilities[0][predicted_index].item()

    return {
        "label": LABEL_MAP[predicted_index],
        "score": round(confidence_score, 4),
        "label_index": predicted_index
    }


async def run_sentiment_analysis() -> dict:
    """
    Menjalankan prediksi sentimen pada SEMUA komentar dalam _current_data
    (data global hasil pipeline dari pipeline_service.py).

    Mengembalikan hasil analisis lengkap beserta ringkasan statistik.
    """
    from services.pipeline_service import _current_data  # Import di sini agar selalu ambil versi terbaru

    if not _current_data:
        return {
            "status": "error",
            "message": "Tidak ada data. Jalankan pipeline preprocessing terlebih dahulu.",
            "data": [],
            "summary": {}
        }

    total_comments = 0
    sentiment_counts = {"Positif": 0, "Netral": 0, "Negatif": 0}

    # Loop setiap video
    for video in _current_data:
        if "comment_sample" not in video or not isinstance(video["comment_sample"], list):
            continue

        # Loop setiap komentar dalam video
        for comment in video["comment_sample"]:
            # Gunakan stemmed_text jika ada, fallback ke text
            text_to_analyze = comment.get("stemmed_text") or comment.get("text") or ""

            result = predict_sentiment(text_to_analyze)

            # Tambahkan hasil prediksi langsung ke object komentar
            comment["sentiment_label"] = result["label"]
            comment["sentiment_score"] = result["score"]

            # Akumulasi statistik
            sentiment_counts[result["label"]] += 1
            total_comments += 1

    # Hitung persentase
    summary = {}
    if total_comments > 0:
        summary = {
            "total_comments": total_comments,
            "positif": sentiment_counts["Positif"],
            "netral": sentiment_counts["Netral"],
            "negatif": sentiment_counts["Negatif"],
            "pct_positif": round(sentiment_counts["Positif"] / total_comments * 100, 1),
            "pct_netral": round(sentiment_counts["Netral"] / total_comments * 100, 1),
            "pct_negatif": round(sentiment_counts["Negatif"] / total_comments * 100, 1),
        }

    return {
        "status": "done",
        "message": f"Analisis selesai. {total_comments} komentar dianalisis.",
        "data": _current_data,   # Data dengan field sentiment_label & sentiment_score sudah ditambahkan
        "summary": summary
    }
```

---

### Tahap 3: Update Backend Route — `analysis_routes.py`

Ganti placeholder dengan pemanggilan fungsi service yang baru dibuat.

**File**: `backend/routes/analysis_routes.py`

**Sebelum:**
```python
from fastapi import APIRouter
router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])

@router.post("/sentiment")
async def run_sentiment():
    # Placeholder for sentiment analysis logic
    return {"status": "ok", "message": "Analisis sentimen berhasil dijalankan"}
```

**Sesudah:**
```python
from fastapi import APIRouter
from services.sentiment_service import run_sentiment_analysis

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])

@router.post("/sentiment")
async def run_sentiment():
    """
    Endpoint untuk menjalankan analisis sentimen pada data yang sudah
    melalui pipeline preprocessing (hasil stemming).
    """
    result = await run_sentiment_analysis()
    return result
```

---

### Tahap 4: Update Pydantic Model — `models.py`

Tambahkan field `sentiment_label` dan `sentiment_score` ke class `ProcessedData` agar data sentimen bisa disimpan ke MongoDB.

**File**: `backend/models.py`

Cari class `ProcessedData` (sekitar baris 38–48):

**Sebelum:**
```python
class ProcessedData(BaseModel):
    raw_text: str
    cleaned_text: str
    stemmed_text: str
    platform: Optional[str] = "tiktok"
    video_id: Optional[str] = None
    author: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
```

**Sesudah:**
```python
class ProcessedData(BaseModel):
    raw_text: str
    cleaned_text: str
    stemmed_text: str
    sentiment_label: Optional[str] = None   # <-- TAMBAHKAN: "Positif", "Netral", "Negatif"
    sentiment_score: Optional[float] = None  # <-- TAMBAHKAN: confidence score 0.0 - 1.0
    platform: Optional[str] = "tiktok"
    video_id: Optional[str] = None
    author: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
```

---

### Tahap 5: Update Frontend Store — `crawlStore.js`

Saat ini `runSentimentAnalysis()` memanggil API tapi tidak menyimpan hasilnya. Kita perlu menyimpan `summary` dan `data` agar bisa ditampilkan di dashboard.

**File**: `frontend/src/stores/crawlStore.js`

#### A. Tambahkan State untuk Menyimpan Hasil Sentimen

Cari baris awal store (sekitar baris 5–15) dan tambahkan dua state baru setelah `isAnalyzing`:

**Sebelum:**
```javascript
  const isAnalyzing = ref(false);

  const startCrawl = async ...
```

**Sesudah:**
```javascript
  const isAnalyzing = ref(false);
  const sentimentSummary = ref(null);  // <-- TAMBAHKAN
  const analyzedData = ref([]);         // <-- TAMBAHKAN

  const startCrawl = async ...
```

#### B. Update Fungsi `runSentimentAnalysis()`

Cari fungsi `runSentimentAnalysis` (sekitar baris 94–103):

**Sebelum:**
```javascript
  const runSentimentAnalysis = async () => {
    isAnalyzing.value = true;
    try {
      // Endpoint: /api/v1/analysis/sentiment
      await api.post("/analysis/sentiment");
      // Add notification or redirect to dashboard here if needed
    } finally {
      isAnalyzing.value = false;
    }
  };
```

**Sesudah:**
```javascript
  const runSentimentAnalysis = async () => {
    isAnalyzing.value = true;
    try {
      const res = await api.post("/analysis/sentiment");
      if (res.data && res.data.status === "done") {
        sentimentSummary.value = res.data.summary;  // <-- Simpan ringkasan
        analyzedData.value = res.data.data;          // <-- Simpan data lengkap
      }
    } catch (err) {
      console.error("Analisis sentimen gagal:", err.message);
    } finally {
      isAnalyzing.value = false;
    }
  };
```

#### C. Expose State Baru di Return

Cari blok `return` di akhir store (sekitar baris 105–112):

**Sebelum:**
```javascript
  return {
    rawData,
    stats,
    pipelineStatus,
    isAnalyzing,
    startCrawl,
    runSentimentAnalysis,
  };
```

**Sesudah:**
```javascript
  return {
    rawData,
    stats,
    pipelineStatus,
    isAnalyzing,
    sentimentSummary,  // <-- TAMBAHKAN
    analyzedData,       // <-- TAMBAHKAN
    startCrawl,
    runSentimentAnalysis,
  };
```

---

### Tahap 6: Update Dashboard Charts untuk Gunakan Data Real

#### A. Update `SentimentDistribution.vue`

Dashboard chart sentimen saat ini menggunakan data dummy. Ganti dengan data dari store.

**File**: `frontend/src/components/dashboard/SentimentDistribution.vue`

Ganti **seluruh blok `<script setup>`** (mulai baris 30 hingga akhir tag `</script>`) dengan:

```javascript
<script setup>
import { computed } from 'vue';
import { Bar } from 'vue-chartjs';
import {
  Chart as ChartJS, Title, Tooltip, Legend,
  BarElement, CategoryScale, LinearScale,
} from 'chart.js';
import { useCrawlStore } from '@/stores/crawlStore';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const crawlStore = useCrawlStore();

const chartData = computed(() => {
  const summary = crawlStore.sentimentSummary;

  if (!summary || summary.total_comments === 0) {
    return {
      labels: ['Belum Ada Data'],
      datasets: [
        { label: 'Positif',  backgroundColor: '#2563eb', data: [0], borderRadius: 6 },
        { label: 'Netral',   backgroundColor: '#4b5563', data: [0], borderRadius: 6 },
        { label: 'Negatif',  backgroundColor: '#dc2626', data: [0], borderRadius: 6 },
      ],
    };
  }

  return {
    labels: ['TikTok'],
    datasets: [
      { label: 'Positif',  backgroundColor: '#2563eb', data: [summary.positif],  borderRadius: 6 },
      { label: 'Netral',   backgroundColor: '#4b5563', data: [summary.netral],   borderRadius: 6 },
      { label: 'Negatif',  backgroundColor: '#dc2626', data: [summary.negatif],  borderRadius: 6 },
    ],
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#1e293b', padding: 12,
      titleFont: { size: 14, weight: 'bold' },
      bodyFont: { size: 13 }, cornerRadius: 12,
    },
  },
  scales: {
    x: { stacked: true, grid: { display: false }, ticks: { font: { weight: 'bold', size: 11 }, color: '#94a3b8' } },
    y: { stacked: true, grid: { color: '#f1f5f9' }, ticks: { font: { weight: 'bold', size: 11 }, color: '#94a3b8' } },
  },
};
</script>
```

#### B. Update `AIInsightsEngine.vue`

Ganti insights hardcoded dengan insight dinamis berdasarkan `sentimentSummary`.

**File**: `frontend/src/components/dashboard/AIInsightsEngine.vue`

Ganti seluruh blok `<script setup>` (baris 51–69) dengan:

```javascript
<script setup>
import { computed } from 'vue';
import { useCrawlStore } from '@/stores/crawlStore';

const crawlStore = useCrawlStore();

const insights = computed(() => {
  const s = crawlStore.sentimentSummary;

  if (!s || s.total_comments === 0) {
    return [
      { icon: '⏳', title: 'Menunggu Data', content: 'Jalankan crawling dan analisis sentimen terlebih dahulu untuk melihat insights.' },
    ];
  }

  const dominantLabel = s.pct_positif >= s.pct_negatif && s.pct_positif >= s.pct_netral
    ? 'Positif'
    : s.pct_negatif >= s.pct_netral ? 'Negatif' : 'Netral';

  return [
    {
      icon: '📊',
      title: 'Ringkasan Sentimen',
      content: `Dari ${s.total_comments} komentar: ${s.pct_positif}% Positif, ${s.pct_netral}% Netral, ${s.pct_negatif}% Negatif.`
    },
    {
      icon: dominantLabel === 'Positif' ? '📈' : dominantLabel === 'Negatif' ? '⚠️' : '➡️',
      title: 'Sentimen Dominan',
      content: `Sentimen dominan adalah ${dominantLabel} (${s['pct_' + dominantLabel.toLowerCase()]}%). ${
        dominantLabel === 'Negatif' ? 'Disarankan pemantauan ketat pada isu-isu yang beredar.' :
        dominantLabel === 'Positif' ? 'Persepsi publik secara umum positif terhadap topik ini.' :
        'Publik belum menunjukkan sentimen yang kuat ke arah tertentu.'
      }`
    },
    {
      icon: '🔢',
      title: 'Volume Data',
      content: `Total ${s.total_comments} komentar telah dianalisis: ${s.positif} positif, ${s.netral} netral, ${s.negatif} negatif.`
    }
  ];
});
</script>
```

#### C. Update `Dashboard.vue` — Ganti StatCard Hardcoded

**File**: `frontend/src/views/Dashboard.vue`

**Langkah 1** — Ganti seluruh blok `<script setup>` (baris 87–95):

```javascript
<script setup>
import { computed } from 'vue';
import AppTopbar from "@/components/layout/AppTopbar.vue";
import AppSidebar from "@/components/layout/AppSidebar.vue";
import SentimentDistribution from "@/components/dashboard/SentimentDistribution.vue";
import EmotionalSpectrum from "@/components/dashboard/EmotionalSpectrum.vue";
import TopKeywords from "@/components/dashboard/TopKeywords.vue";
import AIInsightsEngine from "@/components/dashboard/AIInsightsEngine.vue";
import StatCard from "@/components/dashboard/StatCard.vue";
import { useCrawlStore } from '@/stores/crawlStore';

const crawlStore = useCrawlStore();
const summary = computed(() => crawlStore.sentimentSummary);
</script>
```

**Langkah 2** — Ganti 3 `<StatCard>` hardcoded di template (sekitar baris 49–70):

```html
<StatCard
  label="Total Komentar"
  :value="summary?.total_comments?.toLocaleString() ?? '-'"
  icon="💬"
  :trend="0"
  variant="indigo"
/>
<StatCard
  label="Sentimen Positif"
  :value="summary ? summary.pct_positif + '%' : '-'"
  icon="😊"
  :trend="summary?.pct_positif ?? 0"
  variant="emerald"
/>
<StatCard
  label="Sentimen Negatif"
  :value="summary ? summary.pct_negatif + '%' : '-'"
  icon="😠"
  :trend="-(summary?.pct_negatif ?? 0)"
  variant="amber"
/>
```

---

## Alur Kerja Sistem Setelah Implementasi

```
[User Input Keyword]
       ↓
[Crawl TikTok → Ambil Video + Komentar]
       ↓
[Obsidian Pipeline: Emoji → Cleansing → Normalisasi → Stopwords → Stemming]
       ↓
[Klik "ANALISIS SEKARANG"]
       ↓
POST /api/v1/analysis/sentiment
       ↓
[sentiment_service.py: Loop tiap komentar → predict_sentiment(stemmed_text)]
       ↓
[Model DistilBERT → LABEL_0/1/2 → "Negatif" / "Netral" / "Positif"]
       ↓
[Return: data + summary (total, pct_positif, pct_netral, pct_negatif)]
       ↓
[crawlStore.js: sentimentSummary.value = summary]
       ↓
[Dashboard: SentimentDistribution + AIInsightsEngine + StatCard tampilkan data real]
```

---

## Tahap 7: Testing & Validasi

### A. Test Backend (Manual via Swagger UI)

1. Jalankan backend: `py main.py` dari folder `backend`
2. Buka browser: `http://localhost:8000/docs`
3. Jalankan `POST /api/v1/crawl/start` dengan body:
   ```json
   { "platforms": ["tiktok"], "keyword": "test", "video_limit": 2 }
   ```
4. Jalankan setiap endpoint pipeline secara berurutan:
   - `POST /api/v1/pipeline/emoji_conversion`
   - `POST /api/v1/pipeline/cleansing`
   - `POST /api/v1/pipeline/normalization`
   - `POST /api/v1/pipeline/stopwords`
   - `POST /api/v1/pipeline/stemming`
5. Jalankan `POST /api/v1/analysis/sentiment`
6. **Ekspektasi**: Response berisi `"status": "done"` dan field `summary` berisi angka persentase sentimen

### B. Test Frontend (End-to-End)

1. Jalankan frontend: `npm run dev` dari folder `frontend`
2. Buka `http://localhost:5173/data-engine`
3. Input keyword, klik "Mulai Crawling", tunggu pipeline selesai
4. Klik tombol **"ANALISIS SEKARANG"**
5. Buka `http://localhost:5173/` (Dashboard)
6. **Ekspektasi**:
   - Chart `SentimentDistribution` menampilkan data real
   - `AIInsightsEngine` menampilkan insight dinamis sesuai hasil analisis
   - `StatCard` menampilkan jumlah komentar dan persentase sentimen yang real

---

## Potensi Masalah & Solusinya

| Masalah | Kemungkinan Penyebab | Solusi |
|---|---|---|
| `ModuleNotFoundError: No module named 'transformers'` | Library belum terinstall | Jalankan `py -m pip install transformers torch` |
| Server startup sangat lambat (30–60 detik) | Model 268MB dimuat saat startup | Normal; hanya terjadi sekali. Tunggu hingga log `Model berhasil dimuat.` muncul |
| Response API `/sentiment` sangat lambat | Inferensi CPU untuk banyak komentar | Normal untuk CPU. Bisa dioptimasi dengan batch inference jika diperlukan |
| `_current_data` kosong saat analisis | Pipeline belum dijalankan | Pastikan semua 5 langkah pipeline sudah `done` sebelum klik "Analisis" |
| Chart di Dashboard tidak update | State tidak reactive | Pastikan `sentimentSummary` dideklarasikan sebagai `ref()`, bukan variable biasa |

---

## Ringkasan File yang Harus Diubah

| Aksi | File |
|---|---|
| 🆕 **BUAT BARU** | `backend/services/sentiment_service.py` |
| ✏️ **MODIFIKASI** | `backend/routes/analysis_routes.py` |
| ✏️ **MODIFIKASI** | `backend/models.py` |
| ✏️ **MODIFIKASI** | `frontend/src/stores/crawlStore.js` |
| ✏️ **MODIFIKASI** | `frontend/src/components/dashboard/SentimentDistribution.vue` |
| ✏️ **MODIFIKASI** | `frontend/src/components/dashboard/AIInsightsEngine.vue` |
| ✏️ **MODIFIKASI** | `frontend/src/views/Dashboard.vue` |
