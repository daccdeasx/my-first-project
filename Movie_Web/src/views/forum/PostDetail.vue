<template>
  <div class="post-detail-container">
    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-state">
      <p>加载中...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <p>加载帖子失败：{{ error.message }}</p>
    </div>

    <!-- 内容显示 -->
    <div v-else-if="post" class="post-content">
      <div class="post-header">
        <h1 class="post-title">{{ post.title }}</h1>
        <div class="post-meta">
          <span class="post-author">作者：{{ post.username || '未知用户' }}</span>
          <span class="post-time">发布时间：{{ formatDate(post.created_at) }}</span>
        </div>
      </div>

      <!-- 帖子内容 -->
      <div class="post-body">
        <div v-html="post.content"></div>

        <!-- 图片展示区域 -->
        <div class="post-images-grid" v-if="post.images && post.images.length > 0">
          <div
            v-for="(image, index) in post.images"
            :key="image.id"
            class="post-image-item"
          >
            <img
              :src="image.image"
              :alt="`帖子图片 ${index + 1}`"
              class="post-image"
              loading="lazy"
              @error="handleImageError"
            />
          </div>
        </div>
      </div>

      <!-- 评论区域 -->
      <div class="comments">
        <h2>评论 ({{ replies.length }})</h2>

        <!-- 评论列表 -->
        <div v-if="replies.length" class="comment-list">
          <CommentItem
            v-for="reply in replies"
            :key="reply.id"
            :reply="reply"
            :post-id="postId"
            :format-date="formatDate"
            :activeReplyId="activeReplyId"
            :folded="foldStates[reply.id] || false"
            :fold-states="foldStates"
            @reply-submitted="handleReplySubmitted"
            @toggle-reply="toggleReplyForm"
            @toggle-fold="toggleFold"
          />
        </div>

        <!-- 暂无评论 -->
        <div v-else class="no-comments">
          <p>暂无评论，快来发表你的看法吧！</p>
        </div>

        <!-- 主评论表单 -->
        <div class="comment-form">
          <div class="form-header">
            <h3 class="form-title">发表评论</h3>
            <span class="char-count">{{ newReplyContent.length }}/500</span>
          </div>

          <div class="mention-container">
            <textarea
              v-model.trim="newReplyContent"
              @input="handleMention"
              placeholder="发表评论... @用户名 提及用户"
              rows="4"
              :class="{ 'error': commentError }"
              :maxlength="500"
              class="comment-textarea"
            ></textarea>

            <!-- 提及用户下拉框 -->
            <div
              v-if="mentionUsers.length > 0"
              class="mention-dropdown"
            >
              <div
                v-for="user in mentionUsers"
                :key="user.id"
                @click="selectMentionedUser(user)"
                class="mention-item"
              >
                <span class="mention-username">{{ user.username }}</span>
                <span class="mention-email">{{ user.email }}</span>
              </div>
            </div>
          </div>

          <div v-if="commentError" class="error-message">
            <svg class="error-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2"/>
              <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2"/>
            </svg>
            {{ commentError }}
          </div>

          <!-- 图片上传区域 -->
          <div class="image-upload-section">
            <div class="upload-controls">
              <div class="upload-button-wrapper">
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  @change="handleMainImageSelect"
                  class="upload-input"
                  id="main-image-upload"
                />
                <label
                  for="main-image-upload"
                  class="upload-button"
                >
                  <svg class="upload-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                    <circle cx="8.5" cy="8.5" r="1.5" stroke="currentColor" stroke-width="2"/>
                    <polyline points="21,15 16,10 5,21" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  选择图片
                </label>
              </div>
              <span class="upload-tip">
                支持JPG/PNG等图片格式
              </span>
            </div>

            <!-- 图片预览 -->
            <div class="image-preview-grid" v-if="mainPreviewImages.length > 0">
              <div
                v-for="preview in mainPreviewImages"
                :key="preview.id"
                class="image-preview-item"
              >
                <img
                  :src="preview.url"
                  alt="预览图"
                  class="preview-image"
                >
                <button
                  @click="removeMainSelectedImage(preview.index)"
                  class="remove-image-btn"
                  title="删除图片"
                >
                  ×
                </button>
              </div>
            </div>
          </div>

          <!-- 提交按钮 -->
          <div class="form-actions">
            <button
              @click="submitMainReply"
              :disabled="!newReplyContent.trim() && mainSelectedImages.length === 0 || isSubmitting"
              class="submit-btn"
            >
              <svg v-if="isSubmitting" class="loading-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-dasharray="31.416" stroke-dashoffset="31.416">
                  <animate attributeName="stroke-dasharray" dur="2s" values="0 31.416;15.708 15.708;0 31.416" repeatCount="indefinite"/>
                  <animate attributeName="stroke-dashoffset" dur="2s" values="0;-15.708;-31.416" repeatCount="indefinite"/>
                </circle>
              </svg>
              <svg v-else class="submit-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <line x1="22" y1="2" x2="11" y2="13" stroke="currentColor" stroke-width="2"/>
                <polygon points="22,2 15,22 11,13 2,9 22,2" stroke="currentColor" stroke-width="2"/>
              </svg>
              {{ isSubmitting ? '提交中...' : '提交评论' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <p>帖子不存在</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { fetchPost, createReply, fetchUserSuggestions } from '@/api/forum';
import CommentItem from '@/components/CommentItem.vue';
import { debounce as lodashDebounce } from 'lodash-es';

const route = useRoute();
const post = ref(null);
const replies = ref([]);
const isLoading = ref(true);
const error = ref(null);
const newReplyContent = ref('');
const commentError = ref('');
const isSubmitting = ref(false);
const activeReplyId = ref(null);
const foldStates = ref({});
const postId = ref(route.params.pk); // ✅ 从 route.params.pk 获取帖子ID

// 主评论图片选择
const mainSelectedImages = ref([]);

// 提及功能相关变量
const mentionUsers = ref([]);
const currentMention = ref('');
const mentionStartPos = ref(-1);

// 计算属性：生成并缓存图片预览URL
const mainPreviewImages = computed(() => {
  if (!window || !window.URL) return [];

  return mainSelectedImages.value.map((file, index) => ({
    id: `${file.name}_${index}_${file.size}`,
    url: window.URL.createObjectURL(file),
    index
  }));
});

// 处理主评论图片选择
const handleMainImageSelect = (e) => {
  const files = Array.from(e.target.files).filter(file =>
    file.type.startsWith('image/')
  );

  if (files.length === 0) {
    commentError.value = '请选择有效的图片文件';
    return;
  }

  commentError.value = '';
  mainSelectedImages.value = [...mainSelectedImages.value, ...files];
};

// 移除已选择的主评论图片
const removeMainSelectedImage = (index) => {
  if (window.URL && mainSelectedImages.value[index]) {
    window.URL.revokeObjectURL(mainSelectedImages.value[index].url);
  }

  mainSelectedImages.value.splice(index, 1);
};

// 处理图片加载错误
const handleImageError = (e) => {
  console.error(`图片加载失败: ${e.target.src}`);
  e.target.src = '/static/default-image.png'; // 确保有默认图片
  e.target.alt = '加载失败的图片';
};

// 提交主评论
const submitMainReply = lodashDebounce(async () => {
  const content = newReplyContent.value.trim();
  const images = mainSelectedImages.value;
  const hasContent = content.length > 0;
  const hasImages = images.length > 0;

  if (!hasContent && !hasImages) {
    commentError.value = '请输入评论内容或上传图片';
    return;
  }

  isSubmitting.value = true;
  commentError.value = '';

  try {
    const formData = new FormData();
    if (hasContent) formData.append('content', content);

    // 将图片字段名统一为'images'，与后端保持一致
    images.forEach((file) => {
      formData.append('images', file);
    });

    // 调用API创建评论
    const response = await createReply(postId.value, formData);

    // 构造新评论对象
    const newMainReply = {
      ...response.data,
      children: [],
    };

    // 避免重复添加
    if (!replies.value.some(reply => reply.id === newMainReply.id)) {
      replies.value.unshift(newMainReply);
      foldStates.value[newMainReply.id] = false;
    }

    // 重置表单
    newReplyContent.value = '';
    mainSelectedImages.value = [];
  } catch (err) {
    commentError.value = err.response?.data?.detail || '评论提交失败，请重试';
    console.error('提交主评论失败:', err);
  } finally {
    isSubmitting.value = false;
  }
}, 500);

// 处理子回复提交
const handleReplySubmitted = (newReply) => {
  // 强制初始化新评论的折叠状态
  foldStates.value[newReply.id] = false;

  // 递归查找父评论并插入
  const findAndInsert = (repliesArray) => {
    for (let i = 0; i < repliesArray.length; i++) {
      const reply = repliesArray[i];
      // 找到父评论
      if (reply.id === (newReply.parent_id || newReply.parent?.id)) {
        if (!reply.children.some(child => child.id === newReply.id)) {
          reply.children.push(newReply);
          return true;
        }
        return false;
      }
      // 递归搜索子评论
      if (reply.children.length && findAndInsert(reply.children)) {
        return true;
      }
    }
    return false;
  };

  // 执行搜索插入
  if (!findAndInsert(replies.value)) {
    // 未找到父评论则作为顶级评论
    replies.value.unshift(newReply);
  }

  // 展开父评论
  if (newReply.parent_id) {
    foldStates.value[newReply.parent_id] = false;
  }
};

// 切换回复表单显示状态
const toggleReplyForm = (replyId) => {
  activeReplyId.value = replyId;
};

// 切换评论折叠状态
const toggleFold = (replyId) => {
  foldStates.value[replyId] = !foldStates.value[replyId];
};

// 日期格式化函数
const formatDate = (dateStr) => {
  return dateStr ? new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  }) : '';
};

// 加载帖子数据
const loadPost = async () => {
  try {
    isLoading.value = true;
    error.value = null;

    if (!postId.value) throw new Error('帖子ID缺失');

    // ✅ 使用 postId.value（即 pk）
    const res = await fetchPost(postId.value);
    post.value = res.data;

    // 构建嵌套评论结构
    const rawReplies = post.value?.replies || [];
    replies.value = buildNestedReplies(rawReplies);
    initFoldStates(replies.value);
  } catch (err) {
    error.value = err.response?.data?.detail || '加载帖子失败，请重试';
    console.error('加载失败:', err);
  } finally {
    isLoading.value = false;
  }
};

// 构建嵌套评论结构
const buildNestedReplies = (allReplies) => {
  const replyMap = new Map();

  // 创建映射表并初始化children
  allReplies.forEach(reply => {
    reply.children = [];
    replyMap.set(reply.id, reply);
  });

  const rootReplies = [];

  allReplies.forEach(reply => {
    const parentId = reply.parent?.id || reply.parent_id;
    if (parentId && replyMap.has(parentId)) {
      const parent = replyMap.get(parentId);
      parent.children.push(reply);
    } else {
      rootReplies.push(reply);
    }
  });

  // 排序逻辑
  rootReplies.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  rootReplies.forEach(root => {
    root.children.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
  });

  return rootReplies;
};

// 初始化折叠状态
const initFoldStates = (replies) => {
  replies.forEach(reply => {
    foldStates.value[reply.id] = reply.children.length > 0;
    if (reply.children.length) {
      initFoldStates(reply.children);
    }
  });
};

// 监听路由变化重新加载数据（关键修改：监听 pk）
watch(
  () => route.params.pk, // ✅ 监听 pk 而非 id
  (newPk) => {
    postId.value = newPk;
    loadPost();
  },
  { immediate: true }
);

// 提及功能处理
const handleMention = lodashDebounce(async (e) => {
  const input = e.target.value;
  const cursorPos = e.target.selectionStart;

  // 重置状态
  mentionUsers.value = [];
  currentMention.value = '';
  mentionStartPos.value = -1;

  // 检测@符号
  const textBeforeCursor = input.substring(0, cursorPos);
  const atIndex = textBeforeCursor.lastIndexOf('@');

  if (atIndex > -1) {
    // 检查是否在单词中间
    const prevChar = textBeforeCursor.charAt(atIndex - 1);
    if (atIndex > 0 && !/\s/.test(prevChar)) return;

    const searchText = textBeforeCursor.substring(atIndex + 1).trim();
    mentionStartPos.value = atIndex + 1;

    if (searchText.length >= 2) {
      try {
        const res = await fetchUserSuggestions(searchText);
        mentionUsers.value = res.data.slice(0, 5); // 限制最多5个结果
        currentMention.value = searchText;
      } catch (error) {
        console.error('用户搜索失败:', error);
      }
    }
  }
}, 300);

// 选择用户
const selectMentionedUser = (user) => {
  if (mentionStartPos.value === -1) return;

  const textarea = document.querySelector('.mention-container textarea');
  const content = newReplyContent.value;

  // 替换@内容
  const newContent =
    content.substring(0, mentionStartPos.value - 1) + // 保留@符号前的内容
    `@${user.username} ` + // 插入完整用户名
    content.substring(mentionStartPos.value + currentMention.value.length);

  newReplyContent.value = newContent;

  // 重置状态
  mentionUsers.value = [];
  currentMention.value = '';
  mentionStartPos.value = -1;

  // 保持焦点
  textarea.focus();
  const newCursorPos = mentionStartPos.value - 1 + user.username.length + 2;
  setTimeout(() => {
    textarea.selectionStart = newCursorPos;
    textarea.selectionEnd = newCursorPos;
  }, 0);
};

// 点击外部关闭下拉框
const clickOutsideHandler = (e) => {
  const container = document.querySelector('.mention-container');
  if (!container.contains(e.target)) {
    mentionUsers.value = [];
  }
};

// 添加/移除事件监听
onMounted(() => {
  loadPost();
  window.addEventListener('click', clickOutsideHandler);
});

onUnmounted(() => {
  window.removeEventListener('click', clickOutsideHandler);
});
</script>

<style scoped>
/* 深色主题样式 */
.post-detail-container {
  min-height: 100vh;
  background: var(--dark-bg);
  color: var(--light-text);
  padding: 100px 20px 40px; /* 增加顶部距离 */
  max-width: 900px;
  margin: 0 auto;
}

/* 确保所有表单元素正确计算宽度 */
.post-detail-container *,
.post-detail-container *::before,
.post-detail-container *::after {
  box-sizing: border-box;
}

.post-header {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.post-title {
  font-size: 2rem;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 1rem;
  line-height: 1.3;
}

.post-meta {
  display: flex;
  gap: 1.5rem;
  font-size: 0.9rem;
  color: #b3b3b3;
}

.post-author {
  color: #d1d1d1;
}

.post-time {
  color: #999;
}

.post-body {
  line-height: 1.8;
  margin-bottom: 3rem;
  color: #e5e5e5;
  font-size: 1rem;
}

/* 帖子图片网格布局 */
.post-images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
  margin-top: 24px;
  max-width: 100%;
}

.post-image-item {
  position: relative;
  width: 100%;
  height: 150px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
}

.post-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: pointer;
  transition: all 0.3s ease;
}

.post-image:hover {
  transform: scale(1.05);
  filter: brightness(1.1);
}

.comments {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.comments h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 1.5rem;
}

.comment-list {
  margin-bottom: 2rem;
}

.no-comments {
  text-align: center;
  padding: 3rem 2rem;
  color: #b3b3b3;
  font-style: italic;
}

/* 评论表单样式 */
.comment-form {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 24px;
  margin-top: 2rem;
  backdrop-filter: blur(10px);
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.form-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.char-count {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.mention-container {
  position: relative;
  margin-bottom: 16px;
}

.comment-header {
  margin-bottom: 8px;
  font-size: 0.9em;
  color: #6b7280;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.comment-body {
  line-height: 1.6;
  padding: 10px;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #e5e7eb;
}

.comment-actions {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}

.reply-btn {
  padding: 6px 12px;
  background-color: #f3f4f6;
  color: #3b82f6;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  font-size: 0.9em;
  transition: all 0.2s ease;
}

.reply-btn:hover {
  background-color: #e5e7eb;
  color: #2563eb;
}

.reply-form-container {
  margin-top: 15px;
  padding: 15px;
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.reply-form-container textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  resize: vertical;
  min-height: 60px;
}

.reply-form-buttons {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.cancel-btn {
  padding: 8px 16px;
  background-color: #f3f4f6;
  color: #4b5563;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background-color: #e5e7eb;
}

.nested-replies {
  margin-left: 30px;
  padding-left: 15px;
  border-left: 2px dashed #e5e7eb;
  margin-top: 10px;
  max-height: 1000px;
  overflow: hidden;
  transition: max-height 0.3s ease-out;
}

.nested-replies.folded {
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
  margin-top: 0;
  margin-bottom: 0;
  opacity: 0;
}

.nested-reply {
  margin-bottom: 10px;
  padding: 12px;
  background-color: #ffffff;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.nested-reply-header {
  margin-bottom: 5px;
  font-size: 0.85em;
  color: #6b7280;
}

.nested-reply-body {
  line-height: 1.5;
  font-size: 0.95em;
}

.no-comments {
  padding: 20px;
  text-align: center;
  color: #6b7280;
  font-style: italic;
}

.comment-form,
.reply-form {
  margin-top: 20px;
}

/* 文本输入框样式 */
.comment-textarea {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #ffffff;
  resize: vertical;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  line-height: 1.5;
  min-height: 100px;
  font-family: inherit;
}

.comment-textarea::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.comment-textarea:focus {
  outline: none;
  border-color: #e50914;
  box-shadow: 0 0 0 2px rgba(229, 9, 20, 0.1);
  background: rgba(255, 255, 255, 0.12);
}

.comment-textarea.error {
  border-color: #ef4444;
  box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2);
}

/* 兼容回复表单 */
.reply-form-container textarea {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #ffffff;
  resize: vertical;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  line-height: 1.5;
  min-height: 80px;
  font-family: inherit;
}

.reply-form-container textarea::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.reply-form-container textarea:focus {
  outline: none;
  border-color: #e50914;
  box-shadow: 0 0 0 2px rgba(229, 9, 20, 0.1);
  background: rgba(255, 255, 255, 0.12);
}

.reply-form-container textarea.error {
  border-color: #ef4444;
  box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2);
}

/* 错误消息样式 */
.error-message {
  color: #ef4444;
  font-size: 0.85rem;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.error-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

/* 图片上传区域样式 */
.image-upload-section {
  margin-bottom: 20px;
}

.upload-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.upload-button-wrapper {
  position: relative;
}

.upload-input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.upload-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.85rem;
  font-weight: 500;
}

.upload-button:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;
}

.upload-icon {
  width: 16px;
  height: 16px;
}

.upload-tip {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
}

/* 图片预览网格 */
.image-preview-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 12px;
}

.image-preview-item {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-image-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 20px;
  height: 20px;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  transition: all 0.3s ease;
}

.remove-image-btn:hover {
  background: #e50914;
  transform: scale(1.1);
}

/* 表单操作区域 */
.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.submit-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #e50914;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 0.9rem;
  min-width: 120px;
  justify-content: center;
}

.submit-btn:hover:not(:disabled) {
  background: #b8070f;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(229, 9, 20, 0.3);
}

.submit-btn:disabled {
  background: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.5);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.loading-icon,
.submit-icon {
  width: 16px;
  height: 16px;
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 50px;
}

/* 新增图片上传区域样式 */
.image-upload-area {
  margin-top: 10px;
}

.image-upload-area .grid-cols-3 {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.5rem;
}

.image-upload-area .h-8 {
  height: 30px !important;
}

.image-upload-area .relative {
  position: relative;
}

.image-upload-area .rounded-sm {
  border-radius: 4px;
}

.image-upload-area .overflow-hidden {
  overflow: hidden;
}

.image-upload-area .border {
  border-width: 1px;
}

.image-upload-area .border-gray-100 {
  border-color: #f3f4f6;
}

.image-upload-area .absolute {
  position: absolute;
}

.image-upload-area .top-0 {
  top: 0;
}

.image-upload-area .right-0 {
  right: 0;
}

.image-upload-area .bg-black\/50 {
  background-color: rgba(0, 0, 0, 0.5);
}

.image-upload-area .text-white {
  color: white;
}

.image-upload-area .rounded-full {
  border-radius: 9999px;
}

.image-upload-area .w-4 {
  width: 12px;
}

.image-upload-area .h-4 {
  height: 12px;
}

.image-upload-area .flex {
  display: flex;
}

.image-upload-area .items-center {
  align-items: center;
}

.image-upload-area .justify-center {
  justify-content: center;
}

.image-upload-area .text-\[8px\] {
  font-size: 8px;
}

/* 评论图片（缩小尺寸） */
.comment-images .h-24 {
  height: 60px !important;
}

/* 折叠按钮样式 */
.fold-btn {
  display: flex;
  align-items: center;
  color: #6b7280;
  font-size: 0.9em;
  cursor: pointer;
  transition: color 0.2s ease;
}

.fold-btn:hover {
  color: #3b82f6;
}

.fold-btn i {
  margin-right: 5px;
  transition: transform 0.3s ease;
}

.fold-btn.folded i {
  transform: rotate(-90deg);
}

/* 提及功能样式 */
.mention-dropdown {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  background: #2a2a2a;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  max-height: 200px;
  overflow-y: auto;
  z-index: 50;
  margin-bottom: 4px;
}

.mention-item {
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.mention-item:hover {
  background: rgba(229, 9, 20, 0.1);
}

.mention-item:last-child {
  border-bottom: none;
}

.mention-username {
  font-weight: 600;
  color: #fff;
  font-size: 0.9rem;
}

.mention-email {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
}
</style>