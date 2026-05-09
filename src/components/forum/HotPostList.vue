<template>
  <div class="hot-topics">
    <h3 class="hot-topics-title">
      <span class="hot-icon">🔥</span>
      热门话题
      <span v-if="isLoading" class="loading-text">加载中...</span>
    </h3>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-else>
      <div v-if="hotPosts.length" class="hot-posts">
        <div
          v-for="post in hotPosts"
          :key="post.id"
          class="hot-post"
          @click="$router.push(`/forum/post/${post.id}`)"
        >
          <div class="post-header">
            <span class="theme-tag" 
                  :class="getThemeClass(post.theme)">
              {{ getThemeLabel(post.theme) }}
            </span>
            <span v-if="post.is_pinned" class="pin-badge">
              📌 置顶
            </span>
          </div>
          
          <h4 class="post-title">
            {{ post.title }}
          </h4>

          <div class="post-meta">
            <span class="meta-item">
              <i class="fas fa-user"></i>
              {{ post.username }}
            </span>
            <span class="meta-item">
              <i class="fas fa-heart"></i>
              {{ post.like_count || 0 }}
            </span>
            <span class="meta-item">
              <i class="fas fa-comment"></i>
              {{ post.reply_count || 0 }}
            </span>
          </div>
        </div>
      </div>
      <div v-else-if="!isLoading" class="empty-state">
        暂无热门帖子
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { fetchHotPosts } from '@/api/forum';

const hotPosts = ref([]);
const isLoading = ref(true);
const error = ref('');

// 主题标签样式
const getThemeClass = (theme) => {
  switch (theme) {
    case 'tech': return 'bg-blue-100 text-blue-600';
    case 'life': return 'bg-green-100 text-green-600';
    case 'entertainment': return 'bg-pink-100 text-pink-600';
    default: return 'bg-gray-100 text-gray-600';
  }
};

// 主题标签文本
const getThemeLabel = (theme) => {
  switch (theme) {
    case 'tech': return '技术';
    case 'life': return '生活';
    case 'entertainment': return '娱乐';
    default: return '其他';
  }
};

const loadHotPosts = async () => {
  isLoading.value = true;
  error.value = '';
  
  try {
    const res = await fetchHotPosts();
    if (Array.isArray(res.data)) {
      hotPosts.value = res.data;
    } else if (res.data?.results && Array.isArray(res.data.results)) {
      hotPosts.value = res.data.results;
    } else {
      throw new Error('返回数据格式不正确');
    }
  } catch (err) {
    error.value = '加载热门帖子失败，请稍后重试';
    console.error('加载热门帖子失败:', err);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => loadHotPosts());
</script>

<style scoped>
.hot-topics {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  border: 1px solid var(--border-color);
}

.hot-topics-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.hot-icon {
  font-size: 1.5rem;
}

.loading-text {
  font-size: 0.875rem;
  color: #666;
  font-weight: normal;
  margin-left: auto;
}

.hot-posts {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.hot-post {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.hot-post:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.post-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.theme-tag {
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.pin-badge {
  font-size: 0.75rem;
  color: #e50914;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.post-title {
  color: #ffffff;
  font-size: 1rem;
  font-weight: 500;
  margin: 0 0 0.75rem 0;
  line-height: 1.4;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: #b3b3b3;
  font-size: 0.8rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.meta-item i {
  font-size: 0.9rem;
}

.error-message {
  color: #e50914;
  text-align: center;
  padding: 1rem;
  background: rgba(229, 9, 20, 0.1);
  border-radius: 8px;
  margin-top: 1rem;
}

.empty-state {
  text-align: center;
  color: #666;
  padding: 2rem;
  font-size: 0.9rem;
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
</style>