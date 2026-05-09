<template>
  <div class="chart-container" :style="{ height }">
    <canvas ref="chartRef"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  settings: {
    type: Object,
    default: () => ({ x: 'x', y: 'y' })
  },
  height: {
    type: String,
    default: '300px'
  }
})

const chartRef = ref(null)
let chartInstance = null

const initChart = () => {
  if (!chartRef.value || !props.data.length) return
  
  // 销毁现有图表
  if (chartInstance) {
    chartInstance.destroy()
  }
  
  // 准备图表数据
  const labels = props.data.map(item => item[props.settings.x])
  const values = props.data.map(item => item[props.settings.y])
  
  // 创建新图表
  chartInstance = new Chart(chartRef.value, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: '',
        data: values,
        backgroundColor: '#409EFF',
        borderRadius: 4,
        barPercentage: 0.6,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          padding: 10,
          titleFont: {
            size: 14
          },
          bodyFont: {
            size: 13
          },
          displayColors: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        x: {
          grid: {
            display: false
          }
        }
      },
      animation: {
        duration: 1000,
        easing: 'easeOutQuart'
      }
    }
  })
}

onMounted(() => {
  initChart()
})

watch(() => props.data, () => {
  initChart()
})
</script>

<style scoped>
.chart-container {
  width: 100%;
}
</style>    