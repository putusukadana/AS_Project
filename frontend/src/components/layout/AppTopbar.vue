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
      <!-- Notifications -->
      <button disabled title="Coming Soon" class="relative p-2 text-slate-400 cursor-not-allowed opacity-50 transition-colors">
        <span class="text-xl">🔔</span>
      </button>

      <!-- User Profile Dropdown -->
      <div class="relative" ref="dropdownContainer">
        <div class="flex items-center gap-3 cursor-pointer group" @click.stop="toggleDropdown">
          <div class="flex flex-col text-right hidden sm:flex">
            <span class="text-sm font-semibold text-slate-700 group-hover:text-indigo-600 transition-colors">{{ user.username || 'User' }}</span>
            <span class="text-[11px] text-slate-400 leading-tight uppercase tracking-wider font-bold">Administrator</span>
          </div>
          <img 
            src="@/assets/hero.png" 
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
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const showDropdown = ref(false);
const dropdownContainer = ref(null);
let user = {};
try {
  user = JSON.parse(localStorage.getItem('user') || '{}');
} catch (e) {
  console.error("Failed to parse user from localStorage:", e);
}

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value;
};

const closeDropdown = (e) => {
  if (dropdownContainer.value && !dropdownContainer.value.contains(e.target)) {
    showDropdown.value = false;
  }
};

onMounted(() => {
  window.addEventListener("click", closeDropdown);
});

onUnmounted(() => {
  window.removeEventListener("click", closeDropdown);
});

const handleLogout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  router.push("/login");
};
</script>
