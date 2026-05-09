<template>
  <div class="notification-list-container">
    <h1 class="page-title">我的通知</h1>
    
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <span>加载中...</span>
    </div>
    
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    
    <div v-else>
      <div v-if="notifications.length === 0" class="empty">
        <div class="empty-icon">📭</div>
        <p>暂无通知</p>
      </div>
      
      <div v-else class="notification-list">
        <div 
          v-for="notification in notifications" 
          :key="notification.id"
          class="notification-item"
          :class="{ 'unread': !notification.is_read }"
        >
          <router-link 
            :to="getNotificationUrl(notification)"
            @click="handleClick(notification)"
          >
            <div class="content" v-html="formatNotificationContent(notification)"></div>
            <div class="time">{{ formatTimeAgo(notification.created_at) }}</div>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { fetchUserNotifications } from '@/api/forum';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';

const router = useRouter();
const notifications = ref([]);
const loading = ref(true);
const error = ref('');

// 加载通知
const fetchData = async () => {
  try {
    const res = await fetchUserNotifications();
    console.log('获取通知数据:', res.data);
    notifications.value = res.data || [];
  } catch (err) {
    error.value = err.message || '获取通知失败';
  } finally {
    loading.value = false;
  }
};

// 格式化通知内容（优化类型判断逻辑）
const formatNotificationContent = (notification) => {
  if (!notification) return '';
  
  let content = '';
  const type = notification.type || 'unknown';
  
  // 提取用户名和帖子信息（统一使用 pk 字段）
  const username = notification.username || '用户';
  const postPk = notification.post?.pk || notification.reply?.post?.pk; // 使用 pk 字段
  const postTitle = postPk ? 
    `"${notification.post?.title?.substring(0, 20)}${notification.post?.title?.length > 20 ? '...' : ''}"` : 
    '帖子';
  
  switch (type) {
    case 'reply':
      content = `<span class="username">${username}</span> 回复了你的 ${postTitle}`;
      break;
      
    case 'mention':
      content = `<span class="username">${username}</span> 在回复中提到了你 ${postTitle}`;
      break;
      
    case 'like':
      content = `<span class="username">${username}</span> 赞了你的`;
      if (notification.post) {
        content += `帖子 ${postTitle}`;
      } else if (notification.reply) {
        content += '回复';
      }
      break;
      
    case 'system':
      content = `<span class="system">系统通知</span>: ${notification.content || '未知通知'}`;
      break;
      
    default:
      content = notification.content || '未知通知';
  }
  
  return content;
};

// 获取通知链接（统一使用 pk 作为参数）
const getNotificationUrl = (notification) => {
  if (!notification) return { name: 'Forum' };

  // 记录通知对象，用于调试
  console.log('通知对象:', notification);

  // 获取帖子ID的优先级：
  // 1. 直接从post字段获取id
  // 2. 从reply关联的post获取id
  const postId = notification.post?.id || notification.reply?.post?.id;

  console.log('获取到的帖子ID:', postId);

  if (postId) {
    return { 
      name: 'PostDetail', 
      params: { pk: String(postId) }
    };
  }

  // 系统通知或无关联帖子的情况
  if (notification.type === 'system') {
    return { name: 'Notifications' };
  }

  return { name: 'Forum' };
};

// 格式化时间
const formatTimeAgo = (dateStr) => {
  if (!dateStr) return '未知时间';
  
  try {
    return formatDistanceToNow(new Date(dateStr), {
      addSuffix: true,
      locale: zhCN
    });
  } catch (err) {
    console.error('格式化时间失败:', err);
    return dateStr;
  }
};

// 处理点击事件
const handleClick = (notification) => {
  console.log('点击通知:', notification);
  const url = getNotificationUrl(notification);
  
  router.push(url).catch(err => {
    console.error('路由导航失败:', err);
    alert(`导航失败: ${err.message}`);
  });
};

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.notification-list-container {
  padding: 2rem;
  max-width: 800px;
  margin: 80px auto 0;
  min-height: calc(100vh - 80px);
}

.page-title {
  font-size: 2rem;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 2rem;
  text-align: center;
}

.notification-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.notification-item {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.notification-item a {
  display: block;
  padding: 1.25rem;
  text-decoration: none;
  color: inherit;
}

.notification-item:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.notification-item.unread {
  background: rgba(59, 130, 246, 0.1);
  border-left: 4px solid #3b82f6;
}

.content {
  color: #e5e7eb;
  line-height: 1.6;
  font-size: 0.95rem;
}

.username {
  color: #3b82f6;
  font-weight: 600;
}

.post-title {
  color: #60a5fa;
  font-weight: 500;
}

.system {
  color: #e50914;
  font-weight: 600;
}

.time {
  margin-top: 0.75rem;
  font-size: 0.8rem;
  color: #9ca3af;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #9ca3af;
  gap: 1rem;
}

.loading-spinner {
  width: 2.5rem;
  height: 2.5rem;
  border: 3px solid #2563eb;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error {
  text-align: center;
  padding: 2rem;
  color: #e50914;
  background: rgba(229, 9, 20, 0.1);
  border-radius: 12px;
  margin-top: 1rem;
}

.empty {
  text-align: center;
  padding: 4rem 2rem;
  color: #9ca3af;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty p {
  font-size: 1rem;
  color: #6b7280;
}
</style>