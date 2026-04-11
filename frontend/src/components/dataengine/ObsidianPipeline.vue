<template>
  <div class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm shadow-slate-200/50">
    <div class="flex justify-between items-center mb-8">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-indigo-50 rounded-lg text-lg border border-indigo-100">🔮</div>
        <h3 class="text-lg font-bold text-slate-900">Obsidian Pipeline</h3>
      </div>
      <span 
        v-if="allDone" 
        class="bg-emerald-50 text-emerald-600 text-[11px] font-bold px-3 py-1 rounded-full border border-emerald-200 animate-in fade-in zoom-in duration-300"
      >
        Ready for Analysis
      </span>
    </div>

    <div class="space-y-3">
      <div
        v-for="step in steps"
        :key="step.id"
        class="flex items-center gap-4 p-3.5 bg-slate-50 border rounded-xl transition-all duration-300 group"
        :class="{
          'border-amber-200 bg-amber-50/50 shadow-sm shadow-amber-100': step.status === 'running',
          'border-emerald-200 bg-emerald-50/30': step.status === 'done',
          'border-slate-200': step.status === 'idle'
        }"
      >
        <div class="relative w-11 h-11 bg-white border border-slate-200 rounded-lg flex items-center justify-center text-xl shadow-sm group-hover:scale-105 transition-transform">
          <span class="z-10">{{ step.icon }}</span>
          <!-- Loading Spinner -->
          <div v-if="step.status === 'running'" class="absolute inset-0 border-2 border-amber-300 border-t-transparent rounded-lg animate-spin"></div>
        </div>
        
        <div class="flex flex-col flex-1">
          <span class="text-sm font-bold text-slate-800">{{ step.label }}</span>
          <span 
            class="text-[11px] font-bold uppercase tracking-wider"
            :class="{
              'text-amber-500': step.status === 'running',
              'text-emerald-500': step.status === 'done',
              'text-slate-400': step.status === 'idle'
            }"
          >
            {{ statusLabel(step.status) }}
          </span>
        </div>

        <div class="w-8 h-8 flex items-center justify-center">
          <span v-if="step.status === 'done'" class="text-emerald-500 font-bold text-lg animate-in zoom-in duration-300">✔</span>
          <div v-else-if="step.status === 'running'" class="w-2.5 h-2.5 bg-amber-400 rounded-full animate-pulse shadow-[0_0_8px_rgba(251,191,36,0.6)]"></div>
          <div v-else class="w-1.5 h-1.5 bg-slate-200 rounded-full"></div>
        </div>
      </div>
    </div>

    <!-- Tombol Analisis -->
    <button
      v-if="allDone"
      class="w-full p-4 bg-gradient-to-r from-indigo-600 to-violet-600 text-white rounded-xl font-bold mt-8 shadow-xl shadow-indigo-100 hover:scale-[1.02] active:scale-[0.98] transition-all animate-in slide-in-from-bottom-4 fade-in duration-500"
      :disabled="isAnalyzing"
      @click="$emit('analyze')"
    >
      <span v-if="isAnalyzing" class="animate-spin mr-2 inline-block">⏳</span>
      🧠 Analisis Sekarang
    </button>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  steps: { type: Array, required: true },
  isAnalyzing: { type: Boolean, default: false }
});

defineEmits(["analyze"]);

const allDone = computed(() => props.steps.length > 0 && props.steps.every((s) => s.status === "done"));

const statusLabel = (s) =>
  ({
    idle: "Menunggu",
    running: "Sedang Berjalan...",
    done: "Selesai",
    error: "Gagal",
  })[s] || "-";
</script>
