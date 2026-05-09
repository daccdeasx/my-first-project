<template>
  <el-card class="stat-card" shadow="hover">
    <div class="flex items-center">
      <el-icon :size="40" :class="iconColor">
        <component :is="iconMap[icon]" />
      </el-icon>
      <div class="stat-content">
        <div class="stat-title">{{ title }}</div>
        <div class="stat-value">{{ value }}</div>
        <div class="stat-trend">
          <el-icon :class="trendColor">
            <CaretTop v-if="trend === 'up'" />
            <CaretBottom v-else-if="trend === 'down'" />
            <Minus v-else />
          </el-icon>
          <span :class="trendColor">{{ trendText }}</span>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import {
  User,
  Film,
  Comment,
  Monitor,
  CaretTop,
  CaretBottom,
  Minus
} from '@element-plus/icons-vue'

const props = defineProps({
  title: String,
  value: [String, Number],
  icon: String,
  trend: String // 'up' | 'down' | 'steady'
})

const iconMap = {
  user: User,
  film: Film,
  comment: Comment,
  monitor: Monitor
}

const iconColor = computed(() => {
  const colors = {
    'user': '#409eff',
    'film': '#67c23a',
    'comment': '#e6a23c',
    'monitor': '#f56c6c'
  }
  return { color: colors[props.icon] || '#409eff' }
})

const trendText = computed(() => {
  return {
    up: '+12%',
    down: '-5%',
    steady: '稳定'
  }[props.trend]
})

const trendColor = computed(() => {
  const colors = {
    'down': { color: '#ff4757' },
    'up': { color: '#2ed573' },
    'steady': { color: '#b3b3b3' }
  }
  return colors[props.trend] || { color: '#b3b3b3' }
})
</script>

<style scoped>
.stat-card {
  margin-bottom: 16px;
  transition: all 0.3s;
  background: #ffffff;
  border: 1px solid #e4e7ed;
  box-shadow: none;
}

.stat-card:hover {
  border-color: #409eff;
  transform: translateY(-1px);
}

.flex {
  display: flex;
}

.items-center {
  align-items: center;
}

.stat-content {
  margin-left: 16px;
  flex: 1;
}

.stat-title {
  color: #909399;
  font-size: 13px;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin: 4px 0;
}

.stat-trend {
  display: flex;
  align-items: center;
  font-size: 12px;
  gap: 4px;
}
</style>