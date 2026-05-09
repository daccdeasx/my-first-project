<template>
  <div class="data-analytics p-4 md:p-6">
    <!-- 页面标题 -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-800">数据分析仪表盘</h1>
      <p class="text-gray-500 mt-1">查看系统关键指标和用户行为分析</p>
    </div>

    <!-- 顶部工具栏 -->
    <div class="bg-white rounded-lg shadow-sm p-4 mb-6">
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div class="flex flex-wrap items-center gap-4">
          <div class="flex items-center">
            <span class="text-gray-600 mr-2">时间范围:</span>
            <el-date-picker
              v-model="timeRange"
              type="daterange"
              @change="loadData"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              size="small"
            />
          </div>
          
          <el-button 
            type="primary" 
            @click="exportData"
            :loading="exporting"
            size="small"
          >
            <el-icon><Download /></el-icon>导出报表
          </el-button>
          
          <el-button 
            type="text" 
            @click="refreshData"
            size="small"
            class="flex items-center text-gray-600 hover:text-primary"
          >
            <el-icon><Refresh /></el-icon>
            <span class="ml-1">刷新数据</span>
          </el-button>
        </div>
        
        <div class="text-sm text-gray-500 flex items-center">
          <el-icon class="mr-1"><Clock /></el-icon>
          上次更新: {{ lastUpdated || '未更新' }}
        </div>
      </div>
    </div>

    <!-- 快速指标卡片 -->
    <el-row :gutter="20" class="mb-6">
      <el-col :xs="24" :sm="12" :md="6" :lg="3" v-for="(metric, index) in metrics" :key="index">
        <MetricCard 
          :title="metric.title" 
          :value="metric.value"
          :icon="metric.icon"
          :color="metric.color"
          :trend="metric.trend"
        />
      </el-col>
    </el-row>

    <!-- 主图表区 (增加高度和宽度) -->
    <el-row :gutter="20" class="mb-6">
      <el-col :xs="24" :md="12">
        <el-card class="h-full" shadow="hover">
          <div class="flex justify-between items-center mb-4 px-4 pt-4">
            <h3 class="chart-title">用户增长趋势</h3>
          </div>
          <div class="p-4">
            <LineChart 
              :data="userGrowth"
              :settings="{ x: 'date', y: 'value' }"
              height="400px"
            />
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :md="12">
        <el-card class="h-full" shadow="hover">
          <div class="flex justify-between items-center mb-4 px-4 pt-4">
            <h3 class="chart-title">内容类型分布</h3>
          </div>
          <div class="p-4 flex items-center justify-center">
            <PieChart 
              :data="genreDistribution"
              :settings="{ name: 'name', value: 'value' }"
              height="400px"
              width="400px"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 次级图表区 -->
    <el-row :gutter="20" class="mb-6">
      <el-col :xs="24" :md="12">
        <el-card class="h-full chart-container" shadow="hover">
          <div class="flex justify-between items-center mb-4 px-4 pt-4">
            <h3 class="chart-title">评分分布</h3>
          </div>
          <div class="p-4">
            <BarChart
              :data="ratingDistribution"
              :settings="{ x: 'rating', y: 'count' }"
              height="300px"
            />
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :md="12">
        <el-card class="h-full chart-container" shadow="hover">
          <div class="px-4 pt-4">
            <h3 class="chart-title mb-4">系统负载</h3>
            <SystemLoad :performance="performance" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 活跃用户排行榜 -->
    <el-card shadow="hover">
      <div class="flex justify-between items-center mb-4 px-4 pt-4">
        <h3 class="mb-0">活跃用户TOP10</h3>
        <div class="flex items-center gap-2">
          <el-tooltip content="按登录次数排序">
            <el-button size="small" type="text" @click="sortBy('login_count')">
              <el-icon><ArrowUpBold /></el-icon>
              <span class="ml-1">登录次数</span>
            </el-button>
          </el-tooltip>
          <el-tooltip content="按评论数排序">
            <el-button size="small" type="text" @click="sortBy('review_count')">
              <el-icon><ArrowUpBold /></el-icon>
              <span class="ml-1">评论数</span>
            </el-button>
          </el-tooltip>
          <el-tooltip content="按收藏数排序">
            <el-button size="small" type="text" @click="sortBy('favorite_count')">
              <el-icon><ArrowUpBold /></el-icon>
              <span class="ml-1">收藏数</span>
            </el-button>
          </el-tooltip>
        </div>
      </div>
      <div class="p-4">
        <el-table 
          :data="activeUsers" 
          stripe 
          border
          highlight-current-row
          @row-click="handleRowClick"
        >
          <el-table-column 
            label="排名" 
            width="60"
          >
            <template #default="scope">
              <span class="font-semibold text-gray-600">{{ scope.$index + 1 }}</span>
            </template>
          </el-table-column>
          <el-table-column 
            label="用户信息"
            min-width="150"
          >
            <template #default="scope">
              <div>
                <div class="font-medium text-gray-800">{{ scope.row.username || scope.row.email }}</div>
                <div class="text-sm text-gray-500">{{ scope.row.email }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column 
            prop="login_count" 
            label="登录次数" 
            width="100"
            align="center"
          />
          <el-table-column 
            prop="review_count" 
            label="评论数" 
            width="100"
            align="center"
          />
          <el-table-column 
            prop="favorite_count" 
            label="收藏数" 
            width="100"
            align="center"
          />
          <el-table-column 
            label="最后登录" 
            width="160"
            align="center"
          >
            <template #default="scope">
              {{ formatDate(scope.row.last_login) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80" align="center">
            <template #default="scope">
              <el-button 
                size="mini" 
                type="text" 
                @click="viewUserDetail(scope.row)"
              >
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 用户详情对话框 -->
    <el-dialog v-model="detailVisible" title="用户详情">
      <UserDetail :user="selectedUser" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { ElCard, ElRow, ElCol, ElDatePicker, ElButton, ElTable, ElTableColumn, ElTooltip, ElMessage, ElSkeleton, ElDialog } from 'element-plus'
import { Download, More, Refresh, ArrowUpBold, Clock, ArrowDownBold } from '@element-plus/icons-vue'

import LineChart from '@/components/charts/LineChart.vue'
import PieChart from '@/components/charts/PieChart.vue'
import BarChart from '@/components/charts/BarChart.vue'
import SystemLoad from '@/components/admin/SystemLoad.vue'
import { fetchDataAnalytics, exportAnalyticsReport } from '@/api/admin'
import { useRouter } from 'vue-router'
import UserDetail from '@/components/users/UserDetail.vue'


// 数据状态
const stats = ref({
  total_users: 0,
  total_movies: 0,
  today_reviews: 0,
  user_growth: [],
  genre_distribution: [],
  rating_distribution: [],
  active_users: [],
  performance: {
    response_time: { min: 0, avg: 0, max: 0 },
    server_load: { cpu: 0, memory: 0 },
    database: { queries: 0, connections: 0 }
  }
})

// 计算属性
const userGrowth = ref([])
const genreDistribution = ref([])
const ratingDistribution = ref([])
const activeUsers = ref([])
const performance = ref({})
const lastUpdated = ref('')
const timeRange = ref([])
const metrics = ref([])
const exporting = ref(false)
const router = useRouter()

// 排序状态
const sortField = ref('login_count')
const sortOrder = ref('descending')

// 自动刷新定时器
let refreshTimer = null
let isComponentVisible = ref(true) // 组件可见性状态

// 新增详情相关状态
const detailVisible = ref(false)
const selectedUser = ref(null)

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '未登录'
  const date = new Date(dateStr)
  return date.toLocaleString()
}

// 初始化指标数据
const initMetrics = () => {
  metrics.value = [
    {
      title: '总用户数',
      value: stats.value.total_users,
      icon: 'user',
      color: '#409EFF',
      trend: Math.floor(Math.random() * 10) + 1
    },
    {
      title: '总电影数',
      value: stats.value.total_movies,
      icon: 'film',
      color: '#67C23A',
      trend: Math.floor(Math.random() * 10) + 1
    },
    {
      title: '今日评论',
      value: stats.value.today_reviews,
      icon: 'comment',
      color: '#E6A23C',
      trend: -(Math.floor(Math.random() * 5) + 1)
    },
    {
      title: '平均响应',
      value: `${performance.value?.response_time?.avg || 0}ms`,
      icon: 'timer',
      color: '#F56C6C',
      trend: Math.floor(Math.random() * 3) - 1
    }
  ]
}

// 加载数据
const loadData = async (timeRange = null) => {
  try {
    const params = timeRange? { start_date: timeRange[0], end_date: timeRange[1] } : {}
    const res = await fetchDataAnalytics(params)
    
    // 检查数据结构完整性
    if (!res.data) {
      throw new Error('返回数据格式不正确')
    }
    
    stats.value = res.data
    
    // 处理图表数据
    userGrowth.value = res.data.user_growth || []
    genreDistribution.value = res.data.genre_distribution || []
    ratingDistribution.value = res.data.rating_distribution || []
    
    // 处理活跃用户数据
    activeUsers.value = (res.data.active_users || []).map(user => ({
      ...user,
      avatar: user.avatar || 'https://picsum.photos/40/40'
    }))
    
    // 处理系统负载数据
    performance.value = res.data.performance || {
      response_time: { min: 0, avg: 0, max: 0 },
      server_load: { cpu: 0, memory: 0 },
      database: { queries: 0, connections: 0 }
    }
    
    initMetrics()
    
    // 更新最后更新时间
    const now = new Date()
    lastUpdated.value = now.toLocaleString()
    
    // 显示加载成功提示
    ElMessage({
      message: '数据刷新成功',
      type:'success',
      duration: 1500
    })
  } catch (error) {
    console.error('数据加载失败:', error)
    ElMessage({
      message: '数据加载失败，请稍后重试',
      type: 'error'
    })
    
    // 设置默认值避免界面一直加载
    performance.value = {
      response_time: { min: 0, avg: 0, max: 0 },
      server_load: { cpu: 0, memory: 0 },
      database: { queries: 0, connections: 0 }
    }
  }
}

// 手动刷新数据
const refreshData = () => {
  loadData(timeRange.value)
}

// 导出报表
const exportData = async () => {
  exporting.value = true
  
  try {
    const params = timeRange.value.length 
      ? { start_date: timeRange.value[0], end_date: timeRange.value[1] } 
      : {}
      
    const res = await exportAnalyticsReport(params)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `数据分析报表_${new Date().toISOString().slice(0, 10)}.xlsx`)
    document.body.appendChild(link)
    link.click()
    
    // 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage({
      message: '报表导出成功',
      type:'success'
    })
  } catch (error) {
    console.error('报表导出失败:', error)
    ElMessage({
      message: '报表导出失败，请稍后重试',
      type: 'error'
    })
  } finally {
    exporting.value = false
  }
}

// 处理排序变化
const sortBy = (field) => {
  // 切换排序方向
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'ascending' ? 'descending' : 'ascending'
  } else {
    sortField.value = field
    sortOrder.value = 'descending'
  }
  
  // 排序数据
  const sortType = sortOrder.value === 'ascending' ? 1 : -1
  activeUsers.value.sort((a, b) => {
    return sortType * (a[sortField.value] - b[sortField.value])
  })
}

// 查看详情
const showDetail = (type) => {
  router.push({ name: 'AnalyticsDetail', params: { type } })
}

// 查看用户详情
const viewUserDetail = (user) => {
  selectedUser.value = user
  detailVisible.value = true
}

// 处理行点击
const handleRowClick = (row) => {
  // 可以添加行点击的其他逻辑
}

// 监听页面可见性变化
const handleVisibilityChange = () => {
  isComponentVisible.value = document.visibilityState === 'visible'
}

// 生命周期钩子
onMounted(async () => {
  // 加载初始数据
  await loadData()
  
  // 设置自动刷新定时器
  refreshTimer = setInterval(() => {
    // 只有当组件可见且在当前路由时才刷新数据
    if (isComponentVisible.value && router.currentRoute.value.name === 'AdminDashboard') {
      loadData(timeRange.value)
    }
  }, 300000) // 5分钟
  
  // 监听页面可见性变化
  document.addEventListener('visibilitychange', handleVisibilityChange)
  
  // 监听时间范围变化
  watch(timeRange, (newVal) => {
    if (newVal && newVal.length === 2) {
      loadData(newVal)
    }
  })
})

onUnmounted(() => {
  // 清理定时器
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  
  // 移除事件监听
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})
</script>

<style scoped>
.data-analytics {
  background-color: #f5f7fa;
  min-height: 100vh;
}

.chart-title {
  @apply text-lg font-medium text-gray-700;
}

.el-card {
  border-radius: 10px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.el-table .cell {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.el-table__header th {
  background-color: #fafafa;
}

.el-date-picker {
  width: 280px;
}

/* 调整表格列间距 */
.el-table .user-info {
  padding-left: 0;
}

/* 新增：统一图表容器样式 */
.chart-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chart-container .el-card__body {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>