<template>
  <div class="min-h-screen bg-slate-50/50 p-8">
    <div class="max-w-4xl mx-auto">
      <div class="mb-8">
        <router-link to="/dashboard" class="inline-flex items-center gap-2 text-sm font-bold text-slate-400 hover:text-indigo-600 transition-colors mb-3">
          ← Kembali
        </router-link>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">Settings</h1>
        <p class="text-sm text-slate-500 mt-1">Konfigurasi profil dan preferensi sistem</p>
      </div>

      <div class="flex gap-6">
        <!-- Sidebar -->
        <div class="w-56 shrink-0">
          <div class="bg-white border border-slate-200 rounded-3xl p-2 shadow-2xl shadow-slate-200/40">
            <button
              @click="activeSection = 'profile'"
              class="w-full flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-bold transition-all"
              :class="activeSection === 'profile' ? 'bg-indigo-50 text-indigo-600' : 'text-slate-500 hover:bg-slate-50'"
            >
              <span class="text-lg">👤</span>
              Profile Info
            </button>
            <button
              @click="activeSection = 'apikey'"
              class="w-full flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-bold transition-all"
              :class="activeSection === 'apikey' ? 'bg-indigo-50 text-indigo-600' : 'text-slate-500 hover:bg-slate-50'"
            >
              <span class="text-lg">🔑</span>
              API Key
            </button>
          </div>
        </div>

        <!-- Content -->
        <div class="flex-1 min-w-0">
          <!-- Profile Info -->
          <div v-if="activeSection === 'profile'" class="bg-white border border-slate-200 rounded-3xl p-6 shadow-2xl shadow-slate-200/40">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center text-lg border border-indigo-100">
                👤
              </div>
              <div>
                <h3 class="text-lg font-black text-slate-900 tracking-tight">Profile Info</h3>
                <p class="text-xs text-slate-400">Informasi akun Anda</p>
              </div>
            </div>

            <div class="space-y-4">
              <div>
                <label class="text-xs font-bold text-slate-400 uppercase tracking-widest block mb-1.5">Username</label>
                <div class="px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-700">
                  {{ user.username || '-' }}
                </div>
              </div>
              <div>
                <label class="text-xs font-bold text-slate-400 uppercase tracking-widest block mb-1.5">Email</label>
                <div class="px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-700">
                  {{ user.email || '-' }}
                </div>
              </div>
              <div>
                <label class="text-xs font-bold text-slate-400 uppercase tracking-widest block mb-1.5">Bergabung sejak</label>
                <div class="px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-700">
                  {{ user.created_at ? new Date(user.created_at).toLocaleDateString('id-ID', { year: 'numeric', month: 'long', day: 'numeric' }) : '-' }}
                </div>
              </div>
            </div>
          </div>

          <!-- API Key -->
          <div v-if="activeSection === 'apikey'" class="bg-white border border-slate-200 rounded-3xl p-6 shadow-2xl shadow-slate-200/40">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center text-lg border border-indigo-100">
                🔑
              </div>
              <div>
                <h3 class="text-lg font-black text-slate-900 tracking-tight">RapidAPI Key</h3>
                <p class="text-xs text-slate-400">API key untuk TikTok API 23 (opsional)</p>
              </div>
            </div>

            <div class="mb-4">
              <label class="text-xs font-bold text-slate-400 uppercase tracking-widest block mb-2">API Key</label>
              <div class="flex gap-3">
                <input
                  v-model="apiKey"
                  :type="showKey ? 'text' : 'password'"
                  placeholder="Masukkan RapidAPI key Anda"
                  class="flex-1 px-4 py-3 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                />
                <button
                  @click="showKey = !showKey"
                  class="px-4 py-3 border border-slate-200 rounded-xl text-sm hover:bg-slate-50 transition-colors"
                >
                  {{ showKey ? '🙈' : '👁️' }}
                </button>
              </div>
              <p class="text-xs text-slate-400 mt-2">
                {{ apiKey ? `Key berisi ${apiKey.length} karakter` : 'Kosong — akan menggunakan key default dari server' }}
              </p>
            </div>

            <button
              @click="saveKey"
              :disabled="saving"
              class="w-full px-6 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 text-white font-bold rounded-xl transition-colors text-sm"
            >
              {{ saving ? 'Menyimpan...' : 'Simpan API Key' }}
            </button>

            <div
              v-if="apiMessage"
              class="mt-4 px-4 py-3 rounded-xl text-sm font-medium"
              :class="apiMessageType === 'success' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-red-50 text-red-700 border border-red-200'"
            >
              {{ apiMessage }}
            </div>

            <div class="mt-6 pt-4 border-t border-slate-100">
              <ul class="text-sm text-slate-500 space-y-2 list-disc list-inside">
                <li>Key disimpan di database dan akan digunakan untuk semua request crawling</li>
                <li>Jika dikosongkan, sistem akan menggunakan key default dari server</li>
                <li>Dapatkan API key di <a href="https://rapidapi.com" target="_blank" class="text-indigo-600 hover:underline">rapidapi.com</a></li>
                <li>Layanan: <code class="bg-slate-100 px-1.5 py-0.5 rounded text-xs">TikTok API 23</code></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "@/services/api";

const activeSection = ref("profile");

const user = ref({
  username: "",
  email: "",
  created_at: "",
});

const apiKey = ref("");
const showKey = ref(false);
const saving = ref(false);
const apiMessage = ref("");
const apiMessageType = ref("success");

onMounted(() => {
  const stored = localStorage.getItem("user");
  if (stored) {
    try {
      user.value = JSON.parse(stored);
    } catch {
      // ignore
    }
  }
  fetchKey();
});

const fetchKey = async () => {
  try {
    const res = await api.get("/settings/rapidapi-key");
    if (res.data.status === "success" && res.data.data.value) {
      apiKey.value = res.data.data.value;
    }
  } catch {
    // Silent fail
  }
};

const saveKey = async () => {
  saving.value = true;
  apiMessage.value = "";
  try {
    const res = await api.put("/settings/rapidapi-key", { value: apiKey.value });
    if (res.data.status === "success") {
      apiMessage.value = "API key berhasil disimpan ✅";
      apiMessageType.value = "success";
    }
  } catch (err) {
    apiMessage.value = `Gagal menyimpan: ${err.message}`;
    apiMessageType.value = "error";
  } finally {
    saving.value = false;
  }
};
</script>
