<template>
  <div class="ranking-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <i class="icon-trophy"></i>
        电影排行榜
      </h1>
      <p class="page-subtitle">数据更新于 {{ lastUpdated }}</p>
    </div>

    <!-- 分类选项卡 -->
    <div class="ranking-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        :class="['tab-btn', { 'active': activeTab === tab.key }]"
        @click="activeTab = tab.key"
      >
        <i :class="`icon-${tab.icon}`"></i>
        {{ tab.title }}
      </button>
    </div>

    <!-- 内容区域 -->
    <div class="tab-content">
      <template v-if="currentTab.loading">
        <!-- 骨架屏 -->
        <div class="skeleton-grid">
          <div
            v-for="n in 8"
            :key="n"
            class="skeleton-item"
          >
            <div class="skeleton-poster"></div>
            <div class="skeleton-text"></div>
            <div class="skeleton-meta"></div>
          </div>
        </div>
      </template>

      <template v-else>
        <!-- 电影网格 -->
        <div v-if="currentTab.movies.length" class="movies-grid">
          <div
            v-for="(movie, index) in currentTab.movies"
            :key="movie.id"
            class="ranking-card"
            @click="$router.push(`/movie/${movie.id}`)"
          >
            <div class="movie-poster">
              <img
                :src="movie.poster_path"
                :alt="movie.title"
                class="poster-image"
                @error="handleImageError"
              >
              <div class="ranking-badge" :class="getRankingClass(getRealRanking(index))">
                {{ getRealRanking(index) }}
              </div>
            </div>
            <div class="movie-info">
              <h3 class="movie-title">{{ movie.title }}</h3>
              <div class="movie-meta">
                <div class="rating-info">
                  <i class="icon-star"></i>
                  <span class="rating-score">{{ (movie.rating / 10).toFixed(1) }}</span>
                </div>
                <div class="movie-year">{{ movie.year }}</div>
              </div>
              <div class="vote-count">{{ formatVotes(movie.votes) }}人评价</div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <div class="empty-icon">
            <i class="icon-trophy"></i>
          </div>
          <h3>暂时没有相关内容</h3>
          <p>请尝试其他分类或稍后重试</p>
        </div>

        <!-- 分页 -->
        <div v-if="currentTab.totalPages > 1" class="pagination">
          <button
            :disabled="currentTab.currentPage === 1"
            @click="changePage(currentTab.currentPage - 1)"
            class="page-btn prev-btn"
          >
            <i class="icon-arrow-left"></i>
            上一页
          </button>

          <div class="page-numbers">
            <button
              v-for="page in pageNumbers"
              :key="page"
              :class="['page-number', { active: currentTab.currentPage === page }]"
              @click="changePage(page)"
            >
              {{ page }}
            </button>
          </div>

          <button
            :disabled="currentTab.currentPage === currentTab.totalPages"
            @click="changePage(currentTab.currentPage + 1)"
            class="page-btn next-btn"
          >
            下一页
            <i class="icon-arrow-right"></i>
          </button>
        </div>
      </template>
    </div>
  </div>
</template>
<script>
import http from '@/utils/axios'
import dayjs from 'dayjs'

export default {
  data: () => ({
    activeTab: 'top_rated',
    lastUpdated: dayjs().format('YYYY-MM-DD HH:mm'),
    tabs: [
      {
        key: 'top_rated',
        title: '高分神作',
        icon: 'star',
        movies: [],
        loading: false,
        currentPage: 1,
        totalPages: 1,
        params: {
          type: 'top_rated',
          region: 'CN',
          language: 'zh-CN'
        }
      },
      {
        key: 'popular',
        title: '热门精选',
        icon: 'mdi-fire',
        movies: [],
        loading: false,
        currentPage: 1,
        totalPages: 1,
        params: {
          type: 'popular',
          region: 'CN',
          language: 'zh-CN'
        }
      },
      {
        key: 'classic',
        title: '影史经典',
        icon: 'mdi-history',
        movies: [],
        loading: false,
        currentPage: 1,
        totalPages: 1,
        params: {
          type: 'discover',
          sort_by: 'vote_average.desc',
          'vote_count.gte': 5000,
          'primary_release_date.lte': '2000-01-01',
          language: 'zh-CN'
        }
      }
    ]
  }),
  computed: {
    currentTab() {
      return this.tabs.find(t => t.key === this.activeTab) || {}
    },
    pageNumbers() {
      return Array.from({ length: this.currentTab.totalPages }, (_, i) => i + 1)
    }
  },
  watch: {
    activeTab(newVal) {
      this.loadTabData(newVal)
    }
  },
  mounted() {
    this.loadTabData(this.activeTab)
  },
  methods: {
    async loadTabData(tabKey) {
      const tab = this.tabs.find(t => t.key === tabKey)
      if (!tab) return

      try {
        tab.loading = true
        console.log('正在请求：', '/movies/tmdb/', {
          params: {
            ...tab.params,
            page: tab.currentPage
          }
        })

        const { data } = await http.get('/movies/tmdb/', {
          params: {
            ...tab.params,
            page: tab.currentPage
          }
        }).catch(error => {
          console.log('请求错误详情：', error.config)
          throw error
        })

        tab.movies = (data.results || [])
          .filter(m => m.poster_path)
          .map((m, index) => ({
            ...m,
            id: m.id || Date.now() + index,
            rating: Math.round((m.vote_average || 0) * 10),
            year: m.release_date ? dayjs(m.release_date).format('YYYY') : '--',
            votes: m.vote_count || 0,
            title: m.title || m.original_title,
            poster_path: m.poster_path
              ? `https://image.tmdb.org/t/p/w500${m.poster_path}`
              : require('@/assets/default-poster.jpg')
          }))

        tab.totalPages = Math.min(data.total_pages || 1, 10)
        this.lastUpdated = dayjs().format('YYYY-MM-DD HH:mm')
      } catch (error) {
        this.handleApiError(error, '加载榜单数据')
        tab.movies = []
      } finally {
        tab.loading = false
      }
    },

    changePage(page) {
      if (page < 1 || page > this.currentTab.totalPages) return
      this.currentTab.currentPage = page
      this.loadTabData(this.activeTab)
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      })
    },

    getRealRanking(index) {
      // 计算真实的全局排名
      // 假设每页显示20部电影（这是TMDB API的默认值）
      const itemsPerPage = 20
      return (this.currentTab.currentPage - 1) * itemsPerPage + index + 1
    },

    getRankingClass(rank) {
      if (rank === 1) return 'gold'
      if (rank === 2) return 'silver'
      if (rank === 3) return 'bronze'
      return 'normal'
    },

    formatVotes(votes) {
      if (votes >= 10000) {
        return (votes / 10000).toFixed(1) + '万'
      }
      return votes.toString()
    },

    handleImageError(e) {
      e.target.src = '/placeholder-movie.jpg'
    },

    handleApiError(error, context = '未知操作') {
      const statusCode = error.response?.status ?? '无响应'
      const errorData = error.response?.data ?? {}
      const errorMessage = errorData.error
        || error.message
        || '未知错误'

      this.$toast.error(`${context}失败：${errorMessage}`)

      console.groupCollapsed(`API错误 - ${context}`)
      console.error('错误对象:', error)
      console.log('请求配置:', error.config)
      console.log('状态码:', statusCode)
      console.log('响应数据:', errorData)
      console.groupEnd()

      return {
        code: statusCode,
        message: errorMessage,
        details: errorData
      }
    }
  }
}
</script>

<style scoped>
/* 排行页面样式 */
.ranking-page {
  min-height: 100vh;
  background: #141414;
  color: #fff;
  padding: 80px 20px 40px;
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 2.5rem;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px 0;
  background: linear-gradient(45deg, #e50914, #ff6b6b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-title i {
  width: 32px;
  height: 32px;
  background: #f5b50a;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-title i::before {
  content: '';
  width: 16px;
  height: 16px;
  background: white;
  border-radius: 2px;
}

.page-subtitle {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

/* 选项卡 */
.ranking-tabs {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 40px;
  flex-wrap: wrap;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 500;
}

.tab-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  transform: translateY(-2px);
}

.tab-btn.active {
  background: #e50914;
  color: #fff;
  border-color: #e50914;
  box-shadow: 0 4px 12px rgba(229, 9, 20, 0.3);
}

.tab-btn i {
  width: 16px;
  height: 16px;
  background: currentColor;
  border-radius: 3px;
  opacity: 0.8;
}

.tab-btn i::before {
  content: '';
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 1px;
}

/* 电影网格 */
.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
}

/* 排行卡片 */
.ranking-card {
  background: var(--card-bg);
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid var(--border-color);
}

.ranking-card:hover {
  transform: translateY(-8px);
  background: #2a2a2a;
  border-color: rgba(229, 9, 20, 0.3);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
}

/* 电影海报 */
.movie-poster {
  position: relative;
  aspect-ratio: 2/3;
  overflow: hidden;
}

.poster-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.ranking-card:hover .poster-image {
  transform: scale(1.05);
}

/* 排名徽章 */
.ranking-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.ranking-badge.gold {
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  color: #1a1a1a;
  border-color: #ffd700;
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.4);
}

.ranking-badge.silver {
  background: linear-gradient(135deg, #c0c0c0, #e5e5e5);
  color: #1a1a1a;
  border-color: #c0c0c0;
  box-shadow: 0 4px 12px rgba(192, 192, 192, 0.4);
}

.ranking-badge.bronze {
  background: linear-gradient(135deg, #cd7f32, #daa520);
  color: #fff;
  border-color: #cd7f32;
  box-shadow: 0 4px 12px rgba(205, 127, 50, 0.4);
}

.ranking-badge.normal {
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.3);
}

/* 电影信息 */
.movie-info {
  padding: 16px;
}

.movie-title {
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  margin: 0 0 8px 0;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.movie-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.rating-info {
  display: flex;
  align-items: center;
  gap: 4px;
}

.rating-info i {
  width: 12px;
  height: 12px;
  background: #f5b50a;
  border-radius: 2px;
}

.rating-info i::before {
  content: '';
  width: 6px;
  height: 6px;
  background: white;
  border-radius: 1px;
}

.rating-score {
  font-weight: 600;
  color: #f5b50a;
  font-size: 0.9rem;
}

.movie-year {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
}

.vote-count {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  max-width: 500px;
  margin: 0 auto;
}

.empty-icon {
  width: 80px;
  height: 80px;
  background: rgba(229, 9, 20, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
}

.empty-icon i {
  font-size: 2rem;
  color: #e50914;
}

.empty-state h3 {
  font-size: 1.5rem;
  color: #fff;
  margin-bottom: 12px;
}

.empty-state p {
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.6;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 40px;
  padding: 20px;
}

.page-btn {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.page-btn:hover:not(:disabled) {
  background: #e50914;
  border-color: #e50914;
  transform: translateY(-2px);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.page-numbers {
  display: flex;
  gap: 8px;
}

.page-number {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-number:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.page-number.active {
  background: #e50914;
  border-color: #e50914;
  color: #fff;
}

/* 骨架屏 */
.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.skeleton-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.skeleton-poster {
  aspect-ratio: 2/3;
  background: linear-gradient(90deg,
    rgba(255, 255, 255, 0.05) 25%,
    rgba(255, 255, 255, 0.1) 50%,
    rgba(255, 255, 255, 0.05) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 2s infinite;
}

.skeleton-text,
.skeleton-meta {
  height: 16px;
  background: linear-gradient(90deg,
    rgba(255, 255, 255, 0.05) 25%,
    rgba(255, 255, 255, 0.1) 50%,
    rgba(255, 255, 255, 0.05) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 2s infinite;
  margin: 12px 16px;
  border-radius: 4px;
}

.skeleton-meta {
  width: 60%;
  margin-bottom: 16px;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ranking-page {
    padding: 60px 16px 20px;
  }

  .page-title {
    font-size: 2rem;
  }

  .ranking-tabs {
    gap: 8px;
  }

  .tab-btn {
    padding: 8px 16px;
    font-size: 0.8rem;
  }

  .movies-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 16px;
  }

  .pagination {
    flex-direction: column;
    gap: 12px;
  }

  .page-btn {
    width: 100%;
    justify-content: center;
  }

  .page-numbers {
    order: -1;
  }
}

@media (max-width: 480px) {
  .movies-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .ranking-tabs {
    flex-direction: column;
    align-items: center;
  }

  .tab-btn {
    width: 200px;
    justify-content: center;
  }
}
</style>