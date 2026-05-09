<template>
  <div class="activity-timeline">
    <el-timeline v-if="activities.length">
      <el-timeline-item
        v-for="activity in activities"
        :key="activity.timestamp"
        placement="top"
        :timestamp="formatTime(activity.time_ago)"
        :type="getActivityType(activity.type)"
        :color="getActivityColor(activity.type)"
      >
        <template #icon>
          <el-icon :size="20" :color="getActivityColor(activity.type)">
            <component :is="getActivityIcon(activity.type)" />
          </el-icon>
        </template>

        <div class="activity-content">
          <!-- 用户注册活动 -->
          <div v-if="activity.type === 'user'" class="activity-item user-activity">
            <el-tag type="success" size="small">新用户</el-tag>
            <span class="username">{{ activity.user }}</span>
            <span class="action-text">注册了系统</span>
          </div>

          <!-- 评论活动 -->
          <div v-if="activity.type === 'review'" class="activity-item review-activity">
            <el-tag type="info" size="small">影评</el-tag>
            <span class="username">{{ activity.user }}</span>
            <span class="action-text">在电影</span>
            <el-link type="primary" underline="never" @click="handleMovieClick(activity.movie)">
              《{{ activity.movie }}》
            </el-link>
            <span class="action-text">发表了评论</span>
          </div>

          <!-- 绝对时间 -->
          <div class="absolute-time">
            {{ formatAbsoluteTime(activity.timestamp) }}
          </div>
        </div>
      </el-timeline-item>
    </el-timeline>

    <el-empty v-else description="暂无近期活动记录" />
  </div>
</template>

<script setup>
import { User, Comment } from '@element-plus/icons-vue'

const props = defineProps({
  activities: {
    type: Array,
    default: () => []
  }
})

// 图标映射
const typeIcons = {
  user: User,
  review: Comment
}

// 颜色映射
const typeColors = {
  user: '#67C23A',  // 绿色
  review: '#409EFF'  // 蓝色
}

// 时间格式化
const formatTime = (timeStr) => timeStr.replace(/ /g, ' ') // 处理特殊空格
const formatAbsoluteTime = (timestamp) => new Date(timestamp).toLocaleString('zh-CN', {
  year: 'numeric', month: '2-digit', day: '2-digit',
  hour: '2-digit', minute: '2-digit'
})

const getActivityIcon = (type) => typeIcons[type] || User
const getActivityColor = (type) => typeColors[type] || '#909399'
const getActivityType = (type) => type === 'user' ? 'success' : 'primary'

const handleMovieClick = (movieName) => {
  // 跳转到电影详情页逻辑（保留业务逻辑，去除调试日志）
  console.log('查看电影:', movieName) // 可替换为实际路由跳转
}
</script>

<style scoped>
.activity-timeline {
  padding: 0 16px;
}

.activity-content {
  padding: 12px;
  background: #fafafa;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  box-shadow: none;
  transition: all 0.3s;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.username {
  font-weight: 500;
  color: #303133;
}

.action-text {
  color: #606266;
}

.absolute-time {
  margin-top: 8px;
  font-size: 0.85em;
  color: #909399;
}

.el-link {
  vertical-align: baseline;
  color: #409eff;
}

.el-link:hover {
  color: #66b1ff;
}

.activity-content:hover {
  transform: translateY(-1px);
  border-color: #409eff;
  background: #ffffff;
}

/* 时间线样式覆盖 */
:deep(.el-timeline-item__node) {
  background-color: #409eff;
  border-color: #409eff;
}

:deep(.el-timeline-item__wrapper) {
  padding-left: 24px;
}

:deep(.el-timeline-item__tail) {
  border-left: 2px solid #e4e7ed;
}
</style>