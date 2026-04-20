<template>
  <div class="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm flex flex-col h-full">
    <div class="mb-6">
      <h3 class="text-xl font-black text-slate-900 tracking-tight">Emotional Spectrum</h3>
      <p class="text-xs font-bold text-slate-400 uppercase tracking-widest mt-1">Intensity Analysis</p>
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
  labels: ['Senang', 'Marah', 'Sedih', 'Takut', 'Terkejut', 'Lainnya'],
  datasets: [
    {
      label: 'Intensity',
      data: [85, 45, 30, 20, 55, 25],
      backgroundColor: [
        '#2563eb', // blue-600 (Senang)
        '#dc2626', // red-600 (Marah)
        '#D2DAFF', // (Sedih)
        '#9CB4CC', // (Takut)
        '#9EA1D4', // (Terkejut)
        '#c084fc', // purple-400 (Lainnya)
      ],
      borderRadius: 10,
      barThickness: 24,
    },
  ],
};

const chartOptions = {
  indexAxis: 'y', // Makes it a horizontal bar chart
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      backgroundColor: '#1e293b',
      padding: 12,
      cornerRadius: 12,
    },
  },
  scales: {
    x: {
      grid: {
        display: false,
      },
      ticks: {
        display: false,
      },
      border: {
        display: false,
      }
    },
    y: {
      grid: {
        display: false,
      },
      ticks: {
        font: {
          weight: 'black',
          size: 11,
        },
        color: '#64748b',
      },
      border: {
        display: false,
      }
    },
  },
};
</script>
