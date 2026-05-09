<template>
  <div class="video-feed">
    <div class="feed-header">
      <h3>精彩视频</h3>
      <!-- 自定义频道选择器 -->
      <div class="custom-channel-select">
        <div class="channel-display" @click="toggleChannelDropdown">
          {{ selectedChannelName }}
          <span class="dropdown-arrow" :class="{ 'open': channelDropdownOpen }">▼</span>
        </div>
        <div v-if="channelDropdownOpen" class="channel-dropdown">
          <div
            v-for="channel in channels"
            :key="channel.id"
            class="channel-option"
            @click="selectChannel(channel)"
          >
            {{ channel.name }}
          </div>
        </div>
      </div>
    </div>

    <!-- 自定义标签页 -->
    <div class="custom-tabs">
      <div class="tab-header">
        <div
          class="tab-item"
          :class="{ 'active': activeTab === 'normal' }"
          @click="switchTab('normal')"
        >
          推荐视频
        </div>
        <div
          class="tab-item"
          :class="{ 'active': activeTab === 'short' }"
          @click="switchTab('short')"
        >
          短视频
        </div>
      </div>

      <div class="tab-content">
        <div v-if="activeTab === 'normal'" class="tab-pane">
          <div class="video-grid">
            <div
              v-for="video in normalVideos"
              :key="video.id"
              class="video-card"
              @click="playVideo(video)"
            >
              <div class="video-thumbnail">
                <img :src="video.cover" :alt="video.title" @error="handleImageError">
                <div class="play-overlay">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                    <path d="M8 5v14l11-7z" fill="var(--light-text)"/>
                  </svg>
                </div>
                <div class="duration">{{ formatDuration(video.duration) }}</div>
              </div>
              <div class="video-info">
                <h4>{{ video.title }}</h4>
                <p class="video-desc">{{ video.description }}</p>
                <div class="video-meta">
                  <span class="views">{{ formatViews(video.playCount) }}次播放</span>
                  <span class="date">{{ formatDate(video.publishTime) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'short'" class="tab-pane">
          <div class="short-video-grid">
            <div
              v-for="video in shortVideos"
              :key="video.id"
              class="short-video-card"
              @click="playVideo(video)"
            >
              <div class="short-video-thumbnail">
                <img :src="video.cover" :alt="video.title" @error="handleImageError">
                <div class="play-overlay">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M8 5v14l11-7z" fill="var(--light-text)"/>
                  </svg>
                </div>
              </div>
              <div class="short-video-info">
                <h5>{{ video.title }}</h5>
                <p>{{ formatViews(video.playCount) }}次播放</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="load-more" v-if="hasMore">
      <button class="custom-load-more-btn" @click="loadMore" :disabled="loading">
        {{ loading ? '加载中...' : '加载更多' }}
      </button>
    </div>

    <!-- 自定义视频播放弹窗 -->
    <div v-if="videoDialogVisible" class="custom-video-modal" @click="closeVideo">
      <div class="video-modal-content" @click.stop>
        <button class="close-button" @click="closeVideo">×</button>
        <div class="video-player-container" v-if="currentVideo">
          <div class="video-player">
            <video
              v-if="currentVideo.videoUrl"
              :src="currentVideo.videoUrl"
              controls
              autoplay
              width="100%"
              height="100%"
            ></video>
            <div v-else class="video-placeholder">
              <p>视频暂时无法播放</p>
              <p>{{ currentVideo.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'VideoFeed',
  setup() {
    const activeTab = ref('normal')
    const selectedChannel = ref(4)
    const channelDropdownOpen = ref(false)
    const normalVideos = ref([])
    const shortVideos = ref([])
    const loading = ref(false)
    const hasMore = ref(true)
    const currentOffset = ref(0)
    const videoDialogVisible = ref(false)
    const currentVideo = ref(null)

    const channels = ref([
      { id: 4, name: '推荐' },
      { id: 1067226, name: '预告片' },
      { id: 1331498, name: '热片解读' },
      { id: 1074953, name: '说电影' },
      { id: 1307354, name: '娱乐' }
    ])

    // 计算属性
    const selectedChannelName = computed(() => {
      const channel = channels.value.find(c => c.id === selectedChannel.value)
      return channel ? channel.name : '推荐'
    })

    const loadNormalVideos = async (offset = 0, reset = false) => {
      try {
        loading.value = true

        // 直接使用模拟数据，避免API限频问题
        console.log('使用模拟视频数据，避免API限频')
        const mockVideos = Array.from({ length: 10 }, (_, i) => ({
          id: `mock_${offset}_${i}`,
          title: getRandomVideoTitle(offset + i + 1),
          description: getRandomVideoDescription(),
          cover: `https://picsum.photos/300/200?random=${offset + i + 1}`,
          duration: Math.floor(Math.random() * 600) + 60,
          playCount: Math.floor(Math.random() * 100000),
          publishTime: Date.now() - Math.random() * 86400000 * 30,
          videoUrl: getRandomVideoUrl()
        }))

        if (reset) {
          normalVideos.value = mockVideos
        } else {
          normalVideos.value.push(...mockVideos)
        }

        hasMore.value = offset < 50 // 限制最多加载到50个
      } catch (error) {
        console.error('加载视频失败:', error)
        ElMessage.error('加载视频失败')
      } finally {
        loading.value = false
      }
    }

    const loadShortVideos = async (offset = 0, reset = false) => {
      try {
        loading.value = true

        // 直接使用模拟数据
        const mockVideos = Array.from({ length: 8 }, (_, i) => ({
          id: `short_mock_${offset}_${i}`,
          title: getRandomShortVideoTitle(offset + i + 1),
          cover: `https://picsum.photos/200/300?random=${100 + offset + i}`,
          playCount: Math.floor(Math.random() * 50000),
          videoUrl: getRandomVideoUrl()
        }))

        if (reset) {
          shortVideos.value = mockVideos
        } else {
          shortVideos.value.push(...mockVideos)
        }

        hasMore.value = offset < 40
      } catch (error) {
        console.error('加载短视频失败:', error)
        ElMessage.error('加载短视频失败')
      } finally {
        loading.value = false
      }
    }

    // 生成随机视频标题
    const getRandomVideoTitle = (index) => {
      const titles = [
        `《阿凡达：水之道》幕后制作特辑 ${index}`,
        `漫威宇宙最新预告片解析 ${index}`,
        `好莱坞大片精彩片段合集 ${index}`,
        `电影特效制作揭秘 ${index}`,
        `明星访谈：谈论新作品 ${index}`,
        `经典电影回顾与分析 ${index}`,
        `最新院线电影推荐 ${index}`,
        `电影节获奖作品展示 ${index}`,
        `导演创作理念分享 ${index}`,
        `电影音乐原声带赏析 ${index}`
      ]
      return titles[index % titles.length]
    }

    // 生成随机视频描述
    const getRandomVideoDescription = () => {
      const descriptions = [
        '这是一个精彩的电影解说视频，带你了解电影背后的故事和制作过程。',
        '深度解析电影情节，揭示隐藏的细节和彩蛋。',
        '专业影评人为你解读最新上映的热门电影。',
        '幕后花絮大揭秘，看看明星们在片场的真实表现。',
        '电影特效制作过程全记录，感受科技与艺术的完美结合。',
        '经典电影重温，回味那些永恒的银幕时光。'
      ]
      return descriptions[Math.floor(Math.random() * descriptions.length)]
    }

    // 生成随机短视频标题
    const getRandomShortVideoTitle = (index) => {
      const titles = [
        `电影精彩片段 ${index}`,
        `明星搞笑瞬间 ${index}`,
        `经典台词合集 ${index}`,
        `动作场面集锦 ${index}`,
        `感人情节回顾 ${index}`,
        `电影彩蛋揭秘 ${index}`
      ]
      return titles[index % titles.length]
    }

    // 生成随机视频URL（模拟）
    const getRandomVideoUrl = () => {
      // 返回一些公开的测试视频URL
      const testVideos = [
        'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4',
        'https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-mp4-file.mp4',
        null // 有些视频没有URL，用于测试占位符
      ]
      return testVideos[Math.floor(Math.random() * testVideos.length)]
    }

    // 自定义组件方法
    const toggleChannelDropdown = () => {
      channelDropdownOpen.value = !channelDropdownOpen.value
    }

    const selectChannel = (channel) => {
      selectedChannel.value = channel.id
      channelDropdownOpen.value = false
      currentOffset.value = 0
      loadNormalVideos(0, true)
    }

    const switchTab = (tabName) => {
      activeTab.value = tabName
      currentOffset.value = 0
      if (tabName === 'normal') {
        loadNormalVideos(0, true)
      } else {
        loadShortVideos(0, true)
      }
    }

    const handleChannelChange = () => {
      currentOffset.value = 0
      loadNormalVideos(0, true)
    }

    const handleTabClick = (tab) => {
      currentOffset.value = 0
      if (tab.name === 'normal') {
        loadNormalVideos(0, true)
      } else {
        loadShortVideos(0, true)
      }
    }

    const loadMore = () => {
      currentOffset.value += activeTab.value === 'normal' ? 15 : 10
      if (activeTab.value === 'normal') {
        loadNormalVideos(currentOffset.value)
      } else {
        loadShortVideos(currentOffset.value)
      }
    }

    const playVideo = (video) => {
      currentVideo.value = video
      videoDialogVisible.value = true
      if (!video.videoUrl) {
        ElMessage.warning('该视频暂时无法播放')
      }
    }

    const closeVideo = () => {
      videoDialogVisible.value = false
      currentVideo.value = null
    }

    const formatDuration = (seconds) => {
      if (!seconds) return '00:00'
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }

    const formatViews = (count) => {
      if (count >= 10000) {
        return (count / 10000).toFixed(1) + '万'
      }
      return count.toString()
    }

    const formatDate = (timestamp) => {
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now - date
      const days = Math.floor(diff / (1000 * 60 * 60 * 24))

      if (days === 0) return '今天'
      if (days === 1) return '昨天'
      if (days < 7) return `${days}天前`
      return date.toLocaleDateString()
    }

    const handleImageError = (e) => {
      e.target.src = 'https://via.placeholder.com/300x200?text=加载失败'
    }

    onMounted(() => {
      loadNormalVideos(0, true)
    })

    return {
      activeTab,
      selectedChannel,
      selectedChannelName,
      channelDropdownOpen,
      channels,
      normalVideos,
      shortVideos,
      loading,
      hasMore,
      videoDialogVisible,
      currentVideo,
      toggleChannelDropdown,
      selectChannel,
      switchTab,
      handleChannelChange,
      handleTabClick,
      loadMore,
      playVideo,
      closeVideo,
      formatDuration,
      formatViews,
      formatDate,
      handleImageError
    }
  }
}
</script>

<style scoped>
.video-feed {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-color);
}

.feed-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.feed-header h3 {
  margin: 0;
  color: var(--light-text);
}

/* 自定义频道选择器样式 */
.custom-channel-select {
  position: relative;
  width: 120px;
}

.channel-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  color: var(--light-text);
  transition: border-color 0.3s ease;
}

.channel-display:hover {
  border-color: var(--primary-color);
}

.dropdown-arrow {
  color: var(--gray-text);
  transition: transform 0.3s ease;
  font-size: 12px;
}

.dropdown-arrow.open {
  transform: rotate(180deg);
}

.channel-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-top: none;
  border-radius: 0 0 8px 8px;
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
}

.channel-option {
  padding: 10px 12px;
  color: var(--light-text);
  cursor: pointer;
  transition: background-color 0.3s ease;
  border-bottom: 1px solid var(--border-color);
}

.channel-option:hover {
  background: rgba(229, 9, 20, 0.1);
}

.channel-option:last-child {
  border-bottom: none;
}

/* 自定义标签页样式 */
.custom-tabs {
  margin-top: 20px;
}

.tab-header {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 20px;
}

.tab-item {
  padding: 12px 20px;
  cursor: pointer;
  color: var(--gray-text);
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
}

.tab-item:hover {
  color: var(--light-text);
}

.tab-item.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.tab-content {
  min-height: 200px;
}

.tab-pane {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.video-card {
  cursor: pointer;
  border-radius: 8px;
  overflow: hidden;
  transition: border-color 0.3s ease;
  background: var(--darker-bg);
  border: 1px solid var(--border-color);
}

.video-card:hover {
  border-color: var(--primary-color);
}

.video-thumbnail {
  position: relative;
  width: 100%;
  height: 180px;
  overflow: hidden;
}

.video-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  opacity: 0;
  transition: opacity 0.3s;
  color: white;
  font-size: 24px;
}

.video-card:hover .play-overlay {
  opacity: 1;
}

.duration {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.video-info {
  padding: 15px;
}

.video-info h4 {
  margin: 0 0 8px 0;
  color: var(--light-text);
  font-size: 16px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.video-desc {
  margin: 0 0 10px 0;
  color: var(--gray-text);
  font-size: 14px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.video-meta {
  display: flex;
  justify-content: space-between;
  color: var(--gray-text);
  font-size: 12px;
}

.short-video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.short-video-card {
  cursor: pointer;
  border-radius: 8px;
  overflow: hidden;
  transition: border-color 0.3s ease;
  background: var(--darker-bg);
  border: 1px solid var(--border-color);
}

.short-video-card:hover {
  border-color: var(--primary-color);
}

.short-video-thumbnail {
  position: relative;
  width: 100%;
  height: 250px;
  overflow: hidden;
}

.short-video-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.short-video-info {
  padding: 10px;
}

.short-video-info h5 {
  margin: 0 0 5px 0;
  color: var(--light-text);
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.short-video-info p {
  margin: 0;
  color: var(--gray-text);
  font-size: 12px;
}

.load-more {
  text-align: center;
  margin-top: 20px;
}

.video-player-container {
  text-align: center;
}

.video-player-container h3 {
  margin: 0 0 20px 0;
  color: var(--light-text);
}

.video-player {
  position: relative;
  background: var(--dark-bg);
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.video-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: var(--gray-text);
  background: var(--card-bg);
}

/* 自定义加载更多按钮 */
.load-more {
  text-align: center;
  margin-top: 20px;
}

.custom-load-more-btn {
  padding: 10px 20px;
  background: var(--primary-color);
  color: var(--light-text);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.custom-load-more-btn:hover:not(:disabled) {
  background: rgba(229, 9, 20, 0.8);
}

.custom-load-more-btn:disabled {
  background: var(--gray-text);
  cursor: not-allowed;
}

/* 自定义视频弹窗样式 */
.custom-video-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.video-modal-content {
  position: relative;
  width: 80%;
  max-width: 800px;
  background: var(--card-bg);
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.close-button {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 30px;
  height: 30px;
  background: rgba(0, 0, 0, 0.5);
  color: var(--light-text);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  background: rgba(0, 0, 0, 0.7);
}

.custom-video-modal .video-player {
  position: relative;
  width: 100%;
  height: 0;
  padding-bottom: 56.25%; /* 16:9 aspect ratio */
  background: var(--dark-bg);
}

.custom-video-modal .video-player video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.custom-video-modal .video-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--gray-text);
  background: var(--card-bg);
}

/* Element Plus 组件深色主题覆盖 */
:deep(.el-button) {
  border-radius: 8px;
  background-color: var(--card-bg);
  border-color: var(--border-color);
  color: var(--light-text);
}

:deep(.el-button:hover) {
  border-color: var(--primary-color);
  color: var(--light-text);
  background-color: rgba(229, 9, 20, 0.1);
}

:deep(.el-button--primary) {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
  color: var(--light-text);
}

:deep(.el-button--primary:hover) {
  background-color: rgba(229, 9, 20, 0.8);
  border-color: rgba(229, 9, 20, 0.8);
  color: var(--light-text);
}

:deep(.el-dialog) {
  background-color: var(--card-bg);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

:deep(.el-dialog__header) {
  background-color: var(--darker-bg);
  border-bottom: 1px solid var(--border-color);
  border-radius: 12px 12px 0 0;
}

:deep(.el-dialog__title) {
  color: var(--light-text);
}

:deep(.el-dialog__body) {
  background-color: var(--card-bg);
  color: var(--light-text);
}

:deep(.el-dialog__footer) {
  background-color: var(--darker-bg);
  border-top: 1px solid var(--border-color);
  border-radius: 0 0 12px 12px;
}
</style>