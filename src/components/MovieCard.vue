<!-- frontend/src/components/MovieCard.vue -->
<template>
    <div
      class="movie-card"
      :class="{ 'ranking-card': showRank }"
      @click="handleClick"
    >
      <!-- 排名角标 -->
      <div v-if="showRank" class="rank-badge">
        <span class="rank-number">{{ rank }}</span>
      </div>

      <!-- 电影海报 -->
      <div class="poster-wrapper">
        <img
          :src="posterUrl"
          :alt="movie.title"
          class="poster-image"
        />

        <!-- 评分信息 -->
        <div class="rating-chip">
          <span class="rating-text">{{ movie.rating }}%</span>
        </div>
      </div>

      <!-- 电影信息 -->
      <div class="movie-info">
        <h3 class="movie-title">{{ movie.title }}</h3>
        <div class="movie-meta">
          <span class="year">{{ movie.year }}</span>
          <span class="votes">{{ movie.votes | formatNumber }}</span>
        </div>
      </div>
    </div>
  </template>

  <script>
  export default {
    props: {
      movie: Object,
      rank: Number,
      showRank: {
        type: Boolean,
        default: false
      }
    },
    emits: ['show-detail'],
    methods: {
      handleClick() {
        console.log('[MovieCard] 点击事件触发', {
          movie: this.movie,
          movieId: this.movie?.id,
          tmdbId: this.movie?.tmdb_id
        })
        const movieId = this.movie?.id || this.movie?.tmdb_id
        if (movieId) {
          console.log('[MovieCard] 发送 show-detail 事件，ID:', movieId)
          this.$emit('show-detail', movieId)
        } else {
          console.error('[MovieCard] 无法获取电影ID', this.movie)
        }
      }
    },
    computed: {
      posterUrl() {
        return this.movie.poster_path
          ? `https://image.tmdb.org/t/p/w500${this.movie.poster_path}`
          : require('@/assets/placeholder-poster.jpg')
      }
    },
    filters: {
      formatNumber(value) {
        if (value >= 1000000) return `${(value/1000000).toFixed(1)}M`
        if (value >= 1000) return `${(value/1000).toFixed(1)}K`
        return value
      }
    }
  }
  </script>

  <style lang="scss" scoped>
  .movie-card {
    position: relative;
    transition: transform 0.2s ease;
    background-color: transparent;
    border-radius: 8px;
    overflow: hidden;
    cursor: pointer;

    &:hover {
      transform: translateY(-4px);
    }
  }

  .poster-wrapper {
    position: relative;
    aspect-ratio: 2/3;
    overflow: hidden;
    border-radius: 8px;
  }

  .poster-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }

  .rank-badge {
    position: absolute;
    top: 8px;
    left: 8px;
    z-index: 2;
    background-color: #FF9800;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 0.85rem;
  }

  .rating-chip {
    position: absolute;
    bottom: 8px;
    right: 8px;
    background-color: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 500;
  }

  .movie-info {
    padding: 12px 0;
  }

  .movie-title {
    margin: 0;
    font-size: 0.95rem;
    font-weight: 500;
    line-height: 1.2;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 1;
    -webkit-box-orient: vertical;
  }

  .movie-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 4px;
    font-size: 0.8rem;
    color: rgba(0, 0, 0, 0.6);
  }
  </style>