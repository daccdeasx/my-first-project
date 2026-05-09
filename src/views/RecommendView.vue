<template>
  <div class="recommend-container">
    <div class="header">
    </div>
    <div v-if="loading" class="loading-container">
      <div class="loader"></div>
      <p>数据加载中...</p>
    </div>

    <div v-else class="recommend-grid">
      <div 
        v-for="movie in recommendations" 
        :key="movie.id"
        class="movie-card"
        @click="showMovieDetail(movie)"
      >
        <div class="poster-wrapper">
          <!-- 添加加载状态和过渡效果 -->
          <transition name="fade">
            <div v-if="!imageLoaded" class="poster-skeleton">
              <div class="loading-spinner"></div>
            </div>
          </transition>
          
          <img 
            :src="getPosterUrl(movie.poster_path)" 
            :alt="movie.title + '海报'"
            class="poster-image"
            loading="lazy"
            @load="handleImageLoad"
            @error="handleImageError"
            :style="{ opacity: imageLoaded ? 1 : 0 }"
          />
        </div>
        
        <div class="movie-info">
          <h3 class="title">{{ movie.title }}</h3>
          <div class="rating-badge">
            <el-rate
              v-model="movie.rating"
              disabled
              :max="10"
              :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
              allow-half
            />
            <span class="rating-text">{{ movie.rating || '0.0' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getRecommendations } from '@/api/recommend'
import placeholderImage from '@/assets/placeholder.jpg'

export default {
  name: 'RecommendView',
  data() {
    return {
      loading: true,
      recommendations: [],
      imageLoaded: false
    }
  },
  computed: {
    // 移除重复的过滤器，改用计算属性
    posterUrl() {
      return (path) => {
        if (!path) return placeholderImage
        const cleanPath = String(path).replace(/^\/+/, '')
        return `https://image.tmdb.org/t/p/w500/${cleanPath}`
      }
    }
  },
  async created() {
    await this.fetchRecommendations()
  },
  methods: {
    // 新增方法处理海报路径
    getPosterUrl(path) {
      if (!path || typeof path !== 'string') return placeholderImage
      
      // 清洗路径并拼接完整URL
      const cleanPath = String(path)
        .replace(/^\/+/, '') // 移除开头斜杠
        .replace(/\/{2,}/g, '/') // 处理多余斜杠
      
      // 验证是否为有效图片路径
      const isValid = /\.(jpe?g|png|webp)$/i.test(cleanPath)
      
      return isValid 
        ? `https://image.tmdb.org/t/p/w500/${cleanPath}`
        : placeholderImage
    },

    async fetchRecommendations() {
      try {
        const { data } = await getRecommendations()
        if (data?.status === 'success') {
          this.recommendations = (data.recommendations || [])
            .map(movie => ({
              id: movie.tmdb_id,
              title: this.sanitizeTitle(movie.title),
              poster_path: movie.poster_path,
              rating: parseFloat(movie.vote_average?.toFixed(1)) || 0.0
            }))
        }
      } catch (error) {
        console.error('获取推荐失败:', error)
        this.$message.error('获取推荐失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },

    // 新增数据清洗方法
    normalizePosterPath(path) {
      if (!path) return ''
      // 移除可能存在的域名部分
      return String(path)
        .replace(/^https?:\/\/image\.tmdb\.org\/t\/p\/\w+\//, '')
        .replace(/^\/+/, '')
    },

    sanitizeTitle(title) {
      return (title || '未知标题')
        .replace('临时标题', '')
        .trim() || '默认标题'
    },
    showMovieDetail(movie) {
      this.$router.push({
        name: 'MovieDetail',
        params: { id: movie.id }
      })
    },
    handleImageLoad(event) {
      this.imageLoaded = true
      event.target.style.opacity = 1
    },
    handleImageError(event) {
      event.target.src = placeholderImage
      this.imageLoaded = true
    }
  }
}
</script>

<style scoped>
.recommend-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
  padding: 1.5rem;
  margin: 0 auto;
  max-width: 1400px;
}

.movie-card {
  background: transparent;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  overflow: hidden;
}

.movie-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.poster-wrapper {
  position: relative;
  aspect-ratio: 2/3;
  border-radius: 12px 12px 0 0;
  overflow: hidden;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.poster-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.movie-card:hover .poster-image {
  transform: scale(1.05);
}

.movie-info {
  padding: 1rem;
  background: #1a1a1a;
  border-radius: 0 0 12px 12px;
}

.title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0.5rem 0;
  height: 3em;
  line-height: 1.5;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  color: #ffffff;
}

.rating-badge {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin-top: 0.5rem;
}

.rating-text {
  font-weight: 600;
  font-size: 1.1rem;
  color: #f39c12;
  min-width: 2.5rem;
}

.el-rate {
  transform: scale(0.75);
  transform-origin: left;
  margin-right: -15px;
  display: inline-flex;
  align-items: center;
}

:deep(.el-rate__item) {
  margin-right: 2px !important;
}

:deep(.el-rate__icon) {
  font-size: 14px;
  margin-right: 0;
}

:deep(.el-rate__decimal) {
  right: 0;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: #666;
}

.loader {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.poster-skeleton {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
}

.loading-spinner {
  width: 35px;
  height: 35px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>