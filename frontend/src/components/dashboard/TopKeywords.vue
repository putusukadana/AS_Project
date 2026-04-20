<template>
  <div class="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm flex flex-col h-full">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
      <div>
        <h3 class="text-xl font-black text-slate-900 tracking-tight">Top Keywords</h3>
        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Trending Topics</p>
      </div>
      
      <!-- Filter Tabs -->
      <div class="flex bg-slate-100 p-1 rounded-xl">
        <button 
          v-for="f in filters" 
          :key="f.id"
          @click="activeFilter = f.id"
          class="px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-tight transition-all"
          :class="activeFilter === f.id 
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
        <span class="text-[10px] font-black px-1.5 py-0.5 rounded-lg" :class="sentimentColor(kw.sentiment)">
          {{ kw.count }}
        </span>
      </div>
    </div>

    <div class="mt-auto pt-6 border-t border-slate-50 flex items-center justify-between">
      <span class="text-[10px] font-bold text-slate-400">Total Unique: 1,240</span>
      <button class="text-[10px] font-black text-indigo-600 hover:underline">View All Keywords</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const activeFilter = ref('all');

const filters = [
  { id: 'all', label: 'All' },
  { id: 'pos', label: 'Positive' },
  { id: 'neu', label: 'Neutral' },
  { id: 'neg', label: 'Negative' },
];

const keywords = [
  { text: 'Viral', count: 850, sentiment: 'pos' },
  { text: 'Terpercaya', count: 720, sentiment: 'pos' },
  { text: 'Kualitas', count: 640, sentiment: 'pos' },
  { text: 'Mahal', count: 520, sentiment: 'neg' },
  { text: 'Lambat', count: 480, sentiment: 'neg' },
  { text: 'Standar', count: 420, sentiment: 'neu' },
  { text: 'Cukup', count: 390, sentiment: 'neu' },
  { text: 'Bagus', count: 350, sentiment: 'pos' },
  { text: 'Kecewa', count: 310, sentiment: 'neg' },
  { text: 'Update', count: 280, sentiment: 'neu' },
  { text: 'Rekomendasi', count: 250, sentiment: 'pos' },
  { text: 'Error', count: 210, sentiment: 'neg' },
  { text: 'Normal', count: 180, sentiment: 'neu' },
  { text: 'Mantap', count: 150, sentiment: 'pos' },
];

const filteredKeywords = computed(() => {
  if (activeFilter.value === 'all') return keywords;
  return keywords.filter(k => k.sentiment === activeFilter.value);
});

const sentimentColor = (s) => {
  if (s === 'pos') return 'bg-blue-100 text-blue-600';
  if (s === 'neg') return 'bg-red-100 text-red-600';
  return 'bg-slate-200 text-slate-600';
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
