<template>
  <div class="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm hover:shadow-md transition-all group overflow-hidden relative">
    <!-- Decorative Glow -->
    <div 
      class="absolute -right-4 -top-4 w-24 h-24 rounded-full opacity-0 group-hover:opacity-20 transition-opacity blur-2xl"
      :class="colorClass"
    ></div>

    <div class="flex items-center justify-between mb-4">
      <div 
        class="w-12 h-12 flex items-center justify-center rounded-2xl text-2xl shadow-sm"
        :class="bgClass"
      >
        {{ icon }}
      </div>
      <div v-if="trend" class="flex items-center gap-1 text-xs font-black" :class="trend > 0 ? 'text-emerald-500' : 'text-rose-500'">
        <span>{{ trend > 0 ? '↑' : '↓' }}</span>
        <span>{{ Math.abs(trend) }}%</span>
      </div>
    </div>

    <div class="flex flex-col">
      <span class="text-xs font-black text-slate-400 uppercase tracking-widest">{{ label }}</span>
      <span class="text-3xl font-black text-slate-900 mt-1 tabular-nums">{{ value }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  label: String,
  value: [String, Number],
  icon: String,
  trend: Number,
  variant: {
    type: String,
    default: 'indigo'
  }
});

const colorClass = computed(() => {
  const map = {
    indigo: 'bg-indigo-500',
    emerald: 'bg-emerald-500',
    rose: 'bg-rose-500',
    amber: 'bg-amber-500'
  };
  return map[props.variant] || map.indigo;
});

const bgClass = computed(() => {
  const map = {
    indigo: 'bg-indigo-50 text-indigo-600',
    emerald: 'bg-emerald-50 text-emerald-600',
    rose: 'bg-rose-50 text-rose-600',
    amber: 'bg-amber-50 text-amber-600'
  };
  return map[props.variant] || map.indigo;
});
</script>
