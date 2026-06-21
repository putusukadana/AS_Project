<template>
  <div class="flex flex-col gap-6 w-full">
    <RawSnapshotTable :rows="rawData" />
    <DataSummary />
    <ObsidianPipeline :steps="pipelineSteps" :is-analyzing="isAnalyzing" @analyze="runAnalysis" @retry="handleRetry" />
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import RawSnapshotTable from "./RawSnapshotTable.vue";
import ObsidianPipeline from "./ObsidianPipeline.vue";
import DataSummary from "./DataSummary.vue";
import { useCrawlStore } from "@/stores/crawlStore";

const crawlStore = useCrawlStore();
const router = useRouter();

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
  if (crawlStore.analyzedData && crawlStore.analyzedData.length > 0) {
    router.push("/dashboard");
  }
};

const handleRetry = async (stepId) => {
  // We need to pass the same onStatus callback or a similar one if we want logs.
  // ExtractionPanel usually provides the onStatus to startCrawl, but here we can just run it.
  await crawlStore.retryStep(stepId, (msg) => console.log(msg.message));
};
</script>
