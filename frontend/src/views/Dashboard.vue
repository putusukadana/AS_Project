<template>
  <div class="flex flex-col h-screen bg-slate-50 overflow-hidden text-slate-900">
    <AppTopbar />
    <div class="flex flex-1 overflow-hidden">
      <AppSidebar activePage="dashboard" />
      <main class="flex-1 overflow-y-auto p-6 md:p-10 lg:p-12">
        <div class="max-w-[1600px] mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
          <!-- Page Header -->
          <div class="mb-10">
            <h1 class="text-4xl font-black tracking-tight text-slate-900 mb-2">Analytics Dashboard</h1>
            <p class="text-slate-500 font-medium">Visualisasi real-time hasil ekstraksi dan analisis sentimen platform.</p>
          </div>

          <!-- Stats Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
            <div v-for="i in 4" :key="i" class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm animate-pulse">
              <div class="h-4 bg-slate-100 rounded-full w-1/3 mb-4"></div>
              <div class="h-8 bg-slate-100 rounded-lg w-2/3"></div>
            </div>
          </div>
          
          <!-- Charts Section Placeholder -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div class="bg-white border border-slate-200 rounded-3xl h-[400px] flex items-center justify-center shadow-sm relative overflow-hidden group">
              <div class="absolute inset-0 bg-gradient-to-br from-indigo-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <p class="text-slate-400 font-bold italic tracking-wide group-hover:scale-110 transition-transform">📉 Chart: Sentiment Over Time</p>
            </div>
            <div class="bg-white border border-slate-200 rounded-3xl h-[400px] flex items-center justify-center shadow-sm relative overflow-hidden group">
              <div class="absolute inset-0 bg-gradient-to-br from-violet-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <p class="text-slate-400 font-bold italic tracking-wide group-hover:scale-110 transition-transform">📊 Chart: Platform Distribution</p>
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
</script>
