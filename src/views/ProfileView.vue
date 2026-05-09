<template>
  <div class="profile-page">
    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMessage" class="error-alert">
      {{ errorMessage }}
      <button @click="fetchProfile">重试</button>
    </div>

    <!-- 导航菜单 -->
    <nav class="profile-nav">
      <button @click="activeTab = 'info'" :class="{active: activeTab === 'info'}">基本信息</button>
      <button @click="activeTab = 'orders'" :class="{active: activeTab === 'orders'}">我的订单</button>
      <button @click="activeTab = 'reviews'" :class="{active: activeTab === 'reviews'}">我的评价</button>
      <button @click="activeTab = 'collections'" :class="{active: activeTab === 'collections'}">帖子收藏</button>
      <button @click="activeTab = 'posts'" :class="{active: activeTab === 'posts'}">我的帖子</button>
    </nav>

    <!-- 基本信息 -->
    <div v-show="activeTab === 'info'" class="profile-container">
      <div class="profile-cards-wrapper">
        <!-- 用户头像和基本信息卡片 -->
        <div class="profile-card left-card">
          <div class="card-header">
            <h3 class="card-title">
              <i class="icon-user"></i>
              个人资料
            </h3>
          </div>
          <div class="card-content">
            <!-- 头像区域 -->
            <div class="avatar-section">
              <div class="avatar-upload">
                <div class="avatar-wrapper">
                  <img :src="user.avatar || '/default-avatar.png'" class="avatar" />
                  <div class="upload-mask">
                    <i class="icon-camera"></i>
                    <span>更换头像</span>
                  </div>
                  <input
                    type="file"
                    @change="handleAvatarUpload"
                    class="upload-input"
                  />
                </div>
              </div>
              <div class="user-info">
                <h2 class="username">{{ user.username || '未设置用户名' }}</h2>
                <p class="user-email">{{ user.email }}</p>
                <div class="user-stats">
                  <div class="stat-item">
                    <span class="stat-number">{{ reviews.length }}</span>
                    <span class="stat-label">评价</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-number">{{ collections.length }}</span>
                    <span class="stat-label">收藏</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 个人信息编辑卡片 -->
        <div class="profile-card right-card">
          <div class="card-header">
            <h3 class="card-title">
              <i class="icon-edit"></i>
              编辑信息
            </h3>
          </div>
          <div class="card-content">
            <div class="form-section">
              <!-- 个人简介 -->
              <div class="form-group">
                <div class="form-header">
                  <label class="form-label">个人简介</label>
                  <button
                    class="save-btn"
                    @click="updateProfile"
                    :disabled="!hasChanges"
                  >
                    <i class="icon-save"></i>
                    保存
                  </button>
                </div>
                <textarea
                  v-model="user.bio"
                  placeholder="介绍一下你自己..."
                  class="form-textarea"
                  rows="3"
                ></textarea>
              </div>

              <!-- 基本信息表单 -->
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">用户名</label>
                  <input
                    v-model="user.username"
                    @blur="updateProfile"
                    class="form-input"
                    placeholder="请输入用户名"
                  />
                </div>
                <div class="form-group">
                  <label class="form-label">手机号</label>
                  <input
                    v-model="user.phone"
                    @blur="updateProfile"
                    class="form-input"
                    placeholder="请输入手机号"
                  />
                </div>
              </div>

              <!-- 只读信息 -->
              <div class="readonly-section">
                <div class="readonly-item">
                  <label class="form-label">邮箱地址</label>
                  <span class="readonly-value">{{ user.email }}</span>
                </div>
                <div class="readonly-item">
                  <label class="form-label">注册时间</label>
                  <span class="readonly-value">{{ formatDate(user.date_joined) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 我的订单 -->
    <div v-show="activeTab === 'orders'" class="orders-section">
      <h3><i class="icon-shopping-cart"></i> 我的订单（{{ orders.length }}）</h3>

      <div v-if="isOrdersLoading" class="loading-indicator">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="ordersError" class="error-message">
        {{ ordersError }}
        <button @click="loadUserOrders">重试</button>
      </div>

      <div v-else-if="orders.length > 0" class="order-list">
        <div
          v-for="order in orders"
          :key="order.id"
          class="order-card"
        >
          <div class="order-header">
            <div class="order-info">
              <h4>
                <span class="order-status" :class="getStatusClass(order.status)">
                  {{ getStatusText(order.status) }}
                </span>
                订单号：{{ order.order_number }}
              </h4>
            </div>
            <div class="order-price">
              ¥{{ order.total_price }}
            </div>
          </div>

          <div class="order-content">
            <div class="movie-info">
              <div class="movie-poster">
                <img
                  :src="getMoviePoster(order)"
                  :alt="order.movie_title || '电影海报'"
                  @error="handlePosterError"
                >
              </div>
              <div class="movie-details">
                <h5>{{ order.movie_title || '未知电影' }}</h5>
                <p>影院：{{ order.cinema_name || '未知影院' }}</p>
                <p v-if="order.show_time">场次：{{ formatDateTime(order.show_time) }}</p>
                <p v-if="order.seats && order.seats.length">座位：{{ formatSeats(order.seats) }}</p>
              </div>
            </div>
          </div>

          <div class="order-footer">
            <span class="order-date">下单时间：{{ formatDate(order.created_at) }}</span>
            <div class="order-actions">
              <button
                v-if="order.status === 'paid'"
                @click="refundOrder(order)"
                class="btn-refund"
              >
                申请退票
              </button>
              <button
                v-if="order.status === 'paid'"
                @click="changeOrder(order)"
                class="btn-change"
              >
                申请改签
              </button>
              <button
                @click="viewOrderDetail(order)"
                class="btn-detail"
              >
                查看详情
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <i class="icon-shopping-cart"></i>
        <p>暂无订单记录</p>
        <router-link to="/movies" class="btn-primary">去看电影</router-link>
      </div>
    </div>

    <!-- 我的评价 -->
    <div v-show="activeTab === 'reviews'" class="reviews-container">
      <!-- 页面标题 -->
      <div class="reviews-header">
        <h3 class="reviews-title">
          <i class="icon-star"></i>
          我的评价
        </h3>
        <div class="reviews-count">共 {{ reviews.length }} 条评价</div>
      </div>

      <!-- 评价列表 -->
      <div v-if="reviews.length > 0" class="reviews-list">
        <div v-for="review in reviews" :key="review.id" class="review-card">
          <!-- 电影海报 -->
          <div class="movie-poster-section">
            <img
              :src="review.movie?.poster_path
                ? `https://image.tmdb.org/t/p/w200${review.movie.poster_path}`
                : '/placeholder-poster.jpg'"
              @error="handlePosterError"
              class="movie-poster"
              @click="goToMovieDetail(review.movie?.tmdb_id)"
            >
          </div>

          <!-- 评价内容 -->
          <div class="review-content">
            <div class="review-header">
              <div class="title-rating-section">
                <h4 class="movie-title" @click="goToMovieDetail(review.movie?.tmdb_id)">
                  {{ review.movie?.title || '未知电影' }}
                </h4>
                <div class="rating-badge">
                  <span class="rating-score">{{ review.rating }}</span>
                  <span class="rating-max">/10</span>
                </div>
              </div>
              <div class="review-date">{{ formatDate(review.created_at) }}</div>
            </div>

            <div class="review-text">
              {{ review.content || '暂无评价内容' }}
            </div>

            <div class="review-actions">
              <button @click="editReview(review)" class="action-btn edit-btn">
                <i class="icon-edit"></i>
                编辑
              </button>
              <button @click="deleteReview(review)" class="action-btn delete-btn">
                <i class="icon-trash"></i>
                删除
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <div class="empty-icon">
          <i class="icon-star"></i>
        </div>
        <h3>还没有评价任何电影</h3>
        <p>去发现一些精彩的电影并分享你的观后感吧！</p>
        <router-link to="/" class="discover-btn">
          <i class="icon-search"></i>
          发现电影
        </router-link>
      </div>
    </div>

    <!-- 帖子收藏 -->
    <div v-show="activeTab === 'collections'" class="collections-section">
      <div class="collections-container">
        <div class="collections-header">
          <h3 class="collections-title">
            <i class="icon-star"></i>
            帖子收藏
          </h3>
          <span class="collections-count" v-if="!isCollectionsLoading">共收藏了 {{ collections.length }} 个帖子</span>
        </div>

        <!-- 加载状态 -->
        <div v-if="isCollectionsLoading" class="loading-container">
          <div class="loading-spinner">
            <div class="spinner"></div>
            <p>正在加载收藏列表...</p>
          </div>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="collectionsError" class="error-message">
          {{ collectionsError }}
          <button @click="fetchCollections" class="retry-btn">重试</button>
        </div>

        <!-- 帖子列表 -->
        <div v-else-if="collections.length > 0" class="collections-list">
          <div
            v-for="post in collections"
            :key="post.id"
            class="collection-card"
            @click="goToPost(post.id)"
          >
            <div class="post-content">
              <div class="post-header">
                <h4 class="post-title">{{ post.title }}</h4>
              </div>
              <p class="post-excerpt">{{ post.content.length > 120 ? post.content.slice(0, 120) + '...' : post.content }}</p>
              <div class="post-meta">
                <span class="meta-item">
                  <svg class="like-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  {{ post.like_count || 0 }}
                </span>
                <span class="meta-item">
                  <svg class="comment-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  {{ post.reply_count || 0 }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <div class="empty-icon">
            <i class="icon-star"></i>
          </div>
          <h3>还没有收藏任何帖子</h3>
          <p>去论坛发现一些有趣的讨论吧！</p>
          <router-link to="/forum" class="discover-btn">
            <i class="icon-search"></i>
            浏览论坛
          </router-link>
        </div>
      </div>
    </div>

    <!-- 我的帖子 -->
    <div v-show="activeTab === 'posts'" class="posts-section">
      <div class="posts-container">
        <div class="posts-header">
          <h3 class="posts-title">
            <i class="icon-file"></i>
            我的帖子
          </h3>
          <span class="posts-count" v-if="!isPostsLoading">共发布了 {{ userPosts.length }} 个帖子</span>
        </div>

        <!-- 加载状态 -->
        <div v-if="isPostsLoading" class="loading-container">
          <div class="loading-spinner">
            <div class="spinner"></div>
            <p>正在加载帖子列表...</p>
          </div>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="postsError" class="error-message">
          {{ postsError }}
          <button @click="loadUserPosts" class="retry-btn">重试</button>
        </div>

        <!-- 帖子列表 -->
        <div v-else-if="userPosts.length > 0" class="posts-list">
          <div
            v-for="post in userPosts"
            :key="post.id"
            class="user-post-card"
            @click="goToPost(post.id)"
          >
            <div class="user-post-content">
              <div class="user-post-header">
                <h4 class="user-post-title">{{ post.title }}</h4>
                <button
                  @click.stop="deleteUserPost(post)"
                  class="delete-post-btn"
                  title="删除帖子"
                >
                  <svg class="delete-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6h14zM10 11v6M14 11v6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
              </div>
              <p class="user-post-excerpt">{{ post.content.length > 120 ? post.content.slice(0, 120) + '...' : post.content }}</p>
              <div class="user-post-meta">
                <span class="meta-item">
                  <svg class="time-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                    <polyline points="12,6 12,12 16,14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  {{ formatDate(post.created_at) }}
                </span>
                <span class="meta-item">
                  <svg class="like-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  {{ post.like_count || 0 }}
                </span>
                <span class="meta-item">
                  <svg class="comment-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  {{ post.reply_count || 0 }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <div class="empty-icon">
            <i class="icon-file"></i>
          </div>
          <h3>还没有发布任何帖子</h3>
          <p>去论坛分享你的想法和见解吧！</p>
          <router-link to="/forum/create" class="discover-btn">
            <i class="icon-edit"></i>
            发布新帖子
          </router-link>
        </div>
      </div>
    </div>

    <!-- 自定义改签弹窗 -->
    <div v-if="changeOrderModalVisible" class="custom-change-modal" @click="closeChangeModal">
      <div class="change-modal-content" @click.stop>
        <div class="modal-header">
          <h3>申请改签</h3>
          <button class="close-button" @click="closeChangeModal">×</button>
        </div>
        <div class="modal-body">
          <div class="current-schedule">
            <p class="current-label">当前场次：</p>
            <p class="current-time">{{ formatDateTime(currentChangeOrder?.show_time || currentChangeOrder?.schedule_time) }}</p>
          </div>

          <div class="form-group">
            <label class="form-label">选择新日期</label>
            <input
              type="date"
              v-model="newScheduleDate"
              class="form-input"
              :min="new Date().toISOString().split('T')[0]"
            >
          </div>

          <div class="form-group">
            <label class="form-label">选择新时间</label>
            <select v-model="newScheduleTime" class="form-select">
              <option value="">请选择时间</option>
              <option value="09:00">09:00 上午场</option>
              <option value="11:30">11:30 上午场</option>
              <option value="14:00">14:00 下午场</option>
              <option value="16:30">16:30 下午场</option>
              <option value="19:00">19:00 晚上场</option>
              <option value="21:30">21:30 晚上场</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-button" @click="closeChangeModal">取消</button>
          <button
            class="confirm-button"
            @click="confirmChangeOrder"
            :disabled="!newScheduleDate || !newScheduleTime"
          >
            确认改签
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑评价对话框 -->
    <dialog ref="editDialog" class="edit-dialog">
      <div class="dialog-content">
        <div class="dialog-header">
          <h3 class="dialog-title">编辑评价</h3>
          <button @click="closeDialog" class="close-btn">
            ×
          </button>
        </div>

        <div class="dialog-body">
          <!-- 评分选择 -->
          <div class="rating-section">
            <label class="rating-label">评分</label>
            <div class="rating-selector">
              <span
                v-for="n in 10"
                :key="n"
                @click="editingReview.rating = n"
                :class="['rating-star', {active: editingReview.rating >= n}]"
              >
                ★
              </span>
              <span class="rating-text">{{ editingReview.rating }}/10</span>
            </div>
          </div>

          <!-- 评价内容 -->
          <div class="content-section">
            <label class="content-label">评价内容</label>
            <textarea
              v-model="editingReview.content"
              class="content-textarea"
              placeholder="分享你对这部电影的看法..."
              rows="4"
            ></textarea>
          </div>
        </div>

        <div class="dialog-actions">
          <button @click="closeDialog" class="btn-cancel">取消</button>
          <button @click="saveReview" class="btn-save">保存修改</button>
        </div>
      </div>
    </dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useToast } from '@/composables/useToast'
import {
  fetchUserProfile,
  updateUserProfile,
  fetchUserReviews,
  updateReview,
  deleteReview as apiDeleteReview,
  fetchUserCollections,
  fetchUserPosts as apiFetchUserPosts, // 重命名导入的函数
  deletePost as apiDeletePost // 重命名导入的函数
} from '@/api/user'

const { showSuccess, showError } = useToast()
const userStore = useUserStore()
const router = useRouter()
const activeTab = ref('info')
const user = ref({})
const originalUser = ref({})
const reviews = ref([])
const settings = ref({})
const editDialog = ref(null)
const editingReview = ref({})
const isLoading = ref(false)
const errorMessage = ref('')
const collections = ref([])
const isCollectionsLoading = ref(false)
const collectionsError = ref('')

// 我的帖子相关状态
const userPosts = ref([])
const isPostsLoading = ref(false)
const postsError = ref('')

// 我的订单相关状态
const orders = ref([])
const isOrdersLoading = ref(false)
const ordersError = ref('')

// 改签弹窗相关状态
const changeOrderModalVisible = ref(false)
const currentChangeOrder = ref(null)
const newScheduleDate = ref('')
const newScheduleTime = ref('')

// 计算属性 - 检测是否有变更
const hasChanges = computed(() => {
  return user.value.username !== originalUser.value.username ||
         user.value.bio !== originalUser.value.bio ||
         user.value.phone !== originalUser.value.phone
})

// 获取用户信息
const fetchProfile = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await fetchUserProfile()
    user.value = response.data
    // 保存原始数据用于变更检测
    originalUser.value = {
      username: response.data.username,
      bio: response.data.bio,
      phone: response.data.phone
    }
    settings.value = {
      notification_prefs: response.data.notification_prefs || 'all',
      theme: response.data.theme || 'light'
    }
  } catch (error) {
    errorMessage.value = '用户信息加载失败，请稍后重试'
    console.error('获取用户信息失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 获取用户评论
const fetchReviews = async () => {
  try {
    const response = await fetchUserReviews()
    reviews.value = response.data.results || response.data
  } catch (error) {
    console.error('获取评价列表失败:', error)
    reviews.value = []
  }
}

// 获取用户收藏
const fetchCollections = async () => {
  isCollectionsLoading.value = true
  collectionsError.value = ''
  try {
    const response = await fetchUserCollections()
    collections.value = response.data.results || response.data
  } catch (error) {
    collectionsError.value = '收藏列表加载失败，请重试'
    console.error('获取收藏失败:', error)
  } finally {
    isCollectionsLoading.value = false
  }
}

// 获取用户帖子
const loadUserPosts = async () => {
  isPostsLoading.value = true
  postsError.value = ''
  try {
    const response = await apiFetchUserPosts()
    userPosts.value = response.data.results || response.data
  } catch (error) {
    postsError.value = '帖子列表加载失败，请重试'
    console.error('获取用户帖子失败:', error)
  } finally {
    isPostsLoading.value = false
  }
}

// 处理海报加载错误
const handlePosterError = (e) => {
  console.log('海报加载失败，切换到占位图片')
  // 使用base64编码的占位图片，避免网络请求失败
  e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+CiAgPHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNiIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPueUteW9seaWt+aKpTwvdGV4dD4KPC9zdmc+'
  e.target.onerror = null // 防止无限循环
}

// 更新个人信息
const updateProfile = async () => {
  try {
    const formData = new FormData()
    Object.entries(user.value).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        formData.append(key, value)
      }
    })

    await updateUserProfile(formData)
    showSuccess('个人信息更新成功')
  } catch (error) {
    showError('更新失败，请稍后重试')
    console.error('更新失败:', error)
  }
}

// 头像上传处理
const handleAvatarUpload = async (event) => {
  const file = event.target.files[0]
  if (file) {
    const formData = new FormData()
    formData.append('avatar', file)

    try {
      const response = await updateUserProfile(formData)

      user.value.avatar = response.data.avatar
      userStore.updateAvatar(response.data.avatar)
      userStore.avatarTimestamp = Date.now()
      showSuccess('头像更新成功')
    } catch (error) {
      showError('头像上传失败')
      console.error('头像上传失败:', error)
    }
  }
}

// 删除评论
const deleteReview = async (review) => {
  if (confirm('确定要删除这条评论吗？')) {
    try {
      await apiDeleteReview(review.id)
      reviews.value = reviews.value.filter(r => r.id !== review.id)
      showSuccess('评论已删除')
    } catch (error) {
      showError(`删除失败: ${error.response?.data?.detail || '未知错误'}`)
      console.error('删除失败:', error)
    }
  }
}

// 打开编辑对话框
const editReview = (review) => {
  editingReview.value = { ...review }
  editDialog.value.showModal()
}

// 保存评论修改
const saveReview = async () => {
  if (!editingReview.value.movie?.tmdb_id || !editingReview.value.id) {
    showError('评论数据不完整')
    return
  }

  const payload = {
    content: editingReview.value.content,
    rating: editingReview.value.rating
  }

  try {
    const response = await updateReview(
      editingReview.value.movie.tmdb_id,
      editingReview.value.id,
      payload
    )

    const updatedReview = {
      ...response.data,
      movie: response.data.movie || editingReview.value.movie
    }

    const index = reviews.value.findIndex(r => r.id === updatedReview.id)
    if (index !== -1) {
      reviews.value.splice(index, 1, updatedReview)
    }

    showSuccess('评价更新成功')
    closeDialog()
  } catch (error) {
    console.error('更新失败详情:', error.response?.data)
    const errorMsg = error.response?.data?.content?.[0] ||
                    error.response?.data?.rating?.[0] ||
                    '数据校验失败'
    showError(`更新失败: ${errorMsg}`)
  }
}

// 关闭对话框
const closeDialog = () => {
  editDialog.value.close()
}

// 跳转到电影详情页
const goToMovieDetail = (tmdbId) => {
  if (tmdbId) {
    router.push(`/movie/${tmdbId}`)
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知时间'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return '未知时间'
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 更新设置
const updateSettings = async () => {
  try {
    await axios.patch('/api/settings/', settings.value, {
      headers: {
        Authorization: `Token ${localStorage.getItem('authToken')}`
      }
    })
    showSuccess('设置已更新')
  } catch (error) {
    showError('更新设置失败')
    console.error('更新设置失败:', error)
  }
}

// 删除帖子
const deleteUserPost = async (post) => {
  if (confirm(`确定要删除帖子《${post.title}》吗？此操作不可撤销。`)) {
    try {
      await apiDeletePost(post.id)
      userPosts.value = userPosts.value.filter(p => p.id !== post.id)
      showSuccess('帖子已成功删除')
    } catch (error) {
      showError(`删除失败: ${error.response?.data?.detail || '未知错误'}`)
      console.error('删除帖子失败:', error)
    }
  }
}

// 跳转到帖子详情
const goToPost = (postId) => {
  if (postId) {
    window.open(`/forum/post/${postId}`, '_blank')
  }
}

// 获取用户订单
const loadUserOrders = async () => {
  isOrdersLoading.value = true
  ordersError.value = ''
  try {
    let finalOrders = []

    // 首先尝试从API获取订单
    try {
      const response = await axios.get('/api/orders/', {
        headers: {
          'Authorization': `Token ${localStorage.getItem('authToken')}`
        }
      })
      let apiOrders = response.data.results || response.data || []
      console.log('API订单数据:', apiOrders)

      // 为API订单补充电影信息（如果缺失）
      apiOrders = apiOrders.map(order => {
        if (!order.movie && order.movie_title) {
          // 如果没有movie对象但有movie_title，创建一个基本的movie对象
          order.movie = {
            title: order.movie_title,
            poster_path: order.movie_poster || null
          }
        }
        return order
      })

      finalOrders = apiOrders
    } catch (apiError) {
      console.log('API获取订单失败，使用本地存储:', apiError)
      finalOrders = []
    }

    // 获取本地存储的订单（包含状态更新）
    const allLocalOrders = JSON.parse(localStorage.getItem('localOrders') || '[]')
    // 过滤出当前用户的本地订单
    const currentUserId = userStore.user?.id
    const localOrders = currentUserId ? allLocalOrders.filter(order => 
      order.user_id === currentUserId || order.user === currentUserId
    ) : []
    console.log('本地存储订单数据:', localOrders)

    // 合并API订单和本地订单，本地订单优先
    const mergedOrders = []

    // 首先添加所有API订单
    finalOrders.forEach(apiOrder => {
      // 检查本地存储中是否有相同订单的更新
      const localUpdate = localOrders.find(localOrder =>
        localOrder.id === apiOrder.id ||
        localOrder.order_number === apiOrder.order_number ||
        (localOrder.id && localOrder.id.toString() === apiOrder.id?.toString())
      )

      if (localUpdate) {
        // 如果本地有更新，使用本地数据覆盖API数据
        console.log(`订单 ${apiOrder.id} 使用本地更新数据:`, localUpdate)
        mergedOrders.push({
          ...apiOrder,
          ...localUpdate,
          // 确保保留API中的一些关键字段
          id: apiOrder.id,
          order_number: apiOrder.order_number || localUpdate.order_number
        })
      } else {
        // 没有本地更新，使用API数据
        mergedOrders.push(apiOrder)
      }
    })

    // 添加纯本地订单（不在API中的订单）
    localOrders.forEach(localOrder => {
      const existsInApi = finalOrders.some(apiOrder =>
        apiOrder.id === localOrder.id ||
        apiOrder.order_number === localOrder.order_number ||
        (apiOrder.id && apiOrder.id.toString() === localOrder.id?.toString())
      )

      if (!existsInApi) {
        // 为本地订单补充电影信息（如果缺失）
        if (!localOrder.movie && localOrder.movie_title) {
          localOrder.movie = {
            title: localOrder.movie_title,
            poster_path: localOrder.movie_poster || localOrder.poster_path || null
          }
        }
        mergedOrders.push(localOrder)
      }
    })

    orders.value = mergedOrders
    console.log('最终合并后的订单数据:', orders.value)

  } catch (error) {
    ordersError.value = '订单列表加载失败，请重试'
    console.error('获取用户订单失败:', error)
  } finally {
    isOrdersLoading.value = false
  }
}

// 获取订单状态样式类
const getStatusClass = (status) => {
  switch (status) {
    case 'paid':
      return 'status-paid'
    case 'pending':
      return 'status-pending'
    case 'cancelled':
      return 'status-cancelled'
    case 'refunded':
      return 'status-refunded'
    default:
      return 'status-unknown'
  }
}

// 获取订单状态文本
const getStatusText = (status) => {
  switch (status) {
    case 'paid':
      return '已支付'
    case 'pending':
      return '待支付'
    case 'cancelled':
      return '已取消'
    case 'refunded':
      return '已退款'
    default:
      return '未知状态'
  }
}

// 格式化日期时间
const formatDateTime = (dateString) => {
  if (!dateString) return '未知时间'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化座位信息
const formatSeats = (seats) => {
  if (!seats || !Array.isArray(seats)) return '未知座位'
  return seats.join(', ')
}

// 获取电影海报
const getMoviePoster = (order) => {
  // 检查多种可能的海报路径
  let posterPath = null

  // 1. 检查 order.movie.poster_path
  if (order.movie && order.movie.poster_path) {
    posterPath = order.movie.poster_path
  }
  // 2. 检查 order.poster_path
  else if (order.poster_path) {
    posterPath = order.poster_path
  }
  // 3. 检查 order.movie_poster
  else if (order.movie_poster) {
    posterPath = order.movie_poster
  }
  // 4. 检查 order.movie_poster_path
  else if (order.movie_poster_path) {
    posterPath = order.movie_poster_path
  }

  // 如果找到海报路径，构建完整URL
  if (posterPath) {
    // 如果已经是完整URL，直接返回
    if (posterPath.startsWith('http')) {
      return posterPath
    }
    // 如果是TMDB路径，构建完整URL
    if (posterPath.startsWith('/')) {
      return `https://image.tmdb.org/t/p/w300${posterPath}`
    }
    // 其他情况，尝试作为TMDB路径处理
    return `https://image.tmdb.org/t/p/w300/${posterPath}`
  }

  // 如果没有找到海报，返回占位图片
  return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+CiAgPHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNiIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPueUteW9seaWt+aKpTwvdGV4dD4KPC9zdmc+'
}

// 申请退票
const refundOrder = async (order) => {
  if (confirm(`确定要申请退票吗？订单号：${order.order_number}`)) {
    try {
      // 直接更新本地存储，不依赖API
      console.log('用户申请退票，更新本地存储')

      // 先立即更新当前显示的订单状态
      const currentOrderIndex = orders.value.findIndex(o => o.id === order.id)
      if (currentOrderIndex !== -1) {
        orders.value[currentOrderIndex].status = 'refunded'
        orders.value[currentOrderIndex].refund_time = new Date().toISOString()
        orders.value[currentOrderIndex].refund_reason = '用户申请退票'
      }

      // 更新本地存储中的订单
      const localOrders = JSON.parse(localStorage.getItem('localOrders') || '[]')
      const orderIndex = localOrders.findIndex(o =>
        o.id === order.id ||
        o.order_number === order.order_number ||
        (o.id && o.id.toString() === order.id?.toString())
      )

      if (orderIndex !== -1) {
        localOrders[orderIndex].status = 'refunded'
        localOrders[orderIndex].refund_time = new Date().toISOString()
        localOrders[orderIndex].refund_reason = '用户申请退票'
        localStorage.setItem('localOrders', JSON.stringify(localOrders))
      } else {
        // 如果在localOrders中找不到，添加新的退票记录
        const refundedOrder = {
          ...order,
          status: 'refunded',
          refund_time: new Date().toISOString(),
          refund_reason: '用户申请退票'
        }
        localOrders.push(refundedOrder)
        localStorage.setItem('localOrders', JSON.stringify(localOrders))
      }

      showSuccess('退票申请已提交，管理员将会处理您的申请')

      // 可选：尝试通过API通知后端（如果API存在）
      try {
        await axios.post(`/api/orders/${order.id}/refund/`, {
          reason: '用户申请退票'
        }, {
          headers: {
            'Authorization': `Token ${localStorage.getItem('authToken')}`
          }
        })
        console.log('API通知成功')
      } catch (apiError) {
        console.log('API通知失败，但本地更新已完成:', apiError)
      }

    } catch (error) {
      console.error('退票申请失败:', error)
      showError('退票申请失败，请重试')
      // 如果失败，恢复原状态
      const currentOrderIndex = orders.value.findIndex(o => o.id === order.id)
      if (currentOrderIndex !== -1) {
        orders.value[currentOrderIndex].status = order.status
        delete orders.value[currentOrderIndex].refund_time
        delete orders.value[currentOrderIndex].refund_reason
      }
    }
  }
}

// 申请改签
const changeOrder = (order) => {
  currentChangeOrder.value = order
  newScheduleDate.value = new Date().toISOString().split('T')[0]
  newScheduleTime.value = ''
  changeOrderModalVisible.value = true
}

// 关闭改签弹窗
const closeChangeModal = () => {
  changeOrderModalVisible.value = false
  currentChangeOrder.value = null
  newScheduleDate.value = ''
  newScheduleTime.value = ''
}

// 确认改签
const confirmChangeOrder = async () => {
  if (!newScheduleDate.value || !newScheduleTime.value) {
    showError('请选择完整的日期和时间')
    return
  }

  const newDateTime = `${newScheduleDate.value} ${newScheduleTime.value}`
  const order = currentChangeOrder.value

  try {
    // 直接更新本地存储，不依赖API
    console.log('用户申请改签，更新本地存储')

    // 先立即更新当前显示的订单状态
    const currentOrderIndex = orders.value.findIndex(o => o.id === order.id)
    if (currentOrderIndex !== -1) {
      orders.value[currentOrderIndex].status = 'changed'
      orders.value[currentOrderIndex].original_schedule_time = orders.value[currentOrderIndex].schedule_time || orders.value[currentOrderIndex].show_time
      orders.value[currentOrderIndex].schedule_time = newDateTime
      orders.value[currentOrderIndex].show_time = newDateTime
      orders.value[currentOrderIndex].change_time = new Date().toISOString()
      orders.value[currentOrderIndex].change_reason = '用户申请改签'
    }

    // 更新本地存储中的订单
    const localOrders = JSON.parse(localStorage.getItem('localOrders') || '[]')
    const orderIndex = localOrders.findIndex(o =>
      o.id === order.id ||
      o.order_number === order.order_number ||
      (o.id && o.id.toString() === order.id?.toString())
    )

    if (orderIndex !== -1) {
      localOrders[orderIndex].status = 'changed'
      localOrders[orderIndex].original_schedule_time = localOrders[orderIndex].schedule_time || localOrders[orderIndex].show_time
      localOrders[orderIndex].schedule_time = newDateTime
      localOrders[orderIndex].show_time = newDateTime
      localOrders[orderIndex].change_time = new Date().toISOString()
      localOrders[orderIndex].change_reason = '用户申请改签'
      localStorage.setItem('localOrders', JSON.stringify(localOrders))
    } else {
      // 如果在localOrders中找不到，添加新的改签记录
      const changedOrder = {
        ...order,
        status: 'changed',
        original_schedule_time: order.schedule_time || order.show_time,
        schedule_time: newDateTime,
        show_time: newDateTime,
        change_time: new Date().toISOString(),
        change_reason: '用户申请改签'
      }
      localOrders.push(changedOrder)
      localStorage.setItem('localOrders', JSON.stringify(localOrders))
    }

    showSuccess('改签申请已提交，管理员将会处理您的申请')
    closeChangeModal()

    // 可选：尝试通过API通知后端（如果API存在）
    try {
      await axios.post(`/api/orders/${order.id}/change/`, {
        new_schedule_time: newDateTime,
        reason: '用户申请改签'
      }, {
        headers: {
          'Authorization': `Token ${localStorage.getItem('authToken')}`
        }
      })
      console.log('API通知成功')
    } catch (apiError) {
      console.log('API通知失败，但本地更新已完成:', apiError)
    }

  } catch (error) {
    console.error('改签申请失败:', error)
    showError('改签申请失败，请重试')
    // 如果失败，恢复原状态
    const currentOrderIndex = orders.value.findIndex(o => o.id === order.id)
    if (currentOrderIndex !== -1) {
      orders.value[currentOrderIndex].status = order.status
      orders.value[currentOrderIndex].schedule_time = order.schedule_time
      orders.value[currentOrderIndex].show_time = order.show_time
      delete orders.value[currentOrderIndex].original_schedule_time
      delete orders.value[currentOrderIndex].change_time
      delete orders.value[currentOrderIndex].change_reason
    }
  }
}

// 查看订单详情
const viewOrderDetail = (order) => {
  // 可以跳转到订单详情页面或显示详情对话框
  router.push(`/orders/${order.id}`)
}

// 初始化加载
onMounted(() => {
  fetchProfile()
  fetchReviews()
  fetchCollections()
  loadUserPosts() // 使用本地函数加载帖子
  loadUserOrders() // 加载订单数据
})
</script>
<style scoped>
/* 个人信息页面样式 */
.profile-page {
  min-height: 100vh;
  background: #141414;
  color: #fff;
  padding: 80px 20px 40px;
}

/* 导航标签 */
.profile-nav {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 30px;
}

.profile-nav button {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 8px 20px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 500;
}

.profile-nav button:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.profile-nav button.active {
  background: #e50914;
  color: #fff;
  border-color: #e50914;
}

/* 个人信息容器 */
.profile-container {
  max-width: 1200px;
  margin: 0 auto;
}

/* 卡片包装器 - 左右布局 */
.profile-cards-wrapper {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 24px;
  align-items: start;
}

/* 个人信息卡片 */
.profile-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  overflow: hidden;
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.1rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.card-title i {
  width: 16px;
  height: 16px;
  background: #e50914;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-title i::before {
  content: '';
  width: 6px;
  height: 6px;
  background: white;
  border-radius: 1px;
}

.card-content {
  padding: 20px;
}

/* 头像区域 */
.avatar-section {
  display: flex;
  align-items: center;
  gap: 24px;
}

.avatar-upload {
  position: relative;
}

.avatar-wrapper {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.avatar-wrapper:hover {
  transform: scale(1.05);
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  color: white;
  font-size: 0.8rem;
}

.avatar-wrapper:hover .upload-mask {
  opacity: 1;
}

.upload-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

/* 用户信息 */
.user-info {
  flex: 1;
}

.username {
  font-size: 1.5rem;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px 0;
}

.user-email {
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 16px 0;
  font-size: 0.9rem;
}

.user-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 1.2rem;
  font-weight: 700;
  color: #e50914;
}

.stat-label {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 表单区域 */
.form-section {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-label {
  font-size: 0.8rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-input,
.form-textarea {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 0.9rem;
  color: #fff;
  transition: all 0.3s ease;
  height: 32px;
}

.form-textarea {
  height: auto;
  resize: vertical;
  min-height: 60px;
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #e50914;
  background: rgba(255, 255, 255, 0.12);
  box-shadow: 0 0 0 2px rgba(229, 9, 20, 0.1);
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}



/* 保存按钮 */
.save-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #e50914;
  color: #fff;
  border: none;
  padding: 6px 16px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  height: 28px;
}

.save-btn:hover:not(:disabled) {
  background: #b8070f;
  transform: translateY(-1px);
}

.save-btn:disabled {
  background: rgba(229, 9, 20, 0.5);
  cursor: not-allowed;
  transform: none;
}

/* 只读信息 */
.readonly-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.readonly-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.readonly-value {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .profile-cards-wrapper {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}

/* 改签弹窗响应式设计 */
@media (max-width: 768px) {
  .custom-change-modal {
    padding: 15px;
  }

  .change-modal-content {
    max-width: 100%;
  }

  .custom-change-modal .modal-header {
    padding: 12px 16px;
  }

  .custom-change-modal .modal-header h3 {
    font-size: 16px;
  }

  .custom-change-modal .modal-body {
    padding: 16px;
  }

  .custom-change-modal .modal-footer {
    padding: 12px 16px;
    flex-direction: column;
    gap: 8px;
  }

  .custom-change-modal .cancel-button,
  .custom-change-modal .confirm-button {
    width: 100%;
    justify-content: center;
  }
}

/* 订单页面响应式设计 */
@media (max-width: 768px) {
  .orders-section .order-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .orders-section .order-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .orders-section .movie-info {
    flex-direction: column;
    gap: 12px;
  }

  .orders-section .movie-info .movie-poster {
    flex: none;
    align-self: center;
  }

  .orders-section .order-actions {
    flex-wrap: wrap;
    gap: 6px;
  }

  .orders-section .btn-refund,
  .orders-section .btn-change,
  .orders-section .btn-detail {
    font-size: 11px;
    padding: 5px 10px;
  }
}

@media (max-width: 768px) {
  .profile-page {
    padding: 60px 16px 20px;
  }

  .profile-nav {
    flex-wrap: wrap;
    gap: 6px;
  }

  .profile-nav button {
    padding: 6px 16px;
    font-size: 0.8rem;
  }

  .avatar-section {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }

  .user-stats {
    justify-content: center;
  }

  .form-row,
  .readonly-section {
    grid-template-columns: 1fr;
  }

  .card-content {
    padding: 16px;
  }

  .form-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}

/* 评价页面样式 */
.reviews-container {
  max-width: 1200px;
  margin: 0 auto;
}

.reviews-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.reviews-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.5rem;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.reviews-title i {
  width: 20px;
  height: 20px;
  background: #e50914;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.reviews-title i::before {
  content: '';
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 2px;
}

.reviews-count {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

/* 评价列表布局 */
.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.review-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  display: flex;
  align-items: stretch;
}

.review-card:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(229, 9, 20, 0.3);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

/* 电影海报区域 */
.movie-poster-section {
  position: relative;
  width: 120px;
  flex-shrink: 0;
  overflow: hidden;
}

.movie-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.movie-poster:hover {
  transform: scale(1.05);
}

/* 评价内容区域 */
.review-content {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
  min-height: 160px;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.title-rating-section {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.movie-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
  cursor: pointer;
  transition: color 0.3s ease;
  line-height: 1.3;
}

.movie-title:hover {
  color: #e50914;
}

.rating-badge {
  background: rgba(245, 181, 10, 0.15);
  border: 1px solid rgba(245, 181, 10, 0.3);
  border-radius: 6px;
  padding: 4px 8px;
  display: flex;
  align-items: baseline;
  gap: 2px;
  flex-shrink: 0;
}

.rating-score {
  font-size: 0.9rem;
  font-weight: 700;
  color: #f5b50a;
}

.rating-max {
  font-size: 0.75rem;
  color: rgba(245, 181, 10, 0.8);
}

.review-date {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
  white-space: nowrap;
}

.review-text {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
  line-height: 1.5;
  flex: 1;
}

/* 评价操作按钮 */
.review-actions {
  display: flex;
  gap: 8px;
  margin-top: auto;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.edit-btn {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.edit-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.delete-btn {
  background: rgba(229, 9, 20, 0.1);
  color: #e50914;
  border: 1px solid rgba(229, 9, 20, 0.3);
}

.delete-btn:hover {
  background: #e50914;
  color: #fff;
  border-color: #e50914;
}

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  max-width: 500px;
  margin: 0 auto;
}

.empty-icon {
  width: 80px;
  height: 80px;
  background: rgba(229, 9, 20, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
}

.empty-icon i {
  font-size: 2rem;
  color: #e50914;
}

.empty-state h3 {
  font-size: 1.5rem;
  color: #fff;
  margin-bottom: 12px;
}

.empty-state p {
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 32px;
  line-height: 1.6;
}

.discover-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #e50914;
  color: #fff;
  padding: 12px 24px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
}

.discover-btn:hover {
  background: #b8070f;
  transform: translateY(-2px);
}

/* 编辑对话框样式 */
.edit-dialog {
  background: transparent;
  border: none;
  padding: 0;
  max-width: 500px;
  width: 90vw;
}

.edit-dialog::backdrop {
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
}

.dialog-content {
  background: #1a1a1a;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.dialog-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: 300;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.dialog-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 评分选择区域 */
.rating-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rating-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
}

.rating-selector {
  display: flex;
  align-items: center;
  gap: 4px;
}

.rating-star {
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
}

.rating-star:hover,
.rating-star.active {
  color: #f5b50a;
  transform: scale(1.1);
}

.rating-text {
  margin-left: 12px;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

/* 内容编辑区域 */
.content-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.content-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
}

.content-textarea {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 12px;
  font-size: 0.9rem;
  color: #fff;
  resize: vertical;
  min-height: 80px;
  transition: all 0.3s ease;
}

.content-textarea::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.content-textarea:focus {
  outline: none;
  border-color: #e50914;
  background: rgba(255, 255, 255, 0.12);
  box-shadow: 0 0 0 2px rgba(229, 9, 20, 0.1);
}

/* 对话框操作按钮 */
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-cancel,
.btn-save {
  padding: 8px 20px;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.btn-cancel {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.15);
}

.btn-save {
  background: #e50914;
  color: #fff;
}

.btn-save:hover {
  background: #b8070f;
  transform: translateY(-1px);
}

/* 帖子收藏页面样式 */
.collections-section {
  max-width: 1200px;
  margin: 0 auto;
}

.collections-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.collections-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.collections-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.5rem;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.collections-title i {
  width: 20px;
  height: 20px;
  background: #e50914;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.collections-title i::before {
  content: '';
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 2px;
}

.collections-count {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

/* 帖子收藏列表 */
.collections-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.collection-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  cursor: pointer;
}

.collection-card:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(229, 9, 20, 0.3);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.post-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.post-header {
  margin-bottom: 4px;
}

.post-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
  line-height: 1.4;
  transition: color 0.3s ease;
}

.collection-card:hover .post-title {
  color: #e50914;
}

.post-excerpt {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
}

.post-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.like-icon,
.comment-icon {
  width: 16px;
  height: 16px;
  color: rgba(255, 255, 255, 0.6);
  transition: color 0.3s ease;
}

.collection-card:hover .like-icon {
  color: #e50914;
}

.collection-card:hover .comment-icon {
  color: #4a9eff;
}

/* 加载和错误状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 16px;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top: 3px solid #e50914;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-spinner p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  margin: 0;
}

.error-message {
  text-align: center;
  padding: 40px 20px;
  color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: center;
}

.retry-btn {
  background: #e50914;
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.retry-btn:hover {
  background: #b8070f;
  transform: translateY(-1px);
}

/* 订单页面样式 - 覆盖profile.css中的浅色主题 */
.orders-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0;
  background: transparent;
  border-radius: 0;
  box-shadow: none;
}

.orders-section h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--light-text);
  margin: 0 0 24px 0;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.orders-section h3 i {
  width: 20px;
  height: 20px;
  background: var(--primary-color);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.orders-section h3 i::before {
  content: '';
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 2px;
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.order-card {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
  box-shadow: none;
}

.order-card:hover {
  border-color: var(--primary-color);
  background: rgba(229, 9, 20, 0.05);
  transform: none;
  box-shadow: none;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
}

.order-info h4 {
  margin: 0;
  color: var(--light-text);
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.order-status {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}

.status-paid {
  background: rgba(64, 158, 255, 0.2);
  color: #409eff;
  border: 1px solid rgba(64, 158, 255, 0.3);
}

.status-pending {
  background: rgba(230, 162, 60, 0.2);
  color: #e6a23c;
  border: 1px solid rgba(230, 162, 60, 0.3);
}

.status-cancelled {
  background: rgba(245, 108, 108, 0.2);
  color: #f56c6c;
  border: 1px solid rgba(245, 108, 108, 0.3);
}

.status-refunded {
  background: rgba(144, 147, 153, 0.2);
  color: #909399;
  border: 1px solid rgba(144, 147, 153, 0.3);
}

.status-unknown {
  background: rgba(144, 147, 153, 0.2);
  color: #909399;
  border: 1px solid rgba(144, 147, 153, 0.3);
}

.order-price {
  font-size: 16px;
  font-weight: bold;
  color: var(--primary-color);
}

.order-content {
  margin-bottom: 10px;
}

.movie-info {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.movie-info .movie-poster {
  flex: 0 0 60px;
}

.movie-info .movie-poster img {
  width: 100%;
  height: 90px;
  object-fit: cover;
  border-radius: 6px;
}

.movie-details {
  flex: 1;
}

.movie-details h5 {
  margin: 0 0 4px 0;
  color: var(--light-text);
  font-size: 14px;
  font-weight: 600;
}

.movie-details p {
  margin: 2px 0;
  color: var(--gray-text);
  font-size: 12px;
  line-height: 1.4;
}

.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 10px;
  border-top: 1px solid var(--border-color);
}

.order-date {
  color: var(--gray-text);
  font-size: 11px;
}

.order-actions {
  display: flex;
  gap: 6px;
}

.btn-refund,
.btn-change,
.btn-detail {
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid var(--border-color);
  background: var(--card-bg);
  color: var(--light-text);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 11px;
  font-weight: 500;
}

.btn-refund {
  border-color: #e6a23c;
  color: #e6a23c;
}

.btn-refund:hover {
  background: rgba(230, 162, 60, 0.1);
  border-color: #e6a23c;
  transform: none;
}

.btn-change {
  border-color: #9b59b6;
  color: #9b59b6;
}

.btn-change:hover {
  background: rgba(155, 89, 182, 0.1);
  border-color: #9b59b6;
  transform: none;
}

.btn-detail {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.btn-detail:hover {
  background: rgba(229, 9, 20, 0.1);
  border-color: var(--primary-color);
  transform: none;
}

.orders-section .empty-state {
  text-align: center;
  padding: 80px 20px;
  max-width: 500px;
  margin: 0 auto;
}

.orders-section .empty-state i {
  font-size: 3rem;
  color: var(--primary-color);
  margin-bottom: 24px;
  display: block;
}

.orders-section .empty-state p {
  color: var(--gray-text);
  margin: 16px 0 32px 0;
  font-size: 16px;
  line-height: 1.6;
}

.orders-section .btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--primary-color);
  color: var(--light-text);
  padding: 12px 24px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
}

.orders-section .btn-primary:hover {
  background: rgba(229, 9, 20, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(229, 9, 20, 0.3);
}

/* 加载和错误状态 */
.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 16px;
}

.loading-indicator .spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-indicator p {
  color: var(--gray-text);
  font-size: 14px;
  margin: 0;
}

.orders-section .error-message {
  text-align: center;
  padding: 40px 20px;
  color: var(--gray-text);
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: center;
}

.orders-section .error-message button {
  background: var(--primary-color);
  color: var(--light-text);
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.orders-section .error-message button:hover {
  background: rgba(229, 9, 20, 0.8);
  transform: translateY(-1px);
}

/* 自定义改签弹窗样式 */
.custom-change-modal {
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

.change-modal-content {
  background: var(--card-bg);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
}

.custom-change-modal .modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.custom-change-modal .modal-header h3 {
  margin: 0;
  color: var(--light-text);
  font-size: 18px;
  font-weight: 600;
}

.custom-change-modal .close-button {
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

.custom-change-modal .close-button:hover {
  background: rgba(229, 9, 20, 0.1);
  color: var(--primary-color);
}

.custom-change-modal .modal-body {
  padding: 20px;
}

.custom-change-modal .current-schedule {
  margin-bottom: 20px;
  padding: 12px;
  background: var(--darker-bg);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.custom-change-modal .current-label {
  margin: 0 0 4px 0;
  color: var(--gray-text);
  font-size: 14px;
}

.custom-change-modal .current-time {
  margin: 0;
  color: var(--light-text);
  font-size: 16px;
  font-weight: 600;
}

.custom-change-modal .form-group {
  margin-bottom: 16px;
}

.custom-change-modal .form-label {
  display: block;
  margin-bottom: 6px;
  color: var(--light-text);
  font-size: 14px;
  font-weight: 500;
}

.custom-change-modal .form-input,
.custom-change-modal .form-select {
  width: 100%;
  padding: 10px 12px;
  background: var(--darker-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--light-text);
  font-size: 14px;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.custom-change-modal .form-input:focus,
.custom-change-modal .form-select:focus {
  outline: none;
  border-color: var(--primary-color);
  background: rgba(229, 9, 20, 0.05);
}

.custom-change-modal .form-select option {
  background: var(--card-bg);
  color: var(--light-text);
}

.custom-change-modal .modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
}

.custom-change-modal .cancel-button,
.custom-change-modal .confirm-button {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: var(--card-bg);
  color: var(--light-text);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
}

.custom-change-modal .cancel-button:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.custom-change-modal .confirm-button {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: var(--light-text);
}

.custom-change-modal .confirm-button:hover {
  background: rgba(229, 9, 20, 0.8);
  border-color: rgba(229, 9, 20, 0.8);
}

.custom-change-modal .confirm-button:disabled {
  background: var(--gray-text);
  border-color: var(--gray-text);
  cursor: not-allowed;
  opacity: 0.6;
}

/* 我的帖子页面样式 */
.posts-section {
  max-width: 1200px;
  margin: 0 auto;
}

.posts-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.posts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.posts-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.5rem;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.posts-title i {
  width: 20px;
  height: 20px;
  background: #e50914;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.posts-title i::before {
  content: '';
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 2px;
}

.posts-count {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

/* 我的帖子列表 */
.posts-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.user-post-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  cursor: pointer;
}

.user-post-card:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(229, 9, 20, 0.3);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.user-post-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.user-post-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
  line-height: 1.4;
  flex: 1;
  transition: color 0.3s ease;
}

.user-post-card:hover .user-post-title {
  color: #e50914;
}

.delete-post-btn {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.delete-post-btn:hover {
  background: #e50914;
  color: #fff;
  transform: scale(1.1);
}

.delete-icon {
  width: 14px;
  height: 14px;
}

.user-post-excerpt {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
}

.user-post-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.user-post-meta .meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.time-icon,
.user-post-meta .like-icon,
.user-post-meta .comment-icon {
  width: 16px;
  height: 16px;
  color: rgba(255, 255, 255, 0.6);
  transition: color 0.3s ease;
}

.user-post-card:hover .time-icon {
  color: #4a9eff;
}

.user-post-card:hover .user-post-meta .like-icon {
  color: #e50914;
}

.user-post-card:hover .user-post-meta .comment-icon {
  color: #4a9eff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .posts-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .user-post-content {
    padding: 16px;
  }

  .user-post-meta {
    gap: 12px;
  }

  .user-post-meta .meta-item {
    font-size: 0.75rem;
  }
  .collections-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .post-content {
    padding: 16px;
  }

  .post-meta {
    gap: 12px;
  }

  .meta-item {
    font-size: 0.75rem;
  }

  .reviews-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .review-card {
    flex-direction: column;
  }

  .movie-poster-section {
    width: 100%;
    height: 200px;
  }

  .review-content {
    min-height: auto;
    padding: 16px;
  }

  .title-rating-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .rating-badge {
    align-self: flex-start;
  }

  .edit-dialog {
    width: 95vw;
  }

  .dialog-body {
    padding: 16px;
  }

  .dialog-actions {
    flex-direction: column;
    padding: 16px;
  }

  .btn-cancel,
  .btn-save {
    width: 100%;
    justify-content: center;
  }
}
</style>