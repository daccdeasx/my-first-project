<!-- HomeView.vue -->
<template>
  <div class="home-view">
    <!-- 轮播图 -->
    <div class="hero-section">
      <Carousel :movies="sections.featured.results" />
      <div class="hero-fade"></div>
    </div>

    <!-- 动态区块 -->
    <div class="content-container">
      <div v-for="section in dynamicSections" :key="section.type">
        <MovieSection
          :title="section.title"
          :movies="section.results"
          @show-detail="showMovieDetail"
        />
      </div>

      <!-- 主网格 -->
      <div class="popular-section">
        <h2 class="section-title">热门电影</h2>
        <MovieGrid
          :movies="sections.popular.results"
          :loading="loading"
          :error="error"
          @load-more="loadMore"
          @show-detail="showMovieDetail"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/utils/axios'
import Carousel from '@/components/Carousel.vue'
import MovieSection from '@/components/MovieSection.vue'
import MovieGrid from '@/components/MovieGrid.vue'

type MovieListType = 'featured' | 'now_playing' | 'top_rated' | 'popular'

interface MovieSectionConfig {
  title: string
  type: MovieListType
  slice?: number
  results: any[]
  page: number
  totalPages: number
}

const router = useRouter()
const loading = ref(false)
const error = ref<string | null>(null)

// 响应式区块配置
const sections = reactive<Record<MovieListType, MovieSectionConfig>>({
  featured: {
    title: '特别推荐',
    type: 'featured',
    slice: 5,
    results: [],
    page: 1,
    totalPages: 1
  },
  now_playing: {
    title: '正在热映',
    type: 'now_playing',
    slice: 10,
    results: [],
    page: 1,
    totalPages: 1
  },
  top_rated: {
    title: '高分推荐',
    type: 'top_rated',
    slice: 10,
    results: [],
    page: 1,
    totalPages: 1
  },
  popular: {
    title: '热门电影',
    type: 'popular',
    results: [],
    page: 1,
    totalPages: 1
  }
})

// 动态区块列表（排除popular）
const dynamicSections = computed(() => {
  const { popular, ...rest } = sections
  return Object.values(rest)
})

// 通用数据获取方法
const fetchMovieData = async (
  type: MovieListType,
  params: { page?: number; slice?: number } = {}
) => {

  try {
    loading.value = true
    error.value = null

    const response = await axios.get('/movies/tmdb/', {
      params: {
        type,
        page: params.page || sections[type].page
      }
    })

    return {
      results: params.slice
        ? response.data.results.slice(0, params.slice)
        : response.data.results,
      page: response.data.page,
      totalPages: response.data.total_pages
    }
  } catch (err) {
    error.value = '数据加载失败，请稍后重试'
    console.error(`获取${type}数据失败:`, err)
    throw err
  } finally {
    loading.value = false
  }
}

// 初始化加载
const initializeData = async () => {
  try {
    await Promise.all([
      fetchSectionData('featured'),
      fetchSectionData('now_playing'),
      fetchSectionData('top_rated'),
      fetchSectionData('popular')
    ])
  } catch (err) {
    error.value = '初始化数据加载失败'
  }
}

// 加载更多
const loadMore = async () => {
  if (sections.popular.page >= sections.popular.totalPages) return

  try {
    sections.popular.page++
    const { results, page, totalPages } = await fetchMovieData('popular')
    sections.popular.results = [...sections.popular.results, ...results]
    sections.popular.page = page
    sections.popular.totalPages = totalPages
  } catch (err) {
    sections.popular.page-- // 回滚页码
  }
}

// 统一处理区块数据
const fetchSectionData = async (type: MovieListType) => {
  const section = sections[type]
  const { results, page, totalPages } = await fetchMovieData(type, {
    slice: section.slice
  })
  section.results = results
  section.page = page
  section.totalPages = totalPages
}

// 电影详情跳转 - 在新标签页打开
const showMovieDetail = (id: number) => {
  console.log('[HomeView] showMovieDetail 被调用，ID:', id)
  console.log('[HomeView] 准备在新标签页打开电影详情页')
  try {
    // 使用 router.resolve 生成完整的URL
    const route = router.resolve({ name: 'MovieDetail', params: { id } })
    // 在新标签页打开
    window.open(route.href, '_blank')
    console.log('[HomeView] 新标签页打开成功')
  } catch (error) {
    console.error('[HomeView] 新标签页打开失败:', error)
  }
}

// 生命周期
onMounted(() => {
  initializeData()
  window.addEventListener('scroll', handleScroll)
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
})

// 滚动加载
const handleScroll = () => {
  const { scrollTop, clientHeight, scrollHeight } = document.documentElement
  if (scrollTop + clientHeight >= scrollHeight - 500 && !loading.value) {
    loadMore()
  }
}
</script>

<style scoped>
.home-view {
  background-color: var(--dark-bg);
  color: var(--light-text);
  min-height: 100vh;
  padding: 0;
}

.hero-section {
  position: relative;
  height: 110vh;
}

.hero-fade {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 200px;
  background: linear-gradient(to bottom,
    rgba(26,26,26,0) 0%,
    rgba(26,26,26,0.7) 60%,
    rgba(26,26,26,1) 100%);
  z-index: 2;
}

.content-container {
  padding: 0 4%;
  position: relative;
  z-index: 3;
}

.popular-section {
  margin-top: 80px;
  margin-bottom: 80px;
}

.section-title {
  font-size: 1.4rem;
  font-weight: 700;
  margin: 0 0 16px 0;
  color: #fff;
  padding: 0;
}

@media (max-width: 768px) {
  .hero-section {
    height: 110vh;
  }

  .hero-fade {
    height: 150px;
  }

  .content-container {
    padding: 0 2%;
    margin-top: -120px;
  }

  .section-title {
    font-size: 1.2rem;
  }

  .popular-section {
    margin-top: 60px;
    margin-bottom: 60px;
  }
}
</style>