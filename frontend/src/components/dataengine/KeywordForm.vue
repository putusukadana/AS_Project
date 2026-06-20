<template>
  <div class="relative group">
    <span class="absolute left-4 top-4 text-slate-400 group-focus-within:text-indigo-500 transition-colors">🔍</span>
    <input
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      @keyup.enter="$emit('submit')"
      type="text"
      placeholder="Contoh: banjir jakarta 2025"
      class="w-full pl-11 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 placeholder:text-slate-400 outline-none focus:bg-white focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all font-medium"
    />
  </div>
</template>

<script setup>
defineProps({ modelValue: { type: String, default: '' } });
defineEmits(['update:modelValue', 'submit']);
</script>
