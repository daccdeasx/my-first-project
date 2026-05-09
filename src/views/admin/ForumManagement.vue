<template>
  <div class="admin-forum-container">
    <!-- 页面标题 -->
    <div class="forum-header">
      <h1 class="forum-title">论坛管理</h1>
      <p class="forum-subtitle">管理用户发布的帖子内容</p>
    </div>

    <!-- 顶部操作栏 - 只在有选中项时显示 -->
    <div v-if="selectedPosts.length > 0" class="action-bar">
      <!-- 批量操作按钮 -->
      <div class="batch-actions">
        <span class="selected-info">已选择 {{ selectedPosts.length }} 项</span>
        <button
          @click="handleBatchApprove"
          class="batch-btn approve-btn"
        >
          批量通过
        </button>
        <button
          @click="handleBatchDelete"
          class="batch-btn delete-btn"
        >
          批量删除
        </button>
        <button
          @click="selectedPosts = []"
          class="batch-btn cancel-btn"
        >
          取消选择
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <span class="loading-text">加载中...</span>
      </div>
    </div>

    <!-- 状态筛选栏 -->
    <div class="status-filter">
      <button
        v-for="status in statusOptions"
        :key="status.value"
        :class="{ 'active': selectedStatus === status.value }"
        @click="handleStatusChange(status.value)"
        class="filter-btn"
      >
        {{ status.label }}
      </button>
    </div>

    <!-- 帖子列表组件 -->
    <PostTable
      :posts="posts"
      :isEditable="true"
      :selectedPosts="selectedPosts"
      @select="handlePostSelect"
      @select-all="handleSelectAll"
      @approve="handleApprovePost"
      @reject="handleRejectPost"
      @toggle-pin="handleTogglePin"
      @delete="handleDeletePost"
      @view-details="handleViewDetails"
    />

    <!-- 分页控件 -->
    <div class="pagination-container">
      <div class="pagination-info">
        <span class="info-text">
          共 {{ totalCount }} 条记录，第 {{ currentPage }} / {{ totalPages }} 页
        </span>
      </div>

      <div class="pagination-controls">
        <button
          :disabled="currentPage === 1"
          @click="gotoFirstPage"
          class="page-btn"
          :class="{ 'disabled': currentPage === 1 }"
        >
          首页
        </button>
        <button
          :disabled="currentPage === 1"
          @click="prevPage"
          class="page-btn"
          :class="{ 'disabled': currentPage === 1 }"
        >
          上一页
        </button>
        <button
          :disabled="currentPage === totalPages"
          @click="nextPage"
          class="page-btn"
          :class="{ 'disabled': currentPage === totalPages }"
        >
          下一页
        </button>
        <button
          :disabled="currentPage === totalPages"
          @click="gotoLastPage"
          class="page-btn"
          :class="{ 'disabled': currentPage === totalPages }"
        >
          末页
        </button>
      </div>
    </div>

    <!-- 拒绝理由对话框 -->
    <dialog ref="rejectDialog" class="dialog">
      <h3 class="text-lg font-medium mb-4">请输入拒绝理由</h3>
      <textarea
        v-model.trim="rejectReason"
        class="w-full h-32 px-3 py-2 border rounded-md mb-4"
        placeholder="请详细说明拒绝原因（必填）"
        :rows="4"
        required
      ></textarea>
      <div class="flex justify-end gap-4">
        <button
          @click="cancelReject"
          class="px-4 py-2 border rounded-md text-gray-700 hover:bg-gray-100"
        >
          取消
        </button>
        <button
          @click="confirmReject"
          class="px-4 py-2 bg-red-600 text-white border-red-600 rounded-md hover:bg-red-700"
        >
          确认拒绝
        </button>
      </div>
    </dialog>

    <!-- 帖子详情对话框 -->
    <dialog ref="detailsDialog" class="dialog">
      <h3 class="text-lg font-medium mb-4">帖子详情</h3>
      <div v-if="currentPost" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">标题</label>
          <p class="mt-1 text-gray-900">{{ currentPost.title }}</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">作者</label>
          <p class="mt-1 text-gray-900">{{ currentPost.author || '未知用户' }}</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">内容</label>
          <p class="mt-1 text-gray-900 whitespace-pre-wrap">{{ currentPost.content }}</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">状态</label>
          <p class="mt-1 text-gray-900">{{ mapStatus(currentPost.status) }}</p>
        </div>
        <div v-if="currentPost.status === 'rejected' && currentPost.reject_reason">
          <label class="block text-sm font-medium text-gray-700">拒绝理由</label>
          <p class="mt-1 text-gray-900">{{ currentPost.reject_reason }}</p>
        </div>
      </div>
      <div class="mt-6 flex justify-end">
        <button
          @click="closeDetails"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
        >
          关闭
        </button>
      </div>
    </dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import {
  fetchAllPosts,
  approvePost,
  rejectPost,
  togglePinPost,
  deletePost,
  fetchPost
} from '@/api/forum.js';
import PostTable from '@/components/admin/PostTable.vue';
import { useToast } from '@/composables/useToast';
import request from '@/utils/request';

const { showSuccess, showError } = useToast();

// 状态选项
const statusOptions = ref([
  { value: 'all', label: '全部' },
  { value: 'pending', label: '待审核' },
  { value: 'approved', label: '已通过' },
  { value: 'rejected', label: '已拒绝' }
]);

// 分页状态
const currentPage = ref(1);
const totalPages = ref(1);
const totalCount = ref(0);
const pageSize = 10;

// 响应式数据
const posts = ref([]);
const selectedPosts = ref([]);
const selectedStatus = ref('all');
const rejectDialog = ref(null);
const rejectReason = ref('');
const currentPostId = ref(null);
const isLoading = ref(true);

// 帖子详情相关
const detailsDialog = ref(null);
const currentPost = ref(null);

// 加载帖子（带分页）
const loadPosts = async (page = 1) => {
  isLoading.value = true;
  try {
    const response = await fetchAllPosts(selectedStatus.value, page);
    console.log('帖子数据:', response.data);
    if (response.data && response.data.results) {
      posts.value = response.data.results;
      currentPage.value = page;
      totalCount.value = response.data.count || 0;
      totalPages.value = Math.ceil(totalCount.value / pageSize);
    } else {
      posts.value = [];
      totalCount.value = 0;
      totalPages.value = 1;
    }
  } catch (error) {
    console.error('加载帖子失败:', error);
    showError('加载帖子失败，请稍后重试');
    posts.value = [];
    totalCount.value = 0;
    totalPages.value = 1;
  } finally {
    isLoading.value = false;
  }
};

// 帖子选择处理
const handlePostSelect = (postId) => {
  const index = selectedPosts.value.indexOf(postId);
  if (index === -1) {
    selectedPosts.value.push(postId);
  } else {
    selectedPosts.value.splice(index, 1);
  }
};

const handleSelectAll = (isSelected) => {
  if (isSelected) {
    selectedPosts.value = posts.value.map(post => post.id);
  } else {
    selectedPosts.value = [];
  }
};

// 批量操作
const handleBatchApprove = async () => {
  if (!confirm(`确定要通过选中的 ${selectedPosts.value.length} 个帖子吗？`)) return;

  try {
    await Promise.all(selectedPosts.value.map(id => approvePost(id)));
    showSuccess('批量通过成功');
    selectedPosts.value = [];
    loadPosts(currentPage.value);
  } catch (error) {
    console.error('批量通过失败:', error);
    showError('批量通过失败，请稍后重试');
  }
};

const handleBatchDelete = async () => {
  if (!confirm(`确定要删除选中的 ${selectedPosts.value.length} 个帖子吗？此操作不可恢复！`)) return;

  try {
    await Promise.all(selectedPosts.value.map(id => deletePost(id)));
    showSuccess('批量删除成功');
    selectedPosts.value = [];
    loadPosts(currentPage.value);
  } catch (error) {
    console.error('批量删除失败:', error);
    showError('批量删除失败，请稍后重试');
  }
};

// 分页操作
const gotoFirstPage = () => handlePageChange(1);
const prevPage = () => handlePageChange(currentPage.value - 1);
const nextPage = () => handlePageChange(currentPage.value + 1);
const gotoLastPage = () => handlePageChange(totalPages.value);

const handlePageChange = (page) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  loadPosts(page);
};

// 状态筛选
const handleStatusChange = (status) => {
  selectedStatus.value = status;
  currentPage.value = 1;
  loadPosts(1);
};

// 审核通过
const handleApprovePost = async (postId) => {
  try {
    await approvePost(postId);
    showSuccess('审核通过成功');
    loadPosts(currentPage.value);
  } catch (error) {
    console.error('审核通过失败:', error);
    showError('审核通过失败，请稍后重试');
  }
};

// 拒绝处理
const handleRejectPost = (postId) => {
  currentPostId.value = postId;
  rejectReason.value = '';
  rejectDialog.value.showModal();
};

// 确认拒绝
const confirmReject = async () => {
  if (!rejectReason.value) {
    showError('请输入拒绝理由');
    return;
  }

  try {
    // 发送拒绝请求
    await rejectPost(currentPostId.value, rejectReason.value);

    // 获取被拒绝的帖子信息
    const rejectedPost = posts.value.find(post => post.id === currentPostId.value);
    if (!rejectedPost) {
      throw new Error('未找到帖子信息');
    }

    try {
      // 发送通知
      const response = await request.post('/users/notifications/', {
        type: 'post_rejected',
        title: '帖子被拒绝',
        content: `您的帖子"${rejectedPost.title}"被管理员拒绝。\n拒绝理由：${rejectReason.value}`,
        user_id: rejectedPost.author_id,
        post_id: currentPostId.value,
        post: {
          id: rejectedPost.id,
          title: rejectedPost.title,
          content: rejectedPost.content,
          author: rejectedPost.author,
          author_id: rejectedPost.author_id,
          status: 'rejected',
          reject_reason: rejectReason.value
        }
      });

      if (!response.data) {
        throw new Error('通知发送失败');
      }
    } catch (notificationError) {
      console.error('发送通知失败:', notificationError);
      showError(`通知发送失败: ${notificationError.message}`);
    }

    showSuccess('拒绝成功');
    rejectDialog.value.close();

    // 更新帖子列表
    const updatedPosts = posts.value.map(post => {
      if (post.id === currentPostId.value) {
        return {
          ...post,
          status: 'rejected',
          reject_reason: rejectReason.value
        };
      }
      return post;
    });
    posts.value = updatedPosts;
    rejectReason.value = '';
  } catch (error) {
    console.error('拒绝失败:', error);
    showError(error.message || '拒绝失败，请稍后重试');
  }
};

// 取消拒绝
const cancelReject = () => {
  rejectDialog.value.close();
  rejectReason.value = '';
};

// 置顶处理
const handleTogglePin = async (postId) => {
  try {
    await togglePinPost(postId);
    showSuccess('置顶状态已更新');
    loadPosts(currentPage.value);
  } catch (error) {
    console.error('置顶操作失败:', error);
    showError('置顶操作失败，请稍后重试');
  }
};

// 删除帖子
const handleDeletePost = async (postId) => {
  if (!confirm('确定要删除该帖子吗？此操作不可恢复')) return;

  try {
    await deletePost(postId);
    showSuccess('删除成功');
    loadPosts(currentPage.value);
  } catch (error) {
    console.error('删除帖子失败:', error);
    showError('删除失败，请稍后重试');
  }
};

// 获取帖子详情
const handleViewDetails = async (postId) => {
  try {
    const response = await fetchPost(postId);
    if (!response.data) {
      throw new Error('未获取到帖子数据');
    }

    // 确保帖子数据包含必要的字段
    currentPost.value = {
      ...response.data,
      author: response.data.author || response.data.username || '未知用户',
      author_id: response.data.author_id || response.data.user_id
    };

    detailsDialog.value.showModal();
  } catch (error) {
    console.error('获取帖子详情失败:', error);
    showError('获取帖子详情失败，请稍后重试');
  }
};

const closeDetails = () => {
  detailsDialog.value.close();
  currentPost.value = null;
};

// 状态映射
const mapStatus = (status) => {
  return {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝'
  }[status] || '未知';
};

// 初始加载
onMounted(() => {
  loadPosts();
});
</script>

<style scoped>
.admin-forum-container {
  padding: 0;
  background: #f5f7fa;
  min-height: calc(100vh - 56px);
}

/* 页面标题 */
.forum-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.forum-title {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 4px 0;
}

.forum-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

/* 操作栏 */
.action-bar {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  padding: 16px;
  margin-bottom: 16px;
  transition: all 0.3s;
}

.batch-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.selected-info {
  color: #606266;
  font-size: 14px;
  font-weight: 500;
  margin-right: 8px;
}

.batch-btn {
  padding: 8px 16px;
  border: 1px solid;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  background: transparent;
}

.approve-btn {
  color: #67c23a;
  border-color: #67c23a;
}

.approve-btn:hover {
  background: #67c23a;
  color: #ffffff;
}

.delete-btn {
  color: #f56c6c;
  border-color: #f56c6c;
}

.delete-btn:hover {
  background: #f56c6c;
  color: #ffffff;
}

.cancel-btn {
  color: #909399;
  border-color: #dcdfe6;
}

.cancel-btn:hover {
  background: #f5f7fa;
  border-color: #c0c4cc;
}

/* 状态筛选 */
.status-filter {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  padding: 16px;
  margin-bottom: 16px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 8px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background: #ffffff;
  color: #606266;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-btn:hover {
  border-color: #409eff;
  color: #409eff;
}

.filter-btn.active {
  background: #409eff;
  border-color: #409eff;
  color: #ffffff;
}

/* 加载状态 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
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
  border: 3px solid #e4e7ed;
  border-top: 3px solid #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  color: #606266;
  font-size: 14px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

/* 分页样式 */
.pagination-container {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  padding: 16px;
  margin-top: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-info {
  display: flex;
  align-items: center;
}

.info-text {
  color: #606266;
  font-size: 14px;
}

.pagination-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #ffffff;
  color: #606266;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-btn:hover:not(.disabled) {
  border-color: #409eff;
  color: #409eff;
}

.page-btn.disabled {
  background: #f5f7fa;
  color: #c0c4cc;
  border-color: #e4e7ed;
  cursor: not-allowed;
}

.dialog {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 32px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 400px;
}

@media (max-width: 768px) {
  .admin-forum-container {
    padding: 16px;
  }

  .batch-actions {
    flex-wrap: wrap;
    gap: 8px;
  }

  .selected-info {
    width: 100%;
    margin-bottom: 8px;
  }

  .status-filter {
    flex-wrap: wrap;
    gap: 8px;
  }

  .pagination-container {
    flex-direction: column;
    gap: 12px;
    align-items: center;
  }

  .pagination-controls {
    flex-wrap: wrap;
    justify-content: center;
  }

  .page-btn {
    padding: 6px 12px;
    font-size: 12px;
  }
}
</style>