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
  { id: "case_folding", icon: "🔡", label: "Case Folding", status: crawlStore.pipelineStatus.case_folding },
  { id: "url_removal", icon: "🔗", label: "URL Removal", status: crawlStore.pipelineStatus.url_removal },
  { id: "stopwords", icon: "🚫", label: "Stopwords Removal", status: crawlStore.pipelineStatus.stopwords },
  { id: "emotion", icon: "😊", label: "Emotion Detection", status: crawlStore.pipelineStatus.emotion },
]);

const runAnalysis = async () => {
  await crawlStore.runSentimentAnalysis();
};
</script>
