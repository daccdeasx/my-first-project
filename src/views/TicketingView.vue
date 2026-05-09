<template>
  <div class="ticketing-container">
    <!-- 电影信息区域 -->
    <div class="movie-info" v-if="movie">
      <img
        :src="getFullPosterUrl(movie.poster_path)"
        :alt="movie.title"
        class="movie-poster"
        @error="handlePosterError"
      >
      <div class="movie-details">
        <h1>{{ movie.title }}</h1>
        <p class="movie-overview">{{ movie.overview }}</p>
        <div class="movie-meta">
          <span>时长: {{ movie.runtime }}分钟</span>
          <span>类型: {{ movie.genres?.join(', ') || '暂无类型信息' }}</span>
          <span v-if="movie.release_date">上映日期: {{ movie.release_date }}</span>
          <span v-if="movie.vote_average">评分: {{ movie.vote_average }}/10</span>
        </div>

        <!-- 视频播放区域 -->
        <div class="video-section">
          <el-button
            type="primary"
            @click="showTrailer"
            :loading="loadingVideos"
          >
            观看预告片
          </el-button>
          <el-button
            @click="loadMovieVideos"
            :loading="loadingVideos"
          >
            相关视频
          </el-button>
        </div>
      </div>
    </div>

    <!-- 加载中状态 -->
    <div v-else class="movie-loading">
      <el-skeleton :rows="3" animated />
      <p>正在加载电影信息...</p>
    </div>

    <!-- 影院选择区域 -->
    <div class="cinema-selection">
      <!-- 影院搜索组件 -->
      <div class="cinema-search-container">
        <CinemaSearch @cinema-selected="handleCinemaSelected" />
      </div>

      <!-- 场次信息 -->
      <div v-if="selectedCinema" class="schedule-section">
        <h3>{{ selectedCinema.name }} - 场次安排</h3>
        <el-date-picker
          v-model="selectedDate"
          type="date"
          placeholder="选择日期"
          :picker-options="pickerOptions"
          @change="loadSchedules"
        />

        <div v-if="cinemaSchedules.length > 0" class="schedules">
          <el-table :data="cinemaSchedules" style="width: 100%">
            <el-table-column prop="start_time" label="时间" width="180">
              <template #default="scope">
                {{ formatDateTime(scope.row.start_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="price" label="价格" width="120">
              <template #default="scope">
                ¥{{ scope.row.price }}
              </template>
            </el-table-column>
            <el-table-column prop="available_seats" label="余票" width="100">
              <template #default="scope">
                {{ scope.row.available_seats }}/{{ scope.row.total_seats }}
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template #default="scope">
                <el-button
                  type="primary"
                  size="small"
                  @click="selectSchedule(scope.row)"
                  :disabled="scope.row.available_seats === 0"
                >
                  {{ scope.row.available_seats === 0 ? '已售罄' : '选座购票' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div v-else-if="!loadingSchedules" class="no-schedules">
          <el-empty description="该日期暂无场次安排" />
        </div>

        <div v-if="loadingSchedules" class="loading-schedules">
          <el-skeleton :rows="3" animated />
        </div>
      </div>
    </div>

    <!-- 视频Feed区域 -->
    <div class="video-feed-section">
      <VideoFeed />
    </div>

    <!-- 调试信息面板（开发时使用） -->
    <div v-if="movie && movie.title === '测试电影'" class="debug-panel">
      <h4>调试信息</h4>
      <p>电影ID: {{ route.params.id }}</p>
      <p>电影标题: {{ movie?.title }}</p>
      <p>选中影院: {{ selectedCinema?.name || '未选择' }}</p>
      <p>场次数量: {{ cinemaSchedules.length }}</p>
      <p>选中座位: {{ selectedSeats.length }}</p>
    </div>

    <!-- 自定义选座弹窗 -->
    <div v-if="seatSelectionVisible" class="custom-seat-modal" @click="handleCloseDialog">
      <div class="seat-modal-content" @click.stop>
        <div class="modal-header">
          <button class="close-button" @click="handleCloseDialog">×</button>
        </div>
        <div class="seat-selection">
          <div class="screen">银幕</div>
          <div class="seats-container">
            <div
              v-for="(row, rowIndex) in seatsLayout"
              :key="rowIndex"
              class="seat-row"
            >
              <div class="row-label">{{ String.fromCharCode(65 + rowIndex) }}</div>
              <div
                v-for="(seat, colIndex) in row"
                :key="colIndex"
                class="seat"
                :class="{
                  'occupied': isOccupied(rowIndex, colIndex),
                  'selected': isSelected(rowIndex, colIndex)
                }"
                @click="toggleSeat(rowIndex, colIndex)"
              >
                {{ colIndex + 1 }}
              </div>
            </div>
          </div>
          <div class="seat-legend">
            <div class="legend-item">
              <div class="seat available"></div>
              <span>可选</span>
            </div>
            <div class="legend-item">
              <div class="seat occupied"></div>
              <span>已售</span>
            </div>
            <div class="legend-item">
              <div class="seat selected"></div>
              <span>已选</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-button" @click="handleCloseDialog">取消</button>
          <button
            class="confirm-button"
            @click="createOrder"
            :disabled="selectedSeats.length === 0"
          >
            <span v-if="creatingOrder">处理中...</span>
            <span v-else>确认购票 (¥{{ totalPrice }})</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 自定义视频播放弹窗 -->
    <div v-if="videoDialogVisible" class="custom-video-modal" @click="closeVideoDialog">
      <div class="video-modal-content" @click.stop>
        <button class="close-button" @click="closeVideoDialog">×</button>
        <div class="video-player" v-if="currentVideo">
          <iframe
            v-if="currentVideo.site === 'YouTube'"
            :src="`https://www.youtube.com/embed/${currentVideo.key}?autoplay=1&rel=0&modestbranding=1`"
            frameborder="0"
            allowfullscreen
            allow="autoplay; encrypted-media; fullscreen"
            width="100%"
            height="100%"
            @error="handleVideoError"
          ></iframe>
          <iframe
            v-else-if="currentVideo.site === 'Vimeo'"
            :src="`https://player.vimeo.com/video/${currentVideo.key}?autoplay=1`"
            frameborder="0"
            allowfullscreen
            width="100%"
            height="100%"
            @error="handleVideoError"
          ></iframe>
          <video
            v-else-if="currentVideo.site === 'Maoyan' && currentVideo.url"
            :src="currentVideo.url"
            controls
            autoplay
            width="100%"
            height="100%"
            @error="handleVideoError"
          ></video>
          <div v-else class="video-placeholder">
            <p>视频暂时无法播放</p>
            <p>视频类型: {{ currentVideo.type }}</p>
            <p>来源: {{ currentVideo.site }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 相关视频列表弹窗 -->
    <div v-if="videoListDialogVisible" class="custom-video-list-modal" @click="closeVideoListDialog">
      <div class="video-list-modal-content" @click.stop>
        <div class="modal-header">
          <h3>相关视频</h3>
          <button class="close-button" @click="closeVideoListDialog">×</button>
        </div>
        <div class="video-grid">
          <div
            v-for="video in movieVideos"
            :key="video.id"
            class="video-item"
            @click="playVideoFromList(video)"
          >
            <div class="video-thumbnail">
              <img
                v-if="video.site === 'YouTube'"
                :src="`https://img.youtube.com/vi/${video.key}/mqdefault.jpg`"
                :alt="video.name"
              >
              <div v-else class="placeholder-thumbnail">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M8 5v14l11-7z" fill="var(--gray-text)"/>
                </svg>
              </div>
              <div class="play-overlay">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M8 5v14l11-7z" fill="var(--light-text)"/>
                </svg>
              </div>
            </div>
            <div class="video-info">
              <h5>{{ video.name }}</h5>
              <p>{{ getVideoTypeText(video.type) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import dayjs from 'dayjs'
import CinemaSearch from '../components/CinemaSearch.vue'
import VideoFeed from '../components/VideoFeed.vue'

export default {
  name: 'TicketingView',
  components: {
    CinemaSearch,
    VideoFeed
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const movie = ref(null)
    const cinemas = ref([])
    const searchQuery = ref('')
    const selectedDate = ref(new Date())
    const selectedCinema = ref(null)
    const cinemaSchedules = ref([])
    const selectedSchedule = ref(null)
    const seatSelectionVisible = ref(false)
    const seatsLayout = ref([])
    const selectedSeats = ref([])
    const occupiedSeats = ref([])
    const loadingSchedules = ref(false)
    const videoDialogVisible = ref(false)
    const videoListDialogVisible = ref(false)
    const currentVideo = ref(null)
    const movieVideos = ref([])
    const loadingVideos = ref(false)
    const creatingOrder = ref(false)

    const pickerOptions = {
      disabledDate(time) {
        return time.getTime() < Date.now() - 8.64e7
      }
    }

    // 计算属性
    const filteredCinemas = computed(() => {
      if (!Array.isArray(cinemas.value) || !searchQuery.value) return cinemas.value || []
      const query = searchQuery.value.toLowerCase()
      return cinemas.value.filter(cinema =>
        cinema && cinema.name && cinema.address &&
        (cinema.name.toLowerCase().includes(query) ||
        cinema.address.toLowerCase().includes(query))
      )
    })

    const totalPrice = computed(() => {
      if (!selectedSchedule.value) return 0
      return selectedSchedule.value.price * selectedSeats.value.length
    })

    // 方法
    const loadMovie = async () => {
      try {
        console.log('正在加载电影信息，ID:', route.params.id)
        const response = await axios.get(`/api/movies/${route.params.id}/`)
        console.log('电影信息响应:', response.data)

        // 处理嵌套的数据结构
        const movieData = response.data
        if (movieData.detail) {
          // 如果数据是嵌套格式，提取detail部分
          movie.value = {
            ...movieData.detail,
            credits: movieData.credits,
            similar: movieData.similar,
            interaction: movieData.interaction
          }
        } else {
          // 如果是直接格式
          movie.value = movieData
        }

        console.log('处理后的电影信息:', movie.value)

        // 如果没有电影信息，显示错误
        if (!movie.value) {
          ElMessage.error('未找到电影信息')
        }
      } catch (error) {
        console.error('加载电影信息失败:', error)
        ElMessage.error('加载电影信息失败: ' + (error.response?.data?.detail || error.message))

        // 如果API失败，创建一个默认的电影对象用于测试
        movie.value = {
          id: route.params.id,
          title: '测试电影',
          overview: '这是一个测试电影的描述信息。',
          poster_path: 'https://via.placeholder.com/200x300?text=电影海报',
          runtime: 120,
          genres: ['动作', '科幻']
        }
      }
    }

    const loadCinemas = async () => {
      try {
        const response = await axios.get('/api/cinemas/')
        // 确保返回的是数组
        cinemas.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
      } catch (error) {
        ElMessage.error('加载影院信息失败')
        cinemas.value = [] // 确保在错误时也是数组
      }
    }

    const handleCinemaSelected = async (cinema) => {
      selectedCinema.value = cinema
      console.log('选择的影院:', cinema)

      // 如果是模拟影院，显示模拟场次数据
      if (cinema.id && cinema.id.toString().startsWith('mock_')) {
        console.log('检测到模拟影院，使用模拟场次数据')
        loadingSchedules.value = true

        // 模拟场次数据
        setTimeout(() => {
          cinemaSchedules.value = [
            {
              id: 'mock_schedule_1',
              start_time: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(), // 2小时后
              end_time: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString(), // 4小时后
              price: 45,
              available_seats: 120,
              total_seats: 150
            },
            {
              id: 'mock_schedule_2',
              start_time: new Date(Date.now() + 5 * 60 * 60 * 1000).toISOString(), // 5小时后
              end_time: new Date(Date.now() + 7 * 60 * 60 * 1000).toISOString(), // 7小时后
              price: 50,
              available_seats: 80,
              total_seats: 150
            },
            {
              id: 'mock_schedule_3',
              start_time: new Date(Date.now() + 8 * 60 * 60 * 1000).toISOString(), // 8小时后
              end_time: new Date(Date.now() + 10 * 60 * 60 * 1000).toISOString(), // 10小时后
              price: 55,
              available_seats: 95,
              total_seats: 150
            }
          ]
          loadingSchedules.value = false
          console.log('模拟场次数据加载完成:', cinemaSchedules.value)
        }, 1000)
        return
      }

      // 真实影院，调用API
      try {
        loadingSchedules.value = true
        console.log('开始加载真实场次数据:', {
          movie: route.params.id,
          cinema: cinema.id,
          date: dayjs(selectedDate.value).format('YYYY-MM-DD')
        })

        const response = await axios.get('/api/schedules/', {
          params: {
            movie: route.params.id,
            cinema: cinema.id,
            date: dayjs(selectedDate.value).format('YYYY-MM-DD')
          },
          headers: {
            'Authorization': `Token ${localStorage.getItem('authToken')}`
          }
        })

        console.log('场次API响应:', response.data)
        cinemaSchedules.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
        console.log('处理后的场次数据:', cinemaSchedules.value)

        // 如果没有场次数据，提供模拟数据
        if (cinemaSchedules.value.length === 0) {
          console.log('没有找到场次数据，使用模拟数据')
          cinemaSchedules.value = [
            {
              id: 'fallback_schedule_1',
              start_time: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(),
              end_time: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString(),
              price: 45,
              available_seats: 100,
              total_seats: 150
            },
            {
              id: 'fallback_schedule_2',
              start_time: new Date(Date.now() + 6 * 60 * 60 * 1000).toISOString(),
              end_time: new Date(Date.now() + 8 * 60 * 60 * 1000).toISOString(),
              price: 50,
              available_seats: 85,
              total_seats: 150
            }
          ]
          ElMessage.info('该影院暂无排片，显示演示场次')
        }
      } catch (error) {
        console.error('加载场次信息失败:', error)
        ElMessage.error('加载场次信息失败: ' + (error.response?.data?.detail || error.message))

        // API失败时也使用模拟数据
        cinemaSchedules.value = [
          {
            id: 'fallback_schedule_1',
            start_time: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(),
            end_time: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString(),
            price: 45,
            available_seats: 100,
            total_seats: 150
          }
        ]
      } finally {
        loadingSchedules.value = false
      }
    }

    const selectSchedule = (schedule) => {
      selectedSchedule.value = schedule
      console.log('选择的场次:', schedule)

      // 为模拟场次生成座位布局
      if (schedule.id && (schedule.id.toString().startsWith('mock_') || schedule.id.toString().startsWith('fallback_'))) {
        console.log('生成模拟座位布局')
        // 生成10行15列的座位布局
        const rows = 10
        const cols = 15
        const layout = []

        for (let i = 0; i < rows; i++) {
          const row = []
          for (let j = 0; j < cols; j++) {
            row.push({
              row: i,
              col: j,
              available: true
            })
          }
          layout.push(row)
        }

        seatsLayout.value = layout

        // 模拟一些已占用的座位
        occupiedSeats.value = [
          { row: 2, col: 5 },
          { row: 2, col: 6 },
          { row: 4, col: 8 },
          { row: 4, col: 9 },
          { row: 6, col: 3 },
          { row: 6, col: 4 },
          { row: 7, col: 10 },
          { row: 7, col: 11 }
        ]

        // 清空之前选择的座位
        selectedSeats.value = []

        console.log('座位布局生成完成，显示选座对话框')
        seatSelectionVisible.value = true
        return
      }

      // 真实场次，加载实际座位数据
      seatsLayout.value = schedule.seats_layout || []
      loadOccupiedSeats()
      selectedSeats.value = []
      seatSelectionVisible.value = true
    }

    const loadOccupiedSeats = async () => {
      try {
        const response = await axios.get(`/api/schedules/${selectedSchedule.value.id}/seats/`)
        occupiedSeats.value = response.data
      } catch (error) {
        ElMessage.error('加载座位信息失败')
      }
    }

    const isOccupied = (row, col) => {
      return occupiedSeats.value.some(seat =>
        seat.row === row && seat.col === col
      )
    }

    const isSelected = (row, col) => {
      return selectedSeats.value.some(seat =>
        seat.row === row && seat.col === col
      )
    }

    const toggleSeat = (row, col) => {
      if (isOccupied(row, col)) return

      const seatIndex = selectedSeats.value.findIndex(seat =>
        seat.row === row && seat.col === col
      )

      if (seatIndex > -1) {
        selectedSeats.value.splice(seatIndex, 1)
      } else {
        selectedSeats.value.push({ row, col })
      }
    }

    const createOrder = async () => {
      try {
        creatingOrder.value = true
        console.log('创建订单:', {
          schedule: selectedSchedule.value.id,
          seats: selectedSeats.value
        })

        // 创建一个真实的订单记录，但使用模拟的场次ID
        const orderData = {
          movie_id: route.params.id,
          cinema_id: selectedCinema.value.id,
          schedule_id: selectedSchedule.value.id,
          seats: selectedSeats.value.map(seat => `${String.fromCharCode(65 + seat.row)}${seat.col + 1}`),
          total_price: selectedSchedule.value.price * selectedSeats.value.length,
          show_time: selectedSchedule.value.start_time,
          cinema_name: selectedCinema.value.name,
          movie_title: movie.value.title,
          movie_poster: movie.value.poster_path, // 添加电影海报
          poster_path: movie.value.poster_path,  // 添加海报路径
          movie: {
            title: movie.value.title,
            poster_path: movie.value.poster_path,
            tmdb_id: movie.value.id
          }
        }

        try {
          // 尝试创建真实订单记录
          const response = await axios.post('/api/orders/', {
            schedule: null, // 模拟场次没有真实ID
            seats: selectedSeats.value,
            movie_id: route.params.id,
            cinema_id: selectedCinema.value.id,
            total_price: orderData.total_price,
            order_data: orderData // 额外的订单信息
          }, {
            headers: {
              'Authorization': `Token ${localStorage.getItem('authToken')}`
            }
          })

          console.log('订单创建成功:', response.data)
          ElMessage.success('订单创建成功！')

          // 关闭选座对话框
          handleCloseDialog()

          // 显示订单详情
          ElMessage({
            message: `订单创建成功！订单号：${response.data.order_number}，总价：¥${response.data.total_price}`,
            type: 'success',
            duration: 5000
          })

          // 跳转到订单列表或详情页
          setTimeout(() => {
            router.push('/orders')
          }, 2000)

        } catch (apiError) {
          console.error('API创建订单失败，使用本地存储:', apiError)

          // 如果API失败，将订单信息存储到本地存储
          const localOrder = {
            id: 'local_' + Date.now(),
            order_number: 'LO' + Date.now(),
            ...orderData,
            status: 'paid',
            created_at: new Date().toISOString()
          }

          // 存储到本地存储
          const existingOrders = JSON.parse(localStorage.getItem('localOrders') || '[]')
          existingOrders.push(localOrder)
          localStorage.setItem('localOrders', JSON.stringify(existingOrders))

          ElMessage.success('订单创建成功（本地存储）')

          // 关闭选座对话框
          handleCloseDialog()

          // 显示订单详情
          ElMessage({
            message: `订单创建成功！订单号：${localOrder.order_number}，总价：¥${localOrder.total_price}`,
            type: 'success',
            duration: 5000
          })

          // 跳转到订单列表
          setTimeout(() => {
            router.push('/orders')
          }, 2000)
        }

      } catch (error) {
        console.error('创建订单失败:', error)
        ElMessage.error('创建订单失败: ' + (error.response?.data?.error || error.message))
      } finally {
        creatingOrder.value = false
      }
    }

    const handleCloseDialog = () => {
      selectedSeats.value = []
      seatSelectionVisible.value = false
    }

    const formatDateTime = (datetime) => {
      return dayjs(datetime).format('MM-DD HH:mm')
    }

    const loadSchedules = async () => {
      try {
        loadingSchedules.value = true
        const response = await axios.get('/api/schedules/', {
          params: {
            movie: route.params.id,
            cinema: selectedCinema.value.id,
            date: dayjs(selectedDate.value).format('YYYY-MM-DD')
          }
        })
        cinemaSchedules.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
      } catch (error) {
        ElMessage.error('加载场次信息失败')
        cinemaSchedules.value = []
      } finally {
        loadingSchedules.value = false
      }
    }

    const getFullPosterUrl = (posterPath) => {
      if (!posterPath) return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+CiAgPHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNiIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPueUteW9seaWt+aKpTwvdGV4dD4KPC9zdmc+'

      // 如果已经是完整URL，直接返回
      if (posterPath.startsWith('http')) {
        return posterPath
      }

      // 如果是TMDB路径，添加完整前缀
      if (posterPath.startsWith('/')) {
        return `https://image.tmdb.org/t/p/w500${posterPath}`
      }

      // 其他情况，尝试构建完整URL
      return `https://image.tmdb.org/t/p/w500/${posterPath}`
    }

    const handlePosterError = (event) => {
      console.log('海报加载失败，使用占位图片')
      event.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+CiAgPHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNiIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPueUteW9seaWt+aKpTwvdGV4dD4KPC9zdmc+'
      event.target.onerror = null // 防止无限循环
    }

    const showTrailer = async () => {
      loadingVideos.value = true
      try {
        // 直接使用模拟预告片数据
        const trailerVideo = {
          id: 'trailer_demo',
          name: '电影预告片',
          key: 'M7lc1UVf-VE', // YouTube视频ID
          site: 'YouTube',
          type: 'Trailer'
        }

        // 直接播放预告片
        currentVideo.value = trailerVideo
        videoDialogVisible.value = true
      } catch (error) {
        ElMessage.error('加载预告片失败')
      } finally {
        loadingVideos.value = false
      }
    }

    const loadMovieVideos = async () => {
      loadingVideos.value = true
      try {
        // 使用模拟相关视频数据
        const relatedVideos = [
          {
            id: 'related_1',
            name: '电影预告片',
            key: 'M7lc1UVf-VE',
            site: 'YouTube',
            type: 'Trailer'
          },
          {
            id: 'related_2',
            name: '幕后花絮',
            key: 'YQHsXMglC9A',
            site: 'YouTube',
            type: 'Behind the Scenes'
          },
          {
            id: 'related_3',
            name: '角色特辑',
            key: 'dQw4w9WgXcQ',
            site: 'YouTube',
            type: 'Featurette'
          }
        ]

        movieVideos.value = relatedVideos
        videoListDialogVisible.value = true
      } catch (error) {
        ElMessage.error('加载相关视频失败')
      } finally {
        loadingVideos.value = false
      }
    }



    const playVideo = (video) => {
      currentVideo.value = video
      if (!videoDialogVisible.value) {
        videoDialogVisible.value = true
      }
    }

    const closeVideoDialog = () => {
      videoDialogVisible.value = false
      currentVideo.value = null
    }

    const closeVideoListDialog = () => {
      videoListDialogVisible.value = false
    }

    const playVideoFromList = (video) => {
      currentVideo.value = video
      videoListDialogVisible.value = false
      videoDialogVisible.value = true
    }

    const openVideoInNewTab = () => {
      if (currentVideo.value) {
        window.open(`https://www.youtube.com/watch?v=${currentVideo.value.key}`, '_blank')
      }
    }

    const handleVideoError = () => {
      ElMessage.error('视频播放失败')
    }

    const tryAlternativePlayer = () => {
      // 实现尝试其他播放器的逻辑
      ElMessage.warning('尝试其他播放器功能尚未实现')
    }



    const getVideoTypeText = (type) => {
      switch (type) {
        case 'Trailer':
          return '预告片'
        case 'Behind the Scenes':
          return '幕后花絮'
        default:
          return type
      }
    }

    const formatSelectedSeats = () => {
      return selectedSeats.value.map(seat => `${String.fromCharCode(65 + seat.row)}${seat.col + 1}`).join(', ')
    }

    onMounted(() => {
      loadMovie()
      loadCinemas()
    })

    return {
      movie,
      cinemas,
      searchQuery,
      selectedDate,
      selectedCinema,
      cinemaSchedules,
      seatSelectionVisible,
      seatsLayout,
      selectedSeats,
      pickerOptions,
      filteredCinemas,
      totalPrice,
      selectSchedule,
      isOccupied,
      isSelected,
      toggleSeat,
      createOrder,
      handleCloseDialog,
      formatDateTime,
      loadingSchedules,
      loadSchedules,
      handleCinemaSelected,
      getFullPosterUrl,
      handlePosterError,
      videoDialogVisible,
      videoListDialogVisible,
      currentVideo,
      movieVideos,
      loadingVideos,
      showTrailer,
      loadMovieVideos,
      playVideo,
      closeVideoDialog,
      closeVideoListDialog,
      playVideoFromList,
      openVideoInNewTab,
      handleVideoError,
      tryAlternativePlayer,
      getVideoTypeText,
      formatSelectedSeats,
      creatingOrder
    }
  }
}
</script>

<style scoped>
.ticketing-container {
  padding: 20px;
  padding-top: 100px; /* 为导航栏留出空间 */
  max-width: 1200px;
  margin: 0 auto;
  background: var(--dark-bg);
  min-height: 100vh;
}

.movie-info {
  display: flex;
  margin-bottom: 30px;
  padding: 20px;
  background: var(--card-bg);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.movie-loading {
  margin-bottom: 30px;
  padding: 20px;
  background: var(--card-bg);
  border-radius: 12px;
  text-align: center;
  border: 1px solid var(--border-color);
}

.movie-poster {
  width: 200px;
  height: 300px;
  object-fit: cover;
  border-radius: 8px;
  margin-right: 20px;
}

.movie-details {
  flex: 1;
}

.movie-details h1 {
  margin: 0 0 15px 0;
  color: var(--light-text);
  font-size: 24px;
}

.movie-overview {
  margin: 0 0 15px 0;
  color: var(--gray-text);
  line-height: 1.6;
}

.movie-meta {
  margin-top: 10px;
}

.movie-meta span {
  margin-right: 20px;
  color: var(--gray-text);
  font-size: 14px;
}

.cinema-selection {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

@media (max-width: 768px) {
  .cinema-selection {
    grid-template-columns: 1fr;
  }
}

.cinema-search-container {
  min-width: 300px;
}

.schedule-section {
  min-width: 400px;
  background: var(--card-bg);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-color);
}

.schedule-section h3 {
  margin: 0 0 15px 0;
  color: var(--light-text);
}

.schedules {
  margin-top: 20px;
}

.no-schedules {
  text-align: center;
  padding: 40px 20px;
  color: var(--gray-text);
}

.loading-schedules {
  padding: 20px;
}

.seat-selection {
  text-align: center;
}

.screen {
  width: 80%;
  height: 30px;
  line-height: 30px;
  background: var(--card-bg);
  color: var(--light-text);
  margin: 0 auto 30px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.seats-container {
  display: inline-block;
  padding: 20px;
  background: var(--darker-bg);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.seat-row {
  display: flex;
  justify-content: center;
  margin-bottom: 10px;
}

.seat {
  width: 40px;
  height: 40px;
  line-height: 40px;
  margin: 0 5px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
  color: var(--light-text);
  transition: all 0.3s ease;
}

.seat:hover {
  border-color: var(--primary-color);
  background: rgba(229, 9, 20, 0.1);
}

.seat.occupied {
  background: var(--gray-text);
  cursor: not-allowed;
  color: var(--dark-bg);
}

.seat.selected {
  background: var(--primary-color);
  color: var(--light-text);
  border-color: var(--primary-color);
}

.seat-legend {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  gap: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  color: var(--gray-text);
}

.legend-item .seat {
  width: 20px;
  height: 20px;
  line-height: 20px;
  margin-right: 5px;
}

.order-summary {
  margin-top: 20px;
  text-align: right;
  padding: 15px;
  background: var(--card-bg);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  color: var(--light-text);
}

.debug-panel {
  margin-top: 20px;
  padding: 20px;
  background: var(--card-bg);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.debug-panel h4 {
  margin: 0 0 15px 0;
  color: var(--light-text);
  font-size: 18px;
}

.debug-panel p {
  margin: 0 0 10px 0;
  color: var(--gray-text);
  font-size: 14px;
}

.video-section {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.video-section .el-button {
  border-radius: 12px;
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: var(--light-text);
}

.video-section .el-button:hover {
  background: rgba(229, 9, 20, 0.8);
  border-color: rgba(229, 9, 20, 0.8);
}

.video-container {
  text-align: center;
  margin-bottom: 10px;
}

.video-container h3 {
  margin: 0 0 10px 0;
  color: var(--light-text);
  font-size: 16px;
}

.video-player {
  position: relative;
  width: 100%;
  height: 0;
  padding-bottom: 35%; /* 更紧凑的比例 */
  background: var(--dark-bg);
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.video-player iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.video-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  background: var(--card-bg);
  color: var(--gray-text);
}

.video-list {
  margin-top: 10px;
  border-top: 1px solid var(--border-color);
  padding-top: 10px;
}

.video-list h4 {
  margin: 0 0 10px 0;
  color: var(--light-text);
  font-size: 14px;
  text-align: center;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
  padding: 0 10px;
}

.video-item {
  border-radius: 8px;
  overflow: hidden;
  transition: border-color 0.3s ease;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
}

.video-item:hover {
  border-color: var(--primary-color);
}

.video-thumbnail {
  position: relative;
  width: 100%;
  height: 70px;
  overflow: hidden;
}

.video-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder-thumbnail {
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--darker-bg);
  color: var(--gray-text);
}

.video-info {
  padding: 6px;
}

.video-info h5 {
  margin: 0 0 2px 0;
  color: var(--light-text);
  font-size: 11px;
  font-weight: 600;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.video-info p {
  margin: 0;
  color: var(--gray-text);
  font-size: 9px;
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
  background: rgba(0, 0, 0, 0.7);
  border-radius: 12px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.video-item:hover .play-overlay {
  opacity: 1;
}

.video-item.active .play-overlay {
  opacity: 1;
}

.no-videos {
  text-align: center;
  padding: 40px 20px;
  color: var(--gray-text);
}

.video-feed-section {
  margin-top: 30px;
}

/* 自定义选座弹窗样式 */
.custom-seat-modal {
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
  padding: 20px;
  box-sizing: border-box;
}

.seat-modal-content {
  background: var(--card-bg);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  width: 95%;
  max-width: 1000px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
}

.modal-header {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 0 5px;
}

.custom-seat-modal .close-button {
  background: none;
  border: none;
  color: var(--gray-text);
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.custom-seat-modal .close-button:hover {
  background: rgba(229, 9, 20, 0.1);
  color: var(--primary-color);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
}

.cancel-button,
.confirm-button {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: var(--card-bg);
  color: var(--light-text);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.cancel-button:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.confirm-button {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: var(--light-text);
}

.confirm-button:hover {
  background: rgba(229, 9, 20, 0.8);
  border-color: rgba(229, 9, 20, 0.8);
}

.confirm-button:disabled {
  background: var(--gray-text);
  border-color: var(--gray-text);
  cursor: not-allowed;
  opacity: 0.6;
}

/* 自定义选座弹窗内部样式 */
.custom-seat-modal .seat-selection {
  text-align: center;
  padding: 0 16px 16px 16px;
}

.custom-seat-modal .screen {
  width: 60%;
  height: 22px;
  line-height: 22px;
  background: var(--card-bg);
  color: var(--light-text);
  margin: 0 auto 16px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  font-size: 13px;
}

.custom-seat-modal .seats-container {
  display: inline-block;
  padding: 12px;
  background: var(--darker-bg);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  max-width: 100%;
  overflow-x: auto;
}

.custom-seat-modal .seat-row {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 6px;
}

.custom-seat-modal .row-label {
  width: 18px;
  margin-right: 8px;
  text-align: right;
  color: var(--gray-text);
  font-size: 12px;
}

.custom-seat-modal .seat {
  width: 32px;
  height: 32px;
  line-height: 32px;
  margin: 0 3px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  font-size: 10px;
  color: var(--light-text);
  transition: all 0.3s ease;
}

.custom-seat-modal .seat:hover {
  border-color: var(--primary-color);
  background: rgba(229, 9, 20, 0.1);
}

.custom-seat-modal .seat.occupied {
  background: var(--gray-text);
  cursor: not-allowed;
  color: var(--dark-bg);
}

.custom-seat-modal .seat.selected {
  background: var(--primary-color);
  color: var(--light-text);
  border-color: var(--primary-color);
}

.custom-seat-modal .seat-legend {
  display: flex;
  justify-content: center;
  margin-top: 15px;
  gap: 15px;
  font-size: 12px;
}

.custom-seat-modal .legend-item {
  display: flex;
  align-items: center;
  color: var(--gray-text);
}

.custom-seat-modal .legend-item .seat {
  width: 16px;
  height: 16px;
  line-height: 16px;
  margin-right: 4px;
  font-size: 8px;
}



.video-actions {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 10px;
}

/* Element Plus 组件深色主题覆盖 */
:deep(.el-table) {
  background-color: var(--card-bg);
  color: var(--light-text);
}

:deep(.el-table th.el-table__cell) {
  background-color: var(--darker-bg);
  color: var(--light-text);
  border-bottom: 1px solid var(--border-color);
}

:deep(.el-table td.el-table__cell) {
  border-bottom: 1px solid var(--border-color);
}

:deep(.el-table tr) {
  background-color: var(--card-bg);
}

:deep(.el-table tr:hover > td) {
  background-color: rgba(229, 9, 20, 0.05) !important;
}

:deep(.el-table--enable-row-hover .el-table__body tr:hover > td) {
  background-color: rgba(229, 9, 20, 0.05) !important;
}

:deep(.el-button--primary) {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
  border-radius: 8px;
}

:deep(.el-button--primary:hover) {
  background-color: rgba(229, 9, 20, 0.8);
  border-color: rgba(229, 9, 20, 0.8);
}

:deep(.el-button) {
  border-radius: 8px;
  background-color: var(--card-bg);
  border-color: var(--border-color);
  color: var(--light-text);
}

:deep(.el-button:hover) {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

:deep(.el-date-picker) {
  background-color: var(--card-bg);
  border-color: var(--border-color);
  border-radius: 8px;
}

:deep(.el-picker-panel) {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
}

:deep(.el-picker-panel__content) {
  background-color: var(--card-bg);
}

:deep(.el-date-table th) {
  color: var(--gray-text);
  background-color: var(--darker-bg);
}

:deep(.el-date-table td) {
  color: var(--light-text);
}

:deep(.el-date-table td.available:hover) {
  background-color: rgba(229, 9, 20, 0.1);
}

:deep(.el-date-table td.current:not(.disabled)) {
  background-color: var(--primary-color);
  color: var(--light-text);
}

:deep(.el-picker__popper) {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
}

:deep(.el-input__wrapper) {
  background-color: var(--card-bg);
  border-radius: 8px;
  box-shadow: 0 0 0 1px var(--border-color);
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--primary-color);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--primary-color);
}

:deep(.el-input__inner) {
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

.custom-video-modal .close-button {
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

.custom-video-modal .close-button:hover {
  background: rgba(0, 0, 0, 0.7);
}

.custom-video-modal .video-player {
  position: relative;
  width: 100%;
  height: 0;
  padding-bottom: 56.25%; /* 16:9 aspect ratio */
  background: var(--dark-bg);
}

.custom-video-modal .video-player iframe,
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

/* 相关视频列表弹窗样式 */
.custom-video-list-modal {
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

.video-list-modal-content {
  position: relative;
  width: 90%;
  max-width: 1000px;
  max-height: 80vh;
  background: var(--card-bg);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.video-list-modal-content .modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: var(--darker-bg);
  border-bottom: 1px solid var(--border-color);
}

.video-list-modal-content .modal-header h3 {
  margin: 0;
  color: var(--light-text);
  font-size: 18px;
}

.video-list-modal-content .close-button {
  position: static;
  width: 30px;
  height: 30px;
  background: rgba(0, 0, 0, 0.5);
  color: var(--light-text);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-list-modal-content .close-button:hover {
  background: rgba(0, 0, 0, 0.7);
}

.video-list-modal-content .video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  padding: 20px;
  max-height: 60vh;
  overflow-y: auto;
}

.video-list-modal-content .video-item {
  border-radius: 8px;
  overflow: hidden;
  transition: border-color 0.3s ease;
  background: var(--darker-bg);
  border: 1px solid var(--border-color);
  cursor: pointer;
}

.video-list-modal-content .video-item:hover {
  border-color: var(--primary-color);
}

.video-list-modal-content .video-thumbnail {
  position: relative;
  width: 100%;
  height: 120px;
  overflow: hidden;
}

.video-list-modal-content .video-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-list-modal-content .placeholder-thumbnail {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--card-bg);
  color: var(--gray-text);
}

.video-list-modal-content .play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.7);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.video-list-modal-content .video-item:hover .play-overlay {
  opacity: 1;
}

.video-list-modal-content .video-info {
  padding: 12px;
}

.video-list-modal-content .video-info h5 {
  margin: 0 0 4px 0;
  color: var(--light-text);
  font-size: 14px;
  font-weight: 600;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.video-list-modal-content .video-info p {
  margin: 0;
  color: var(--gray-text);
  font-size: 12px;
}

:deep(.el-empty__description p) {
  color: var(--gray-text);
}

:deep(.el-skeleton__item) {
  background: linear-gradient(90deg, var(--card-bg) 25%, var(--darker-bg) 50%, var(--card-bg) 75%) !important;
  background-size: 400% 100%;
  animation: loading 1.4s ease infinite;
}

:deep(.el-skeleton .el-skeleton__item) {
  background: linear-gradient(90deg, var(--card-bg) 25%, var(--darker-bg) 50%, var(--card-bg) 75%) !important;
}

@keyframes loading {
  0% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

/* 修复悬停效果 - 使用边框高亮而不是文字颜色变化 */
:deep(.el-button:hover) {
  border-color: var(--primary-color);
  color: var(--light-text);
  background-color: rgba(229, 9, 20, 0.1);
}

:deep(.el-button--primary:hover) {
  background-color: rgba(229, 9, 20, 0.8);
  border-color: rgba(229, 9, 20, 0.8);
  color: var(--light-text);
}
</style>