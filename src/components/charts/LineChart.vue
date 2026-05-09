<template>
  <!-- 明确设置图表容器高度，避免父级无尺寸导致的 0 问题 -->
  <div ref="chartRef" class="echarts" style="width: 100%; height: 100%"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps(['data', 'title']) // 新增 title 用于示例，可按需调整
const chartRef = ref(null)
let chartInstance = null

// 初始化图表（仅在挂载时执行一次）
const initChart = () => {
  if (!chartRef.value || chartInstance) return // 防止重复初始化
  chartInstance = echarts.init(chartRef.value)
  updateChart() // 使用更新函数处理数据
}

// 更新图表（数据变化或窗口Resize时调用）
const updateChart = () => {
  if (!chartInstance || !props.data) return
  const option = {
    title: {
      text: props.title || '用户增长趋势', // 可选标题
      left: 'center',
      textStyle: { color: '#666' }
    },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: props.data.map(item => item.date),
      axisTick: { alignWithLabel: true }
    },
    yAxis: { type: 'value', splitLine: { lineStyle: { opacity: 0.2 } } },
    series: [
      {
        name: '用户数',
        type: 'line',
        smooth: true,
        data: props.data.map(item => item.value),
        areaStyle: {
          color: new echarts.graphic.LinearGradient(
            0, 0, 0, 1,
            [{ offset: 0, color: '#409EFF' }, { offset: 1, color: '#E6F7FF' }]
          )
        },
        itemStyle: { color: '#409EFF', borderColor: '#fff', borderWidth: 2 }
      }
    ]
  }
  chartInstance.setOption(option, true) // 第二个参数为 notMerge: false，合并配置
}

// 窗口Resize时调整图表尺寸
const resizeChart = () => {
  chartInstance?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', resizeChart)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  chartInstance?.dispose() // 销毁实例，避免内存泄漏
  chartInstance = null
})

// 监听数据变化，更新图表（避免重复初始化，使用 setOption）
watch(
  () => props.data,
  (newData) => {
    if (newData.length && chartInstance) {
      updateChart() // 调用更新函数，而非重新初始化
    }
  },
  { immediate: true } // 组件加载时立即更新（处理异步数据加载）
)
</script>