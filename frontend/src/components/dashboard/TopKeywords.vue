<template>
  <div class="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm flex flex-col h-full">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
      <div>
        <h3 class="text-xl font-black text-slate-900 tracking-tight">Top Keywords</h3>
        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">{{ totalUnique }} Unique Keywords</p>
      </div>

      <!-- Filter Tabs -->
      <div class="flex bg-slate-100 p-1 rounded-xl">
        <button
          v-for="f in filters"
          :key="f.key"
          @click="activeFilter = f.key"
          class="px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-tight transition-all"
          :class="activeFilter === f.key
            ? 'bg-white text-indigo-600 shadow-sm'
            : 'text-slate-500 hover:text-slate-700'"
        >
          {{ f.label }}
        </button>
      </div>
    </div>

    <div class="flex flex-wrap gap-2 overflow-y-auto max-h-[300px] pr-2 custom-scrollbar">
      <div
        v-for="kw in filteredKeywords"
        :key="kw.text"
        class="group flex items-center gap-2 px-4 py-2 bg-slate-50 border border-slate-100 rounded-2xl hover:border-indigo-200 hover:bg-white hover:shadow-sm transition-all cursor-default"
      >
        <span class="text-xs font-bold text-slate-700">{{ kw.text }}</span>
        <span class="text-[10px] font-black px-1.5 py-0.5 rounded-lg" :class="sentimentBadge(kw)">
          {{ kw.count }}
        </span>
      </div>
    </div>

    <div v-if="filteredKeywords.length === 0" class="flex-1 flex items-center justify-center py-10">
      <div class="text-center">
        <span class="text-4xl">📭</span>
        <p class="text-sm font-bold text-slate-400 mt-2">Belum ada data keywords</p>
        <p class="text-[10px] font-medium text-slate-300 mt-1">Jalankan crawling dan analisis sentimen terlebih dahulu.</p>
      </div>
    </div>

    <div class="mt-auto pt-6 border-t border-slate-50 flex items-center justify-between">
      <span class="text-[10px] font-bold text-slate-400">Total Unique: {{ totalUnique }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useCrawlStore } from '@/stores/crawlStore';

const crawlStore = useCrawlStore();

const activeFilter = ref('all');

const filters = [
  { key: 'all', label: 'All' },
  { key: 'Positif', label: 'Positive' },
  { key: 'Netral', label: 'Neutral' },
  { key: 'Negatif', label: 'Negative' },
];

const keywords = computed(() => crawlStore.keywords);

const filteredKeywords = computed(() => {
  if (activeFilter.value === 'all') {
    return keywords.value.overall || [];
  }
  return keywords.value.by_label?.[activeFilter.value] || [];
});

const totalUnique = computed(() => keywords.value.overall?.length || 0);

const sentimentBadge = (kw) => {
  const byLabel = keywords.value.by_label;
  if (!byLabel) return 'bg-slate-200 text-slate-600';

  const counts = {
    Positif: byLabel.Positif?.find(k => k.text === kw.text)?.count || 0,
    Netral: byLabel.Netral?.find(k => k.text === kw.text)?.count || 0,
    Negatif: byLabel.Negatif?.find(k => k.text === kw.text)?.count || 0,
  };

  const maxCount = Math.max(counts.Positif, counts.Netral, counts.Negatif);
  const dominant = maxCount === counts.Positif ? 'pos'
    : maxCount === counts.Negatif ? 'neg'
    : 'neu';

  return {
    pos: 'bg-blue-100 text-blue-600',
    neu: 'bg-slate-200 text-slate-600',
    neg: 'bg-red-100 text-red-600',
  }[dominant];
};
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}
</style>
