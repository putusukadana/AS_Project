<template>
  <section class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm shadow-slate-200/50">
    <div class="flex flex-col gap-4 mb-6">
      <h2 class="text-xl font-bold text-slate-900 flex items-center gap-2">
        <span>⚙️</span> Extraction Parameters
      </h2>
      <!-- Mode Switcher -->
      <div class="flex bg-slate-100 p-1 rounded-xl self-start">
        <button 
          v-for="mode in ['keyword', 'url', 'upload']" 
          :key="mode"
          class="px-3 py-1.5 rounded-lg text-[11px] font-bold uppercase tracking-wider transition-all"
          :class="extractionMode === mode ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
          @click="extractionMode = mode"
        >
          {{ mode }}
        </button>
      </div>
    </div>

    <!-- Pilih Platform -->
    <div class="space-y-3" :class="{ 'opacity-50 pointer-events-none': extractionMode === 'url' }">
      <label class="block text-sm font-bold text-slate-500 uppercase tracking-wider">Platform Sumber Data</label>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="p in platforms"
          :key="p.id"
          class="px-4 py-2 rounded-xl text-sm font-medium transition-all border group"
          :class="selectedPlatforms.includes(p.id) 
            ? 'bg-indigo-50 border-indigo-200 text-indigo-600 shadow-sm' 
            : 'bg-slate-50 border-slate-200 text-slate-500 hover:border-slate-300 hover:bg-slate-100'"
          @click="togglePlatform(p.id)"
        >
          <span class="mr-1.5 group-hover:scale-110 inline-block transition-transform">{{ p.icon }}</span>
          {{ p.label }}
        </button>
      </div>
    </div>

    <!-- Input Area -->
    <div class="mt-8 space-y-3" v-if="extractionMode !== 'upload'">
      <div class="flex items-center justify-between">
        <label for="keyword-input" class="block text-sm font-bold text-slate-500 uppercase tracking-wider">
          {{ extractionMode === 'keyword' ? 'Kata Kunci Target' : 'URL Video TikTok' }}
        </label>
        <span v-if="extractionMode === 'url'" class="text-[10px] font-bold text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full uppercase tracking-tighter">
          Max 10 URL
        </span>
      </div>
      
      <div class="relative group">
        <span class="absolute left-4 top-4 text-slate-400 group-focus-within:text-indigo-500 transition-colors">
          {{ extractionMode === 'keyword' ? '🔍' : '🔗' }}
        </span>

        <!-- Textarea for Multiple URLs -->
        <textarea
          v-if="extractionMode === 'url'"
          id="keyword-input"
          v-model="keyword"
          rows="4"
          placeholder="https://www.tiktok.com/@user/video/123...&#10;https://vt.tiktok.com/ZS.../"
          class="w-full pl-11 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 placeholder:text-slate-400 outline-none focus:bg-white focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all font-medium text-sm resize-none"
        ></textarea>

        <!-- Standard Input for Keywords -->
        <input
          v-else
          id="keyword-input"
          v-model="keyword"
          type="text"
          placeholder="Contoh: banjir jakarta 2025"
          class="w-full pl-11 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 placeholder:text-slate-400 outline-none focus:bg-white focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all font-medium"
          @keyup.enter="startCrawl"
        />
      </div>
      <p v-if="extractionMode === 'url'" class="text-[11px] text-slate-400 pl-1 font-medium italic">
        * Gunakan baris baru atau koma untuk memisahkan beberapa URL.
      </p>
    </div>

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

    <!-- Jumlah Video -->
    <div class="mt-6 space-y-3" v-if="extractionMode !== 'upload'" :class="{ 'opacity-30 pointer-events-none': extractionMode === 'url' }">
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

    <!-- Rentang Waktu -->
    <div class="mt-8 space-y-3" v-if="extractionMode !== 'upload'" :class="{ 'opacity-30 pointer-events-none': extractionMode === 'url' }">
      <label class="block text-sm font-bold text-slate-500 uppercase tracking-wider">Rentang Waktu</label>
      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1.5">
          <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest pl-1">Dari</span>
          <input
            v-model="startDate"
            type="date"
            class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 outline-none focus:bg-white focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all text-sm font-medium"
          />
        </div>
        <div class="space-y-1.5">
          <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest pl-1">Hingga</span>
          <input
            v-model="endDate"
            type="date"
            class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 outline-none focus:bg-white focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all text-sm font-medium"
          />
        </div>
      </div>
    </div>

    <!-- Tombol Aksi -->
    <button
      class="w-full p-4 bg-indigo-600 text-white rounded-xl font-bold mt-8 shadow-lg shadow-indigo-100 hover:bg-indigo-700 hover:-translate-y-0.5 transition-all active:scale-95 disabled:opacity-50 disabled:translate-y-0 disabled:shadow-none"
      :disabled="!canCrawl || isCrawling || isUploading"
      @click="startCrawl"
    >
      <span v-if="isCrawling || isUploading" class="animate-spin mr-2 inline-block">⏳</span>
      {{ isUploading ? "Memproses File..." : isCrawling ? "Crawling Data..." : extractionMode === 'upload' ? "📁 Mulai Proses File" : "🚀 Mulai Crawling" }}
    </button>

    <!-- Status Crawling Real-time -->
    <div v-if="crawlStatus.length > 0" class="mt-8">
      <h3 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-3">📡 Status Crawling</h3>
      <div class="bg-slate-900 rounded-xl p-4 max-h-[220px] overflow-y-auto font-mono text-[13px] shadow-inner">
        <ul class="space-y-1.5 capitalize">
          <li v-for="(log, i) in crawlStatus" :key="i" class="flex gap-3 animate-in fade-in slide-in-from-left-2 duration-300">
            <span class="text-slate-600 shrink-0">[{{ formatNow() }}]</span>
            <span :class="{
              'text-slate-400': log.type === 'info',
              'text-emerald-400 font-semibold': log.type === 'success',
              'text-rose-400': log.type === 'error'
            }">{{ log.message }}</span>
          </li>
        </ul>
      </div>
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

const extractionMode = ref("keyword"); // 'keyword' | 'url' | 'upload'
const selectedPlatforms = ref(["tiktok"]);
const keyword = ref("");
const startDate = ref("");
const endDate = ref("");
const isCrawling = ref(false);
const crawlStatus = ref([]);
const uploadedFile = ref(null);
const isDragOver = ref(false);

const canCrawl = computed(() => {
  if (extractionMode.value === "upload") return uploadedFile.value !== null;
  if (extractionMode.value === "url") return keyword.value.trim().includes("tiktok.com");
  return selectedPlatforms.value.length > 0 && keyword.value.trim().length > 0;
});

const togglePlatform = (id) => {
  const idx = selectedPlatforms.value.indexOf(id);
  if (idx >= 0) selectedPlatforms.value.splice(idx, 1);
  else selectedPlatforms.value.push(id);
};

const formatNow = () => new Date().toLocaleTimeString('id-ID', { hour12: false });

const isUploading = ref(false);

const handleFileDrop = (event) => {
  isDragOver.value = false;
  const files = event.dataTransfer.files;
  if (files.length > 0) {
    validateAndSetFile(files[0]);
  }
};

const handleFileSelect = (event) => {
  const files = event.target.files;
  if (files.length > 0) {
    validateAndSetFile(files[0]);
  }
};

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

const startCrawl = async () => {
  if (!canCrawl.value || isCrawling.value) return;

  // Mode Upload
  if (extractionMode.value === "upload") {
    isUploading.value = true;
    crawlStatus.value = [];
    try {
      await crawlStore.uploadFile({
        file: uploadedFile.value,
        onStatus: (log) => {
          crawlStatus.value.push(log);
        },
      });
    } finally {
      isUploading.value = false;
    }
    return;
  }
  
  isCrawling.value = true;
  crawlStatus.value = [];
  try {
    await crawlStore.startCrawl({
      platforms: extractionMode.value === 'url' ? ['tiktok'] : selectedPlatforms.value,
      keyword: keyword.value,
      video_limit: videoLimit.value,
      start_date: (extractionMode.value === 'keyword' && startDate.value) ? new Date(startDate.value).toISOString() : null,
      end_date: (extractionMode.value === 'keyword' && endDate.value) ? new Date(endDate.value).toISOString() : null,
      onStatus: (log) => {
        crawlStatus.value.push(log);
      },
    });
  } finally {
    isCrawling.value = false;
  }
};

const videoLimit = ref(0);

</script>
