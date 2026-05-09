<template>
  <div class="chat-container">


    <!-- 服务状态提示 -->
    <div v-if="serviceStatus" class="service-status" :class="serviceStatus.type">
      {{ serviceStatus.message }}
    </div>

    <!-- 聊天消息区域 -->
    <div class="chat-messages" ref="messagesContainer">
      <transition-group name="message-fade">
        <div
          v-for="(msg, index) in messages"
          :key="msg.id || index"
          :class="['message-bubble', msg.role]"
        >
          <div class="message-content">
            <div class="message-text" v-html="formatMessage(msg.content)"></div>

            <!-- 电影推荐卡片 -->
            <div v-if="msg.movies?.length" class="recommendation-grid">
              <div
                v-for="movie in msg.movies"
                :key="movie.tmdb_id"
                class="movie-card"
                @click="showMovieDetail(movie)"
              >
                <div class="poster-container">
                  <img
                    :src="getPosterUrl(movie.poster_path)"
                    :alt="movie.title"
                    @error="handlePosterError"
                    class="movie-poster"
                  />
                </div>
                <div class="movie-info">
                  <h3 class="movie-title">{{ movie.title }}</h3>
                  <p class="recommend-reason">{{ movie.reason || '精选推荐' }}</p>
                  <div class="movie-meta">
                    <span class="rating">⭐ {{ movie.vote_average?.toFixed(1) }}</span>
                    <span class="year">{{ getYear(movie.release_date) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition-group>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <div class="input-wrapper">
        <input
          v-model="userInput"
          type="text"
          placeholder="告诉我你的喜好，我来为你推荐电影..."
          @keyup.enter="sendMessage"
          :disabled="loading"
        />
        <button
          class="send-button"
          :class="{ loading }"
          @click="sendMessage"
          :disabled="loading"
        >
          <span v-if="loading" class="loading-indicator">
            <div class="spinner"></div>
            处理中...
          </span>
          <span v-else>发送</span>
        </button>
      </div>
    </div>

    <!-- 电影详情模态框 -->
    <movie-detail-modal
      v-if="selectedMovie"
      :movie="selectedMovie"
      @close="selectedMovie = null"
    />
  </div>
</template>

<script>
import axios from '@/utils/axios'
import MovieDetailModal from '@/views/MovieDetail.vue'

export default {
  components: {
    MovieDetailModal
  },
  data() {
    return {
      userInput: '',
      messages: [],
      loading: false,
      selectedMovie: null,
      serviceStatus: null,
      retryCount: 0,
      maxRetries: 3
    }
  },
  methods: {
    async sendMessage() {
      if (!this.userInput.trim() || this.loading) return

      try {
        this.loading = true
        this.clearStatus()

        // 添加用户消息
        const userMsg = this.createMessage('user', this.userInput.trim())
        this.messages = [...this.messages, userMsg]

        // 发送请求
        const response = await this.fetchRecommendations(userMsg.content)

        // 处理AI响应
        const aiMsg = this.createMessage('assistant', response.content, response.movies)
        this.messages = [...this.messages, aiMsg]

        this.retryCount = 0
      } catch (error) {
        this.handleError(error)
      } finally {
        this.loading = false
        this.userInput = ''
        this.scrollToBottom()
      }
    },

    async fetchRecommendations(message) {
      try {
        const response = await axios.post('/llm/chat/', {
          message,
          history: this.messages.slice(-3) // 发送最近3条历史
        })

        if (!response.data?.movies) {
          throw new Error('无效的响应格式')
        }

        // 获取推荐理由
        const moviesWithReason = await Promise.all(
          response.data.movies.map(async movie => ({
            ...movie,
            reason: await this.getRecommendReason(movie.tmdb_id)
          }))
        )

        return {
          content: response.data.response,
          movies: moviesWithReason
        }
      } catch (error) {
        if (this.retryCount < this.maxRetries) {
          this.retryCount++
          await new Promise(resolve => setTimeout(resolve, 2000))
          return this.fetchRecommendations(message)
        }
        throw error
      }
    },

    async getRecommendReason(movieId) {
      try {
        const response = await axios.post('/llm/recommend/', {
          movie_ids: [movieId]
        })
        return response.data.reasons[movieId] || '根据你的兴趣推荐'
      } catch (error) {
        console.error('推荐理由获取失败:', error)
        return null
      }
    },
    // 替换为修改后的 createMessage 方法
    createMessage(role, content, movies = []) {
      return {
        id: Date.now(),
        role,
        content,
        movies: movies.map(movie => ({
          // 确保包含必要字段
          tmdb_id: movie.tmdb_id,
          title: movie.title,
          poster_path: movie.poster_path,
          vote_average: movie.vote_average || 0,
          release_date: movie.release_date || '',
          reason: movie.reason || '精选推荐'
        }))
      }
    },

    getPosterUrl(path) {
      return path
        ? `https://image.tmdb.org/t/p/w400${path}`
        : require('@/assets/default-poster.jpg')
    },

    getYear(dateStr) {
      return dateStr ? new Date(dateStr).getFullYear() : '--'
    },

    handlePosterError(event) {
      event.target.src = require('@/assets/default-poster.jpg')
    },
    // 替换为修改后的 showMovieDetail 方法
    showMovieDetail(movie) {
      // 确保使用正确的ID字段
      const movieId = movie.tmdb_id
      if (!movieId) {
        console.error('无效的电影ID:', movie)
        this.$notify.error('无法获取电影详情')
        return
      }

      // 使用命名路由并验证参数
      this.$router.push({
        name: 'MovieDetail',
        params: {
          id: movieId,
          title: movie.title.replace(/\s+/g, '-') // SEO友好格式
        }
      }).catch(err => {
        if (err.name !== 'NavigationDuplicated') {
          console.error('路由跳转失败:', err)
          this.$notify.error('页面加载失败')
        }
      })
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      })
    },

    handleError(error) {
      let message = '请求失败，请稍后重试'
      let type = 'error'

      if (error.response) {
        const { status, data } = error.response
        message = `服务器错误 (${status})`
        type = status === 503 ? 'service' : 'error'

        if (data?.code === 'TMDB_UNAVAILABLE') {
          message = '电影数据服务暂时不可用'
          type = 'tmdb'
        } else if (data?.code === 'AI_UNAVAILABLE') {
          message = '推荐服务暂时不可用'
          type = 'ai'
        }
      } else if (error.message.includes('timeout')) {
        message = '请求超时，请检查网络连接'
        type = 'network'
      }

      this.serviceStatus = { type, message }
      console.error('[API Error]', error)
    },

    clearStatus() {
      this.serviceStatus = null
      this.retryCount = 0
    },

    formatMessage(content) {
      if (!content) return ''

      // 检测序号模式：数字+点号+空格，但后面不能紧跟数字（排除8.5这种评分）
      const numberPattern = /(\s*)(\d+\.\s+)(?!\d)/g

      // 在序号前添加换行，但保留原有的空格缩进
      const formatted = content.replace(numberPattern, (match, spaces, numberDot) => {
        // 如果是文本开头的序号，不添加换行
        const index = content.indexOf(match)
        if (index === 0) {
          return match
        }
        // 其他位置的序号前添加换行
        return '<br>' + spaces + numberDot
      })

      return formatted
    }
  }
}
</script>

<style scoped>
.chat-container {
  max-width: 900px;
  margin: 6rem auto 2rem;
  height: 80vh;
  display: flex;
  flex-direction: column;
  background: var(--dark-bg);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  overflow: hidden;
}



.service-status {
  padding: 12px 20px;
  font-size: 0.9rem;
  border-radius: 8px;
  margin: 12px;
  text-align: center;
}

.service-status.tmdb {
  background: #fff3cd;
  color: #856404;
}

.service-status.ai {
  background: #f8d7da;
  color: #721c24;
}

.service-status.network {
  background: #d4edda;
  color: #155724;
}

.chat-messages {
  flex: 1;
  padding: 1rem 1.2rem 0.8rem;
  overflow-y: auto;
  background: var(--darker-bg);
}

.message-bubble {
  margin: 0.6rem 0;
  max-width: 55%;
  padding: 0.7rem 1rem;
  border-radius: 12px;
  line-height: 1.4;
  font-size: 0.85rem;
  transition: all 0.3s ease;
}

.message-bubble.user {
  background: #2a2a2a;
  color: #e8e8e8;
  margin-left: auto;
  border: 1px solid #404040;
}

.message-bubble.assistant {
  background: #2a2a2a;
  color: #e8e8e8;
  margin-right: auto;
  border: 1px solid #404040;
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}

.recommendation-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 1rem;
}

.movie-card {
  width: 180px;
  border-radius: 8px;
  overflow: hidden;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.movie-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.4);
  border-color: var(--primary-color);
}

.poster-container {
  position: relative;
  padding-top: 75%;
  background: #f0f0f0;
}

.movie-poster {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.movie-info {
  padding: 0.8rem;
}

.movie-title {
  font-size: 0.9rem;
  margin: 0 0 0.4rem;
  color: var(--light-text);
  font-weight: 600;
  line-height: 1.2;
}

.recommend-reason {
  font-size: 0.75rem;
  color: var(--gray-text);
  margin: 0.4rem 0;
  line-height: 1.3;
}

.movie-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: var(--gray-text);
}

.input-area {
  padding: 0.8rem 1rem;
  background: var(--card-bg);
  border-top: 1px solid var(--border-color);
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  max-width: 600px;
  margin: 0 auto;
}

input {
  flex: 1;
  padding: 0;
  padding-left: 1rem;
  padding-right: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 0.85rem;
  background: var(--dark-bg);
  color: var(--light-text);
  transition: all 0.3s ease;
  height: 2.4rem;
  box-sizing: border-box;
  line-height: 1;
}

input:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(229, 9, 20, 0.1);
  outline: none;
}

input::placeholder {
  color: var(--gray-text);
}

.send-button {
  padding: 0;
  border: 1px solid var(--primary-color);
  border-radius: 8px;
  background: var(--primary-color);
  color: white;
  font-weight: 500;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
  height: 2.4rem;
  min-width: 4rem;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-button:hover:not(:disabled) {
  background: #c8070f;
  transform: translateY(-1px);
}

.send-button:disabled {
  background: #e0e0e0;
  cursor: not-allowed;
  opacity: 0.7;
}

.send-button.loading {
  padding-left: 20px;
  padding-right: 20px;
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes gradient-flow {
  0% {
    background-position: 0% 50%;
  }
  100% {
    background-position: 400% 50%;
  }
}

@media (max-width: 768px) {
  .chat-container {
    margin: 0;
    height: 100vh;
    border-radius: 0;
  }

  .recommendation-grid {
    grid-template-columns: 1fr;
  }

  .input-wrapper {
    flex-direction: column;
  }

  .send-button {
    width: 100%;
  }
}
</style>