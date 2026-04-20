<template>
  <div class="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm flex flex-col h-full">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h3 class="text-xl font-black text-slate-900 tracking-tight">Sentiment Distribution</h3>
        <p class="text-xs font-bold text-slate-400 uppercase tracking-widest mt-1">Platform Comparison</p>
      </div>
      <div class="flex gap-2">
        <div class="flex items-center gap-1.5">
          <div class="w-2.5 h-2.5 rounded-full bg-blue-600"></div>
          <span class="text-[10px] font-black text-slate-500">Positive</span>
        </div>
        <div class="flex items-center gap-1.5">
          <div class="w-2.5 h-2.5 rounded-full bg-slate-400"></div>
          <span class="text-[10px] font-black text-slate-500">Neutral</span>
        </div>
        <div class="flex items-center gap-1.5">
          <div class="w-2.5 h-2.5 rounded-full bg-red-600"></div>
          <span class="text-[10px] font-black text-slate-500">Negative</span>
        </div>
      </div>
    </div>

    <div class="flex-1 min-h-[300px] relative">
      <Bar :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import { Bar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const chartData = {
  labels: ['TikTok', 'Instagram', 'Twitter', 'YouTube', 'Facebook'],
  datasets: [
    {
      label: 'Positive',
      backgroundColor: '#2563eb', // blue-600
      data: [45, 52, 38, 65, 42],
      borderRadius: 6,
    },
    {
      label: 'Neutral',
      backgroundColor: '#4b5563', // gray-600
      data: [30, 25, 42, 20, 38],
      borderRadius: 6,
    },
    {
      label: 'Negative',
      backgroundColor: '#dc2626', // red-600
      data: [25, 23, 20, 15, 20],
      borderRadius: 6,
    },
  ],
};

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      backgroundColor: '#1e293b',
      padding: 12,
      titleFont: { size: 14, weight: 'bold' },
      bodyFont: { size: 13 },
      cornerRadius: 12,
    },
  },
  scales: {
    x: {
      stacked: true,
      grid: {
        display: false,
      },
      ticks: {
        font: {
          weight: 'bold',
          size: 11,
        },
        color: '#94a3b8',
      },
    },
    y: {
      stacked: true,
      grid: {
        color: '#f1f5f9',
      },
      ticks: {
        font: {
          weight: 'bold',
          size: 11,
        },
        color: '#94a3b8',
      },
    },
  },
};
</script>
