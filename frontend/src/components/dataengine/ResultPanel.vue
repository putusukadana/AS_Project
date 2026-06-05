<template>
  <div class="flex flex-col gap-6 w-full">
    <RawStats :totalData="stats.total" :signalQuality="stats.quality" />
    <RawSnapshotTable :rows="rawData" />
    <DataSummary :pipeline-meta="crawlStore.pipelineMeta" />
    <ObsidianPipeline :steps="pipelineSteps" :is-analyzing="isAnalyzing" :pipeline-meta="crawlStore.pipelineMeta" @analyze="runAnalysis" @retry="handleRetry" />

    <!-- Dataset Summary -->
    <!-- <div v-if="crawlStore.pipelineStatus.stemming === 'done'" class="bg-white/80 backdrop-blur-xl border border-slate-200/60 rounded-3xl p-6 shadow-2xl shadow-slate-200/40">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center text-lg border border-indigo-100">
          📋
        </div>
        <h4 class="text-lg font-black text-slate-900 tracking-tight">Dataset Summary</h4>
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
    </div> -->
  </div>
</template>

<script setup>
import { computed } from "vue";
import RawStats from "./RawStats.vue";
import RawSnapshotTable from "./RawSnapshotTable.vue";
import ObsidianPipeline from "./ObsidianPipeline.vue";
import DataSummary from "./DataSummary.vue";
import { useCrawlStore } from "@/stores/crawlStore";

const crawlStore = useCrawlStore();

const stats = computed(() => crawlStore.stats);
const rawData = computed(() => crawlStore.rawData);
const isAnalyzing = computed(() => crawlStore.isAnalyzing);

const pipelineMeta = computed(() => crawlStore.pipelineMeta);

const pipelineSteps = computed(() => [
  { id: "emoji_conversion", icon: "🎭", label: "Emoji Conversion", status: crawlStore.pipelineStatus.emoji_conversion },
  { id: "cleansing", icon: "🧹", label: "Data Cleansing", status: crawlStore.pipelineStatus.cleansing },
  { id: "normalization", icon: "📏", label: "Slang Normalization", status: crawlStore.pipelineStatus.normalization },
  { id: "stopwords", icon: "🚫", label: "Stopwords Removal", status: crawlStore.pipelineStatus.stopwords },
  { id: "stemming", icon: "🌱", label: "Indonesian Stemming", status: crawlStore.pipelineStatus.stemming },
]);

const runAnalysis = async () => {
  await crawlStore.runSentimentAnalysis();
};

const handleRetry = async (stepId) => {
  // We need to pass the same onStatus callback or a similar one if we want logs.
  // ExtractionPanel usually provides the onStatus to startCrawl, but here we can just run it.
  await crawlStore.retryStep(stepId, (msg) => console.log(msg.message));
};
</script>
