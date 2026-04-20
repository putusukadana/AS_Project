<template>
  <div class="bg-indigo-600 p-6 rounded-3xl shadow-xl shadow-indigo-100 flex flex-col h-full relative overflow-hidden group">
    <!-- Decorative Particles -->
    <div class="absolute top-0 right-0 w-32 h-32 bg-indigo-500 rounded-full blur-3xl opacity-50 -mr-16 -mt-16 group-hover:scale-125 transition-transform duration-1000"></div>
    <div class="absolute bottom-0 left-0 w-24 h-24 bg-white rounded-full blur-3xl opacity-10 -ml-12 -mb-12"></div>

    <div class="relative z-10 h-full flex flex-col">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center text-xl backdrop-blur-md border border-white/30">
            ✨
          </div>
          <div>
            <h3 class="text-xl font-black text-white tracking-tight">AI Insights Engine</h3>
            <p class="text-[10px] font-bold text-indigo-200 uppercase tracking-widest leading-none mt-1">Automated Analysis</p>
          </div>
        </div>
        
        <button class="flex items-center gap-2 px-3 py-1.5 bg-white/10 text-white rounded-lg border border-white/20 hover:bg-white hover:text-indigo-600 transition-all text-[10px] font-black uppercase tracking-tight backdrop-blur-sm shadow-sm group-hover:border-white/40">
          <span>📄</span> PDF Report
        </button>
      </div>

      <div class="space-y-4">
        <div 
          v-for="(insight, index) in insights" 
          :key="index"
          class="p-4 bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl hover:bg-white/15 transition-all cursor-default"
        >
          <div class="flex items-start gap-3">
            <span class="text-lg">{{ insight.icon }}</span>
            <div class="flex flex-col">
              <span class="text-[10px] font-black text-indigo-200 uppercase tracking-tighter">{{ insight.title }}</span>
              <p class="text-xs font-medium text-white/90 mt-1 leading-relaxed">
                {{ insight.content }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-auto pt-6 relative z-10">
      <button class="w-full py-3 bg-white text-indigo-600 rounded-xl font-black text-xs shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all active:scale-95">
        REGENERATE INSIGHTS
      </button>
    </div>
  </div>
</template>

<script setup>
const insights = [
  {
    icon: '📈',
    title: 'Trend Detection',
    content: 'Peningkatan sentimen positif sebesar 15% pada platform TikTok terkait keyword "Viral" dalam 24 jam terakhir.'
  },
  {
    icon: '⚠️',
    title: 'Crisis Alert',
    content: 'Terdeteksi akumulasi emosi "Marah" yang signifikan di Twitter. Disarankan pemantauan ketat pada keyword "Lambat".'
  },
  {
    icon: '💡',
    title: 'Content Strategy',
    content: 'Audiens merespon positif konten bertema "Edukasi Produk". Pertimbangkan untuk meningkatkan intensitas posting.'
  }
];
</script>
