# 📋 Issue: Implementasi Halaman Data Engine

> **Halaman:** `/data-engine`
> **Stack:** Vue 3 + Tailwind CSS (Frontend) · FastAPI + MongoDB (Backend)
> **Prioritas:** High
> **Dikerjakan oleh:** Junior Programmer / AI Model

---

## 🗺️ Gambaran Umum

Halaman **Data Engine** adalah inti dari platform AS_Project yang memungkinkan pengguna mengumpulkan data dari berbagai platform media sosial dan berita, lalu memprosesnya melalui pipeline NLP otomatis hingga siap dianalisis sentimen.

### Wireframe Konseptual

```
┌─────────────────────────────────────────────────────────────┐
│  AS_Project                    🔔  ⚙️  [Avatar] ▼          │  ← Topbar
├──────────┬──────────────────────────────────────────────────┤
│          │                                                  │
│ 📊 Anal..│   ┌─────────────────┐  ┌────────────────────┐   │
│ ⚙️ Data  │   │ Extraction      │  │  Raw Stats         │   │
│ 📖 Docs  │   │ Parameters      │  │  Raw Snapshot Table│   │
│ 💬 Supp  │   │                 │  │  Obsidian Pipeline │   │
│          │   │ [Platform Pills]│  │  [Analisis Sekarang│   │
│ [+ Crawl]│   │ [Keyword Input] │  │   muncul jika done]│   │
│          │   │ [Mulai Crawling]│  └────────────────────┘   │
│          │   │ -- Live Status- │                            │
│          │   └─────────────────┘                            │
└──────────┴──────────────────────────────────────────────────┘
```

---

## 📦 Tahapan Implementasi

---

### ✅ Tahap 1 — Buat Layout Shell Halaman Data Engine

**Tujuan:** Membuat kerangka halaman dengan struktur tiga area utama: Topbar, Sidebar, dan Content Area (dua panel).

**File yang perlu dibuat/diubah:**

#### [BUAT BARU] `frontend/src/views/DataEngine.vue`

```vue
<template>
  <div class="app-shell">
    <!-- Topbar -->
    <AppTopbar />

    <div class="body-wrapper">
      <!-- Sidebar -->
      <AppSidebar activePage="data-engine" />

      <!-- Content -->
      <main class="content-area">
        <div class="panel-grid">
          <!-- Panel Kiri -->
          <ExtractionPanel />
          <!-- Panel Kanan -->
          <ResultPanel />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import AppTopbar from "@/components/layout/AppTopbar.vue";
import AppSidebar from "@/components/layout/AppSidebar.vue";
import ExtractionPanel from "@/components/dataengine/ExtractionPanel.vue";
import ResultPanel from "@/components/dataengine/ResultPanel.vue";
</script>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  height: 100vh;
}
.body-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
}
.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}
.panel-grid {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 1.5rem;
}
</style>
```

#### [UBAH] `frontend/src/routes/index.js`

Tambahkan route baru untuk halaman Data Engine:

```js
import DataEngine from '@/views/DataEngine.vue'

// Tambahkan ke dalam array routes:
{
  path: '/data-engine',
  name: 'DataEngine',
  component: DataEngine,
  meta: { requiresAuth: true }
}
```

**✔ Kriteria Selesai:**

- Navigasi ke `/data-engine` tidak error
- Tiga area (Topbar, Sidebar, Content) tampil secara visual (boleh placeholder dulu)

---

### ✅ Tahap 2 — Buat Komponen Topbar (`AppTopbar.vue`)

**Tujuan:** Topbar dengan brand name di kiri dan tiga ikon (notifikasi, pengaturan, avatar) di kanan.

**File yang perlu dibuat:**

#### [BUAT BARU] `frontend/src/components/layout/AppTopbar.vue`

```vue
<template>
  <header class="topbar">
    <!-- Kiri: Brand -->
    <RouterLink to="/" class="brand-name">AS_Project</RouterLink>

    <!-- Kanan: Actions -->
    <div class="topbar-actions">
      <!-- Notifikasi -->
      <button class="icon-btn" title="Notifikasi" @click="toggleNotif">
        <span class="icon">🔔</span>
        <span v-if="hasUnread" class="badge">{{ unreadCount }}</span>
      </button>

      <!-- Pengaturan -->
      <RouterLink to="/settings" class="icon-btn" title="Pengaturan">
        <span class="icon">⚙️</span>
      </RouterLink>

      <!-- Avatar dropdown -->
      <div class="avatar-wrapper" @click="toggleAvatarMenu">
        <img :src="userAvatar" alt="User Avatar" class="avatar-img" />
        <span class="chevron">▼</span>

        <!-- Dropdown Menu -->
        <div v-if="showAvatarMenu" class="dropdown-menu">
          <RouterLink to="/profile">👤 Profil</RouterLink>
          <RouterLink to="/settings">⚙️ Pengaturan Akun</RouterLink>
          <button @click="logout">🔓 Logout</button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const showAvatarMenu = ref(false);
const showNotif = ref(false);
const notifications = ref([]); // akan diisi dari store/API nanti

const hasUnread = computed(() => notifications.value.some((n) => !n.read));
const unreadCount = computed(
  () => notifications.value.filter((n) => !n.read).length,
);
// Ambil avatar dari localStorage atau store
const userAvatar = ref(
  localStorage.getItem("user_avatar") || "/default-avatar.png",
);

const toggleAvatarMenu = () => {
  showAvatarMenu.value = !showAvatarMenu.value;
};
const toggleNotif = () => {
  showNotif.value = !showNotif.value;
};
const logout = () => {
  localStorage.removeItem("token");
  router.push("/login");
};
</script>
```

**✔ Kriteria Selesai:**

- Brand "AS_Project" tampil di kiri, 3 ikon tampil di kanan
- Klik avatar membuka dropdown dengan link Profil, Pengaturan, dan Logout
- Logout menghapus token dan redirect ke `/login`

---

### ✅ Tahap 3 — Buat Komponen Sidebar (`AppSidebar.vue`)

**Tujuan:** Sidebar navigasi dengan 4 menu utama dan tombol "New Crawl".

**File yang perlu dibuat:**

#### [BUAT BARU] `frontend/src/components/layout/AppSidebar.vue`

```vue
<template>
  <aside class="sidebar">
    <!-- Menu Navigasi -->
    <nav class="sidebar-nav">
      <RouterLink
        to="/dashboard"
        class="nav-item"
        :class="{ active: activePage === 'dashboard' }"
      >
        <span class="nav-icon">📊</span>
        <span class="nav-label">Analytics Dashboard</span>
      </RouterLink>

      <RouterLink
        to="/data-engine"
        class="nav-item"
        :class="{ active: activePage === 'data-engine' }"
      >
        <span class="nav-icon">⚙️</span>
        <span class="nav-label">Data Engine</span>
      </RouterLink>

      <RouterLink
        to="/documentation"
        class="nav-item"
        :class="{ active: activePage === 'docs' }"
      >
        <span class="nav-icon">📖</span>
        <span class="nav-label">Documentation</span>
      </RouterLink>

      <RouterLink
        to="/support"
        class="nav-item"
        :class="{ active: activePage === 'support' }"
      >
        <span class="nav-icon">💬</span>
        <span class="nav-label">Support</span>
      </RouterLink>
    </nav>

    <!-- Tombol New Crawl -->
    <div class="sidebar-footer">
      <RouterLink to="/data-engine" class="btn-new-crawl">
        ＋ New Crawl
      </RouterLink>
    </div>
  </aside>
</template>

<script setup>
defineProps({ activePage: String });
</script>
```

**✔ Kriteria Selesai:**

- 4 menu tampil dengan ikon dan label
- Menu aktif ditandai dengan styling berbeda (highlight)
- Tombol "New Crawl" tampil di bagian bawah sidebar

---

### ✅ Tahap 4 — Buat Panel Kiri: Extraction Parameters

**Tujuan:** Form untuk memilih platform, memasukkan kata kunci, dan memulai crawl. Disertai status real-time.

**File yang perlu dibuat:**

#### [BUAT BARU] `frontend/src/components/dataengine/ExtractionPanel.vue`

```vue
<template>
  <section class="panel extraction-panel">
    <h2 class="panel-title">⚙️ Extraction Parameters</h2>

    <!-- Pilih Platform -->
    <div class="field-group">
      <label>Platform Sumber Data</label>
      <div class="platform-pills">
        <button
          v-for="p in platforms"
          :key="p.id"
          class="pill"
          :class="{ selected: selectedPlatforms.includes(p.id) }"
          @click="togglePlatform(p.id)"
        >
          {{ p.icon }} {{ p.label }}
        </button>
      </div>
    </div>

    <!-- Input Kata Kunci -->
    <div class="field-group">
      <label for="keyword-input">Kata Kunci Target</label>
      <input
        id="keyword-input"
        v-model="keyword"
        type="text"
        placeholder="Contoh: banjir jakarta 2025"
        class="text-input"
      />
    </div>

    <!-- Tombol Aksi -->
    <button
      class="btn-primary btn-crawl"
      :disabled="!canCrawl || isCrawling"
      @click="startCrawl"
    >
      {{ isCrawling ? "⏳ Crawling..." : "🚀 Mulai Crawling" }}
    </button>

    <!-- Status Crawling Real-time -->
    <div v-if="crawlStatus.length > 0" class="crawl-status-log">
      <h3>📡 Status Crawling</h3>
      <ul>
        <li v-for="(log, i) in crawlStatus" :key="i" :class="log.type">
          {{ log.message }}
        </li>
      </ul>
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from "vue";
import { useCrawlStore } from "@/stores/crawlStore";

const crawlStore = useCrawlStore();

const platforms = [
  { id: "tiktok", icon: "🎵", label: "TikTok" },
  { id: "instagram", icon: "📸", label: "Instagram" },
  { id: "youtube", icon: "▶️", label: "YouTube" },
  { id: "news", icon: "📰", label: "News" },
  { id: "facebook", icon: "👤", label: "Facebook" },
];

const selectedPlatforms = ref([]);
const keyword = ref("");
const isCrawling = ref(false);
const crawlStatus = ref([]);

const canCrawl = computed(
  () => selectedPlatforms.value.length > 0 && keyword.value.trim().length > 0,
);

const togglePlatform = (id) => {
  const idx = selectedPlatforms.value.indexOf(id);
  if (idx >= 0) selectedPlatforms.value.splice(idx, 1);
  else selectedPlatforms.value.push(id);
};

const startCrawl = async () => {
  isCrawling.value = true;
  crawlStatus.value = [];
  try {
    await crawlStore.startCrawl({
      platforms: selectedPlatforms.value,
      keyword: keyword.value,
      onStatus: (log) => crawlStatus.value.push(log),
    });
  } finally {
    isCrawling.value = false;
  }
};
</script>
```

**✔ Kriteria Selesai:**

- 5 platform tampil sebagai pill/toggle button, bisa dipilih lebih dari satu
- Input keyword berfungsi
- Tombol disabled jika tidak ada platform atau keyword yang dipilih
- Status log tampil real-time saat crawling berjalan

---

### ✅ Tahap 5 — Buat Panel Kanan: Result Panel

Panel kanan dibagi menjadi tiga sub-komponen.

#### 5a. Statistik Raw Data

#### [BUAT BARU] `frontend/src/components/dataengine/RawStats.vue`

```vue
<template>
  <div class="stats-row">
    <div class="stat-card">
      <span class="stat-value">{{ totalData }}</span>
      <span class="stat-label">Total Data</span>
    </div>
    <div class="stat-card">
      <span class="stat-value">{{ signalQuality }}%</span>
      <span class="stat-label">Kualitas Sinyal</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  totalData: { type: Number, default: 0 },
  signalQuality: { type: Number, default: 0 },
});
</script>
```

#### 5b. Tabel Raw Snapshot

#### [BUAT BARU] `frontend/src/components/dataengine/RawSnapshotTable.vue`

```vue
<template>
  <div class="snapshot-panel">
    <h3>📋 Raw Snapshot</h3>
    <div v-if="rows.length === 0" class="empty-state">
      Belum ada data. Mulai crawling terlebih dahulu.
    </div>
    <table v-else class="data-table">
      <thead>
        <tr>
          <th>#</th>
          <th>Platform</th>
          <th>Teks</th>
          <th>Waktu</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, i) in rows" :key="i">
          <td>{{ i + 1 }}</td>
          <td>{{ row.platform }}</td>
          <td class="text-preview">{{ row.text?.slice(0, 80) }}...</td>
          <td>{{ formatTime(row.created_at) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({ rows: { type: Array, default: () => [] } });
const formatTime = (ts) => new Date(ts).toLocaleString("id-ID");
</script>
```

#### 5c. Obsidian Pipeline (Preprocessing Steps)

#### [BUAT BARU] `frontend/src/components/dataengine/ObsidianPipeline.vue`

```vue
<template>
  <div class="pipeline-panel">
    <h3>🔮 Obsidian Pipeline</h3>

    <!-- Tahapan pipeline -->
    <div class="pipeline-steps">
      <div
        v-for="step in steps"
        :key="step.id"
        class="pipeline-step"
        :class="step.status"
      >
        <span class="step-icon">{{ step.icon }}</span>
        <div class="step-info">
          <span class="step-name">{{ step.label }}</span>
          <span class="step-status-text">{{ statusLabel(step.status) }}</span>
        </div>
        <span class="step-check">{{
          step.status === "done"
            ? "✅"
            : step.status === "running"
              ? "⏳"
              : "⬜"
        }}</span>
      </div>
    </div>

    <!-- Tombol Analisis — muncul jika semua selesai -->
    <button
      v-if="allDone"
      class="btn-primary btn-analyze"
      @click="$emit('analyze')"
    >
      🧠 Analisis Sekarang
    </button>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  steps: {
    type: Array,
    default: () => [
      { id: "case_folding", icon: "🔡", label: "Case Folding", status: "idle" },
      { id: "url_removal", icon: "🔗", label: "URL Removal", status: "idle" },
      {
        id: "stopwords",
        icon: "🚫",
        label: "Stopwords Removal",
        status: "idle",
      },
      { id: "emotion", icon: "😊", label: "Emotion Detection", status: "idle" },
    ],
  },
});
defineEmits(["analyze"]);

const allDone = computed(() => props.steps.every((s) => s.status === "done"));
const statusLabel = (s) =>
  ({
    idle: "Menunggu",
    running: "Berjalan...",
    done: "Selesai",
    error: "Gagal",
  })[s] || "-";
</script>
```

#### [BUAT BARU] `frontend/src/components/dataengine/ResultPanel.vue`

```vue
<template>
  <section class="panel result-panel">
    <RawStats :totalData="stats.total" :signalQuality="stats.quality" />
    <RawSnapshotTable :rows="rawRows" />
    <ObsidianPipeline :steps="pipelineSteps" @analyze="runAnalysis" />
  </section>
</template>

<script setup>
import { ref } from "vue";
import RawStats from "./RawStats.vue";
import RawSnapshotTable from "./RawSnapshotTable.vue";
import ObsidianPipeline from "./ObsidianPipeline.vue";
import { useCrawlStore } from "@/stores/crawlStore";

const crawlStore = useCrawlStore();
const stats = ref({ total: 0, quality: 0 });
const rawRows = ref([]);
const pipelineSteps = ref([
  { id: "case_folding", icon: "🔡", label: "Case Folding", status: "idle" },
  { id: "url_removal", icon: "🔗", label: "URL Removal", status: "idle" },
  { id: "stopwords", icon: "🚫", label: "Stopwords Removal", status: "idle" },
  { id: "emotion", icon: "😊", label: "Emotion Detection", status: "idle" },
]);

const runAnalysis = async () => {
  await crawlStore.runSentimentAnalysis();
};
</script>
```

**✔ Kriteria Selesai:**

- Stat card total data & kualitas sinyal tampil
- Tabel raw snapshot tampil data atau pesan kosong
- Semua stage pipeline tampil dengan status visual
- Tombol "Analisis Sekarang" muncul hanya jika semua stage bernilai `done`

---

### ✅ Tahap 6 — Buat Pinia Store untuk Crawling (`crawlStore.js`)

**Tujuan:** Manajemen state terpusat untuk proses crawl dan preprocessing.

#### [BUAT BARU] `frontend/src/stores/crawlStore.js`

```js
import { defineStore } from "pinia";
import { ref } from "vue";
import api from "@/services/api"; // axios instance

export const useCrawlStore = defineStore("crawl", () => {
  const rawData = ref([]);
  const stats = ref({ total: 0, quality: 0 });
  const pipelineStatus = ref({
    case_folding: "idle",
    url_removal: "idle",
    stopwords: "idle",
    emotion: "idle",
  });
  const isAnalyzing = ref(false);

  const startCrawl = async ({ platforms, keyword, onStatus }) => {
    onStatus({ type: "info", message: `🚀 Memulai crawl untuk: "${keyword}"` });
    try {
      const res = await api.post("/crawl/start", { platforms, keyword });
      rawData.value = res.data.data;
      stats.value = { total: res.data.total, quality: res.data.signal_quality };
      onStatus({
        type: "success",
        message: `✅ ${res.data.total} data berhasil dikumpulkan`,
      });
      // Otomatis jalankan pipeline
      await runPipeline(onStatus);
    } catch (err) {
      onStatus({ type: "error", message: `❌ Gagal: ${err.message}` });
    }
  };

  const runPipeline = async (onStatus) => {
    const steps = ["case_folding", "url_removal", "stopwords", "emotion"];
    for (const step of steps) {
      pipelineStatus.value[step] = "running";
      onStatus({ type: "info", message: `⚙️ Menjalankan ${step}...` });
      try {
        await api.post(`/pipeline/${step}`);
        pipelineStatus.value[step] = "done";
        onStatus({ type: "success", message: `✅ ${step} selesai` });
      } catch {
        pipelineStatus.value[step] = "error";
        onStatus({ type: "error", message: `❌ ${step} gagal` });
        break;
      }
    }
  };

  const runSentimentAnalysis = async () => {
    isAnalyzing.value = true;
    try {
      await api.post("/analysis/sentiment");
      // redirect/notif ke dashboard bisa ditambahkan di sini
    } finally {
      isAnalyzing.value = false;
    }
  };

  return {
    rawData,
    stats,
    pipelineStatus,
    isAnalyzing,
    startCrawl,
    runSentimentAnalysis,
  };
});
```

> **Catatan:** Jika Pinia belum diinstall, jalankan:
>
> ```bash
> npm install pinia
> ```
>
> Lalu daftarkan di `main.js`:
>
> ```js
> import { createPinia } from "pinia";
> app.use(createPinia());
> ```

**✔ Kriteria Selesai:**

- Store dapat dipanggil dari ExtractionPanel dan ResultPanel
- State `rawData`, `stats`, `pipelineStatus` reactive dan terpusat

---

### ✅ Tahap 7 — Buat Backend Endpoint: Crawling

**Tujuan:** Endpoint FastAPI yang menerima request crawl dari frontend.

#### [BUAT BARU] `backend/routes/crawl_routes.py`

```python
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from services.crawl_service import run_crawl

router = APIRouter(prefix="/api/v1/crawl", tags=["crawl"])

class CrawlRequest(BaseModel):
    platforms: List[str]
    keyword: str

@router.post("/start")
async def start_crawl(body: CrawlRequest):
    result = await run_crawl(body.platforms, body.keyword)
    return {
        "total": result["total"],
        "signal_quality": result["signal_quality"],
        "data": result["data"]
    }
```

#### [BUAT BARU] `backend/services/crawl_service.py`

```python
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
                            "nickname": author.get("nickname", "Tidak tersedia"),
                            "description": description,
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
                url = f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id}&cursor={cursor}&count=50&device_id={device_id}&aid=1988"
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
                
                cursor = data.get('cursor', 0)
                has_more = data.get('has_more', False)
                time.sleep(2)
            except:
                break
        return comments

    def get_replies(self, video_id, comment_id):
        url = "https://tiktok-api23.p.rapidapi.com/api/post/comment/replies"
        headers = {
            "x-rapidapi-key": "d501fae7bfmsh3f1de8ef5dc24d3p1d9ebejsnabaf8a976a3e",
            "x-rapidapi-host": "tiktok-api23.p.rapidapi.com"
        }
        params = {"videoId": video_id, "commentId": comment_id, "count": "10", "cursor": "0"}
        try:
            res = requests.get(url, headers=headers, params=params)
            return res.json().get("data", [])
        except:
            return []

# --- Main Service Function ---

async def run_crawl(platforms: list, keyword: str) -> dict:
    all_data = []
    if "tiktok" in platforms:
        tiktok_res = extract_tiktok_data(keywords=keyword, limit=5)
        scraper = TikTokCommentScraper()
        
        for video in tiktok_res["results"]:
            video["comments"] = scraper.get_comments(video["video_id"])
            all_data.append(video)
            
    return {
        "total": len(all_data),
        "signal_quality": 90,
        "data": all_data
    }
```


#### [UBAH] `backend/main.py`

Tambahkan router baru:

```python
from routes.crawl_routes import router as crawl_router
app.include_router(crawl_router)
```

**✔ Kriteria Selesai:**

- `POST /api/v1/crawl/start` mengembalikan data mock
- Response berisi `total`, `signal_quality`, dan `data`

---

### ✅ Tahap 8 — Buat Backend Endpoint: Obsidian Pipeline

**Tujuan:** Endpoint untuk setiap tahap preprocessing NLP.

#### [BUAT BARU] `backend/routes/pipeline_routes.py`

```python
from fastapi import APIRouter
from services.pipeline_service import (
    run_case_folding, run_url_removal, run_stopwords, run_emotion_detection
)

router = APIRouter(prefix="/api/v1/pipeline", tags=["pipeline"])

@router.post("/case_folding")
async def case_folding():
    return await run_case_folding()

@router.post("/url_removal")
async def url_removal():
    return await run_url_removal()

@router.post("/stopwords")
async def stopwords():
    return await run_stopwords()

@router.post("/emotion")
async def emotion():
    return await run_emotion_detection()
```

#### [BUAT BARU] `backend/services/pipeline_service.py`

```python
# Implementasi NLP Pipeline
import re

# Simpan state in-memory (development); gunakan Redis/DB di production
_current_data = []

async def run_case_folding():
    # Lowercase semua teks
    for item in _current_data:
        item['text'] = item['text'].lower()
    return {"status": "done", "step": "case_folding"}

async def run_url_removal():
    # Hapus URL dari teks
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    for item in _current_data:
        item['text'] = url_pattern.sub('', item['text'])
    return {"status": "done", "step": "url_removal"}

async def run_stopwords():
    # Gunakan Sastrawi untuk stopwords Bahasa Indonesia
    # Install: pip install PySastrawi
    from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

    # 1. Buat stopword remover menggunakan Sastrawi
    factory = StopWordRemoverFactory()
    stopword_remover = factory.create_stop_word_remover()

    # 2. Fungsi untuk menghapus stopword dari teks
    def hapus_stopword(teks):
        if not isinstance(teks, str):
            return ""
        return stopword_remover.remove(teks)

    # 3. Terapkan ke setiap item di _current_data
    for item in _current_data:
        item['text'] = hapus_stopword(item.get('text', ''))

    return {"status": "done", "step": "stopwords"}

async def run_emotion_detection():
    # TODO: Integrasikan model Emotion Detection
    # Opsi: IndoNLU, HuggingFace transformers (indobert)
    return {"status": "done", "step": "emotion"}
```

#### [BUAT BARU] `backend/routes/analysis_routes.py`

```python
from fastapi import APIRouter
router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])

@router.post("/sentiment")
async def run_sentiment():
    # TODO: Panggil model sentimen (IndoBERT, dst.)
    return {"status": "ok", "message": "Analisis sentimen dimulai"}
```

**✔ Kriteria Selesai:**

- Semua endpoint pipeline merespons HTTP 200
- Setiap endpoint mengembalikan `{ "status": "done", "step": "..." }`

---

### ✅ Tahap 9 — Styling & Polish

**Tujuan:** Memberikan tampilan yang konsisten dan profesional.

#### Panduan Styling (gunakan Tailwind CSS)

| Elemen                | Class Tailwind yang disarankan                                                    |
| --------------------- | --------------------------------------------------------------------------------- |
| Topbar                | `bg-gray-900 text-white flex items-center justify-between px-6 h-16`              |
| Brand                 | `text-xl font-bold text-indigo-400 hover:text-indigo-300`                         |
| Sidebar               | `w-64 bg-gray-850 border-r border-gray-700 flex flex-col py-6`                    |
| Nav item aktif        | `bg-indigo-600/20 text-indigo-400 border-l-2 border-indigo-400`                   |
| Panel                 | `bg-gray-800 rounded-xl border border-gray-700 p-6`                               |
| Tombol primary        | `bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-lg` |
| Platform pill aktif   | `bg-indigo-600/30 border border-indigo-400 text-indigo-300`                       |
| Pipeline step done    | `text-green-400`                                                                  |
| Pipeline step running | `text-yellow-400 animate-pulse`                                                   |

**✔ Kriteria Selesai:**

- Dark mode konsisten di seluruh halaman
- Semua elemen interaktif punya hover state
- Animasi `animate-pulse` pada step pipeline yang sedang berjalan

---

### ✅ Tahap 10 — Testing & Verifikasi

#### Checklist Manual Testing

| No  | Skenario                        | Expected                                         |
| --- | ------------------------------- | ------------------------------------------------ |
| 1   | Buka `/data-engine` tanpa login | Redirect ke `/login`                             |
| 2   | Brand "AS_Project" diklik       | Redirect ke `/` atau `/dashboard`                |
| 3   | Klik ikon 🔔                    | Dropdown notifikasi muncul                       |
| 4   | Klik avatar ▼                   | Dropdown menu profil/logout tampil               |
| 5   | Klik Logout                     | Token dihapus, redirect ke `/login`              |
| 6   | Pilih platform + isi keyword    | Tombol "Mulai Crawling" aktif                    |
| 7   | Klik "Mulai Crawling"           | Status log muncul real-time                      |
| 8   | Crawl selesai                   | Tabel Raw Snapshot terisi data                   |
| 9   | Pipeline berjalan               | Setiap step berubah: idle→running→done           |
| 10  | Semua pipeline done             | Tombol "Analisis Sekarang" muncul                |
| 11  | Klik "Analisis Sekarang"        | Request ke `/api/v1/analysis/sentiment` terkirim |

---

## 📁 Ringkasan File yang Perlu Dibuat/Diubah

### Frontend (Vue 3)

| Status  | File                                             |
| ------- | ------------------------------------------------ |
| 🆕 Baru | `src/views/DataEngine.vue`                       |
| 🆕 Baru | `src/components/layout/AppTopbar.vue`            |
| 🆕 Baru | `src/components/layout/AppSidebar.vue`           |
| 🆕 Baru | `src/components/dataengine/ExtractionPanel.vue`  |
| 🆕 Baru | `src/components/dataengine/ResultPanel.vue`      |
| 🆕 Baru | `src/components/dataengine/RawStats.vue`         |
| 🆕 Baru | `src/components/dataengine/RawSnapshotTable.vue` |
| 🆕 Baru | `src/components/dataengine/ObsidianPipeline.vue` |
| 🆕 Baru | `src/stores/crawlStore.js`                       |
| ✏️ Ubah | `src/routes/index.js`                            |

### Backend (FastAPI)

| Status  | File                           |
| ------- | ------------------------------ |
| 🆕 Baru | `routes/crawl_routes.py`       |
| 🆕 Baru | `routes/pipeline_routes.py`    |
| 🆕 Baru | `routes/analysis_routes.py`    |
| 🆕 Baru | `services/crawl_service.py`    |
| 🆕 Baru | `services/pipeline_service.py` |
| ✏️ Ubah | `main.py`                      |

---

## 🔗 Dependensi yang Mungkin Perlu Diinstall

### Frontend

```bash
npm install pinia
```

### Backend

```bash
pip install PySastrawi  # untuk stopwords Bahasa Indonesia
# opsional:
pip install transformers torch  # untuk model sentimen IndoBERT
```

---

## ⚠️ Catatan Penting untuk Implementor

1. **Urutan pengerjaan:** Kerjakan tahap per tahap secara berurutan. Jangan skip ke tahap yang lebih tinggi sebelum kriteria selesai tahap sebelumnya terpenuhi.
2. **Backend stub dulu:** Di Tahap 7 & 8, cukup buat endpoint yang mengembalikan data mock. Integrasi crawler asli bisa dilakukan setelah semua UI berfungsi.
3. **State management:** Gunakan Pinia Store (Tahap 6) sebagai satu sumber kebenaran. Jangan passing props antar komponen yang tidak berhubungan langsung.
4. **Auth guard:** Pastikan route `/data-engine` dilindungi oleh `meta: { requiresAuth: true }` dan router guard di `routes/index.js` sudah mengecek token.
5. **CORS:** Pastikan FastAPI sudah mengizinkan request dari `localhost:5173` (atau port Vite yang aktif).
