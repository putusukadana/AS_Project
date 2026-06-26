import { defineStore } from "pinia";
import { ref } from "vue";
import api from "@/services/api";
import { useToast } from "primevue/usetoast";

export const useCrawlStore = defineStore("crawl", () => {
  const rawData = ref([]);
  const stats = ref({ total: 0, quality: 0 });
  const pipelineStatus = ref({
    emoji_conversion: "idle",
    cleansing: "idle",
    normalization: "idle",
    stopwords: "idle",
    stemming: "idle",
  });
  const isAnalyzing = ref(false);
  const sentimentSummary = ref(null);
  const analyzedData = ref([]);
  const pipelineMeta = ref({});
  const keywords = ref({ overall: [], by_label: {} });
  const filterLang = ref(true);
  const convertEmoji = ref(true);

  const uploadFile = async ({ file, onStatus, signal }) => {
    onStatus({ type: "info", message: `📁 Mengupload file: ${file.name} (${(file.size / 1024).toFixed(1)} KB)` });
    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await api.post("/upload/file", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        signal,
      });

      if (res.data.status === "error") {
        onStatus({ type: "error", message: `❌ ${res.data.message}` });
        return;
      }

      rawData.value = res.data.data;
      stats.value = { total: res.data.total, quality: res.data.signal_quality };
      pipelineMeta.value = {};
      keywords.value = { overall: [], by_label: {} };

      pipelineStatus.value = {
        emoji_conversion: "idle",
        cleansing: "idle",
        normalization: "idle",
        stopwords: "idle",
        stemming: "idle",
      };

      onStatus({ type: "success", message: `✅ ${res.data.total} baris data berhasil dimuat — ${res.data.message}` });

      await runPipeline(onStatus);
    } catch (err) {
      if (err.name === 'CanceledError' || err.code === 'ERR_CANCELED') {
        onStatus({ type: "info", message: "⏹️ Crawling dibatalkan" });
        return;
      }
      onStatus({ type: "error", message: `❌ Upload gagal: ${err.message}` });
    }
  };

  const startCrawl = async ({ platforms, keyword, video_limit, start_date, end_date, onStatus, signal }) => {
    onStatus({ type: "info", message: `🚀 Memulai crawl untuk: "${keyword}" (Video limit: ${video_limit || 'Semua'})` });
    try {
      // Endpoint: /api/v1/crawl/start
      const res = await api.post("/crawl/start", { 
        platforms, 
        keyword,
        video_limit: video_limit || 0,
        start_date: start_date || null,
        end_date: end_date || null
      }, { signal });
      rawData.value = res.data.data;
      stats.value = { total: res.data.total, quality: res.data.signal_quality };
      pipelineMeta.value = {};
      pipelineStatus.value = {
        emoji_conversion: "idle",
        cleansing: "idle",
        normalization: "idle",
        stopwords: "idle",
        stemming: "idle",
      };
      keywords.value = { overall: [], by_label: {} };
      onStatus({
        type: "success",
        message: `✅ ${res.data.total} data berhasil dikumpulkan`,
      });
      // Otomatis jalankan pipeline
      await runPipeline(onStatus);
    } catch (err) {
      if (err.name === 'CanceledError' || err.code === 'ERR_CANCELED') {
        onStatus({ type: "info", message: "⏹️ Crawling dibatalkan" });
        return;
      }
      onStatus({ type: "error", message: `❌ Gagal: ${err.message}` });
    }
  };

  const runPipeline = async (onStatus) => {
    const steps = ["emoji_conversion", "cleansing", "normalization", "stopwords", "stemming"];
    
    for (const step of steps) {
      // Skip if already done
      if (pipelineStatus.value[step] === "done") continue;

      pipelineStatus.value[step] = "running";
      const displayStep = step.replace('_', ' ');
      
      if (onStatus) onStatus({ type: "info", message: `⚙️ Menjalankan ${displayStep}...` });
      
      try {
        const params = step === 'emoji_conversion' ? { convert_emoji: convertEmoji.value } : step === 'cleansing' ? { filter_lang: filterLang.value } : {};
        const res = await api.post(`/pipeline/${step}`, null, { params });
        
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

        if (res.data && res.data.meta) {
          pipelineMeta.value = {
            ...pipelineMeta.value,
            [step]: res.data.meta
          };
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
    const steps = ["emoji_conversion", "cleansing", "normalization", "stopwords", "stemming"];
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
      const res = await api.post("/analysis/sentiment");
      if (res.data && res.data.status === "done") {
        sentimentSummary.value = res.data.summary;
        analyzedData.value = res.data.data;
        await fetchKeywords();
      }
    } catch (err) {
      console.error("Analisis sentimen gagal:", err.message);
      const toast = useToast();
      toast.add({ severity: 'error', summary: 'Error', detail: 'Analisis sentimen gagal: ' + err.message, life: 3000 });
    } finally {
      isAnalyzing.value = false;
    }
  };

  const fetchKeywords = async () => {
    try {
      const res = await api.post("/analysis/keywords");
      if (res.data && res.data.status === "done") {
        keywords.value = {
          overall: res.data.overall,
          by_label: res.data.by_label
        };
      }
    } catch (err) {
      console.error("Gagal mengambil keywords:", err.message);
      const toast = useToast();
      toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal mengambil keywords: ' + err.message, life: 3000 });
    }
  };

  return {
    rawData,
    stats,
    pipelineStatus,
    isAnalyzing,
    sentimentSummary,
    analyzedData,
    pipelineMeta,
    keywords,
    startCrawl,
    uploadFile,
    runPipeline,
    retryStep,
    runSentimentAnalysis,
    fetchKeywords,
    filterLang,
    convertEmoji,
  };
});
