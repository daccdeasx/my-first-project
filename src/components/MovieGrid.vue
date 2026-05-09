<!-- src/components/MovieGrid.vue -->
<template>
    <div class="movie-grid">
      <div
        v-for="item in movies"
        :key="item.id"
        class="movie-card"
        @click="handleMovieClick(item)"
      >
        <div class="poster-container">
          <img
            :src="item.poster_path
              ? `https://image.tmdb.org/t/p/w300${item.poster_path}`
              : '/placeholder-movie.jpg'"
            :alt="item.title"
            class="movie-poster"
          />
          <div class="rating-badge">
            {{ item.vote_average?.toFixed(1) }}
          </div>
        </div>
        <div class="movie-info">
          <h3 class="title">{{ item.title }}</h3>
          <p class="year">{{ formatYear(item.release_date) }}</p>
        </div>
      </div>

      <div v-if="loading" class="loading-status">
        <div class="spinner"></div>
        <p>正在加载数据...</p>
      </div>

      <div v-if="error" class="error-message">
        <p>{{ error }}</p>
        <button @click="$emit('load-more')" class="retry-button">重试</button>
      </div>

      <div v-if="pageEnd" class="end-message">
        已经到底啦～
      </div>
    </div>
  </template>

  <script setup lang="ts">
  import { computed } from 'vue'

  defineProps<{
    movies: any[]
    loading: boolean
    error: string | null
  }>()

  const emit = defineEmits<{
    (e: 'show-detail', id: number): void
    (e: 'load-more'): void
  }>()

  const formatYear = (date?: string) => {
    return date ? new Date(date).getFullYear() : '未知年份'
  }

  const pageEnd = computed(() => {
    // 根据你的分页逻辑实现
    return false
  })

  const handleMovieClick = (item: any) => {
    console.log('[MovieGrid] 电影卡片被点击', {
      item,
      itemId: item.id,
      tmdbId: item.tmdb_id
    })

    const movieId = item.id || item.tmdb_id
    if (movieId) {
      console.log('[MovieGrid] 发送 show-detail 事件，ID:', movieId)
      emit('show-detail', movieId)
    } else {
      console.error('[MovieGrid] 无法获取电影ID', item)
    }
  }
  </script>

<style scoped>
  .movie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 24px;
}

.movie-card {
  background: transparent;
  border-radius: 4px;
  overflow: hidden;
  transition: transform 0.2s ease;
  cursor: pointer;
}

.movie-card:hover {
  transform: translateY(-4px);
}

.poster-container {
  position: relative;
  aspect-ratio: 2/3;
  background: #1a1a1a;
  border-radius: 4px;
  overflow: hidden;
}

.movie-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.rating-badge {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background-color: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.movie-info {
  padding: 12px 4px;
}

.title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 500;
  line-height: 1.3;
  color: #fff;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
}

.year {
  margin: 4px 0 0;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
}

.loading-status {
  text-align: center;
  padding: 32px;
  grid-column: 1 / -1;
  color: rgba(255, 255, 255, 0.7);
}

.spinner {
  display: inline-block;
  width: 24px;
  height: 24px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-top: 2px solid #e50914;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  text-align: center;
  padding: 24px;
  background: #1a1a1a;
  border-radius: 8px;
  grid-column: 1 / -1;
  color: #e53935;
}

.retry-button {
  margin-top: 12px;
  padding: 8px 20px;
  background: #e50914;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
  font-weight: 500;
}

.retry-button:hover {
  background: #f40612;
}

.end-message {
  text-align: center;
  padding: 32px;
  color: rgba(255, 255, 255, 0.7);
  grid-column: 1 / -1;
}

@media (max-width: 768px) {
  .movie-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
}

@media (min-width: 1200px) {
  .movie-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
}
</style>