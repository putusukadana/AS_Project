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
      <div class="p-4 bg-slate-50 border border-slate-200 rounded-2xl mb-4 group cursor-help">
        <div class="flex items-center gap-2 mb-2">
          <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">Storage Status</span>
          <span class="ml-auto text-xs font-bold text-indigo-600">85%</span>
        </div>
        <div class="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
          <div class="bg-indigo-500 h-full w-[85%] group-hover:bg-indigo-600 transition-colors"></div>
        </div>
      </div>
      
      <router-link
        to="/data-engine"
        class="flex items-center justify-center gap-2 w-full py-3.5 bg-indigo-600 text-white text-center rounded-xl no-underline font-bold shadow-lg shadow-indigo-100 hover:bg-indigo-700 hover:-translate-y-0.5 transition-all active:scale-95"
      >
        🚀 New Crawl
      </router-link>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  activePage: { type: String, default: "dashboard" },
});

const navItems = [
  { id: "dashboard", icon: "📊", label: "Dashboard", path: "/dashboard" },
  { id: "data-engine", icon: "⚙️", label: "Data Engine", path: "/data-engine" },
  { id: "reports", icon: "📈", label: "Reports", path: "#" },
  { id: "settings", icon: "🛠️", label: "Settings", path: "#" },
];
</script>
