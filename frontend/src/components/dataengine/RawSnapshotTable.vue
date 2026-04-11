<template>
  <div class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm shadow-slate-200/50">
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-slate-100 rounded-lg text-lg">📋</div>
        <h3 class="text-lg font-bold text-slate-900">Raw Snapshot</h3>
      </div>
      <span class="px-3 py-1 bg-slate-100 text-slate-500 rounded-full text-[11px] font-bold uppercase tracking-wider border border-slate-200">
        Latest 5 Records
      </span>
    </div>
    
    <div class="overflow-x-auto min-h-[220px]">
      <div v-if="rows.length === 0" class="flex flex-col items-center justify-center py-12 text-center text-slate-400">
        <div class="text-4xl mb-4 bg-slate-50 w-16 h-16 flex items-center justify-center rounded-2xl">📭</div>
        <p class="text-sm font-medium">Belum ada data. Mulai crawling untuk melihat snapshot.</p>
      </div>
      
      <table v-else class="w-full border-collapse">
        <thead>
          <tr class="text-left border-b-2 border-slate-50">
            <th class="pb-3 text-[11px] font-black text-slate-400 uppercase tracking-widest">Platform</th>
            <th class="pb-3 text-[11px] font-black text-slate-400 uppercase tracking-widest pl-4">Teks / Deskripsi</th>
            <th class="pb-3 text-[11px] font-black text-slate-400 uppercase tracking-widest text-right">Waktu</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-50">
          <tr v-for="(row, i) in rows.slice(0, 5)" :key="i" class="group hover:bg-slate-50/50 transition-colors">
            <td class="py-4">
              <span 
                class="px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-tighter border"
                :class="{
                  'bg-black text-white border-black': row.platform?.toLowerCase() === 'tiktok',
                  'bg-pink-50 text-pink-600 border-pink-100': row.platform?.toLowerCase() === 'instagram',
                  'bg-red-50 text-red-600 border-red-100': row.platform?.toLowerCase() === 'youtube',
                  'bg-blue-50 text-blue-600 border-blue-100': row.platform?.toLowerCase() === 'news'
                }"
              >
                {{ row.platform || 'General' }}
              </span>
            </td>
            <td class="py-4 pl-4">
              <p class="text-sm text-slate-600 line-clamp-1 max-w-[400px] font-medium group-hover:text-slate-900 transition-colors">
                {{ row.text || row.description || 'No content available' }}
              </p>
            </td>
            <td class="py-4 text-right">
              <span class="text-[11px] font-mono font-bold text-slate-400 group-hover:text-slate-600 transition-colors">
                {{ formatTime(row.created_at) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
defineProps({ rows: { type: Array, default: () => [] } });

const formatTime = (ts) => {
  if (!ts) return "-";
  try {
    const d = new Date(ts);
    return isNaN(d.getTime()) ? ts : d.toLocaleString("id-ID", { 
      day: '2-digit', 
      month: '2-digit', 
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return ts;
  }
};
</script>
