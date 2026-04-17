<template>
  <div class="bg-white/80 backdrop-blur-xl border border-slate-200/60 rounded-3xl p-7 shadow-2xl shadow-slate-200/40 relative overflow-hidden">
    <!-- Decorative background element -->
    <div class="absolute -top-24 -right-24 w-48 h-48 bg-indigo-500/5 blur-[100px] rounded-full"></div>
    <div class="absolute -bottom-24 -left-24 w-48 h-48 bg-violet-500/5 blur-[100px] rounded-full"></div>

    <div class="flex justify-between items-center mb-10 relative z-10">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 bg-gradient-to-br from-indigo-500 to-violet-600 rounded-2xl flex items-center justify-center text-2xl shadow-lg shadow-indigo-200/50 border border-white/20">
          <span class="animate-pulse">🔮</span>
        </div>
        <div>
          <h3 class="text-xl font-black text-slate-900 tracking-tight">Obsidian Pipeline</h3>
          <p class="text-[11px] text-slate-400 font-medium uppercase tracking-widest mt-0.5">Automated Intelligence</p>
        </div>
      </div>
      
      <Transition
        enter-active-class="transition duration-500 ease-out"
        enter-from-class="transform scale-95 opacity-0 translate-y-2"
        enter-to-class="transform scale-100 opacity-100 translate-y-0"
      >
        <div 
          v-if="allDone" 
          class="flex items-center gap-2 bg-emerald-500/10 text-emerald-600 text-[10px] font-black px-4 py-1.5 rounded-full border border-emerald-500/20 backdrop-blur-sm"
        >
          <span class="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-ping"></span>
          READY FOR ANALYSIS
        </div>
      </Transition>
    </div>

    <div class="space-y-4 relative z-10">
      <div
        v-for="(step, index) in steps"
        :key="step.id"
        class="relative flex items-center gap-5 p-4 rounded-2xl transition-all duration-500 group border"
        :class="{
          'border-amber-200 bg-gradient-to-r from-amber-50/80 to-transparent shadow-lg shadow-amber-100/20': step.status === 'running',
          'border-emerald-100 bg-emerald-50/20': step.status === 'done',
          'border-slate-100 bg-slate-50/30': step.status === 'idle',
          'border-rose-100 bg-rose-50/30': step.status === 'error'
        }"
      >
        <!-- Connector Line -->
        <div 
          v-if="index < steps.length - 1" 
          class="absolute left-[33px] top-[60px] w-0.5 h-6 bg-slate-100 transition-colors duration-500"
          :class="{ 'bg-emerald-100': step.status === 'done' }"
        ></div>

        <!-- Step Icon Container -->
        <div class="relative w-12 h-12 flex-shrink-0">
          <div 
            class="absolute inset-0 rounded-xl transition-all duration-500"
            :class="{
              'bg-amber-400 rotate-45 scale-90 blur-md opacity-40 animate-pulse': step.status === 'running',
              'bg-emerald-100 opacity-0 group-hover:opacity-100': step.status === 'done'
            }"
          ></div>
          <div 
            class="relative w-full h-full bg-white border rounded-xl flex items-center justify-center text-2xl shadow-sm transition-all duration-500 z-10"
            :class="{
              'border-amber-300 scale-110 shadow-amber-200/50': step.status === 'running',
              'border-emerald-200': step.status === 'done',
              'border-slate-200 grayscale opacity-60': step.status === 'idle'
            }"
          >
            <span :class="{ 'animate-bounce': step.status === 'running' }">{{ step.icon }}</span>
          </div>
        </div>
        
        <div class="flex flex-col flex-1">
          <span class="text-sm font-bold tracking-tight transition-colors duration-300" :class="step.status === 'idle' ? 'text-slate-400' : 'text-slate-800'">
            {{ step.label }}
          </span>
          <div class="flex items-center gap-2 mt-0.5">
            <span 
              class="text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded-md"
              :class="{
                'bg-amber-100 text-amber-600': step.status === 'running',
                'bg-emerald-100 text-emerald-600': step.status === 'done',
                'bg-slate-100 text-slate-400': step.status === 'idle',
                'bg-rose-100 text-rose-600': step.status === 'error'
              }"
            >
              {{ statusLabel(step.status) }}
            </span>
          </div>
        </div>

        <!-- Right Side Indicator -->
        <div class="w-10 h-10 flex items-center justify-center relative">
          <Transition mode="out-in">
            <div v-if="step.status === 'done'" key="done" class="text-emerald-500 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
            </div>
            <div v-else-if="step.status === 'running'" key="running" class="relative">
              <div class="w-6 h-6 border-2 border-amber-500/20 border-t-amber-500 rounded-full animate-spin"></div>
            </div>
            <div v-else key="idle" class="w-2 h-2 bg-slate-200 rounded-full"></div>
          </Transition>
        </div>
      </div>
    </div>

    <!-- Tombol Analisis -->
    <button
      v-if="allDone"
      class="group w-full p-4 bg-gradient-to-r from-indigo-600 to-violet-700 text-white rounded-2xl font-black mt-10 shadow-2xl shadow-indigo-200 hover:shadow-indigo-300 hover:-translate-y-1 active:translate-y-0 transition-all duration-300 relative overflow-hidden"
      :disabled="isAnalyzing"
      @click="$emit('analyze')"
    >
      <div class="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]"></div>
      <div class="flex items-center justify-center gap-3 relative z-10">
        <span v-if="isAnalyzing" class="animate-spin text-xl">🧠</span>
        <span v-else class="group-hover:rotate-12 transition-transform">🧠</span>
        <span class="tracking-wide">ANALISIS SEKARANG</span>
      </div>
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
    running: "Processing",
    done: "Selesai",
    error: "Gagal",
  })[s] || "-";
</script>

<style scoped>
@keyframes shimmer {
  100% {
    transform: translateX(100%);
  }
}

.v-enter-active,
.v-leave-active {
  transition: all 0.5s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
