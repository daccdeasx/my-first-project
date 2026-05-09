<template>
  <div class="create-post-page">
    <!-- 顶部导航 -->
    <div class="top-nav">
      <div class="nav-content">
        <router-link to="/forum" class="back-link">
          <i class="fas fa-arrow-left"></i>
          <span>返回论坛</span>
        </router-link>
        <h1 class="page-title">发布新帖</h1>
        <div class="nav-actions">
          <button
            type="button"
            @click="handleSubmit"
            class="publish-btn"
            :disabled="isSubmitting || !canPublish"
          >
            <i class="fas fa-paper-plane"></i>
            {{ isSubmitting ? '发布中...' : '发布' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <div class="content-wrapper">
        <!-- 编辑器区域 -->
        <div class="editor-section">
          <form @submit.prevent="handleSubmit" class="post-form">
            <!-- 标题输入 -->
            <div class="title-section">
              <input
                type="text"
                v-model.trim="form.title"
                required
                placeholder="请输入帖子标题..."
                class="title-input"
                :class="{ 'error': errors.title.length > 0 }"
              />
              <div v-if="errors.title.length > 0" class="error-text">{{ errors.title[0] }}</div>
            </div>

            <!-- 主题分类 -->
            <div class="category-section">
              <div class="category-label">选择分类：</div>
              <div class="category-options">
                <label
                  v-for="option in categoryOptions"
                  :key="option.value"
                  class="category-option"
                  :class="{ 'selected': form.theme === option.value }"
                >
                  <input
                    type="radio"
                    v-model="form.theme"
                    :value="option.value"
                    class="category-radio"
                  />
                  <span class="category-icon">{{ option.icon }}</span>
                  <span class="category-name">{{ option.label }}</span>
                </label>
              </div>
              <div v-if="errors.theme.length > 0" class="error-text">{{ errors.theme[0] }}</div>
            </div>

            <!-- 内容编辑器 -->
            <div class="content-section">
              <div class="editor-toolbar">
                <span class="toolbar-title">内容</span>
              </div>

              <textarea
                v-model.trim="form.content"
                required
                placeholder="分享你的观影心得、电影评价或讨论话题...

你可以：
• 分享最近看过的电影感受
• 推荐值得观看的影片
• 讨论电影相关话题
• 分享观影技巧和心得"
                class="content-textarea"
                :class="{ 'error': errors.content.length > 0 }"
                @input="updateCharCount"
              ></textarea>

              <div class="editor-footer">
                <div class="char-count">{{ contentLength }}/2000</div>
                <div v-if="errors.content.length > 0" class="error-text">{{ errors.content[0] }}</div>
              </div>
            </div>

            <!-- 图片上传区域 -->
            <div class="images-section">
              <div class="images-header">
                <span class="images-title">图片 ({{ uploadedImages.length }}/3)</span>
              </div>

              <div class="images-grid">
                <div
                  v-for="(img, index) in uploadedImages"
                  :key="index"
                  class="image-item"
                >
                  <img :src="img.preview" alt="预览" class="image-preview" />
                  <button type="button" @click="removeImage(index)" class="remove-image">
                    <i class="fas fa-times"></i>
                  </button>
                </div>

                <label class="add-image" v-if="uploadedImages.length < 3">
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    @change="handleImageUpload"
                    class="hidden-input"
                    ref="fileInput"
                  />
                  <i class="fas fa-plus"></i>
                  <span>添加图片</span>
                </label>
              </div>

              <div v-if="errors.images.length > 0" class="error-text">{{ errors.images[0] }}</div>
            </div>
          </form>
        </div>

        <!-- 侧边栏提示 -->
        <div class="sidebar-tips">
          <div class="tip-card">
            <h3>发帖小贴士</h3>
            <ul>
              <li>标题要简洁明了，突出重点</li>
              <li>内容要详细具体，方便讨论</li>
              <li>选择合适的分类便于他人发现</li>
              <li>可以添加相关图片增加趣味性</li>
            </ul>
          </div>

          <div class="tip-card">
            <h3>社区规范</h3>
            <ul>
              <li>保持友善，尊重他人观点</li>
              <li>禁止发布违法违规内容</li>
              <li>避免恶意刷屏和广告</li>
              <li>鼓励原创，注明转载来源</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- 全局错误提示 -->
    <div v-if="apiError" class="global-error">
      <div class="error-content">
        <i class="fas fa-exclamation-triangle"></i>
        <span>{{ apiError }}</span>
        <button @click="apiError = ''" class="close-error">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { createPost } from '@/api/forum';

const router = useRouter();

// 表单数据
const form = ref({
  title: '',
  content: '',
  theme: ''
});

// 分类选项
const categoryOptions = ref([
  { value: 'tech', label: '技术讨论', icon: '💻' },
  { value: 'life', label: '生活分享', icon: '🎬' },
  { value: 'entertainment', label: '娱乐八卦', icon: '🎭' },
  { value: 'other', label: '其他话题', icon: '💬' }
]);

// 状态管理
const uploadedImages = ref([]);
const isSubmitting = ref(false);
const fileInput = ref(null);

// 错误处理
const errors = ref({
  title: [],
  content: [],
  images: [],
  theme: []
});
const apiError = ref('');

// 计算属性
const contentLength = computed(() => form.value.content.length);
const canPublish = computed(() =>
  form.value.title.trim() &&
  form.value.content.trim() &&
  form.value.theme &&
  !isSubmitting.value
);

// 图片上传处理
const handleImageUpload = (e) => {
  const files = e.target.files;
  if (!files) return;

  const validFiles = [...uploadedImages.value]; // 保留已有图片
  const fileErrors = [];

  // 检查总数量限制
  const remainingSlots = 3 - uploadedImages.value.length;
  const filesToProcess = Array.from(files).slice(0, remainingSlots);

  if (files.length > remainingSlots) {
    fileErrors.push(`最多只能上传3张图片，已忽略多余的${files.length - remainingSlots}张图片`);
  }

  for (const file of filesToProcess) {
    if (!file.type.startsWith('image/')) {
      fileErrors.push('请上传图片文件（支持jpg/png等格式）');
      continue;
    }
    if (file.size > 5 * 1024 * 1024) { // 5MB 限制
      fileErrors.push(`文件 ${file.name} 超过 5MB 限制`);
      continue;
    }
    validFiles.push({ file, preview: URL.createObjectURL(file) });
  }

  uploadedImages.value = validFiles;
  errors.value.images = fileErrors;

  // 清空input，允许重复选择同一文件
  e.target.value = '';
};

// 移除图片
const removeImage = (index) => {
  uploadedImages.value.splice(index, 1);
};

// 更新字符计数
const updateCharCount = () => {
  // 字符计数在computed中自动更新
};

// 提交表单（新增 theme 字段到 FormData）
const handleSubmit = async () => {
  isSubmitting.value = true;
  errors.value = { title: [], content: [], images: [], theme: [] }; // 重置错误
  apiError.value = '';

  // 前端验证
  if (!form.value.title.trim()) {
    errors.value.title = ['标题不能为空'];
    isSubmitting.value = false;
    return;
  }

  if (!form.value.content.trim()) {
    errors.value.content = ['内容不能为空'];
    isSubmitting.value = false;
    return;
  }

  if (!form.value.theme) {
    errors.value.theme = ['请选择帖子主题'];
    isSubmitting.value = false;
    return;
  }

  // 构造FormData（包含 theme 字段）
  const formData = new FormData();
  formData.append('title', form.value.title.trim());
  formData.append('content', form.value.content.trim());
  formData.append('theme', form.value.theme); // 新增主题参数
  uploadedImages.value.forEach((item) => {
    formData.append('images', item.file);
  });

  try {
    const response = await createPost(formData);
    if (response.status === 201) {
      router.push('/forum');
    }
  } catch (error) {
    console.error('发布帖子失败:', error.response?.data);

    if (error.response?.status === 400) {
      const errorData = error.response.data;
      errors.value.title = errorData.title || [];
      errors.value.content = errorData.content || [];
      errors.value.images = errorData.images || [];
      errors.value.theme = errorData.theme || []; // 处理主题错误

      apiError.value = '请检查表单：标题、内容、主题是否完整，图片格式是否正确';
    } else if (error.response?.status === 401) {
      apiError.value = '请登录后发布帖子';
      router.push('/login');
    } else {
      apiError.value = '发布失败，请联系管理员';
    }
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
/* 全新发帖页面样式 */
.create-post-page {
  min-height: 100vh;
  background: #141414;
  color: #ffffff;
}

/* 顶部导航栏 */
.top-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: rgba(20, 20, 20, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 1000;
  height: 64px;
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.back-link {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #b3b3b3;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.2s ease;
}

.back-link:hover {
  color: #ffffff;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
}

.nav-actions .publish-btn {
  background: #e50914;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-actions .publish-btn:hover:not(:disabled) {
  background: #f40612;
  transform: translateY(-1px);
}

.nav-actions .publish-btn:disabled {
  background: #666;
  cursor: not-allowed;
  transform: none;
}

/* 主要内容区域 */
.main-content {
  padding-top: 64px;
  min-height: calc(100vh - 64px);
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 24px;
}

.editor-section {
  min-width: 0;
  overflow: hidden;
}

.post-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 标题输入 */
.title-section {
  margin-bottom: 0;
}

.title-input {
  width: 100%;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
  font-family: inherit;
}

.title-input::placeholder {
  color: #666;
  font-weight: 400;
}

.title-input:focus {
  outline: none;
  border-color: #e50914;
  box-shadow: 0 0 0 3px rgba(229, 9, 20, 0.1);
  background: rgba(255, 255, 255, 0.08);
}

.title-input.error {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

/* 分类选择 */
.category-section {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 16px;
}

.category-label {
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
}

.category-options {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.category-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 13px;
}

.category-option:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
}

.category-option.selected {
  background: rgba(229, 9, 20, 0.1);
  border-color: #e50914;
}

.category-radio {
  display: none;
}

.category-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.category-name {
  color: #ffffff;
  font-size: 13px;
  font-weight: 500;
}

/* 内容编辑器 */
.content-section {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.toolbar-title {
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
}

.toolbar-actions {
  display: none;
}

.content-textarea {
  width: 100%;
  box-sizing: border-box;
  background: transparent;
  border: none;
  color: #ffffff;
  padding: 16px;
  font-size: 14px;
  line-height: 1.6;
  resize: none;
  min-height: 200px;
  font-family: inherit;
}

.content-textarea::placeholder {
  color: #666;
  line-height: 1.6;
}

.content-textarea:focus {
  outline: none;
}

.content-textarea.error {
  background: rgba(239, 68, 68, 0.05);
}

.editor-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.02);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.char-count {
  color: #b3b3b3;
  font-size: 12px;
}

/* 图片上传区域 */
.images-section {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 16px;
}

.images-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.images-title {
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
}

.close-images {
  background: none;
  border: none;
  color: #b3b3b3;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.2s ease;
}

.close-images:hover {
  color: #ffffff;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  max-width: 400px;
}

.image-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 6px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.05);
}

.image-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-image {
  position: absolute;
  top: 6px;
  right: 6px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  transition: background 0.2s ease;
}

.remove-image:hover {
  background: #e50914;
}

.add-image {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  aspect-ratio: 1;
  background: rgba(255, 255, 255, 0.05);
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #b3b3b3;
  font-size: 11px;
  gap: 4px;
}

.add-image:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.3);
  color: #ffffff;
}

.add-image i {
  font-size: 16px;
}

.hidden-input {
  display: none;
}

/* 侧边栏提示 */
.sidebar-tips {
  position: sticky;
  top: 88px;
  height: fit-content;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tip-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 16px;
}

.tip-card h3 {
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.tip-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tip-card li {
  color: #b3b3b3;
  font-size: 13px;
  line-height: 1.4;
  margin-bottom: 6px;
  padding-left: 14px;
  position: relative;
}

.tip-card li:before {
  content: '•';
  color: #e50914;
  position: absolute;
  left: 0;
  font-weight: bold;
}

.tip-card li:last-child {
  margin-bottom: 0;
}

/* 错误提示 */
.error-text {
  color: #ef4444;
  font-size: 13px;
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.global-error {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1001;
  max-width: 500px;
  width: 90%;
}

.error-content {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: #ef4444;
  backdrop-filter: blur(20px);
}

.close-error {
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  margin-left: auto;
  transition: background 0.2s ease;
}

.close-error:hover {
  background: rgba(239, 68, 68, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content-wrapper {
    grid-template-columns: 1fr;
    gap: 24px;
    padding: 24px 16px;
  }

  .sidebar-tips {
    position: static;
    order: -1;
  }

  .category-options {
    grid-template-columns: 1fr;
  }

  .title-input {
    font-size: 18px;
    padding: 14px 16px;
  }

  .content-textarea {
    min-height: 250px;
    padding: 16px;
  }

  .nav-content {
    padding: 0 16px;
  }

  .page-title {
    font-size: 16px;
  }

  .back-link span {
    display: none;
  }
}
</style>