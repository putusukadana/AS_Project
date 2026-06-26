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
          :disabled="p.id !== 'tiktok'"
          class="px-4 py-2 rounded-xl text-sm font-medium transition-all border group"
          :class="selectedPlatforms.includes(p.id) 
            ? 'bg-indigo-50 border-indigo-200 text-indigo-600 shadow-sm' 
            : p.id !== 'tiktok'
              ? 'bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed opacity-50'
              : 'bg-slate-50 border-slate-200 text-slate-500 hover:border-slate-300 hover:bg-slate-100'"
          @click="togglePlatform(p.id)"
        >
          <span class="mr-1.5 group-hover:scale-110 inline-block transition-transform">{{ p.icon }}</span>
          {{ p.label }}{{ p.id !== 'tiktok' ? ' (Coming Soon)' : '' }}
        </button>
      </div>
    </div>

    <!-- Input Area -->
    <div v-if="extractionMode === 'keyword'" class="mt-8 space-y-3">
      <label for="keyword-input" class="block text-sm font-bold text-slate-500 uppercase tracking-wider">Kata Kunci Target</label>
      <KeywordForm v-model="keyword" @submit="startCrawl" />
    </div>

    <div v-if="extractionMode === 'url'" class="mt-8 space-y-3">
      <div class="flex items-center justify-between">
        <label for="keyword-input" class="block text-sm font-bold text-slate-500 uppercase tracking-wider">URL Video TikTok</label>
        <span class="text-[10px] font-bold text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full uppercase tracking-tighter">Max 10 URL</span>
      </div>
      <UrlForm v-model="keyword" />
      <p class="text-[11px] text-slate-400 pl-1 font-medium italic">
        * Gunakan baris baru atau koma untuk memisahkan beberapa URL.
      </p>
    </div>

    <!-- Upload File Area -->
    <UploadForm
      v-if="extractionMode === 'upload'"
      :uploaded-file="uploadedFile"
      :is-drag-over="isDragOver"
      @drag-over="isDragOver = true"
      @drag-leave="isDragOver = false"
      @file-drop="handleFileDrop"
      @file-select="handleFileSelect"
      @remove-file="uploadedFile = null"
    />

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
      <label class="block text-sm font-bold text-slate-500 uppercase tracking-wider"> 🗓️ Rentang Waktu</label>
      <div class="[&_.p-datepicker-input]:!bg-slate-50 [&_.p-datepicker-input]:!rounded-xl [&_.p-datepicker-input]:!border-slate-200 [&_.p-datepicker-input]:!text-slate-900 [&_.p-datepicker-input]:!placeholder:text-slate-400 [&_.p-datepicker-input]:!outline-none [&_.p-datepicker-input]:focus:bg-white [&_.p-datepicker-input]:focus:border-indigo-500 [&_.p-datepicker-input]:focus:ring-4 [&_.p-datepicker-input]:focus:ring-indigo-500/10 [&_.p-datepicker-input]:transition-all [&_.p-datepicker-input]:font-medium">
      <DatePicker v-model="dates" selectionMode="range" :manualInput="false" showIcon iconDisplay="input" />
    </div>
    </div>


    <!-- Tombol Aksi -->
    <div v-if="isCrawling || isUploading" class="flex gap-3 mt-8">
      <button
        class="flex-1 p-4 bg-indigo-600 text-white rounded-xl font-bold cursor-not-allowed opacity-50"
        disabled
      >
        <span class="animate-spin mr-2 inline-block">⏳</span>
        {{ isUploading ? "Memproses File..." : "Crawling Data..." }}
      </button>
      <button
        class="px-6 py-4 bg-white text-rose-600 border-2 border-rose-200 rounded-xl font-bold hover:bg-rose-50 hover:border-rose-300 transition-all active:scale-95"
        @click="confirmCancel"
      >
        ✕ Batal
      </button>
    </div>
    <button
      v-else
      class="w-full p-4 bg-indigo-600 text-white rounded-xl font-bold mt-8 shadow-lg shadow-indigo-100 hover:bg-indigo-700 hover:-translate-y-0.5 transition-all active:scale-95 disabled:opacity-50 disabled:translate-y-0 disabled:shadow-none"
      :disabled="!canCrawl || isCrawling || isUploading"
      @click="startCrawl"
    >
      {{ extractionMode === 'upload' ? "📁 Mulai Proses File" : "🚀 Mulai Crawling" }}
    </button>

    <!-- Confirm Dialog -->
    <ConfirmDialog />

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
import DatePicker from "primevue/datepicker";
import ConfirmDialog from "primevue/confirmdialog";
import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue/usetoast";
import KeywordForm from "./KeywordForm.vue";
import UrlForm from "./UrlForm.vue";
import UploadForm from "./UploadForm.vue";

const crawlStore = useCrawlStore();
const toast = useToast();

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
const dates = ref(null);
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
const confirm = useConfirm();
const abortController = ref(null);

const confirmCancel = () => {
  confirm.require({
    message: 'Apakah Anda yakin ingin membatalkan crawling?',
    header: 'Konfirmasi Pembatalan',
    icon: 'pi pi-exclamation-triangle',
    rejectLabel: 'Tidak',
    acceptLabel: 'Iya',
    accept: () => {
      if (abortController.value) {
        abortController.value.abort();
      }
    }
  });
};

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
    toast.add({ severity: 'error', summary: 'Error', detail: 'Format file tidak didukung. Gunakan .csv, .json, atau .xlsx', life: 3000 });
    return;
  }
  
  if (file.size > 10 * 1024 * 1024) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Ukuran file melebihi 10MB', life: 3000 });
    return;
  }
  
  uploadedFile.value = file;
};

const startCrawl = async () => {
  if (!canCrawl.value || isCrawling.value) return;

  abortController.value = new AbortController();
  const signal = abortController.value.signal;

  // Mode Upload
  if (extractionMode.value === "upload") {
    isUploading.value = true;
    crawlStatus.value = [];
    try {
      await crawlStore.uploadFile({
        file: uploadedFile.value,
        signal,
        onStatus: (log) => {
          crawlStatus.value.push(log);
        },
      });
    } finally {
      isUploading.value = false;
      abortController.value = null;
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
      start_date: (extractionMode.value === 'keyword' && dates.value?.[0]) ? dates.value[0].toISOString() : null,
      end_date: (extractionMode.value === 'keyword' && dates.value?.[1]) ? dates.value[1].toISOString() : null,
      signal,
      onStatus: (log) => {
        crawlStatus.value.push(log);
      },
    });
  } finally {
    isCrawling.value = false;
    abortController.value = null;
  }
};

const videoLimit = ref(0);

</script>
