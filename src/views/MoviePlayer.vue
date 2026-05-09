<template>
  <div class="movie-player-page">
    <header class="player-header">
      <div class="header-content">
        <button class="back-button" @click="goBack">
          <i class="fas fa-arrow-left"></i>
          返回
        </button>
        <h1 class="movie-title">{{ title || '正在播放' }}</h1>
      </div>
    </header>
    <main class="player-main">
      <div v-if="!videoUrl" class="no-video-message">
        <p>未找到播放地址，请尝试切换其他播放源。</p>
      </div>
      <div v-else-if="!isPlayable" class="no-video-message">
        <p>该资源暂不支持直接播放，请尝试切换其他播放源或手动访问：</p>
        <a :href="videoUrl" target="_blank" style="color:#00ccff;word-break:break-all;">{{ videoUrl }}</a>
      </div>
      <div v-else class="video-container">
        <video ref="videoRef" controls autoplay style="width:100%;max-width:900px;border-radius:8px;background:#000;"></video>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Hls from 'hls.js'

const route = useRoute()
const router = useRouter()
const videoUrl = ref(route.query.url)
const title = ref(route.query.title)
const goBack = () => router.back()
const videoRef = ref(null)
const isPlayable = ref(videoUrl.value && (videoUrl.value.endsWith('.m3u8') || videoUrl.value.endsWith('.mp4')))

onMounted(() => {
  setupPlayer()
  console.log('最终播放地址:', videoUrl.value)
})

// 监听路由变化，支持切换电影资源时自动刷新播放器和提示
watch(() => route.query.url, (newUrl) => {
  videoUrl.value = newUrl
  isPlayable.value = newUrl && (newUrl.endsWith('.m3u8') || newUrl.endsWith('.mp4'))
  setupPlayer()
})

function setupPlayer() {
  if (videoUrl.value && videoRef.value) {
    if (videoUrl.value.endsWith('.m3u8') && Hls.isSupported()) {
      const hls = new Hls()
      hls.loadSource(videoUrl.value)
      hls.attachMedia(videoRef.value)
    } else if (videoRef.value.canPlayType('application/vnd.apple.mpegurl')) {
      videoRef.value.src = videoUrl.value
    } else {
      videoRef.value.src = videoUrl.value
    }
  }
}
</script>

<style scoped>
.movie-player-page {
  min-height: 100vh;
  background-color: #000;
  color: #fff;
}
.player-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  padding: 1rem;
}
.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 1rem;
}
.back-button {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}
.back-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
}
.movie-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}
.player-main {
  padding-top: 4rem;
  min-height: calc(100vh - 4rem);
}
.video-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
  display: flex;
  justify-content: center;
}
.no-video-message {
  text-align: center;
  padding: 2rem;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  margin-top: 2rem;
  color: #fff;
}
</style> 