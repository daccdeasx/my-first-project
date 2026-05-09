<!-- src/components/MovieSection.vue -->
<template>
  <section class="movie-section">
    <div class="section-header">
      <h3 class="section-title">{{ title }}</h3>
    </div>
    <div class="movie-grid">
      <div
        v-for="movie in limitedMovies"
        :key="movie.id"
        class="movie-card"
        @click="handleMovieClick(movie)"
      >
        <div class="poster-wrapper">
          <img
            :src="movie.poster_path
              ? `https://image.tmdb.org/t/p/w300${movie.poster_path}`
              : '/placeholder-movie.jpg'"
            class="poster"
            alt="movie poster"
          />
          <div class="rating-chip">{{ movie.vote_average?.toFixed(1) }}</div>
        </div>
        <div class="movie-info">
          <h4 class="movie-title">{{ movie.title }}</h4>
          <div class="movie-meta">{{ formatYear(movie.release_date) }}</div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  title: string
  icon?: string
  movies: any[]
}>()

const emit = defineEmits<{
  (e: 'show-detail', id: number): void
}>()

// 限制每行最多显示7个电影
const limitedMovies = computed(() => {
  return props.movies?.slice(0, 7) || []
})

const formatYear = (date?: string) => {
  return date ? new Date(date).getFullYear() : '未知年份'
}

const handleMovieClick = (movie: any) => {
  console.log('[MovieSection] 电影卡片被点击', {
    movie,
    movieId: movie.id,
    tmdbId: movie.tmdb_id
  })

  const movieId = movie.id || movie.tmdb_id
  if (movieId) {
    console.log('[MovieSection] 发送 show-detail 事件，ID:', movieId)
    emit('show-detail', movieId)
  } else {
    console.error('[MovieSection] 无法获取电影ID', movie)
  }
}
</script>

<style scoped>
.movie-section {
  margin: 40px 0;
}

.section-header {
  margin-bottom: 16px;
  padding: 0;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  color: #fff;
  position: relative;
  border-left: none;
  padding-left: 0;
}

.movie-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr); /* 固定7列 */
  gap: 16px;
}

.movie-card {
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s ease;
  width: 100%;
}

.movie-card:hover {
  transform: translateY(-4px);
}

.poster-wrapper {
  position: relative;
  aspect-ratio: 2/3;
  border-radius: 4px;
  overflow: hidden;
}

.poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.rating-chip {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.movie-info {
  padding: 8px 4px;
}

.movie-title {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 500;
  line-height: 1.3;
  color: #fff;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.movie-meta {
  margin-top: 4px;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
}

@media (max-width: 1400px) {
  .movie-grid {
    grid-template-columns: repeat(6, 1fr);
  }
}

@media (max-width: 1200px) {
  .movie-grid {
    grid-template-columns: repeat(5, 1fr);
  }
}

@media (max-width: 992px) {
  .movie-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 768px) {
  .movie-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
  }

  .section-title {
    font-size: 1.1rem;
  }
}

@media (max-width: 576px) {
  .movie-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>