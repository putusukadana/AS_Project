<template>
    <!-- Data Summary -->
    <div v-if="crawlStore.pipelineStatus.stemming === 'done'" class="bg-white/80 backdrop-blur-xl border border-slate-200/60 rounded-3xl p-6 shadow-2xl shadow-slate-200/40">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center text-lg border border-indigo-100">
          📋
        </div>
        <h4 class="text-lg font-black text-slate-900 tracking-tight">Data Summary</h4>
      </div>
      <div class="grid grid-cols-3 gap-4">
        <div class="bg-slate-50 rounded-2xl p-4 border border-slate-100 text-center">
          <span class="text-2xl font-black text-indigo-600">{{ pipelineMeta.stemming?.total_videos ?? 0 }}</span>
          <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Total Video</p>
        </div>
        <div class="bg-slate-50 rounded-2xl p-4 border border-slate-100 text-center">
          <span class="text-2xl font-black text-emerald-600">{{ pipelineMeta.stemming?.total_comments ?? 0 }}</span>
          <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Komentar Tersimpan</p>
        </div>
        <div class="bg-slate-50 rounded-2xl p-4 border border-slate-100 text-center">
          <span class="text-2xl font-black text-amber-600">{{ pipelineMeta.stemming?.total_filtered ?? 0 }}</span>
          <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Komentar Difilter</p>
        </div>
      </div>
    </div>
</template>

<script setup>
import { computed } from 'vue';
import { useCrawlStore } from '@/stores/crawlStore';

const crawlStore = useCrawlStore();

const pipelineMeta = computed(() => crawlStore.pipelineMeta);
</script>