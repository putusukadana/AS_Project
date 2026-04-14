<template>
  <section class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm shadow-slate-200/50">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-slate-900 flex items-center gap-2">
        <span>⚙️</span> Extraction Parameters
      </h2>
      <!-- Mode Switcher -->
      <div class="flex bg-slate-100 p-1 rounded-xl">
        <button 
          v-for="mode in ['keyword', 'url']" 
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
    <div class="mt-8 space-y-3">
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

    <!-- Rentang Waktu -->
    <div class="mt-8 space-y-3" :class="{ 'opacity-30 pointer-events-none': extractionMode === 'url' }">
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
      :disabled="!canCrawl || isCrawling"
      @click="startCrawl"
    >
      <span v-if="isCrawling" class="animate-spin mr-2 inline-block">⏳</span>
      {{ isCrawling ? "Crawling Data..." : "🚀 Mulai Crawling" }}
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

const extractionMode = ref("keyword"); // 'keyword' | 'url'
const selectedPlatforms = ref(["tiktok"]);
const keyword = ref("");
const startDate = ref("");
const endDate = ref("");
const isCrawling = ref(false);
const crawlStatus = ref([]);

const canCrawl = computed(() => {
  if (extractionMode.value === "url") return keyword.value.trim().includes("tiktok.com");
  return selectedPlatforms.value.length > 0 && keyword.value.trim().length > 0;
});

const togglePlatform = (id) => {
  const idx = selectedPlatforms.value.indexOf(id);
  if (idx >= 0) selectedPlatforms.value.splice(idx, 1);
  else selectedPlatforms.value.push(id);
};

const formatNow = () => new Date().toLocaleTimeString('id-ID', { hour12: false });

const startCrawl = async () => {
  if (!canCrawl.value || isCrawling.value) return;
  
  isCrawling.value = true;
  crawlStatus.value = [];
  try {
    await crawlStore.startCrawl({
      platforms: extractionMode.value === 'url' ? ['tiktok'] : selectedPlatforms.value,
      keyword: keyword.value,
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
</script>
