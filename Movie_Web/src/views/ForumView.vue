<template>
  <div class="forum-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">电影论坛</h1>
      <p class="page-subtitle">分享观影心得，讨论电影话题</p>
    </div>

    <!-- 筛选和操作栏 - 始终显示 -->
    <div class="filter-section">
      <div class="filter-wrapper">
        <div class="filter-left">
          <ThemeFilterDropdown @load-posts="loadPosts" />
        </div>
        <div class="filter-right">
          <router-link to="/forum/create" class="create-post-btn">
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none">
              <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            发布帖子
          </router-link>
        </div>
      </div>
    </div>

    <!-- 热门话题模块 - 只在有帖子时显示 -->
    <div class="hot-topics-section" v-if="hotPosts.length > 0">
      <HotPostList @posts-loaded="handleHotPostsLoaded" />
      <div class="divider"></div>
    </div>

    <!-- 普通论坛内容 -->
    <div class="post-list">
      <div v-if="posts.length" class="space-y-6">
        <div
          v-for="post in sortedPosts"
          :key="post.id"
          class="post-card"
        >
          <div class="post-header">
            <h3 class="post-title">
              <router-link :to="`/forum/post/${post.id}`">
                <span v-if="post.is_pinned" class="pin-badge">置顶</span>
                {{ post.title }}
              </router-link>
            </h3>
            <div class="post-meta-top">
              <span class="theme-tag" :class="getThemeClass(post.theme)">
                {{ getThemeLabel(post.theme) }}
              </span>
              <span class="post-author">{{ post.username || '未知用户' }}</span>
              <span class="post-time">{{ formatDate(post.created_at) }}</span>
            </div>
          </div>

          <p class="post-excerpt">
            {{ post.content.slice(0, 120) }}...
          </p>

          <div class="post-actions">
            <button @click="toggleLike(post.id)" class="action-btn">
              <svg class="action-icon" :class="{ 'liked': post.is_liked }" viewBox="0 0 24 24" fill="none">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
                      :stroke="post.is_liked ? '#e50914' : 'currentColor'"
                      :fill="post.is_liked ? '#e50914' : 'none'"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"/>
              </svg>
              <span>{{ post.like_count || 0 }}</span>
            </button>

            <button @click="toggleFavorite(post.id)" class="action-btn">
              <svg class="action-icon" :class="{ 'favorited': post.is_favorited }" viewBox="0 0 24 24" fill="none">
                <polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"
                         :stroke="post.is_favorited ? '#ffd700' : 'currentColor'"
                         :fill="post.is_favorited ? '#ffd700' : 'none'"
                         stroke-width="2"
                         stroke-linecap="round"
                         stroke-linejoin="round"/>
              </svg>
              <span>{{ post.favorite_count || 0 }}</span>
            </button>

            <span class="comment-count">
              <svg class="action-icon" viewBox="0 0 24 24" fill="none">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
                      stroke="currentColor"
                      fill="none"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"/>
              </svg>
              <span>{{ post.reply_count || 0 }}</span>
            </span>
          </div>
        </div>
      </div>

      <!-- 加载状态/空状态 -->
      <div v-else class="empty-state">
        <div v-if="isLoading" class="loading-state">
          <svg class="loading-icon" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-dasharray="31.416" stroke-dashoffset="31.416">
              <animate attributeName="stroke-dasharray" dur="2s" values="0 31.416;15.708 15.708;0 31.416" repeatCount="indefinite"/>
              <animate attributeName="stroke-dashoffset" dur="2s" values="0;-15.708;-31.416" repeatCount="indefinite"/>
            </circle>
          </svg>
          <p>加载中...</p>
        </div>
        <div v-else class="no-posts-state">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M8 9h8M8 13h6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <h3>还没有帖子</h3>
          <p>成为第一个发帖的人，分享你的观影心得吧！</p>
          <router-link to="/forum/create" class="start-posting-btn">
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none">
              <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            开始发帖
          </router-link>
        </div>
      </div>
    </div>

    <!-- 分页导航 -->
    <div class="pagination-wrapper" v-if="totalPages > 1">
      <div class="pagination">
        <!-- 上一页 -->
        <button
          :disabled="currentPage === 1"
          @click="prevPage"
          class="pagination-btn pagination-prev"
        >
          <i class="fas fa-chevron-left"></i>
          上一页
        </button>

        <!-- 页码 -->
        <div class="pagination-numbers">
          <button
            v-for="page in pageRange"
            :key="page"
            :class="['pagination-number', { 'active': page === currentPage }]"
            @click="loadPosts(filterTheme, page)"
          >
            {{ page }}
          </button>
        </div>

        <!-- 下一页 -->
        <button
          :disabled="currentPage === totalPages"
          @click="nextPage"
          class="pagination-btn pagination-next"
        >
          下一页
          <i class="fas fa-chevron-right"></i>
        </button>
      </div>

      <!-- 分页信息 -->
      <div class="pagination-info">
        <span class="page-info">第 {{ currentPage }} 页 / 共 {{ totalPages }} 页</span>
        <div class="page-size-selector">
          <span>每页</span>
          <select v-model="pageSize" @change="loadPosts(filterTheme, 1)" class="page-size-select">
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="50">50</option>
          </select>
          <span>条</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { fetchPosts, toggleLike as apiToggleLike, toggleFavorite as apiToggleFavorite } from '@/api/forum';

// 组件导入
import HotPostList from '@/components/forum/HotPostList.vue';
import ThemeFilterDropdown from '@/components/forum/ThemeFilterDropdown.vue';

// 分页状态
const currentPage = ref(1);
const pageSize = ref(10);
const totalPages = ref(1);
const totalCount = ref(0);

// 帖子数据
const posts = ref([]);
const hotPosts = ref([]);
const isLoading = ref(true);
const filterTheme = ref('');

// 计算排序后的帖子
const sortedPosts = computed(() => {
  return [...posts.value].sort((a, b) => {
    if (a.is_pinned && !b.is_pinned) return -1;
    if (!a.is_pinned && b.is_pinned) return 1;
    return new Date(b.created_at) - new Date(a.created_at);
  });
});

// 计算页码范围（显示当前页附近的页码）
const pageRange = computed(() => {
  let start = Math.max(1, currentPage.value - 2);
  let end = Math.min(totalPages.value, start + 4);

  if (end - start < 4 && start > 1) {
    start = Math.max(1, end - 4);
  }

  return Array.from({ length: end - start + 1 }, (_, i) => start + i);
});

// 加载帖子
const loadPosts = async (theme = '', page = 1, size = pageSize.value) => {
  filterTheme.value = theme;
  currentPage.value = page;
  pageSize.value = size;
  isLoading.value = true;

  try {
    const res = await fetchPosts(theme, page, size);
    posts.value = res.data.results || [];
    totalCount.value = res.data.count || 0;
    totalPages.value = Math.ceil(totalCount.value / pageSize.value);
  } catch (error) {
    console.error('[ERROR] 获取帖子列表失败:', error);
  } finally {
    isLoading.value = false;
  }
};

// 分页操作
const prevPage = () => loadPosts(filterTheme.value, currentPage.value - 1);
const nextPage = () => loadPosts(filterTheme.value, currentPage.value + 1);

// 处理热门帖子加载完成
const handleHotPostsLoaded = (posts) => {
  hotPosts.value = posts;
};

// 日期格式化
const formatDate = (dateStr) => {
  return dateStr ? new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  }) : '';
};

// 点赞功能
const toggleLike = async (postId) => {
  try {
    const res = await apiToggleLike(postId);
    posts.value = posts.value.map(post =>
      post.id === postId ? { ...post, is_liked: res.data.liked, like_count: res.data.like_count } : post
    );
  } catch (error) {
    console.error('[ERROR] 点赞操作失败:', error);
  }
};

// 收藏功能
const toggleFavorite = async (postId) => {
  try {
    const res = await apiToggleFavorite(postId);
    posts.value = posts.value.map(post =>
      post.id === postId ? { ...post, is_favorited: res.data.favorited, favorite_count: res.data.favorite_count } : post
    );
  } catch (error) {
    console.error('[ERROR] 收藏操作失败:', error);
  }
};

// 辅助函数：获取主题标签显示文本
const getThemeLabel = (theme) => {
  switch (theme) {
    case 'tech': return '技术';
    case 'life': return '生活';
    case 'entertainment': return '娱乐';
    default: return '其他';
  }
};

// 辅助函数：获取主题标签颜色
const getThemeClass = (theme) => {
  switch (theme) {
    case 'tech': return 'bg-blue-100 text-blue-600';
    case 'life': return 'bg-green-100 text-green-600';
    case 'entertainment': return 'bg-pink-100 text-pink-600';
    default: return 'bg-gray-100 text-gray-600';
  }
};

// 生命周期钩子
onMounted(() => loadPosts());
</script>

<style scoped>
/* 论坛页面深色主题样式 */
.forum-container {
  min-height: 100vh;
  background: var(--dark-bg);
  color: var(--light-text);
  padding: 80px 20px 40px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 3rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 0.5rem;
  letter-spacing: -0.5px;
}

.page-subtitle {
  font-size: 1.1rem;
  color: #b3b3b3;
  margin: 0;
}

/* 筛选区域 */
.filter-section {
  margin-bottom: 2rem;
  padding: 1rem 0;
}

.filter-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.filter-right {
  display: flex;
  align-items: center;
}

.create-post-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #e50914;
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.3s ease;
  border: 1px solid #e50914;
}

.create-post-btn:hover {
  background: #f40612;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(229, 9, 20, 0.3);
}

/* 热门话题区域 */
.hot-topics-section {
  margin-bottom: 2rem;
}

.divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: 2rem 0;
}

/* 帖子列表 */
.post-list {
  margin-bottom: 2rem;
}

.post-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 0.75rem;
  transition: all 0.3s ease;
}

.post-card:hover {
  background: #2a2a2a;
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
}

.post-header {
  margin-bottom: 0.75rem;
}

.post-title {
  margin: 0 0 0.5rem 0;
}

.post-title a {
  color: #ffffff;
  text-decoration: none;
  font-size: 1.1rem;
  font-weight: 600;
  line-height: 1.4;
  transition: color 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.post-title a:hover {
  color: #e50914;
}

.pin-badge {
  background: #e50914;
  color: white;
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.post-meta-top {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.8rem;
  color: #b3b3b3;
}

.theme-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 500;
}

.post-author {
  color: #d1d1d1;
}

.post-time {
  color: #999;
}

.post-excerpt {
  color: #d1d1d1;
  line-height: 1.5;
  margin: 0.75rem 0;
  font-size: 0.9rem;
}

.post-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.75rem;
}

.action-btn {
  background: none;
  border: none;
  color: #b3b3b3;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 6px 8px;
  border-radius: 6px;
}

.action-btn:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
}

.action-icon {
  width: 16px;
  height: 16px;
  transition: all 0.2s ease;
}

.action-btn:hover .action-icon {
  transform: scale(1.1);
}

.comment-count {
  color: #b3b3b3;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 6px 8px;
}

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.loading-state {
  color: #b3b3b3;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.loading-icon {
  width: 3rem;
  height: 3rem;
  color: #e50914;
}

.no-posts-state {
  max-width: 400px;
  margin: 0 auto;
}

.empty-icon {
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: center;
}

.empty-icon svg {
  width: 4rem;
  height: 4rem;
  color: #666;
}

.no-posts-state h3 {
  font-size: 1.5rem;
  color: #ffffff;
  margin-bottom: 0.5rem;
}

.no-posts-state p {
  color: #b3b3b3;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.start-posting-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #e50914;
  color: white;
  padding: 14px 28px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.start-posting-btn:hover {
  background: #f40612;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(229, 9, 20, 0.3);
}

.btn-icon {
  width: 16px;
  height: 16px;
}

/* 分页样式 */
.pagination-wrapper {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.pagination-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff;
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
}

.pagination-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.25);
  transform: translateY(-1px);
}

.pagination-btn:disabled {
  cursor: not-allowed;
  opacity: 0.4;
  transform: none;
}

.pagination-btn i {
  font-size: 12px;
}

.pagination-numbers {
  display: flex;
  gap: 0.5rem;
}

.pagination-number {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
  min-width: 40px;
  text-align: center;
}

.pagination-number:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.25);
}

.pagination-number.active {
  background: #e50914;
  border-color: #e50914;
  color: white;
  box-shadow: 0 2px 8px rgba(229, 9, 20, 0.3);
}

.pagination-info {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  color: #b3b3b3;
  font-size: 14px;
}

.page-info {
  font-weight: 500;
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-size-select {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff;
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-size-select:focus {
  outline: none;
  border-color: #e50914;
  box-shadow: 0 0 0 2px rgba(229, 9, 20, 0.2);
}

.page-size-select option {
  background: #2a2a2a;
  color: #ffffff;
}

/* 主题标签颜色 */
.bg-blue-100 {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}

.bg-green-100 {
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
}

.bg-pink-100 {
  background: rgba(236, 72, 153, 0.2);
  color: #f472b6;
}

.bg-gray-100 {
  background: rgba(156, 163, 175, 0.2);
  color: #9ca3af;
}

/* 置顶标签 */
.bg-red-500 {
  background: #e50914;
  color: white;
}
</style>