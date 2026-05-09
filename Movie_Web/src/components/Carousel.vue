<template>
  <div class="carousel">
    <div class="carousel-track" :style="trackStyle">
      <div
        v-for="(movie, index) in movies"
        :key="movie.id"
        class="carousel-item"
        :class="{ active: currentSlide === index }"
        @click="showMovieDetail(movie.id)"
      >
        <img
          :src="`https://image.tmdb.org/t/p/original${movie.backdrop_path}`"
          class="carousel-bg"
          alt="movie backdrop"
        />
        <div class="carousel-overlay"></div>
        <div class="carousel-content">
          <div class="meta-info">
            <span class="top-ten-badge" v-if="index < 10">TOP {{ index + 1 }}</span>
            <span class="match">98% 匹配</span>
            <span class="year">{{ movie.release_date?.substring(0, 4) }}</span>
            <span class="rating">{{ getRating(movie.adult) }}</span>
          </div>
          <h2 class="carousel-title">{{ movie.title }}</h2>
          <p class="carousel-overview">{{ truncateOverview(movie.overview) }}</p>
        </div>
      </div>
    </div>

    <!-- Netflix风格的指示器 -->
    <div class="progress-indicators">
      <div v-for="(_, index) in movies" :key="index" class="progress-item">
        <div class="progress-bar"
          :class="{ 'active': currentSlide === index }"
          @click.stop="goToSlide(index)">
          <div class="progress-fill"
            :style="{ width: getProgressWidth(index) }"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'

// 添加缺省处理
const props = defineProps<{
  movies: any[]
}>()

const router = useRouter()

// 当没有数据时显示默认内容
const displayMovies = computed(() => {
  if (props.movies.length > 0) return props.movies

  return [{
    id: 0,
    backdrop_path: '/defaultBackdrop.jpg',
    title: '欢迎来到电影世界',
    overview: '探索更多精彩电影...'
  }]
})

const currentSlide = ref(0)
const autoPlayTimer = ref<number | null>(null)
const autoplayDuration = 8000; // 8秒切换一次
const progressPercentage = ref(0)

const trackStyle = computed(() => ({
  transform: `translateX(-${currentSlide.value * 100}%)`
}))

// 进度条填充
const updateProgress = () => {
  const interval = 50; // 更新间隔（毫秒）
  const increment = (interval / autoplayDuration) * 100;

  const progressInterval = setInterval(() => {
    progressPercentage.value += increment;
    if (progressPercentage.value >= 100) {
      progressPercentage.value = 0;
    }
  }, interval);

  return progressInterval;
}

const getProgressWidth = (index: number) => {
  if (currentSlide.value === index) {
    return `${progressPercentage.value}%`;
  }
  return currentSlide.value > index ? '100%' : '0%';
}

const startAutoPlay = () => {
  if (autoPlayTimer.value) {
    clearInterval(autoPlayTimer.value);
}

  const progressInterval = updateProgress();

  autoPlayTimer.value = window.setInterval(() => {
    nextSlide();
    progressPercentage.value = 0;
  }, autoplayDuration);

  return () => clearInterval(progressInterval);
}

const nextSlide = () => {
  currentSlide.value = (currentSlide.value + 1) % props.movies.length;
  progressPercentage.value = 0;
}

const goToSlide = (index: number) => {
  currentSlide.value = index;
  progressPercentage.value = 0;
}

const truncateOverview = (text: string, maxLength = 150) => {
  return text?.length > maxLength ? text.substring(0, maxLength) + '...' : text || '';
}

const showMovieDetail = (id: number) => {
  // 在新标签页打开电影详情页
  const route = router.resolve({ name: 'MovieDetail', params: { id } });
  window.open(route.href, '_blank');
}

const getRating = (adult: boolean) => {
  return adult ? '18+' : '13+';
}

// 监听当前幻灯片变化
watch(currentSlide, () => {
  progressPercentage.value = 0;
});

let clearProgressInterval: (() => void) | null = null;

onMounted(() => {
  clearProgressInterval = startAutoPlay();
});

onBeforeUnmount(() => {
  if (autoPlayTimer.value) {
    clearInterval(autoPlayTimer.value);
  }
  if (clearProgressInterval) {
    clearProgressInterval();
  }
});
</script>

<style scoped>
.carousel {
  position: relative;
  width: 100%;
  height: 110vh; /* 增加高度至110vh，确保完全覆盖屏幕 */
  min-height: 700px;
  overflow: hidden;
  background-color: #141414;
  margin: 0;
  padding: 0;
}

.carousel-track {
  display: flex;
  height: 100%;
  width: 100%;
  transition: transform 0.5s cubic-bezier(0.165, 0.84, 0.44, 1);
}

.carousel-item {
  flex: 0 0 100%;
  width: 100%;
  min-width: 100%;
  height: 100%;
  position: relative;
  cursor: pointer;
}

.carousel-bg {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 20%;
  display: block;
}

.carousel-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
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

.carousel-content {
  position: absolute;
  top: 35%;
  left: 4%;
  width: 40%;
  color: white;
  z-index: 2;
}

.meta-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 1rem;
  font-size: 14px;
  color: #fff;
}

.top-ten-badge {
  background-color: #e50914;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: bold;
  font-size: 12px;
}

.match {
  color: #46d369;
  font-weight: bold;
}

.year, .rating {
  border: 1px solid rgba(255,255,255,0.4);
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
}

.carousel-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin: 0 0 1rem 0;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
  line-height: 1.1;
}

.carousel-overview {
  font-size: 1.2rem;
  margin: 0 0 1.5rem 0;
  opacity: 0.9;
  line-height: 1.5;
  text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
  color: rgba(255,255,255,0.9);
}

/* Netflix风格的进度指示器 */
.progress-indicators {
  position: absolute;
  bottom: 12%; /* 上移指示器位置 */
  right: 4%;
  display: flex;
  gap: 2px;
  z-index: 10;
}

.progress-item {
  width: 12px;
  height: 2px;
  margin: 0 2px;
}

.progress-bar {
  width: 12px;
  height: 2px;
  background-color: rgba(255,255,255,0.3);
  cursor: pointer;
  overflow: hidden;
}

.progress-bar.active {
  background-color: rgba(255,255,255,0.3);
}

.progress-fill {
  height: 100%;
  background-color: #fff;
  transition: width 0.1s linear;
}

@media (max-width: 1200px) {
  .carousel-content {
    width: 50%;
  }

  .carousel-title {
    font-size: 2.8rem;
  }
}

@media (max-width: 768px) {
  .carousel {
    height: 110vh;
    min-height: 550px;
}

  .carousel-content {
    width: 80%;
    top: 25%;
}

  .carousel-title {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

  .carousel-overview {
    font-size: 1rem;
    margin-bottom: 1rem;
  }

  .progress-indicators {
    bottom: 15%;
  }
}
</style>