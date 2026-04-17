<template>
  <div class="flex flex-col gap-6 w-full">
    <RawStats :totalData="stats.total" :signalQuality="stats.quality" />
    <RawSnapshotTable :rows="rawData" />
    <ObsidianPipeline :steps="pipelineSteps" @analyze="runAnalysis" />
  </div>
</template>

<script setup>
import { computed } from "vue";
import RawStats from "./RawStats.vue";
import RawSnapshotTable from "./RawSnapshotTable.vue";
import ObsidianPipeline from "./ObsidianPipeline.vue";
import { useCrawlStore } from "@/stores/crawlStore";

const crawlStore = useCrawlStore();

const stats = computed(() => crawlStore.stats);
const rawData = computed(() => crawlStore.rawData);

const pipelineSteps = computed(() => [
  { id: "emoji_conversion", icon: "🎭", label: "Emoji Conversion", status: crawlStore.pipelineStatus.emoji_conversion },
  { id: "cleansing", icon: "🧹", label: "Data Cleansing", status: crawlStore.pipelineStatus.cleansing },
  { id: "normalization", icon: "📏", label: "Slang Normalization", status: crawlStore.pipelineStatus.normalization },
  { id: "stopwords", icon: "🚫", label: "Stopwords Removal", status: crawlStore.pipelineStatus.stopwords },
  { id: "sentiment_analysis", icon: "📊", label: "Sentiment Labeling", status: crawlStore.pipelineStatus.sentiment_analysis },
]);

const runAnalysis = async () => {
  await crawlStore.runSentimentAnalysis();
};
</script>
