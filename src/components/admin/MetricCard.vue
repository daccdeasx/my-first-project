<template>
  <el-card class="metric-card" shadow="hover">
    <div class="flex items-center justify-between">
      <div class="metric-content">
        <div class="metric-title">{{ title }}</div>
        <div class="metric-value">{{ value }}</div>
      </div>
      <div class="metric-icon" :style="{ backgroundColor: `${color}15` }">
        <i :class="`fa fa-${icon}`" :style="{ color }"></i>
      </div>
    </div>
    <div class="metric-trend" v-if="trend !== undefined">
      <span :style="{ color: trend >= 0 ? '#2ed573' : '#ff4757' }">
        <i class="fa" :class="trend >= 0 ? 'fa-arrow-up' : 'fa-arrow-down'"></i>
        {{ Math.abs(trend) }}%
      </span>
      <span class="trend-label">较上周</span>
    </div>
  </el-card>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  color: {
    type: String,
    default: '#409EFF'
  },
  trend: {
    type: Number,
    default: undefined
  }
})
</script>

<style scoped>
.metric-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: #ffffff;
  border: 1px solid #e4e7ed;
  box-shadow: none;
  transition: all 0.3s;
}

.metric-card:hover {
  border-color: #409eff;
  transform: translateY(-1px);
}

.flex {
  display: flex;
}

.items-center {
  align-items: center;
}

.justify-between {
  justify-content: space-between;
}

.metric-content {
  flex: 1;
}

.metric-title {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.metric-icon i {
  font-size: 18px;
}

.metric-trend {
  margin-top: 12px;
  display: flex;
  align-items: center;
  font-size: 12px;
  gap: 8px;
}

.trend-label {
  color: #909399;
}
</style>