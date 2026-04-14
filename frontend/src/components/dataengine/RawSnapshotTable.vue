<template>
  <div class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm shadow-slate-200/50">
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-slate-100 rounded-lg text-lg">📊</div>
        <h3 class="text-lg font-bold text-slate-900">Extraction Summary</h3>
      </div>
      <span class="px-3 py-1 bg-indigo-50 text-indigo-600 rounded-full text-[11px] font-bold uppercase tracking-wider border border-indigo-100">
        Live Summary
      </span>
    </div>
    
    <div class="overflow-x-auto min-h-[200px]">
      <div v-if="rows.length === 0" class="flex flex-col items-center justify-center py-12 text-center text-slate-400">
        <div class="text-4xl mb-4 bg-slate-50 w-16 h-16 flex items-center justify-center rounded-2xl">📭</div>
        <p class="text-sm font-medium">Belum ada data. Mulai crawling untuk melihat ringkasan.</p>
      </div>
      
      <table v-else class="w-full border-collapse">
        <thead>
          <tr class="text-left border-b-2 border-slate-50">
            <th class="pb-3 text-[11px] font-black text-slate-400 uppercase tracking-widest">Platform</th>
            <th class="pb-3 text-[11px] font-black text-slate-400 uppercase tracking-widest text-center">Total Komentar</th>
            <th class="pb-3 text-[11px] font-black text-slate-400 uppercase tracking-widest text-center">Total Video</th>
            <th class="pb-3 text-[11px] font-black text-slate-400 uppercase tracking-widest text-center">Size Ekstraksi</th>
            <th class="pb-3 text-[11px] font-black text-slate-400 uppercase tracking-widest text-right">Preview Data</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-50">
          <tr v-for="summary in summaries" :key="summary.platform" class="group hover:bg-slate-50/50 transition-colors">
            <td class="py-4">
              <span 
                class="px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-tighter border"
                :class="{
                  'bg-black text-white border-black': summary.platform?.toLowerCase() === 'tiktok',
                  'bg-pink-50 text-pink-600 border-pink-100': summary.platform?.toLowerCase() === 'instagram',
                  'bg-red-50 text-red-600 border-red-100': summary.platform?.toLowerCase() === 'youtube',
                  'bg-blue-50 text-blue-600 border-blue-100': summary.platform?.toLowerCase() === 'news'
                }"
              >
                {{ summary.platform }}
              </span>
            </td>
            <td class="py-4 text-center">
              <span class="text-sm font-bold text-slate-700">
                {{ summary.totalComments.toLocaleString() }}
              </span>
            </td>
            <td class="py-4 text-center">
              <span class="text-sm font-bold text-slate-700">
                {{ summary.totalVideos.toLocaleString() }}
              </span>
            </td>
            <td class="py-4 text-center">
              <span class="text-[11px] font-mono font-bold text-slate-400 group-hover:text-slate-600">
                {{ (summary.totalSize / 1024).toFixed(2) }} MB
              </span>
            </td>
            <td class="py-4 text-right">
              <button
                v-if="summary.sampleComments.length > 0"
                @click="openPreview(summary)"
                class="text-[11px] font-bold text-indigo-500 hover:text-indigo-700 hover:underline transition-colors flex items-center gap-1 ml-auto"
              >
                Lihat 10 Komentar ↗
              </button>
              <span v-else class="text-[10px] text-slate-300 italic font-medium">No comments fetched</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({ 
  rows: { type: Array, default: () => [] } 
});

const summaries = computed(() => {
  const groups = {};
  props.rows.forEach(row => {
    const p = row.platform || 'General';
    if (!groups[p]) {
      groups[p] = {
        platform: p,
        totalVideos: 0,
        totalComments: 0,
        totalSize: 0,
        sampleComments: []
      };
    }
    groups[p].totalVideos++;
    groups[p].totalComments += (row.comment_count || 0);
    groups[p].totalSize += (row.estimated_size_kb || 0);
    if (groups[p].sampleComments.length === 0 && row.comment_sample?.length > 0) {
      groups[p].sampleComments = row.comment_sample;
    }
  });
  return Object.values(groups);
});

const openPreview = (summary) => {
  if (!summary.sampleComments || summary.sampleComments.length === 0) return;
  
  const commentsHtml = summary.sampleComments.map(c => `
    <tr style="border-bottom: 1px solid #f1f5f9;">
      <td style="padding: 12px; font-size: 13px; color: #1e293b; font-weight: 600; width: 120px;">@${c.user_unique_id || 'user'}</td>
      <td style="padding: 12px; font-size: 13px; color: #475569;">${c.text}</td>
    </tr>
  `).join('');
  
  const htmlContent = `
    <!DOCTYPE html>
    <html>
      <head>
        <title>Preview Komentar - ${summary.platform}</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
        <style>
          body { font-family: 'Inter', sans-serif; background: #f8fafc; color: #1e293b; padding: 40px; margin: 0; }
          .container { max-width: 800px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); overflow: hidden; }
          .header { padding: 24px; background: #000; color: white; }
          .header h1 { margin: 0; font-size: 20px; }
          .header p { margin: 4px 0 0; opacity: 0.7; font-size: 12px; }
          table { width: 100%; border-collapse: collapse; }
          th { background: #f1f5f9; text-align: left; padding: 12px; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>Preview 10 Komentar - ${summary.platform}</h1>
            <p>Snapshot dari data yang berhasil diekstraksi</p>
          </div>
          <table>
            <thead>
              <tr><th>Username</th><th>Komentar</th></tr>
            </thead>
            <tbody>${commentsHtml}</tbody>
          </table>
        </div>
      </body>
    </html>
  `;
  
  const blob = new Blob([htmlContent], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  window.open(url, '_blank');
};
</script>
