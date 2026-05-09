<template>
  <div class="yearly-report-page">
    <div class="report-container">
      <!-- 页面标题 -->
      <div class="report-header">
        <div class="header-content">
          <div class="title-section">
            <svg class="report-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 11H7a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2v-7a2 2 0 0 0-2-2zM13 7H11a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2zM17 3h-2a2 2 0 0 0-2 2v15a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <h1>{{ yearlyReport.year }}年度报告</h1>
          </div>
          <p class="report-subtitle">回顾您在{{ yearlyReport.year }}年的精彩时光</p>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-container">
        <div class="loading-spinner">
          <div class="spinner"></div>
          <p>正在生成您的年度报告...</p>
        </div>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-container">
        <div class="error-content">
          <svg class="error-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2"/>
            <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2"/>
          </svg>
          <h3>加载失败</h3>
          <p>{{ error }}</p>
          <button @click="loadReport" class="retry-btn">重新加载</button>
        </div>
      </div>

      <!-- 报告内容 -->
      <div v-else class="report-content">
        <!-- 观影数据 -->
        <div class="report-section">
          <div class="section-header">
            <svg class="section-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M23 7l-7 5 7 5V7z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <rect x="1" y="5" width="15" height="14" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
            </svg>
            <h2>观影数据</h2>
          </div>
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                  <polygon points="10,8 16,12 10,16 10,8" fill="currentColor"/>
                </svg>
              </div>
              <h3>观影数量</h3>
              <p class="number">{{ yearlyReport.watched_movies }}</p>
              <p class="unit">部电影</p>
            </div>
            <div class="stat-card">
              <div class="stat-icon">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <h3>评论数量</h3>
              <p class="number">{{ yearlyReport.reviews }}</p>
              <p class="unit">条评论</p>
            </div>
          </div>
        </div>

        <!-- 社区活跃度 -->
        <div class="report-section">
          <div class="section-header">
            <svg class="section-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <h2>社区活跃度</h2>
          </div>
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <h3>发帖数量</h3>
              <p class="number">{{ yearlyReport.posts }}</p>
              <p class="unit">篇帖子</p>
            </div>
            <div class="stat-card">
              <div class="stat-icon">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <h3>获得点赞</h3>
              <p class="number">{{ yearlyReport.likes_received }}</p>
              <p class="unit">个赞</p>
            </div>
          </div>
        </div>

        <!-- 活跃时间 -->
        <div class="report-section">
          <div class="section-header">
            <svg class="section-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <polyline points="12,6 12,12 16,14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <h2>活跃时间</h2>
          </div>
          <div class="time-stats">
            <div class="time-card">
              <div class="time-card-header">
                <svg class="time-card-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                  <polyline points="12,6 12,12 16,14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <h3>最活跃时段</h3>
              </div>
              <div class="time-list">
                <div v-for="hour in yearlyReport.favorite_hours" :key="hour.hour" class="time-item">
                  <span class="time">{{ hour.hour }}:00</span>
                  <div class="time-bar">
                    <div class="time-progress" :style="{ width: getTimePercentage(hour.count, yearlyReport.favorite_hours) + '%' }"></div>
                  </div>
                  <span class="count">{{ hour.count }}次</span>
                </div>
              </div>
            </div>
            <div class="time-card">
              <div class="time-card-header">
                <svg class="time-card-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                  <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2"/>
                  <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2"/>
                  <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2"/>
                </svg>
                <h3>最活跃月份</h3>
              </div>
              <div class="time-list">
                <div v-for="month in yearlyReport.active_months" :key="month.month" class="time-item">
                  <span class="time">{{ month.month }}月</span>
                  <div class="time-bar">
                    <div class="time-progress" :style="{ width: getTimePercentage(month.count, yearlyReport.active_months) + '%' }"></div>
                  </div>
                  <span class="count">{{ month.count }}次</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 个人成就 -->
        <div class="report-section">
          <div class="section-header">
            <svg class="section-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6M14 9h1.5a2.5 2.5 0 0 0 0-5H14M6 9v10a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V9M6 9h12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <h2>个人成就</h2>
          </div>
          <div class="achievement-stats">
            <div class="achievement-card">
              <div class="achievement-icon">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26 12,2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <h3>累计积分</h3>
              <p class="number">{{ yearlyReport.total_points }}</p>
              <p class="unit">积分</p>
            </div>
            <div class="achievement-card">
              <div class="achievement-icon">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                  <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2"/>
                  <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2"/>
                  <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2"/>
                </svg>
              </div>
              <h3>加入天数</h3>
              <p class="number">{{ yearlyReport.join_days }}</p>
              <p class="unit">天</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const isLoading = ref(true)
const error = ref('')

const yearlyReport = ref({
  year: new Date().getFullYear(),
  watched_movies: 0,
  reviews: 0,
  posts: 0,
  likes_received: 0,
  favorite_hours: [],
  active_months: [],
  total_points: 0,
  join_days: 0
})

// 计算时间百分比
const getTimePercentage = (count, dataArray) => {
  if (!dataArray || dataArray.length === 0) return 0
  const maxCount = Math.max(...dataArray.map(item => item.count))
  return maxCount > 0 ? (count / maxCount) * 100 : 0
}

// 加载报告数据
const loadReport = async () => {
  isLoading.value = true
  error.value = ''

  try {
    const response = await axios.get('/api/users/yearly-report/', {
      headers: {
        'Authorization': `Token ${localStorage.getItem('authToken')}`
      }
    })
    yearlyReport.value = response.data
  } catch (err) {
    console.error('获取年度报告失败:', err)
    if (err.response?.status === 401) {
      router.push('/login')
    } else {
      error.value = err.response?.data?.error || '获取年度报告失败，请稍后重试'
    }
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadReport()
})
</script>

<style scoped>
/* 年度报告页面样式 */
.yearly-report-page {
  min-height: 100vh;
  background: #141414;
  color: #fff;
  padding: 100px 20px 40px;
}

.report-container {
  max-width: 1200px;
  margin: 0 auto;
}

/* 页面头部 */
.report-header {
  text-align: center;
  margin-bottom: 40px;
}

.header-content {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 32px;
  backdrop-filter: blur(10px);
}

.title-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 12px;
}

.report-icon {
  width: 32px;
  height: 32px;
  color: #e50914;
}

.report-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.report-subtitle {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.1rem;
  margin: 0;
  line-height: 1.5;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 20px;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top: 4px solid #e50914;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-spinner p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
  margin: 0;
}

/* 错误状态 */
.error-container {
  display: flex;
  justify-content: center;
  padding: 80px 20px;
}

.error-content {
  text-align: center;
  max-width: 400px;
}

.error-icon {
  width: 48px;
  height: 48px;
  color: #ef4444;
  margin: 0 auto 16px;
}

.error-content h3 {
  font-size: 1.5rem;
  color: #fff;
  margin-bottom: 8px;
}

.error-content p {
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 24px;
  line-height: 1.5;
}

.retry-btn {
  background: #e50914;
  color: #fff;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 500;
}

.retry-btn:hover {
  background: #b8070f;
  transform: translateY(-1px);
}

/* 报告内容 */
.report-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* 报告区块 */
.report-section {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 24px;
  backdrop-filter: blur(10px);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.section-icon {
  width: 24px;
  height: 24px;
  color: #e50914;
}

.section-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

/* 统计网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(229, 9, 20, 0.3);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.stat-icon {
  width: 48px;
  height: 48px;
  color: #e50914;
  margin: 0 auto 16px;
}

.stat-card h3 {
  font-size: 1rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 12px;
}

.number {
  font-size: 2.5rem;
  font-weight: 700;
  color: #fff;
  margin: 8px 0;
  line-height: 1;
}

.unit {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
  margin: 0;
}

/* 时间统计 */
.time-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.time-card {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
}

.time-card:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(229, 9, 20, 0.3);
}

.time-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.time-card-icon {
  width: 20px;
  height: 20px;
  color: #e50914;
}

.time-card h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.time-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.time-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
}

.time {
  color: #fff;
  font-weight: 500;
  min-width: 60px;
  font-size: 0.9rem;
}

.time-bar {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.time-progress {
  height: 100%;
  background: linear-gradient(90deg, #e50914, #ff6b6b);
  border-radius: 3px;
  transition: width 0.8s ease;
}

.count {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.85rem;
  min-width: 40px;
  text-align: right;
}

/* 成就统计 */
.achievement-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.achievement-card {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.achievement-card:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(229, 9, 20, 0.3);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.achievement-icon {
  width: 48px;
  height: 48px;
  color: #f5b50a;
  margin: 0 auto 16px;
}

.achievement-card h3 {
  font-size: 1rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .yearly-report-page {
    padding: 80px 16px 40px;
  }

  .header-content {
    padding: 24px;
  }

  .title-section {
    flex-direction: column;
    gap: 12px;
  }

  .report-header h1 {
    font-size: 2rem;
  }

  .report-subtitle {
    font-size: 1rem;
  }

  .stats-grid,
  .time-stats,
  .achievement-stats {
    grid-template-columns: 1fr;
  }

  .time-item {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .time {
    min-width: auto;
    text-align: center;
  }

  .count {
    text-align: center;
    min-width: auto;
  }

  .number {
    font-size: 2rem;
  }
}
</style>