<template>
  <aside class="w-64 bg-white border-r border-slate-200 flex flex-col pt-4 pb-6">
    <!-- Navigation Links -->
    <nav class="flex flex-col flex-1 px-4 gap-1">
      <router-link
        v-for="item in navItems"
        :key="item.id"
        :to="item.path"
        class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group no-underline"
        :class="activePage === item.id 
          ? 'bg-indigo-50 text-indigo-600 font-semibold shadow-sm' 
          : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'"
      >
        <span class="text-xl opacity-80 group-hover:scale-110 transition-transform">{{ item.icon }}</span>
        <span class="text-sm tracking-wide">{{ item.label }}</span>
        <!-- Active indicator -->
        <div v-if="activePage === item.id" class="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-600"></div>
      </router-link>
    </nav>

    <!-- Sidebar Footer -->
    <div class="px-6 mt-auto">
      <div class="p-4 bg-slate-50 border border-slate-200 rounded-2xl mb-4 group cursor-help" :title="`Available: ${quotaRemaining} / ${quotaLimit}`">
        <div class="flex items-center gap-2 mb-2">
          <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">API Quota</span>
          <span class="ml-auto text-xs font-bold" :class="quotaPercentage < 15 ? 'text-red-500' : 'text-indigo-600'">{{ quotaPercentage }}%</span>
        </div>
        <div class="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
          <div 
            class="h-full transition-all duration-700 ease-out"
            :class="quotaPercentage < 15 ? 'bg-red-500' : 'bg-indigo-500 group-hover:bg-indigo-600'"
            :style="{ width: quotaPercentage + '%' }"
          ></div>
        </div>
        <div class="mt-2 text-[10px] text-slate-400 font-medium text-center">
          {{ quotaRemaining }} / {{ quotaLimit }} requests left
        </div>
      </div>

      <div class="mb-4 p-4 bg-indigo-50 border border-indigo-100 rounded-2xl flex flex-col gap-3">
        <div class="flex items-center justify-between">
          <span class="text-[10px] uppercase tracking-tighter font-black text-indigo-400">Account Status</span>
          <span class="text-[10px] px-2 py-0.5 bg-indigo-100 text-indigo-600 rounded-full font-bold">Free Version</span>
        </div>
        <button class="w-full py-2 bg-white text-indigo-600 text-xs font-black rounded-lg border border-indigo-200 shadow-sm hover:bg-indigo-600 hover:text-white transition-all transform hover:-translate-y-0.5 active:scale-95">
          ✨ UPGRADE PLAN
        </button>
      </div>
      
      <!-- <router-link
        v-if="showNewCrawl"
        to="/data-engine"
        class="flex items-center justify-center gap-2 w-full py-3.5 bg-indigo-600 text-white text-center rounded-xl no-underline font-bold shadow-lg shadow-indigo-100 hover:bg-indigo-700 hover:-translate-y-0.5 transition-all active:scale-95"
      >
        🚀 New Crawl
      </router-link> -->
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '@/services/api';

defineProps({
  activePage: { type: String, default: "dashboard" },
  showNewCrawl: { type: Boolean, default: true },
});

const quotaRemaining = ref(0);
const quotaLimit = ref(100);

const quotaPercentage = computed(() => {
  if (quotaLimit.value === 0) return 0;
  return Math.round((quotaRemaining.value / quotaLimit.value) * 100);
});

const fetchQuota = async () => {
  try {
    const response = await api.get('/crawl/quota');
    if (response.data && response.data.status === 'success') {
      quotaRemaining.value = response.data.data.remaining;
      quotaLimit.value = response.data.data.limit;
    }
  } catch (error) {
    console.error('Failed to fetch quota:', error);
  }
};

onMounted(() => {
  fetchQuota();
  // Refresh quota every 30 seconds
  const interval = setInterval(fetchQuota, 30000);
  return () => clearInterval(interval);
});

const navItems = [
  { id: "dashboard", icon: "📊", label: "Dashboard", path: "/dashboard" },
  { id: "data-engine", icon: "⚙️", label: "Data Engine", path: "/data-engine" },
  { id: "reports", icon: "📈", label: "Reports", path: "#" },
  { id: "support", icon: "💬", label: "Support", path: "#" },
];
</script>
