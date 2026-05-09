<template>
  <div class="dashboard-container">
    <!-- 页面标题 -->
    <div class="dashboard-header">
      <h1 class="dashboard-title">仪表盘</h1>
      <p class="dashboard-subtitle">系统概览与数据统计</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <StatCard
        v-for="(stat, index) in stats"
        :key="index"
        :title="stat.title"
        :value="stat.value"
        :icon="stat.icon"
        :trend="stat.trend"
        class="stat-item"
      />
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 图表区域 -->
      <div class="charts-section">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <h3>用户增长趋势</h3>
              <span class="chart-period">最近30天</span>
            </div>
          </template>
          <div class="chart-container">
            <LineChart :data="userGrowthData"/>
          </div>
        </el-card>

        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <h3>电影类型分布</h3>
              <span class="chart-period">当前数据</span>
            </div>
          </template>
          <div class="chart-container">
            <PieChart :data="genreDistribution"/>
          </div>
        </el-card>
      </div>

      <!-- 活动时间线 -->
      <div class="activity-section">
        <el-card class="activity-card">
          <template #header>
            <div class="card-header">
              <h3>最近活动</h3>
              <el-button link size="small" class="refresh-btn">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          <div class="activity-content">
            <ActivityTimeline :activities="recentActivities"/>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElCard, ElButton, ElIcon } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import StatCard from '@/components/admin/StatCard.vue'
import LineChart from '@/components/charts/LineChart.vue'
import PieChart from '@/components/charts/PieChart.vue'
import ActivityTimeline from '@/components/admin/ActivityTimeline.vue'
import { fetchDashboardData } from '@/api/admin'

// 数据状态
const stats = ref([])
const userGrowthData = ref([])
const genreDistribution = ref([])
const recentActivities = ref([])

// 获取数据（去除所有调试日志）
onMounted(async () => {
  try {
    const response = await fetchDashboardData()
    stats.value = [
      { title: '总用户', value: response.total_users, icon: 'user', trend: 'up' },
      { title: '总电影', value: response.total_movies, icon: 'film', trend: 'steady' },
      { title: '今日评论', value: response.today_reviews, icon: 'comment', trend: 'down' },
      { title: '系统状态', value: '健康', icon: 'monitor', trend: 'steady' }
    ]
    userGrowthData.value = response.user_growth
    genreDistribution.value = response.genre_distribution
    recentActivities.value = response.recent_activities
  } catch (error) {
    console.error('仪表盘数据加载失败:', error)
  }
})
</script>

<style scoped>
.dashboard-container {
  padding: 0;
  max-width: 1400px;
  margin: 0 auto;
}

/* 页面标题 */
.dashboard-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.dashboard-title {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 4px 0;
}

.dashboard-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-item {
  height: auto;
}

/* 主要内容区域 */
.main-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  align-items: start;
}

/* 图表区域 */
.charts-section {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.chart-card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  box-shadow: none;
  transition: all 0.3s;
}

.chart-card:hover {
  border-color: #409eff;
  transform: translateY(-1px);
}

.chart-container {
  height: 300px;
  padding: 16px;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 活动区域 */
.activity-section {
  height: fit-content;
}

.activity-card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  box-shadow: none;
  max-height: 600px;
  transition: all 0.3s;
}

.activity-card:hover {
  border-color: #409eff;
  transform: translateY(-1px);
}

.activity-content {
  max-height: 500px;
  overflow-y: auto;
  padding: 8px 0;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.chart-period {
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 4px;
}

.refresh-btn {
  color: #409eff;
  font-size: 12px;
  padding: 4px 8px;
}

.refresh-btn:hover {
  color: #66b1ff;
  background: rgba(64, 158, 255, 0.1);
}

/* 图表样式 */
:deep(.echarts) {
  width: 100% !important;
  height: 100% !important;
}

/* 滚动条样式 */
.activity-content::-webkit-scrollbar {
  width: 4px;
}

.activity-content::-webkit-scrollbar-track {
  background: #f5f7fa;
  border-radius: 2px;
}

.activity-content::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 2px;
}

.activity-content::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .activity-card {
    max-height: none;
  }

  .activity-content {
    max-height: 400px;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .chart-container {
    height: 250px;
    padding: 12px;
  }

  .dashboard-title {
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .chart-container {
    height: 200px;
    padding: 8px;
  }
}
</style>