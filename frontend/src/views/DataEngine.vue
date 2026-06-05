<template>
  <div class="flex flex-col h-screen bg-slate-50 overflow-hidden">
    <!-- Top Navigation -->
    <AppTopbar />

    <div class="flex flex-1 overflow-hidden">
      <!-- Sidebar Navigation -->
      <AppSidebar activePage="data-engine" :show-new-crawl="false" />

      <!-- Main Layout -->
      <main class="flex-1 overflow-y-auto p-6 md:p-8 lg:p-10">
        <div class="max-w-[1600px] mx-auto space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
          
          <!-- Header Section -->
          <div class="flex flex-col md:flex-row md:items-end justify-between gap-4">
            <div>
              <h1 class="text-4xl font-black text-slate-900 tracking-tight">TikTok Scraper & NLP Pipeline</h1>
              <p class="text-slate-500 mt-2 font-medium max-w-2xl">
                Alat ekstraksi data multi-platform yang terintegrasi dengan pipeline pemrosesan bahasa alami "Obsidian" 
                untuk analisis emosi dan sentimen real-time.
              </p>
            </div>
          </div>

          <!-- Component Grid -->
          <div class="grid grid-cols-1 lg:grid-cols-[400px_1fr] gap-8 items-start">
            <!-- Parameter Panel -->
            <ExtractionPanel />

            <!-- Results Section -->
            <ResultPanel />
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import AppTopbar from "@/components/layout/AppTopbar.vue";
import AppSidebar from "@/components/layout/AppSidebar.vue";
import ExtractionPanel from "@/components/dataengine/ExtractionPanel.vue";
import ResultPanel from "@/components/dataengine/ResultPanel.vue";
</script>
