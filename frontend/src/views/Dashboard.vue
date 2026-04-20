<template>
  <div class="flex flex-col h-screen bg-slate-50 overflow-hidden">
    <!-- Top Navigation -->
    <AppTopbar />

    <div class="flex flex-1 overflow-hidden">
      <!-- Sidebar Navigation -->
      <AppSidebar activePage="dashboard" :show-new-crawl="false" />

      <!-- Main Layout -->
      <main class="flex-1 overflow-y-auto p-6 md:p-8 lg:p-10">
        <div class="max-w-[1600px] mx-auto space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
          
          <!-- Header Section -->
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div>
              <h1 class="text-4xl font-black text-slate-900 tracking-tight">Social Intelligence Center</h1>
              <p class="text-slate-500 mt-2 font-medium max-w-2xl">
                Pantau sebaran sentimen, spektrum emosi, dan wawasan cerdas dalam satu antarmuka terpadu.
              </p>
            </div>
          </div>

          <!-- Main Dashboard Grid -->
          <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-4 gap-6">
            <!-- Sentiment Distribution (Large) -->
            <div class="xl:col-span-2">
              <SentimentDistribution />
            </div>
            
            <!-- Emotional Spectrum -->
            <div class="xl:col-span-1">
              <EmotionalSpectrum />
            </div>
            
            <!-- AI Insights -->
            <div class="xl:col-span-1">
              <AIInsightsEngine />
            </div>

            <!-- Top Keywords (Wide on medium, mid on large) -->
            <div class="xl:col-span-4">
              <TopKeywords />
            </div>
          </div>

          <!-- Bottom Summary Statistics -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 pt-4">
            <StatCard 
              label="Global Reach" 
              value="2.4M" 
              icon="🌍" 
              :trend="12.5" 
              variant="indigo" 
            />
            <StatCard 
              label="Active Mentions" 
              value="84.2K" 
              icon="📢" 
              :trend="8.2" 
              variant="emerald" 
            />
            <StatCard 
              label="Avg. Sentiment" 
              value="Neutral+" 
              icon="😊" 
              :trend="2.4" 
              variant="amber" 
            />
          </div>

          <!-- Footer Info -->
          <div class="flex items-center justify-between text-[11px] font-bold text-slate-400 uppercase tracking-widest pb-10">
            <span>© 2026 AS Project Social Intelligence</span>
            <div class="flex gap-6">
              <a href="#" class="hover:text-indigo-600 transition-colors">Privacy Policy</a>
              <a href="#" class="hover:text-indigo-600 transition-colors">Terms of Service</a>
              <a href="#" class="hover:text-indigo-600 transition-colors">Documentation</a>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import AppTopbar from "@/components/layout/AppTopbar.vue";
import AppSidebar from "@/components/layout/AppSidebar.vue";
import SentimentDistribution from "@/components/dashboard/SentimentDistribution.vue";
import EmotionalSpectrum from "@/components/dashboard/EmotionalSpectrum.vue";
import TopKeywords from "@/components/dashboard/TopKeywords.vue";
import AIInsightsEngine from "@/components/dashboard/AIInsightsEngine.vue";
import StatCard from "@/components/dashboard/StatCard.vue";
</script>

<style>
/* Smooth chart entrance */
.chart-container {
  animation: chart-up 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes chart-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
