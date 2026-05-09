<template>
  <div class="notification-dropdown relative">
    <!-- 通知列表 -->
    <div class="notification-list max-h-[300px] overflow-y-auto absolute right-0 top-full mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
      <!-- 通知标题和清空按钮 -->
      <div class="notification-header flex justify-between items-center p-3 border-b">
        <h3 class="font-medium">通知</h3>
        <button
          v-if="hasUnread"
          @click="markAllAsRead"
          class="text-xs text-blue-500 hover:text-blue-700"
        >
          全部标为已读
        </button>
      </div>

      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-state">
        <i class="fa fa-spinner fa-spin"></i>
        <span>加载中...</span>
      </div>

      <!-- 无通知 -->
      <div v-else-if="notifications.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-bell-slash"></i>
        </div>
        <div class="empty-text">暂无通知</div>
        <div class="empty-subtitle">您的通知将在这里显示</div>
      </div>

      <!-- 通知项 -->
      <div
        v-else
        class="divide-y divide-gray-100"
      >
        <div
          v-for="notification in notifications"
          :key="notification.id || `notification-${index}`"
          class="notification-item p-3 border-b hover:bg-gray-50 transition-colors duration-150"
          :class="{ 'bg-blue-50': !notification.is_read }"
        >
          <router-link
            :to="getNotificationUrl(notification)"
            @click="handleNotificationClick(notification)"
            class="flex items-start w-full"
          >
            <!-- 通知图标 -->
            <div class="mr-3 text-gray-400">
              <i
                :class="getNotificationIcon(notification)"
                class="text-lg"
              ></i>
            </div>

            <!-- 通知内容 -->
            <div class="flex-1 min-w-0">
              <div class="notification-content text-sm">
                <span v-html="formatNotificationContent(notification)"></span>
              </div>
              <div class="notification-time text-xs text-gray-500 mt-1">
                {{ formatTimeAgo(notification.created_at) }}
              </div>
            </div>

            <!-- 未读标记 -->
            <div v-if="!notification.is_read" class="ml-2">
              <span class="w-2 h-2 rounded-full bg-blue-500 inline-block"></span>
            </div>
          </router-link>
        </div>
      </div>

      <!-- 查看全部按钮 -->
      <div class="notification-footer p-3 text-center border-t">
        <router-link to="/notifications" class="text-sm text-blue-500 hover:text-blue-700">
          查看全部通知
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, defineEmits } from 'vue';
import { useRouter } from 'vue-router';
import { fetchUserNotifications, markNotificationAsRead } from '@/api/forum';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';

const emit = defineEmits(['update-count']);

const router = useRouter();
const notifications = ref([]);
const isLoading = ref(true);
const error = ref(null);
const isDropdownOpen = ref(false); // 控制下拉菜单显示状态

// 计算是否有未读通知
const hasUnread = computed(() => {
  return notifications.value.some(n => !n.is_read);
});

// 点击外部关闭下拉菜单
const closeDropdown = (e) => {
  if (e.target.closest('.notification-dropdown') === null) {
    isDropdownOpen.value = false;
  }
};

// 监听点击外部事件
onMounted(() => {
  document.addEventListener('click', closeDropdown);
  fetchNotifications();
});

// 组件卸载时移除事件监听
onBeforeUnmount(() => {
  document.removeEventListener('click', closeDropdown);
});

// 加载通知
const fetchNotifications = async () => {
  try {
    isLoading.value = true;
    error.value = null;

    const res = await fetchUserNotifications();

    // 规范化数据结构，确保嵌套关系存在
    const processedNotifications = (res.data || []).map(notification => ({
      ...notification,
      post: notification.post || {},
      reply: notification.reply || {},
      // 确保嵌套路径存在
      'reply.post': notification.reply?.post || {}
    }));

    notifications.value = processedNotifications;

    // 更新未读数量
    const unreadCount = processedNotifications.filter(n => !n.is_read).length;
    emit('update-count', unreadCount);
  } catch (err) {
    error.value = err.message || '获取通知失败';
    console.error('获取通知失败:', err);
  } finally {
    isLoading.value = false;
  }
};

// 格式化通知内容
const formatNotificationContent = (notification) => {
  if (!notification) return '';

  let content = '';

  if (notification.type === 'reply') {
    content = `<span class="font-medium">${notification.username || '用户'}</span> 回复了你的帖子`;
    if (notification.post && notification.post.title) {
      content += ` <span class="font-medium">"${notification.post.title.substring(0, 20)}${notification.post.title.length > 20 ? '...' : ''}"</span>`;
    }
  } else if (notification.type === 'mention') {
    content = `<span class="font-medium">${notification.username || '用户'}</span> 在回复中提到了你`;
    if (notification.post && notification.post.title) {
      content += ` <span class="font-medium">"${notification.post.title.substring(0, 20)}${notification.post.title.length > 20 ? '...' : ''}"</span>`;
    }
  } else if (notification.type === 'like') {
    content = `<span class="font-medium">${notification.username || '用户'}</span> 赞了你的`;
    if (notification.post) {
      content += '帖子';
      if (notification.post.title) {
        content += ` <span class="font-medium">"${notification.post.title.substring(0, 20)}${notification.post.title.length > 20 ? '...' : ''}"</span>`;
      }
    } else if (notification.reply) {
      content += '回复';
    }
  } else if (notification.type === 'system') {
    content = `<span class="font-medium">系统通知</span>: ${notification.content || '未知通知'}`;
  } else {
    content = notification.content || '未知通知';
  }

  return content;
};

// 获取通知图标
const getNotificationIcon = (notification) => {
  if (!notification) return 'fa fa-bell-o';

  switch (notification.type) {
    case 'reply':
      return 'fa fa-comment-o';
    case 'mention':
      return 'fa fa-at';
    case 'like':
      return 'fa fa-thumbs-o-up';
    case 'system':
      return 'fa fa-info-circle';
    default:
      return 'fa fa-bell-o';
  }
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

// 获取通知链接 - 关键修改：将参数名统一为pk
const getNotificationUrl = (notification) => {
  if (!notification) return { name: 'Forum' };

  // 优先使用后端返回的reply_post_id，确保一致性
  const postId =
    notification.reply_post_id ||  // 后端序列化器字段
    notification.post?.id ||       // 帖子直接关联
    notification.reply?.post?.id;  // 回复关联的帖子

  console.log('提取的帖子ID:', postId);

  if (postId) {
    return {
      name: 'PostDetail',
      params: { pk: String(postId) }  // ✅ 参数名改为pk
    };
  }

  if (notification.type === 'system') {
    return { name: 'Notifications' };
  }

  return { name: 'Forum' };
};

// 处理通知点击
const handleNotificationClick = async (notification) => {
  try {
    // 如果是未读通知，标记为已读
    if (!notification.is_read) {
      await markNotificationAsRead(notification.id);
      notification.is_read = true;
    }

    // 导航到对应页面
    const url = getNotificationUrl(notification);
    router.push(url);
    isDropdownOpen.value = false; // 点击后关闭菜单
  } catch (err) {
    console.error('标记通知为已读失败:', err);
    // 即使失败，也继续导航
    const url = getNotificationUrl(notification);
    router.push(url);
    isDropdownOpen.value = false;
  }
};

// 标记所有通知为已读
const markAllAsRead = async () => {
  try {
    const unreadIds = notifications.value
      .filter(n => !n.is_read)
      .map(n => n.id);

    if (unreadIds.length === 0) return;

    // 批量标记为已读（实际项目中建议使用批量API）
    for (const id of unreadIds) {
      await markNotificationAsRead(id);
    }

    // 更新本地状态
    notifications.value.forEach(n => {
      if (!n.is_read) {
        n.is_read = true;
      }
    });

    // 更新未读数量为0
    emit('update-count', 0);
  } catch (err) {
    console.error('批量标记通知为已读失败:', err);
  }
};
</script>

<style scoped>
/* 深色主题通知样式 */
.notification-dropdown {
  position: relative;
}

.notification-list {
  position: absolute;
  top: 100%;
  right: 0;
  min-width: 300px;
  max-width: 320px;
  background: rgba(26, 26, 26, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  margin-top: 0.5rem;
  z-index: 1002;
  color: #ffffff;
  overflow: hidden;
  max-height: 400px;
}

.notification-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.03);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.notification-header h3 {
  color: #ffffff;
  font-size: 13px;
  font-weight: 600;
  margin: 0;
}

.notification-header button {
  color: #e50914;
  font-size: 11px;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s ease;
  padding: 4px 8px;
  border-radius: 4px;
}

.notification-header button:hover {
  color: #f40612;
  background: rgba(229, 9, 20, 0.1);
}

.notification-item {
  padding: 10px 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  transition: background-color 0.15s ease;
  cursor: pointer;
}

.notification-item:hover {
  background-color: rgba(255, 255, 255, 0.06);
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-item .flex {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.notification-content {
  line-height: 1.3;
  color: #ffffff;
  font-size: 12px;
  flex: 1;
}

.notification-time {
  color: #999;
  font-size: 10px;
  margin-top: 3px;
}

.notification-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding: 8px 14px;
  text-align: center;
  background: rgba(255, 255, 255, 0.02);
}

.notification-footer a {
  color: #e50914;
  text-decoration: none;
  font-size: 11px;
  font-weight: 500;
  transition: color 0.2s ease;
}

.notification-footer a:hover {
  color: #f40612;
}

/* 未读标记样式 */
.notification-item.bg-blue-50 {
  background-color: rgba(229, 9, 20, 0.08);
  border-left: 2px solid #e50914;
}

.notification-item.bg-blue-50:hover {
  background-color: rgba(229, 9, 20, 0.12);
}

.notification-item .font-medium {
  color: #ffffff;
  font-weight: 500;
}

/* 未读圆点 */
.notification-item .w-2 {
  width: 6px;
  height: 6px;
  background: #e50914;
  border-radius: 50%;
  margin-top: 2px;
}

/* 加载状态样式 */
.loading-state {
  padding: 24px 20px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #b3b3b3;
  font-size: 12px;
}

.loading-state .fa-spinner {
  color: #e50914;
  font-size: 14px;
}

/* 通用文本样式 */
.notification-list p {
  color: #b3b3b3;
  margin: 0;
  font-size: 12px;
  padding: 16px 14px;
  text-align: center;
}

/* 图标样式 */
.notification-item i {
  color: #999;
  font-size: 14px;
  margin-top: 1px;
}

/* 空状态样式 */
.empty-state {
  padding: 32px 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.empty-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.empty-icon i {
  font-size: 20px;
  color: #666;
}

.empty-text {
  color: #ffffff;
  font-size: 14px;
  font-weight: 500;
  margin: 0;
}

.empty-subtitle {
  color: #999;
  font-size: 11px;
  margin: 0;
  line-height: 1.3;
}
</style>