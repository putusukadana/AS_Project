<template>
  <div class="grid grid-cols-2 gap-6">
    <div class="bg-white border border-slate-200 rounded-2xl p-6 flex items-center gap-5 shadow-sm shadow-slate-200/50 hover:shadow-md transition-shadow duration-300">
      <div class="w-14 h-14 bg-indigo-50 border border-indigo-100 rounded-2xl flex items-center justify-center text-2xl shadow-inner">
        📊
      </div>
      <div class="flex flex-col">
        <span class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Total Data</span>
        <span class="text-3xl font-black text-slate-900 leading-none">{{ totalData }}</span>
      </div>
    </div>
    
    <div class="bg-white border border-slate-200 rounded-2xl p-6 flex items-center gap-5 shadow-sm shadow-slate-200/50 hover:shadow-md transition-shadow duration-300">
      <div class="w-14 h-14 bg-emerald-50 border border-emerald-100 rounded-2xl flex items-center justify-center text-2xl shadow-inner">
        📡
      </div>
      <div class="flex flex-col">
        <span class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Kualitas Sinyal</span>
        <div class="flex items-end gap-1">
          <span class="text-3xl font-black text-slate-900 leading-none">{{ signalQuality }}</span>
          <span class="text-sm font-bold text-emerald-600 mb-1">%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  totalData: { type: Number, default: 0 },
  signalQuality: { type: Number, default: 0 },
});
</script>
