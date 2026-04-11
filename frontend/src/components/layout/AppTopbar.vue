<template>
  <nav class="flex justify-between items-center px-6 h-16 bg-white border-b border-slate-200 sticky top-0 z-40">
    <!-- Logo & Title -->
    <div class="flex items-center gap-4">
      <router-link to="/dashboard" class="text-xl font-bold text-indigo-600 no-underline hover:text-indigo-700 transition-colors">
        🌌 AS Project
      </router-link>
    </div>

    <!-- Right Actions -->
    <div class="flex items-center gap-4">
      <!-- Search Input -->
      <div class="hidden md:flex items-center bg-slate-100 rounded-full px-4 py-1.5 border border-transparent focus-within:border-indigo-300 focus-within:bg-white transition-all">
        <span class="text-slate-400 mr-2 text-sm">🔍</span>
        <input 
          type="text" 
          placeholder="Search something..." 
          class="bg-transparent border-none outline-none text-sm text-slate-700 w-48 placeholder:text-slate-400"
        />
      </div>

      <!-- Notifications -->
      <button class="relative p-2 text-slate-500 hover:text-slate-900 transition-colors">
        <span class="text-xl">🔔</span>
        <span class="absolute top-1 right-1 bg-red-500 text-white text-[10px] px-1.5 py-0.5 rounded-full border-2 border-white">3</span>
      </button>

      <!-- User Profile Dropdown -->
      <div class="relative" @click="toggleDropdown">
        <div class="flex items-center gap-3 cursor-pointer group">
          <div class="flex flex-col text-right hidden sm:flex">
            <span class="text-sm font-semibold text-slate-700 group-hover:text-indigo-600 transition-colors">{{ user.username || 'User' }}</span>
            <span class="text-[11px] text-slate-400 leading-tight uppercase tracking-wider font-bold">Administrator</span>
          </div>
          <img 
            src="../assets/hero.png" 
            alt="Profile" 
            class="w-10 h-10 rounded-full bg-slate-200 border-2 border-transparent group-hover:border-indigo-200 transition-all p-0.5"
          />
        </div>

        <!-- Dropdown Menu -->
        <div 
          v-if="showDropdown" 
          class="absolute top-full right-0 mt-2 bg-white border border-slate-200 rounded-xl p-2 min-width-[200px] z-50 flex flex-col shadow-xl animate-in fade-in slide-in-from-top-2 duration-200"
        >
          <router-link to="/profile" class="p-3 text-slate-600 no-underline text-sm rounded-lg hover:bg-slate-50 hover:text-indigo-600 transition-colors flex items-center gap-3">
            <span>👤</span> Profile Settings
          </router-link>
          <a href="#" class="p-3 text-slate-600 no-underline text-sm rounded-lg hover:bg-slate-50 hover:text-indigo-600 transition-colors flex items-center gap-3">
            <span>🛡️</span> Security
          </a>
          <hr class="my-2 border-slate-100" />
          <button @click="handleLogout" class="p-3 text-red-600 text-sm rounded-lg hover:bg-red-50 transition-colors flex items-center gap-3 text-left w-full">
            <span>🚪</span> Logout
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const showDropdown = ref(false);
const user = JSON.parse(localStorage.getItem('user') || '{}');

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value;
};

const handleLogout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  router.push("/login");
};
</script>
