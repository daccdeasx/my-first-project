<template>
  <div class="collection-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">我的收藏</h1>
      <p class="page-subtitle" v-if="!loading">共收藏了 {{ movies.length }} 部电影</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p>正在加载收藏列表...</p>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="movies.length === 0" class="empty-state">
      <div class="empty-icon">
        <i class="icon-heart"></i>
      </div>
      <h3>还没有收藏任何电影</h3>
      <p>去发现一些精彩的电影吧！</p>
      <router-link to="/" class="discover-btn">
        <i class="icon-search"></i>
        发现电影
      </router-link>
    </div>

    <!-- 电影列表 -->
    <div v-else class="movies-container">
      <div class="movies-grid">
        <div
          v-for="movie in movies"
          :key="movie.tmdb_id"
          class="movie-card"
          @click="goToMovie(movie.tmdb_id)"
        >
          <div class="movie-poster">
            <img
              :src="`https://image.tmdb.org/t/p/w500${movie.poster_path}`"
              :alt="movie.title"
              @error="handleImageError"
            >
            <!-- 取消收藏按钮 - 右上角 -->
            <button
              @click.stop="removeFromCollection(movie.tmdb_id)"
              class="remove-favorite-btn"
            >
              取消收藏
            </button>
          </div>
          <div class="movie-info">
            <h3 class="movie-title">{{ movie.title }}</h3>
          </div>
        </div>
      </div>

      <!-- 分页控制 -->
      <div class="pagination" v-if="totalPages > 1">
        <button
          :disabled="currentPage === 1"
          @click="prevPage"
          class="page-btn"
          :class="{ disabled: currentPage === 1 }"
        >
          <i class="icon-arrow-left"></i>
          上一页
        </button>

        <div class="page-info">
          <span>第 {{ currentPage }} 页，共 {{ totalPages }} 页</span>
        </div>

        <button
          :disabled="currentPage === totalPages"
          @click="nextPage"
          class="page-btn"
          :class="{ disabled: currentPage === totalPages }"
        >
          下一页
          <i class="icon-arrow-right"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
      return {
          movies: [],
          loading: true,
          currentPage: 1,
          totalPages: 1,
          pageSize: 9 // 每页显示的电影数量
      }
  },
  async mounted() {
      await this.fetchCollection()
  },
  methods: {
      async fetchCollection() {
          try {
              const response = await axios.get(`/api/users/collection/?page=${this.currentPage}&page_size=${this.pageSize}`, {
                  headers: {
                      'Authorization': `Token ${localStorage.getItem('authToken')}`
                  }
              })
              this.movies = response.data.results
              this.totalPages = Math.ceil(response.data.count / this.pageSize)
          } catch (error) {
              console.error('获取收藏失败:', error)
              const message = error.response?.data?.error || '请求失败，请检查网络'
              this.$toast.error(`获取失败: ${message}`)
              if (error.response?.status === 401) {
                  this.$router.push('/login')
              }
          } finally {
              this.loading = false
          }
      },
      async removeFromCollection(tmdbId) {
          try {
              const response = await axios.delete(`/api/movies/${tmdbId}/favorite/`, {
                  headers: {
                      'Authorization': `Token ${localStorage.getItem('authToken')}`
                  }
              })

              // 安全访问响应数据
              const responseData = response?.data || {}
              if ([200, 204].includes(response.status)) {
                  this.movies = this.movies.filter(m => m.tmdb_id !== tmdbId)
                  this.$toast.success(responseData.detail || '已移除收藏')
              } else {
                  console.warn('未处理的响应状态:', response.status)
                  this.$toast.warning(responseData.message || '操作状态未知')
              }
          } catch (error) {
              console.error('完整错误日志:', {
                  message: error.message,
                  code: error.code,
                  response: error.response
              })

              // 安全访问错误信息
              const errorData = error.response?.data || {}
              const status = error.response?.status

              let message = '操作失败，请稍后重试'
              if (error.code === 'ERR_NETWORK') {
                  message = '网络连接异常'
              } else if (status === 404) {
                  message = errorData.error?.message || '收藏不存在'
              } else if (status === 401) {
                  message = '登录已过期'
                  this.$router.push('/login')
              } else if (status >= 500) {
                  message = errorData.error?.message || '服务器繁忙'
              } else if (errorData.message) {
                  message = errorData.message
              }

              this.$toast.error(message)

              // 强制刷新数据
              try {
                  await this.fetchCollection()
              } catch (err) {
                  console.error('刷新失败:', err)
                  this.$toast.error('数据同步失败')
              }
          }
      },
      prevPage() {
          if (this.currentPage > 1) {
              this.currentPage--
              this.fetchCollection()
          }
      },
      nextPage() {
          if (this.currentPage < this.totalPages) {
              this.currentPage++
              this.fetchCollection()
          }
      },
      goToMovie(tmdbId) {
          this.$router.push(`/movie/${tmdbId}`)
      },
      handleImageError(e) {
          e.target.src = '/placeholder-movie.jpg'
      }
  }
}
</script>

<style scoped>
/* 页面容器 */
.collection-page {
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
  font-size: 2.5rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 8px;
  background: linear-gradient(45deg, #e50914, #ff6b6b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

/* 加载状态 */
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.loading-spinner {
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(229, 9, 20, 0.3);
  border-top: 3px solid #e50914;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-spinner p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1rem;
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
  margin-bottom: 32px;
  line-height: 1.6;
}

.discover-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #e50914;
  color: #fff;
  padding: 12px 24px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
}

.discover-btn:hover {
  background: #b8070f;
  transform: translateY(-2px);
}

/* 电影容器 */
.movies-container {
  max-width: 1400px;
  margin: 0 auto;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

/* 电影卡片 */
.movie-card {
  background: var(--card-bg);
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid var(--border-color);
}

.movie-card:hover {
  transform: translateY(-8px);
  background: #2a2a2a;
  border-color: rgba(229, 9, 20, 0.3);
}

.movie-poster {
  position: relative;
  aspect-ratio: 2/3;
  overflow: hidden;
}

.movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.movie-card:hover .movie-poster img {
  transform: scale(1.05);
}

/* 取消收藏按钮 - 右上角 */
.remove-favorite-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  border: none;
  background: rgba(0, 0, 0, 0.8);
  color: #fff;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  opacity: 0;
  transform: translateY(-4px);
  white-space: nowrap;
}

.movie-card:hover .remove-favorite-btn {
  opacity: 1;
  transform: translateY(0);
}

.remove-favorite-btn:hover {
  background: #e50914;
  color: #fff;
  transform: translateY(-2px);
}

.movie-info {
  padding: 12px;
}

.movie-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-align: center;
}

/* 分页控制 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 40px;
  padding: 20px;
}

.page-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.page-btn:hover:not(.disabled) {
  background: #e50914;
  border-color: #e50914;
  transform: translateY(-2px);
}

.page-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .collection-page {
    padding: 60px 16px 20px;
  }

  .page-title {
    font-size: 2rem;
  }

  .movies-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 16px;
  }

  .movie-title {
    font-size: 0.8rem;
  }

  .pagination {
    flex-direction: column;
    gap: 12px;
  }

  .page-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>