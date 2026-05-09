<template>
  <div class="movie-detail-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p>正在加载电影信息...</p>
      </div>
    </div>

    <!-- 英雄区域 - 类似Netflix的大背景 -->
    <section class="hero-section" v-if="movieDetail.title">
      <!-- 背景图片（使用poster_path作为背景） -->
      <div class="hero-background" v-if="movieDetail.poster_path">
        <img
          :src="`https://image.tmdb.org/t/p/original${movieDetail.poster_path}`"
          :alt="movieDetail.title"
          class="backdrop-image"
        />
        <div class="hero-overlay"></div>
      </div>

      <!-- 如果没有背景图，使用渐变背景 -->
      <div class="hero-background-fallback" v-else></div>

      <div class="hero-content">
        <div class="meta-info" v-if="movieDetail.title">
          <span class="match">98% 匹配</span>
          <span class="year">{{ releaseYear }}</span>
          <span class="rating">{{ movieDetail.adult ? '18+' : '13+' }}</span>
          <span class="runtime">{{ formattedRuntime }}</span>
        </div>

        <h1 class="movie-title">{{ movieDetail.title || '加载中...' }}</h1>

        <div class="genres" v-if="movieDetail.genres && movieDetail.genres.length">
          <span
            v-for="genre in movieDetail.genres"
            :key="genre"
            class="genre-tag"
          >
            {{ genre }}
          </span>
        </div>

        <p class="overview">{{ movieDetail.overview || '暂无简介' }}</p>

        <div class="action-buttons" v-if="movieDetail.title">
          <button class="btn btn-primary" @click="goToTicketing">
            <i class="icon-play"></i>
            立即购票
          </button>
          <button class="btn btn-play" @click="goToPlayer" :disabled="loading">
            <i class="fas fa-play"></i>
            播放
          </button>
          <button
            :class="['btn', 'btn-secondary', { 'active': interaction.is_favorite }]"
            @click="handleFavorite"
          >
            <i class="icon-heart"></i>
            {{ interaction.is_favorite ? '已收藏' : '收藏' }}
          </button>
        </div>

        <div class="source-select-row" style="margin-top: 1rem;">
          <label for="source-select" style="color:#fff;margin-right:8px;">选择播放源：</label>
          <select id="source-select" v-model="selectedSource" class="source-select">
            <option v-for="key in sourceKeys" :key="key" :value="key">{{ apiSites[key].name }}</option>
          </select>
        </div>
      </div>

      <!-- 添加渐变过渡效果 -->
      <div class="hero-fade"></div>
    </section>

    <!-- 如果电影数据还没加载，显示基本信息区域 -->
    <section class="basic-info-fallback" v-else-if="!loading">
      <div class="fallback-content">
        <h1>电影详情加载中...</h1>
        <p>正在获取电影信息，请稍候...</p>
      </div>
    </section>

    <!-- 内容区域 -->
    <div class="content-container">
      <!-- 演员阵容 -->
      <section class="cast-section">
        <h2 class="section-title">演员阵容</h2>
        <div class="cast-grid">
          <div
            v-for="actor in mainCast"
            :key="actor.id"
            class="cast-card"
          >
            <div class="cast-image">
              <img
                :src="actor.profile_path
                  ? `https://image.tmdb.org/t/p/w300${actor.profile_path}`
                  : '/placeholder-actor.jpg'"
                :alt="actor.name"
                class="actor-photo"
              />
            </div>
            <div class="cast-info">
              <h4 class="actor-name">{{ actor.name }}</h4>
              <p class="character">{{ actor.character }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 电影详细信息 -->
      <section class="details-section">
        <h2 class="section-title">电影详情</h2>

        <!-- 紧凑的信息表格 -->
        <div class="details-table">
          <div class="detail-row">
            <span class="detail-label">标题</span>
            <span class="detail-value">{{ movieDetail.title || '暂无信息' }}</span>
          </div>

          <div class="detail-row" v-if="movieDetail.original_title && movieDetail.original_title !== movieDetail.title">
            <span class="detail-label">原名</span>
            <span class="detail-value">{{ movieDetail.original_title }}</span>
          </div>

          <div class="detail-row">
            <span class="detail-label">上映</span>
            <span class="detail-value">{{ movieDetail.release_date || '暂无信息' }}</span>
          </div>

          <div class="detail-row">
            <span class="detail-label">片长</span>
            <span class="detail-value">{{ formattedRuntime }}</span>
          </div>

          <div class="detail-row">
            <span class="detail-label">评分</span>
            <span class="detail-value rating-compact">
              <span class="score">{{ formattedVoteAverage }}</span>/10
              <span class="vote-count">({{ movieDetail.vote_count || 0 }})</span>
            </span>
          </div>

          <div class="detail-row" v-if="movieDetail.genres && movieDetail.genres.length">
            <span class="detail-label">类型</span>
            <span class="detail-value">
              <span v-for="(genre, index) in movieDetail.genres" :key="genre" class="genre-compact">
                {{ genre }}<span v-if="index < movieDetail.genres.length - 1">, </span>
              </span>
            </span>
          </div>

          <div class="detail-row">
            <span class="detail-label">导演</span>
            <span class="detail-value">{{ directors.map(d => d.name).join(', ') || '暂无信息' }}</span>
          </div>

          <div class="detail-row">
            <span class="detail-label">国家</span>
            <span class="detail-value">{{ movieDetail.production_countries?.join(', ') || '暂无信息' }}</span>
          </div>

          <div class="detail-row">
            <span class="detail-label">语言</span>
            <span class="detail-value">{{ movieDetail.spoken_languages?.join(', ') || '暂无信息' }}</span>
          </div>

          <div class="detail-row" v-if="movieDetail.production_companies && movieDetail.production_companies.length">
            <span class="detail-label">制片</span>
            <span class="detail-value">{{ movieDetail.production_companies.join(', ') }}</span>
          </div>

          <div class="detail-row" v-if="formattedBudget !== '未公开'">
            <span class="detail-label">预算</span>
            <span class="detail-value budget-compact">{{ formattedBudget }}</span>
          </div>

          <div class="detail-row" v-if="formattedRevenue !== '未公开'">
            <span class="detail-label">票房</span>
            <span class="detail-value revenue-compact">{{ formattedRevenue }}</span>
          </div>

          <div class="detail-row" v-if="movieDetail.status">
            <span class="detail-label">状态</span>
            <span class="detail-value">{{ movieDetail.status }}</span>
          </div>
        </div>

        <!-- 剧情简介（如果在英雄区域没有显示或者需要重复显示） -->
        <div class="overview-detail" v-if="movieDetail.overview">
          <h3 class="overview-title">剧情简介</h3>
          <p class="overview-text">{{ movieDetail.overview }}</p>
        </div>
      </section>

      <!-- 相关推荐 -->
      <section class="recommendations-section">
        <h2 class="section-title">相关推荐</h2>
        <div class="recommendations-grid">
          <div
            v-for="movie in similarMovies"
            :key="movie.id"
            class="recommendation-card"
            @click="handleRecommendationClick(movie.id)"
          >
            <div class="recommendation-image">
              <img
                :src="movie.poster_path
                  ? `https://image.tmdb.org/t/p/w400${movie.poster_path}`
                  : '/placeholder-movie.jpg'"
                :alt="movie.title"
                class="recommendation-poster"
              />
            </div>
            <div class="recommendation-info">
              <h4 class="recommendation-title">{{ movie.title }}</h4>
              <p class="recommendation-rating">{{ movie.vote_average?.toFixed(1) }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 用户评价区域 -->
      <section class="reviews-section">
        <h2 class="section-title">用户评价</h2>

        <!-- 评分统计 -->
        <div class="rating-summary">
          <div class="average-rating">
            <span class="rating-score">{{ formattedAverageRating }}</span>
            <div class="rating-stars">
              <span
                v-for="n in 5"
                :key="n"
                :class="['star', { active: n <= Math.round(interaction.average_rating) }]"
              >★</span>
            </div>
          </div>
        </div>

        <!-- 写评论 -->
        <div v-if="isAuthenticated" class="write-review-card">
          <h3>写下你的观后感</h3>
          <div class="review-form">
            <textarea
              v-model="newReview"
              placeholder="分享你对这部电影的看法..."
              class="review-textarea"
            ></textarea>
            <div class="review-controls">
              <div class="rating-select">
                <span class="rating-label">评分：</span>
                <div class="star-rating">
                  <span
                    v-for="n in 10"
                    :key="n"
                    :class="['rating-star', { active: n <= reviewRating, hover: n <= hoverRating }]"
                    @click="reviewRating = n"
                    @mouseenter="hoverRating = n"
                    @mouseleave="hoverRating = 0"
                  >★</span>
                </div>
                <span class="rating-text">{{ reviewRating }}/10</span>
              </div>
              <button @click="submitReview()" class="submit-btn" :disabled="submitting">
                {{ submitting ? '提交中...' : '发布评价' }}
              </button>
            </div>
          </div>
        </div>

        <!-- 评论列表 -->
        <div class="reviews-list">
          <div
            v-for="review in reviews"
            :key="review.id"
            :class="['review-card', { 'featured': review.is_featured }]"
          >
            <div class="review-header">
              <div class="user-info">
                <img :src="review.user.avatar || '/default-avatar.png'" class="user-avatar"/>
                <div class="user-details">
                  <span class="username">{{ review.user.username }}</span>
                  <span class="review-date">{{ formatDate(review.created_at) }}</span>
                </div>
              </div>
              <div class="review-rating">
                <span class="rating-score">{{ review.rating }}/10</span>
                <span v-if="review.is_featured" class="featured-badge">精选</span>
              </div>
            </div>
            <div class="review-content">
              <p class="review-text">{{ review.content }}</p>
              <div class="review-actions">
                <button
                  class="like-btn"
                  :class="{ 'liked': review.is_liked }"
                  @click="handleLike(review)"
                  v-if="isAuthenticated"
                >
                  👍 {{ review.like_count || 0 }}
                </button>
                <span class="like-count" v-else>👍 {{ review.like_count || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-overlay">
      <div class="error-content">
        <h3>加载失败</h3>
        <p>{{ error }}</p>
        <button @click="fetchMovieDetail" class="retry-btn">重试</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/utils/axios'
import { useLoading } from '@/composables/useLoading.js'  // 添加.js扩展名
import { useToast } from '@/composables/useToast.js'
import dayjs from 'dayjs'
import { watch } from 'vue'
import { searchThirdPartySource } from '@/api/thirdpartySearch'
import { API_SITES } from '@/api/thirdparty'

const { showSuccess, showError } = useToast()
const route = useRoute()
const router = useRouter()

// 添加日期格式化函数
const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}

// 在onMounted之后添加watch监听
watch(
  () => route.params.id,
  async (newId) => {
    // 重置数据
    movieDetail.value = {}
    similarMovies.value = []
    interaction.value = {
      is_favorite: false,
      review_count: 0,
      average_rating: 0
    }
    reviews.value = []

    // 重新获取数据
    await Promise.all([
      fetchMovieDetail(),
      fetchInteractionData(),
      fetchReviews()
    ])

    // 滚动到页面顶部
    window.scrollTo(0, 0)
  }
)

// 组合式API封装
const useMovieData = () => {
  const movieDetail = ref({})
  const credits = ref({ cast: [], crew: [] })
  const similarMovies = ref([])
  const { loading, startLoading, endLoading } = useLoading()
  const error = ref(null)

  const fetchMovieDetail = async () => {
    try {
      console.log('[MovieDetail] 开始获取电影详情数据，ID:', route.params.id)
      startLoading()
      error.value = null
      const { data } = await axios.get(`/movies/${route.params.id}/`)
      console.log('[MovieDetail] 原始数据:', data)

      movieDetail.value = data.detail || data
      credits.value = data.credits || {}
      similarMovies.value = data.similar || []

      console.log('[MovieDetail] 处理后的电影详情:', movieDetail.value)
      console.log('[MovieDetail] 演员信息:', credits.value)
      console.log('[MovieDetail] 相似电影:', similarMovies.value)
    } catch (err) {
      console.error('[MovieDetail] 获取电影详情失败:', err)
      error.value = err.response?.data?.error || '获取数据失败'
      showError(error.value)
      if (err.response?.status === 404) {
        console.log('[MovieDetail] 电影不存在，跳转到404页面')
        router.replace('/404')
      }
    } finally {
      endLoading()
    }
  }

  return {
    movieDetail,
    credits,
    similarMovies,
    loading,
    error,
    fetchMovieDetail
  }
}

const useReviews = () => {
  const reviews = ref([])
  const newReview = ref('')
  const reviewRating = ref(5)
  const hoverRating = ref(0)
  const { loading: submitting, startLoading: startSubmit, endLoading: endSubmit } = useLoading()
  const { loading: reviewsLoading, startLoading: startReviewsLoad, endLoading: endReviewsLoad } = useLoading()

  const fetchReviews = async () => {
    try {
      console.log('[MovieDetail] 开始获取评论数据')
      startReviewsLoad()
      const { data } = await axios.get(`/movies/${route.params.id}/reviews/`)
      reviews.value = data.results || []
      console.log('[MovieDetail] 评论数据获取成功:', data)
    } catch (error) {
      console.error('[MovieDetail] 获取评论失败:', error)
      showError('加载评论失败')
      reviews.value = [] // 设置默认值
    } finally {
      endReviewsLoad()
    }
  }

  const submitReview = async () => {
    if (submitting.value) return

    submitting.value = true
    try {
      const response = await axios.post(
        `/movies/${route.params.id}/reviews/`,
        {
          content: newReview.value,
          rating: reviewRating.value
        },
        {
          headers: {
            Authorization: `Token ${localStorage.getItem('authToken')}`
          }
        }
      )

      if (response.status === 201) {
        showSuccess('评价提交成功')
        newReview.value = ''
        await fetchReviews()
      }
    } catch (error) {
      if (error.response?.status === 409) {
        showError('请勿重复提交评论')
      } else if (error.response?.status === 401) {
        showError('请先登录')
        router.push('/login')
      } else {
        showError('提交失败，请稍后重试')
      }
    } finally {
      submitting.value = false
    }
  }

  return {
    reviews,
    newReview,
    reviewRating,
    hoverRating,
    submitting,
    reviewsLoading,
    fetchReviews,
    submitReview
  }
}

const useInteraction = () => {
  const interaction = ref({
    is_favorite: false,
    review_count: 0,
    average_rating: 0.0
  })
  const userRating = ref(0)
  const isAuthenticated = computed(() => !!localStorage.getItem('authToken'))

  const fetchInteractionData = async () => {
    try {
      console.log('[MovieDetail] 开始获取互动数据')
      const token = localStorage.getItem('authToken')

      if (!token) {
        console.log('[MovieDetail] 用户未登录，使用默认互动数据')
        // 用户未登录时，使用默认值，不跳转到登录页
        interaction.value = {
          is_favorite: false,
          review_count: 0,
          average_rating: 0.0
        }
        return
      }

      const { data } = await axios.get(`/movies/${route.params.id}/interaction/`, {
        headers: {
          Authorization: `Token ${token}`
        }
      })

      console.log('[MovieDetail] 互动数据获取成功:', data)
      // 数据校验
      interaction.value = {
        is_favorite: data.is_favorite ?? false,
        review_count: Number(data.review_count) || 0,
        average_rating: Number(data.average_rating) || 0
      }
    } catch (error) {
      console.error('[MovieDetail] 获取互动数据失败:', error)
      if (error.response?.status === 401) {
        console.log('[MovieDetail] 认证失败，清除token并使用默认数据')
        // 认证失败时，清除无效token，但不跳转到登录页
        localStorage.removeItem('authToken')
        interaction.value = {
          is_favorite: false,
          review_count: 0,
          average_rating: 0.0
        }
      } else {
        showError('获取互动数据失败，请稍后重试')
        // 使用默认值
        interaction.value = {
          is_favorite: false,
          review_count: 0,
          average_rating: 0.0
        }
      }
    }
  }

  const handleFavorite = async () => {
    if (!isAuthenticated.value) {
      showError('请先登录')
      return router.push('/login')
    }

    try {
      const { data } = await axios.post(`/movies/${route.params.id}/favorite/`)
      interaction.value.is_favorite = data.is_favorite
      showSuccess(data.is_favorite ? '已收藏' : '已取消收藏')
    } catch (error) {
      showError('收藏操作失败')
    }
  }

  return {
    interaction,
    userRating,
    isAuthenticated,
    fetchInteractionData,
    handleFavorite
  }
}

// 组合数据
const { movieDetail, credits, similarMovies, loading, error, fetchMovieDetail } = useMovieData()
const { reviews, newReview, reviewRating, hoverRating, submitting, reviewsLoading, fetchReviews, submitReview } = useReviews()
const { interaction, userRating, isAuthenticated, fetchInteractionData, handleFavorite } = useInteraction()

// 计算属性
const releaseYear = computed(() => movieDetail.value.release_date?.split('-')[0] || '未知年份')
const formattedRuntime = computed(() => {
  const runtime = movieDetail.value.runtime
  return runtime ? `${Math.floor(runtime / 60)}小时${runtime % 60}分钟` : '片长未知'
})
const directors = computed(() => credits.value.crew.filter(c => c.job === 'Director'))
const mainCast = computed(() => credits.value.cast.slice(0, 5))
const formattedBudget = computed(() =>
  movieDetail.value.budget ? `$${(movieDetail.value.budget / 1e6).toFixed(1)}M` : '未公开'
)
const formattedRevenue = computed(() =>
  movieDetail.value.revenue ? `$${(movieDetail.value.revenue / 1e6).toFixed(1)}M` : '未公开'
)

// 新增的计算属性
const formattedVoteAverage = computed(() => {
  return (movieDetail.value.vote_average || 0).toFixed(1)
})

// 初始化
onMounted(async () => {
  console.log('[MovieDetail] 组件挂载，路由参数:', route.params)
  console.log('[MovieDetail] 电影ID:', route.params.id)

  try {
    await Promise.all([
      fetchMovieDetail(),
      fetchInteractionData(),
      fetchReviews()
    ])
    console.log('[MovieDetail] 数据加载完成')
  } catch (error) {
    console.error('[MovieDetail] 数据加载失败:', error)
  }
})

// 工具方法
const goToMovie = (id) => router.push(`/movie/${id}`)
const goToTicketing = () => router.push(`/movie/${route.params.id}/ticketing`)
const handleImageError = (e) => {
  e.target.src = '/placeholder-movie.jpg'
}

const formattedAverageRating = computed(() => {
  // 使用可选链操作符和空值合并运算符
  const rating = interaction.value.average_rating ?? 0
  return rating.toFixed(1)
})

const handleRecommendationClick = (id) => {
  // 使用replace方式跳转避免路由历史堆积
  router.replace(`/movie/${id}`)
}

const handleLike = async (review) => {
  if (!isAuthenticated.value) {
    showError('请先登录')
    return router.push('/login')
  }

  try {
    const { data } = await axios.post(`/movies/reviews/${review.id}/like/`)
    review.is_liked = data.is_liked
    review.like_count = data.is_liked ? (review.like_count || 0) + 1 : (review.like_count || 1) - 1
    review.is_featured = review.like_count >= 5
  } catch (error) {
    showError('点赞失败，请稍后重试')
  }
}

const apiSites = API_SITES
const sourceKeys = Object.keys(apiSites)
const selectedSource = ref(sourceKeys[0])

const goToPlayer = async () => {
  if (!movieDetail.value.title) return;
  const movieName = movieDetail.value.title;
  showSuccess('正在为您查找播放源...');
  const m3u8 = await searchThirdPartySource(movieName, selectedSource.value);
  if (m3u8) {
    router.push({ name: 'MoviePlayer', query: { url: m3u8, title: movieName } });
  } else {
    showError('未找到可用播放源，请尝试切换下一个资源！');
  }
}

</script>

<style scoped>
/* Netflix风格的电影详情页样式 */
.movie-detail-page {
  background-color: var(--dark-bg);
  color: var(--light-text);
  min-height: 100vh;
  overflow-x: hidden;
}

/* 加载状态 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(20, 20, 20, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top: 3px solid #e50914;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 英雄区域 */
.hero-section {
  position: relative;
  height: 110vh;
  min-height: 700px;
  overflow: hidden;
}

.hero-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.hero-background-fallback {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    135deg,
    #1a1a1a 0%,
    #2d2d2d 50%,
    #1a1a1a 100%
  );
}

.backdrop-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 20%;
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(77deg,
    rgba(0,0,0,0.8) 0%,
    rgba(0,0,0,0.5) 35%,
    rgba(0,0,0,0.3) 50%,
    rgba(0,0,0,0) 100%),
    linear-gradient(to bottom,
    rgba(20,20,20,0) 80%,
    rgba(20,20,20,0.7) 95%,
    rgba(20,20,20,1) 100%);
}

.hero-content {
  position: absolute;
  top: 35%;
  left: 4%;
  width: 50%;
  color: white;
  z-index: 10;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: 1rem;
}

.meta-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 1rem;
  font-size: 14px;
  color: #fff;
}

.match {
  color: #46d369;
  font-weight: bold;
}

.year, .rating, .runtime {
  border: 1px solid rgba(255,255,255,0.4);
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
  margin-right: 8px;
}

.genres {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 1rem;
}

.genre-tag {
  display: inline-block;
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 0.85rem;
}

.overview {
  font-size: 1.2rem;
  margin: 0 0 1.5rem 0;
  opacity: 0.9;
  line-height: 1.5;
  text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
  color: rgba(255,255,255,0.9);
  /* 限制显示两行 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 1rem;
  position: relative;
  z-index: 15;
}

.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn-primary {
  background-color: #e50914;
  color: white;
}

.btn-primary:hover {
  background-color: #f40612;
}

.btn-secondary {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.btn-secondary:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

.btn-secondary.active {
  background-color: #e50914;
}

.movie-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin: 0 0 1rem 0;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
  line-height: 1.1;
}

/* 基本信息回退区域 */
.basic-info-fallback {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(
    135deg,
    #1a1a1a 0%,
    #2d2d2d 50%,
    #1a1a1a 100%
  );
}

.fallback-content {
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
}

.fallback-content h1 {
  font-size: 2rem;
  margin: 0 0 16px 0;
  color: #fff;
}

.fallback-content p {
  font-size: 1.1rem;
  margin: 0;
  color: rgba(255, 255, 255, 0.7);
}

/* 内容区域 */
.content-container {
  padding: 0 4%;
  position: relative;
  z-index: 3;
  margin-top: -100px;
}

.section-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0 0 24px 0;
  color: #fff;
}

/* 演员阵容 */
.cast-section {
  margin: 60px 0;
}

.cast-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 16px;
}

.cast-card {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.cast-card:hover {
  transform: translateY(-4px);
  background-color: #2a2a2a;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
}

.cast-image {
  width: 100%;
  aspect-ratio: 3/4;
  overflow: hidden;
}

.actor-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.cast-card:hover .actor-photo {
  transform: scale(1.05);
}

.cast-info {
  padding: 12px;
}

.actor-name {
  margin: 0;
  font-size: 1rem;
  font-weight: 500;
  color: white;
}

.character {
  margin: 4px 0 0 0;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
}

/* 详细信息 */
.details-section {
  margin-bottom: 30px;
}

/* 紧凑表格布局 */
.details-table {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 16px;
  border: 1px solid var(--border-color);
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  transition: background-color 0.2s ease;
}

.detail-row:hover {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 4px;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-size: 0.8rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
  flex-shrink: 0;
  min-width: 60px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  font-size: 0.85rem;
  color: #fff;
  font-weight: 400;
  text-align: right;
  flex: 1;
  margin-left: 12px;
}

/* 紧凑布局特殊样式 */
.rating-compact {
  display: flex;
  align-items: baseline;
  gap: 2px;
  justify-content: flex-end;
}

.rating-compact .score {
  font-size: 0.95rem;
  font-weight: 700;
  color: #f5b50a;
}

.rating-compact .vote-count {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.5);
  margin-left: 4px;
}

.genre-compact {
  color: #e50914;
  font-weight: 500;
}

.budget-compact,
.revenue-compact {
  font-weight: 600;
  color: #4ade80;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .details-table {
    grid-template-columns: 1fr;
    padding: 12px;
  }

  .detail-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
    padding: 8px 4px;
  }

  .detail-label {
    font-size: 0.75rem;
    min-width: auto;
  }

  .detail-value {
    text-align: left;
    margin-left: 0;
    font-size: 0.8rem;
  }

  .rating-compact {
    justify-content: flex-start;
  }
}

/* 剧情简介详情 */
.overview-detail {
  margin-top: 32px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
}

.overview-title {
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0 0 16px 0;
  color: #fff;
}

.overview-text {
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.7;
  margin: 0;
  font-size: 1.1rem;
}

/* 相关推荐 */
.recommendations-section {
  margin: 60px 0;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.recommendation-card {
  cursor: pointer;
  transition: transform 0.2s ease;
}

.recommendation-card:hover {
  transform: translateY(-4px);
}

.recommendation-image {
  position: relative;
  aspect-ratio: 2/3;
  border-radius: 4px;
  overflow: hidden;
}

.recommendation-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 移除播放按钮相关样式 */

.recommendation-info {
  padding: 8px 4px;
}

.recommendation-title {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 500;
  line-height: 1.3;
  color: #fff;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recommendation-rating {
  margin-top: 4px;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

/* 评价区域 */
.reviews-section {
  margin-bottom: 60px;
}

.rating-summary {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 32px;
  border-radius: 16px;
  margin-bottom: 40px;
  backdrop-filter: blur(10px);
}

.average-rating {
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.rating-score {
  font-size: 3rem;
  font-weight: 800;
  color: #e50914;
  text-shadow: 0 2px 4px rgba(229, 9, 20, 0.3);
}

.rating-stars {
  display: flex;
  gap: 6px;
}

.star {
  font-size: 1.8rem;
  color: rgba(255, 255, 255, 0.2);
  transition: color 0.3s ease;
}

.star.active {
  color: #e50914;
  text-shadow: 0 0 8px rgba(229, 9, 20, 0.5);
}

.rating-count {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.2rem;
  font-weight: 500;
}

/* 写评论 */
.write-review-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 32px;
  border-radius: 16px;
  margin-bottom: 40px;
  backdrop-filter: blur(10px);
}

.write-review-card h3 {
  margin: 0 0 24px 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 12px;
}

.review-form {
  width: 100%;
}

.review-textarea {
  width: 100%;
  min-height: 140px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
  color: #fff;
  font-size: 1rem;
  line-height: 1.6;
  resize: vertical;
  margin-bottom: 20px;
  transition: all 0.3s ease;
  font-family: inherit;
  box-sizing: border-box;
}

.review-textarea:focus {
  outline: none;
  border-color: #e50914;
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 3px rgba(229, 9, 20, 0.2);
}

.review-textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.review-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.rating-select {
  display: flex;
  align-items: center;
  gap: 16px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  flex-wrap: wrap;
}

.rating-label {
  font-size: 1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.star-rating {
  display: flex;
  gap: 4px;
}

.rating-star {
  font-size: 1.8rem;
  color: rgba(255, 255, 255, 0.2);
  cursor: pointer;
  transition: all 0.3s ease;
  user-select: none;
}

.rating-star:hover,
.rating-star.hover {
  color: #e50914;
  transform: scale(1.1);
  text-shadow: 0 0 8px rgba(229, 9, 20, 0.5);
}

.rating-star.active {
  color: #e50914;
  text-shadow: 0 0 8px rgba(229, 9, 20, 0.5);
}

.rating-text {
  font-size: 1rem;
  font-weight: 600;
  color: #e50914;
  background: rgba(229, 9, 20, 0.1);
  padding: 6px 12px;
  border-radius: 20px;
  border: 1px solid rgba(229, 9, 20, 0.3);
  min-width: 50px;
  text-align: center;
}

.submit-btn {
  background: linear-gradient(135deg, #e50914 0%, #f40612 100%);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(229, 9, 20, 0.3);
}

.submit-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #f40612 0%, #e50914 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(229, 9, 20, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 评论列表 */
.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.review-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 28px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.review-card:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.review-card.featured {
  border: 2px solid #e50914;
  background: rgba(229, 9, 20, 0.05);
  position: relative;
}

.review-card.featured::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #e50914 0%, #f40612 100%);
  border-radius: 16px 16px 0 0;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.username {
  font-weight: 700;
  font-size: 1.1rem;
  color: #fff;
}

.review-date {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 400;
}

.review-rating {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.rating-score {
  color: #e50914;
  font-weight: 700;
  font-size: 1.1rem;
  background: rgba(229, 9, 20, 0.1);
  padding: 6px 12px;
  border-radius: 20px;
  border: 1px solid rgba(229, 9, 20, 0.3);
}

.featured-badge {
  background: linear-gradient(135deg, #e50914 0%, #f40612 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 8px rgba(229, 9, 20, 0.3);
}

.review-content {
  margin-left: 64px;
}

.review-text {
  color: rgba(255, 255, 255, 0.95);
  line-height: 1.7;
  margin: 0 0 20px 0;
  font-size: 1rem;
}

.review-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.like-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 20px;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

.like-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: #fff;
  transform: translateY(-1px);
}

.like-btn.liked {
  background: rgba(229, 9, 20, 0.1);
  border-color: rgba(229, 9, 20, 0.3);
  color: #e50914;
}

.like-count {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  font-weight: 500;
}

/* 错误状态 */
.error-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(20, 20, 20, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.error-content {
  background: rgba(255, 255, 255, 0.1);
  padding: 40px;
  border-radius: 12px;
  text-align: center;
  max-width: 400px;
}

.error-content h3 {
  color: #e50914;
  margin: 0 0 16px 0;
}

.error-content p {
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 24px 0;
}

.retry-btn {
  background: #e50914;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s ease;
}

.retry-btn:hover {
  background: #f40612;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .hero-content {
    grid-template-columns: 1fr;
    gap: 24px;
    text-align: center;
  }

  .movie-title {
    font-size: 2.5rem;
  }

  .content-container {
    padding: 40px 3%;
  }

  .cast-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }

  .recommendations-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}

@media (max-width: 768px) {
  .hero-section {
    height: 110vh;
    min-height: 550px;
  }

  .hero-content {
    width: 90%;
    padding: 0 4%;
  }

  .movie-title {
    font-size: 2rem;
    margin-bottom: 0.5rem;
  }

  .hero-fade {
    height: 150px;
  }

  .content-container {
    margin-top: -80px;
  }

  /* 评论区域响应式 */
  .rating-summary {
    padding: 24px 20px;
  }

  .average-rating {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .rating-score {
    font-size: 2.5rem;
  }

  .write-review-card {
    padding: 24px 20px;
  }

  .review-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }

  .rating-select {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .star-rating {
    gap: 6px;
  }

  .rating-star {
    font-size: 1.5rem;
  }

  .review-card {
    padding: 20px 16px;
  }

  .review-content {
    margin-left: 0;
    margin-top: 16px;
  }

  .user-info {
    gap: 12px;
  }

  .user-avatar {
    width: 40px;
    height: 40px;
    border-radius: 6px;
  }

  .review-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .review-rating {
    align-self: flex-end;
  }
}

/* 添加电影详情页专用的过渡效果 */
.hero-fade {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 300px;
  background: linear-gradient(to bottom,
    rgba(26,26,26,0) 0%,
    rgba(26,26,26,0.3) 30%,
    rgba(26,26,26,0.7) 60%,
    rgba(26,26,26,0.9) 80%,
    rgba(26,26,26,1) 100%);
  z-index: 2;
  pointer-events: none;
}

.source-select-row {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}
.source-select {
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid #444;
  background: #222;
  color: #fff;
  font-size: 1rem;
}
.source-select:focus {
  outline: none;
  border-color: #e50914;
}
</style>

