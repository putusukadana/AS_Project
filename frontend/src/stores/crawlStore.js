import { defineStore } from "pinia";
import { ref } from "vue";
import api from "@/services/api"; // Ensure this service exists

export const useCrawlStore = defineStore("crawl", () => {
  const rawData = ref([]);
  const stats = ref({ total: 0, quality: 0 });
  const pipelineStatus = ref({
    emoji_conversion: "idle",
    cleansing: "idle",
    normalization: "idle",
    stopwords: "idle",
    sentiment_analysis: "idle",
  });
  const isAnalyzing = ref(false);

  const startCrawl = async ({ platforms, keyword, start_date, end_date, onStatus }) => {
    onStatus({ type: "info", message: `🚀 Memulai crawl untuk: "${keyword}"` });
    try {
      // Endpoint: /api/v1/crawl/start
      const res = await api.post("/crawl/start", { 
        platforms, 
        keyword,
        start_date: start_date || null,
        end_date: end_date || null
      });
      rawData.value = res.data.data;
      stats.value = { total: res.data.total, quality: res.data.signal_quality };
      onStatus({
        type: "success",
        message: `✅ ${res.data.total} data berhasil dikumpulkan`,
      });
      // Otomatis jalankan pipeline
      await runPipeline(onStatus);
    } catch (err) {
      onStatus({ type: "error", message: `❌ Gagal: ${err.message}` });
    }
  };

  const runPipeline = async (onStatus) => {
    const steps = ["emoji_conversion", "cleansing", "normalization", "stopwords", "sentiment_analysis"];
    for (const step of steps) {
      pipelineStatus.value[step] = "running";
      onStatus({ type: "info", message: `⚙️ Menjalankan ${step.replace('_', ' ')}...` });
      try {
        // Endpoint: /api/v1/pipeline/{step}
        const res = await api.post(`/pipeline/${step}`);
        
        if (res.data && res.data.status === "error") {
          pipelineStatus.value[step] = "error";
          onStatus({ 
            type: "error", 
            message: res.data.message || `❌ Gagal pada ${step.replace('_', ' ')}` 
          });
          return;
        }

        if (res.data && res.data.data) {
          rawData.value = res.data.data;
        }
        pipelineStatus.value[step] = "done";
        onStatus({ type: "success", message: `✅ ${step.replace('_', ' ')} selesai` });
      } catch {
        pipelineStatus.value[step] = "error";
        onStatus({ type: "error", message: `❌ ${step.replace('_', ' ')} gagal` });
        break;
      }
    }
  };

  const runSentimentAnalysis = async () => {
    isAnalyzing.value = true;
    try {
      // Endpoint: /api/v1/analysis/sentiment
      await api.post("/analysis/sentiment");
      // Add notification or redirect to dashboard here if needed
    } finally {
      isAnalyzing.value = false;
    }
  };

  return {
    rawData,
    stats,
    pipelineStatus,
    isAnalyzing,
    startCrawl,
    runSentimentAnalysis,
  };
});
