<template>
  <div class="comment-container">
    <div class="comment-card">
      <!-- 评论头部 -->
      <div class="comment-header">
        <div class="comment-user-info">
          <h4 class="comment-username">
            {{ reply.username || '匿名用户' }}
          </h4>
          <p class="comment-time">
            {{ formatDate(reply.created_at) }}
          </p>
        </div>
        <!-- 折叠按钮 -->
        <div v-if="reply.children && reply.children.length > 0">
          <button
            @click="toggleFold(reply.id)"
            class="fold-btn flex items-center text-sm text-gray-500 hover:text-blue-600 transition-colors duration-200"
            :class="{ 'folded': folded }"
          >
            <i class="fa fa-chevron-down mr-1.5 transition-transform duration-300" :style="{ transform: folded ? 'rotate(-90deg)' : 'rotate(0)' }"></i>
            <span>{{ folded ? '展开' : '收起' }}回复 ({{ reply.children.length }})</span>
          </button>
        </div>
      </div>

      <!-- 评论内容 -->
      <div class="comment-content">
        <p>{{ reply.content }}</p>

        <!-- 评论图片 -->
        <div class="comment-images-grid" v-if="reply.images && reply.images.length > 0">
          <div
            v-for="(image, index) in reply.images"
            :key="image.id || `image-${index}`"
            class="comment-image-item"
          >
            <img
              :src="image.image"
              :alt="`评论图片 ${index + 1}`"
              class="comment-image"
              @error="handleImageError"
            >
          </div>
        </div>
      </div>

      <!-- 评论操作区 -->
      <div class="comment-actions">
        <button
          @click="toggleReplyForm(reply.id)"
          class="reply-btn"
        >
          <svg class="reply-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 10h10a8 8 0 0 1 8 8v2M3 10l6 6m-6-6l6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          回复
        </button>
      </div>

      <!-- 回复表单 -->
      <div v-if="activeReplyId === reply.id" class="reply-form-container">
        <div class="reply-form-header">
          <h4 class="reply-form-title">回复 {{ reply.username || '用户' }}</h4>
          <span class="reply-char-count">{{ replyContent.length }}/500</span>
        </div>

        <div class="reply-form-content">
          <textarea
            v-model.trim="replyContent"
            placeholder="发表回复..."
            rows="3"
            class="reply-textarea"
            :class="{ 'error': replyError }"
            :maxlength="500"
          ></textarea>

          <!-- 错误提示 -->
          <div v-if="replyError" class="reply-error-message">
            <svg class="error-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2"/>
              <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2"/>
            </svg>
            {{ replyError }}
          </div>

          <!-- 图片上传区域 -->
          <div class="reply-image-upload-section">
            <div class="reply-upload-controls">
              <div class="reply-upload-button-wrapper">
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  @change="handleImageSelect"
                  class="upload-input"
                  :id="'image-upload-' + reply.id"
                />
                <label
                  :for="'image-upload-' + reply.id"
                  class="reply-upload-button"
                >
                  <svg class="upload-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                    <circle cx="8.5" cy="8.5" r="1.5" stroke="currentColor" stroke-width="2"/>
                    <polyline points="21,15 16,10 5,21" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  选择图片
                </label>
              </div>
              <span class="reply-upload-tip">
                支持JPG/PNG等图片格式
              </span>
            </div>

            <!-- 图片预览 -->
            <div class="reply-image-preview-grid" v-if="previewImages.length > 0">
              <div
                v-for="preview in previewImages"
                :key="preview.id"
                class="reply-image-preview-item"
              >
                <img
                  :src="preview.url"
                  alt="预览图"
                  class="reply-preview-image"
                >
                <button
                  @click="removeSelectedImage(preview.index)"
                  class="reply-remove-image-btn"
                  title="删除图片"
                >
                  ×
                </button>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="reply-form-actions">
            <button
              @click="cancelReply"
              class="reply-cancel-btn"
            >
              取消
            </button>
            <button
              @click="submitReply(reply.id)"
              :disabled="!replyContent.trim() && selectedImages.length === 0 || isSubmitting"
              class="reply-submit-btn"
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
              {{ isSubmitting ? '提交中...' : '发表回复' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 子回复区域 -->
      <div
        class="nested-replies pl-6 border-l-2 border-gray-100 ml-4 mt-4 transition-all duration-300"
        v-if="reply.children && reply.children.length > 0"
        :style="{
          maxHeight: folded ? '0px' : '1000px',
          opacity: folded ? '0' : '1',
          paddingTop: folded ? '0' : '10px',
          paddingBottom: folded ? '0' : '10px'
        }"
      >
        <CommentItem
          v-for="child in reply.children"
          :key="child.id"
          :reply="child"
          :format-date="formatDate"
          :activeReplyId="activeReplyId"
          :folded="foldStates[child.id] || false"
          :fold-states="foldStates"
          :post-id="postId"
          @reply-submitted="handleReplySubmitted"
          @toggle-reply="toggleReplyForm"
          @toggle-fold="toggleFold"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue';
import { createReply } from '@/api/forum';
import { debounce } from 'lodash-es';

const props = defineProps({
  reply: { type: Object, required: true },
  activeReplyId: { type: Number, default: null },
  formatDate: { type: Function, required: true },
  folded: { type: Boolean, default: false },
  postId: { type: String, required: true },
  foldStates: { type: Object, required: true }
});

const emit = defineEmits([
  'reply-submitted',
  'toggle-reply',
  'toggle-fold'
]);

// 回复表单状态
const replyContent = ref('');
const replyError = ref('');
const isSubmitting = ref(false);
const selectedImages = ref([]);

// 回复表单图片选择（无限制）

// 计算属性：生成并缓存图片预览URL
const previewImages = computed(() => {
  if (!window || !window.URL) return [];

  return selectedImages.value.map((file, index) => ({
    id: `${file.name}_${index}_${file.size}`,
    url: window.URL.createObjectURL(file),
    index
  }));
});

// 处理图片选择
const handleImageSelect = (e) => {
  const files = Array.from(e.target.files).filter(file =>
    file.type.startsWith('image/')
  );

  if (files.length === 0) {
    replyError.value = '请选择有效的图片文件';
    return;
  }

  replyError.value = '';
  selectedImages.value = [...selectedImages.value, ...files];
};

// 移除已选择的图片
const removeSelectedImage = (index) => {
  if (window.URL && selectedImages.value[index]) {
    window.URL.revokeObjectURL(selectedImages.value[index].url);
  }

  selectedImages.value.splice(index, 1);
};

// 处理图片加载错误
const handleImageError = (e) => {
  console.error(`图片加载失败: ${e.target.src}`);
  e.target.src = '/static/default-image.png'; // 确保有默认图片
  e.target.alt = '加载失败的图片';
};

// 提交回复
const submitReply = debounce(async (parentId) => {
  const content = replyContent.value.trim();
  const images = selectedImages.value;

  // 验证内容和图片
  if (!content && images.length === 0) {
    replyError.value = '请输入回复内容或上传图片';
    return;
  }

  isSubmitting.value = true;
  replyError.value = '';

  try {
    const formData = new FormData();
    formData.append('content', content);
    formData.append('parent_id', parentId);

    // 修复：将图片字段名统一为'images'，与后端保持一致
    images.forEach((file) => {
      formData.append('images', file);
    });

    // 调用API创建回复
    const response = await createReply(props.postId, formData);

    // 添加调试日志
    console.log('API返回的回复数据:', response.data);

    // 构造新回复对象
    const newReply = {
      ...response.data,
      parent: { id: parentId },
      children: [],
      created_at: new Date().toISOString(),
    };

    // 通知父组件处理新回复
    emit('reply-submitted', newReply);

    // 重置表单
    resetReplyForm();
  } catch (err) {
    replyError.value = err.response?.data?.detail || '回复提交失败，请重试';
    console.error('提交回复失败:', err);
  } finally {
    isSubmitting.value = false;
  }
}, 500);

// 取消回复
const cancelReply = () => {
  resetReplyForm();
};

// 重置回复表单
const resetReplyForm = () => {
  if (window.URL) {
    selectedImages.value.forEach(file => {
      window.URL.revokeObjectURL(file.url);
    });
  }

  replyContent.value = '';
  selectedImages.value = [];
  replyError.value = '';
  emit('toggle-reply', null);
};

// 切换回复表单显示状态
const toggleReplyForm = (replyId) => {
  emit('toggle-reply', replyId);
};

// 切换折叠状态
const toggleFold = (replyId) => {
  emit('toggle-fold', replyId);
};

// 处理子回复提交
const handleReplySubmitted = (newReply) => {
  if (props.reply.id === newReply.parent?.id) {
    if (!props.reply.children.some(child => child.id === newReply.id)) {
      props.reply.children.push(newReply);
      emit('toggle-fold', props.reply.id);
    }
  }
};
</script>
<style scoped>
.comment-container {
  margin-bottom: 1.5rem;
}

.comment-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1rem;
  transition: all 0.3s ease;
}

.comment-card:hover {
  background: #2a2a2a;
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.comment-user-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.comment-username {
  color: #ffffff;
  font-weight: 600;
  font-size: 1rem;
  margin: 0;
}

.comment-time {
  color: #b3b3b3;
  font-size: 0.8rem;
  margin: 0;
}

.comment-content {
  color: #e5e5e5;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.comment-content p {
  margin: 0;
}

/* 评论图片网格布局 */
.comment-images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
  margin-top: 16px;
  max-width: 100%;
}

.comment-image-item {
  position: relative;
  width: 100%;
  height: 120px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
}

.comment-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: pointer;
  transition: all 0.3s ease;
}

.comment-image:hover {
  transform: scale(1.05);
  filter: brightness(1.1);
}

.comment-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-top: 12px;
}

.reply-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.reply-btn:hover {
  color: #e50914;
  background: rgba(229, 9, 20, 0.1);
  transform: translateY(-1px);
}

.reply-icon {
  width: 14px;
  height: 14px;
}

/* 回复表单样式 */
.reply-form-container {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 20px;
  margin-top: 16px;
  backdrop-filter: blur(10px);
}

.reply-form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.reply-form-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.reply-char-count {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.reply-form-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reply-textarea {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: #ffffff;
  resize: vertical;
  transition: all 0.3s ease;
  font-size: 0.85rem;
  line-height: 1.5;
  min-height: 80px;
  font-family: inherit;
}

.reply-textarea::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.reply-textarea:focus {
  outline: none;
  border-color: #e50914;
  box-shadow: 0 0 0 2px rgba(229, 9, 20, 0.1);
  background: rgba(255, 255, 255, 0.12);
}

.reply-textarea.error {
  border-color: #ef4444;
  box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2);
}

.reply-error-message {
  color: #ef4444;
  font-size: 0.8rem;
  padding: 8px 12px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}

.reply-error-message .error-icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

/* 图片上传区域样式 */
.reply-image-upload-section {
  margin-bottom: 12px;
}

.reply-upload-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.reply-upload-button-wrapper {
  position: relative;
}

.upload-input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.reply-upload-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.8rem;
  font-weight: 500;
}

.reply-upload-button:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;
}

.upload-icon {
  width: 14px;
  height: 14px;
}

.reply-upload-tip {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.5);
}

/* 图片预览网格 */
.reply-image-preview-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: 8px;
}

.reply-image-preview-item {
  position: relative;
  width: 60px;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.reply-preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.reply-remove-image-btn {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 16px;
  height: 16px;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: bold;
  transition: all 0.3s ease;
}

.reply-remove-image-btn:hover {
  background: #e50914;
  transform: scale(1.1);
}

/* 表单操作区域 */
.reply-form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 12px;
}

.reply-cancel-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.8rem;
  font-weight: 500;
}

.reply-cancel-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.reply-submit-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #e50914;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 0.8rem;
  min-width: 80px;
  justify-content: center;
}

.reply-submit-btn:hover:not(:disabled) {
  background: #b8070f;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(229, 9, 20, 0.3);
}

.reply-submit-btn:disabled {
  background: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.5);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.loading-icon,
.submit-icon {
  width: 12px;
  height: 12px;
}

.nested-replies {
  margin-left: 1.5rem;
  padding-left: 1rem;
  border-left: 2px solid rgba(229, 9, 20, 0.3);
  overflow: hidden;
  transition: all 0.3s ease;
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}

.error-message {
  display: flex;
  align-items: center;
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
  padding: 8px 12px;
  border-radius: 6px;
  gap: 0.5rem;
}

.fold-btn {
  display: flex;
  align-items: center;
  color: #b3b3b3;
  font-size: 0.9em;
  cursor: pointer;
  transition: color 0.2s ease;
  background: none;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
}

.fold-btn:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
}

.fold-btn i {
  margin-right: 5px;
  transition: transform 0.3s ease;
}

.fold-btn.folded i {
  transform: rotate(-90deg);
}

.reply-form {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 1rem;
  margin-top: 1rem;
}

@media (max-width: 640px) {
  .nested-replies {
    margin-left: 1rem;
    padding-left: 0.75rem;
  }
}
</style>