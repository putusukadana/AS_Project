<template>
  <section class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm shadow-slate-200/50">
    <h2 class="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
      <span>⚙️</span> Extraction Parameters
    </h2>

    <!-- Pilih Platform -->
    <div class="space-y-3">
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

    <!-- Input Kata Kunci -->
    <div class="mt-8 space-y-3">
      <label for="keyword-input" class="block text-sm font-bold text-slate-500 uppercase tracking-wider">Kata Kunci Target</label>
      <div class="relative group">
        <span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-indigo-500 transition-colors">🔍</span>
        <input
          id="keyword-input"
          v-model="keyword"
          type="text"
          placeholder="Contoh: banjir jakarta 2025"
          class="w-full pl-11 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 placeholder:text-slate-400 outline-none focus:bg-white focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all font-medium"
          @keyup.enter="startCrawl"
        />
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

const selectedPlatforms = ref(["tiktok"]);
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

const formatNow = () => new Date().toLocaleTimeString('id-ID', { hour12: false });

const startCrawl = async () => {
  if (!canCrawl.value || isCrawling.value) return;
  
  isCrawling.value = true;
  crawlStatus.value = [];
  try {
    await crawlStore.startCrawl({
      platforms: selectedPlatforms.value,
      keyword: keyword.value,
      onStatus: (log) => {
        crawlStatus.value.push(log);
      },
    });
  } finally {
    isCrawling.value = false;
  }
};
</script>
