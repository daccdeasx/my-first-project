<template>
  <div ref="chartRef" class="echarts" style="width: 100%; height: 100%"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps(['data', 'title'])
const chartRef = ref(null)
let chartInstance = null

const initChart = () => {
  if (!chartRef.value || chartInstance) return
  chartInstance = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  if (!chartInstance || !props.data) return
  const option = {
    title: {
      text: props.title || '电影类型分布',
      left: 'center',
      textStyle: { fontSize: 14, color: '#666' }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a}<br/><span style="color:{color};">■</span> {b}: {c} ({d}%)',
      padding: 8,
      fontSize: 12
    },
    legend: {
      type: 'scroll', // 启用滚动
      orient: 'horizontal',
      bottom: '5%',
      left: 'center',
      pageButtonItemGap: 5,
      pageButtonStyle: { color: '#999' },
      itemWidth: 10,
      itemHeight: 10,
      textStyle: { fontSize: 11, color: '#666' },
      itemGap: 10, // 图例项间距
      pageIconColor: '#666',
      pageIconInactiveColor: '#ccc'
    },
    series: [
      {
        name: '类型占比',
        type: 'pie',
        radius: ['45%', '65%'], // 调整半径留出底部空间放图例
        center: ['50%', '40%'], // 上移饼图，留出底部空间
        avoidLabelOverlap: true,
        label: {
          show: false // 完全隐藏标签
        },
        labelLine: {
          show: false // 隐藏标签线
        },
        data: props.data.map(item => ({
          name: item.name.join('/'),
          value: item.value
        }))
      }
    ]
  }
  chartInstance.setOption(option, true)
}

const resizeChart = () => {
  chartInstance?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', resizeChart)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  chartInstance?.dispose()
  chartInstance = null
})

watch(
  () => props.data,
  (newData) => {
    if (newData.length && chartInstance) updateChart()
  },
  { immediate: true }
)
</script>