<template>
  <div class="mt-8 space-y-3">
    <label class="block text-sm font-bold text-slate-500 uppercase tracking-wider">Upload Dataset</label>

    <div
      class="relative border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer"
      :class="isDragOver
        ? 'border-indigo-400 bg-indigo-50'
        : 'border-slate-200 bg-slate-50 hover:border-slate-300 hover:bg-slate-100'"
      @dragover.prevent="$emit('dragOver')"
      @dragleave.prevent="$emit('dragLeave')"
      @drop.prevent="$emit('fileDrop', $event)"
      @click="$refs.fileInput.click()"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".csv,.json,.xlsx,.xls"
        class="hidden"
        @change="$emit('fileSelect', $event)"
      />

      <div v-if="!uploadedFile">
        <span class="text-4xl block mb-3">📂</span>
        <p class="text-sm font-bold text-slate-600">
          Drag & drop file di sini, atau <span class="text-indigo-600 underline">browse</span>
        </p>
        <p class="text-[11px] text-slate-400 mt-2 font-medium">
          Format: .xlsx, .csv, .json — Maks 10MB
        </p>
      </div>

      <div v-else class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <span class="text-2xl">
            {{ uploadedFile.name.endsWith('.csv') ? '📊' : uploadedFile.name.endsWith('.json') ? '📋' : '📗' }}
          </span>
          <div class="text-left">
            <p class="text-sm font-bold text-slate-800 truncate max-w-[200px]">{{ uploadedFile.name }}</p>
            <p class="text-[11px] text-slate-400 font-medium">{{ (uploadedFile.size / 1024).toFixed(1) }} KB</p>
          </div>
        </div>
        <button
          class="text-xs font-bold text-rose-500 hover:text-rose-700 bg-rose-50 hover:bg-rose-100 px-3 py-1.5 rounded-lg transition-all"
          @click.stop="$emit('removeFile')"
        >
          ✕ Hapus
        </button>
      </div>
    </div>

    <p class="text-[11px] text-slate-400 pl-1 font-medium italic">
      * File harus memiliki kolom teks (misal: "text", "comment", "review", "content"). Kolom pertama akan digunakan jika tidak terdeteksi.
    </p>
  </div>
</template>

<script setup>
defineProps({
  uploadedFile: { type: Object, default: null },
  isDragOver: { type: Boolean, default: false },
});
defineEmits(['dragOver', 'dragLeave', 'fileDrop', 'fileSelect', 'removeFile']);
</script>
