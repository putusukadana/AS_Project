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
      // Skip if already done
      if (pipelineStatus.value[step] === "done") continue;

      pipelineStatus.value[step] = "running";
      const displayStep = step.replace('_', ' ');
      
      if (onStatus) onStatus({ type: "info", message: `⚙️ Menjalankan ${displayStep}...` });
      
      try {
        const res = await api.post(`/pipeline/${step}`);
        
        if (res.data && res.data.status === "error") {
          pipelineStatus.value[step] = "error";
          if (onStatus) {
            onStatus({ 
              type: "error", 
              message: res.data.message || `❌ Gagal pada ${displayStep}` 
            });
          }
          return; // Stop the loop on error
        }

        if (res.data && res.data.data) {
          rawData.value = res.data.data;
        }
        
        pipelineStatus.value[step] = "done";
        if (onStatus) onStatus({ type: "success", message: `✅ ${displayStep} selesai` });
      } catch (err) {
        pipelineStatus.value[step] = "error";
        if (onStatus) onStatus({ type: "error", message: `❌ ${displayStep} gagal: ${err.message}` });
        break;
      }
    }
  };

  const retryStep = async (stepId, onStatus) => {
    // Reset targeted step and any subsequent steps to idle if they aren't done
    const steps = ["emoji_conversion", "cleansing", "normalization", "stopwords", "sentiment_analysis"];
    const startIndex = steps.indexOf(stepId);
    
    if (startIndex !== -1) {
      // Optional: you might want to reset subsequent steps too, 
      // but runPipeline's loop logic already handles this by stopping at the first non-done step.
      pipelineStatus.value[stepId] = "idle"; 
      await runPipeline(onStatus);
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
