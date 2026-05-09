<template>
  <div class="post-table-container">
    <table class="post-table">
      <thead>
        <tr>
          <th class="table-header">
            <input
              type="checkbox"
              :checked="isAllSelected"
              @change="$emit('select-all', !isAllSelected)"
              class="table-checkbox"
            />
          </th>
          <th class="table-header">ID</th>
          <th class="table-header">标题</th>
          <th class="table-header">作者</th>
          <th class="table-header">状态</th>
          <th class="table-header">主题</th>
          <th class="table-header">置顶</th>
          <th class="table-header table-header-right">操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="post in posts" :key="post.id" class="table-row">
          <td class="table-cell">
            <input
              type="checkbox"
              :checked="selectedPosts.includes(post.id)"
              @change="$emit('select', post.id)"
              class="table-checkbox"
            />
          </td>
          <td class="table-cell">{{ post.id }}</td>
          <td class="table-cell">
            <div class="title-container">
              <span class="title-text">{{ post.title }}</span>
              <span v-if="post.is_pinned" class="pin-badge">置顶</span>
            </div>
          </td>
          <td class="table-cell">
            <div class="author-container">
              <span class="author-text">{{ post.author || post.username || '未知用户' }}</span>
            </div>
          </td>
          <td class="table-cell">
            <span :class="getStatusClass(post.status)">
              {{ mapStatus(post.status) }}
              <span v-if="post.status === 'rejected' && post.reject_reason"
                    class="reject-reason-link"
                    @click="showRejectReason(post.reject_reason)"
                    title="点击查看拒绝理由">
                (查看理由)
              </span>
            </span>
          </td>
          <td class="table-cell">
            <span class="theme-badge" :class="getThemeClass(post.theme)">
              {{ mapTheme(post.theme) }}
            </span>
          </td>
          <td class="table-cell" v-if="post.status !== 'rejected'">
            <button
              @click="$emit('toggle-pin', post.id)"
              :class="post.is_pinned ? 'pin-btn active' : 'pin-btn'"
            >
              {{ post.is_pinned ? '已置顶' : '置顶' }}
            </button>
          </td>
          <td class="table-cell" v-else>
            <span class="disabled-text">—</span>
          </td>
          <td class="table-cell table-cell-right">
            <div class="action-buttons">
              <template v-if="post.status === 'pending' && isEditable">
                <button
                  @click="$emit('approve', post.id)"
                  class="action-btn approve-btn"
                >
                  通过
                </button>
                <button
                  @click="$emit('reject', post.id)"
                  class="action-btn reject-btn"
                >
                  拒绝
                </button>
              </template>
              <template v-else-if="post.status === 'approved' && isEditable">
                <button
                  @click="$emit('delete', post.id)"
                  class="action-btn delete-btn"
                >
                  删除
                </button>
              </template>
              <template v-else>
                <span class="status-text">
                  {{ post.status === 'approved' ? '已通过' : '已拒绝' }}
                </span>
                <button
                  @click="$emit('view-details', post.id)"
                  class="action-btn view-btn"
                >
                  查看详情
                </button>
              </template>
            </div>
          </td>
        </tr>
        <tr v-if="posts.length === 0">
          <td colspan="8" class="table-cell empty-cell">
            暂无帖子
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useToast } from '@/composables/useToast';

const { showError } = useToast();

const props = defineProps({
  posts: { type: Array, required: true },
  isEditable: { type: Boolean, default: false },
  selectedPosts: { type: Array, default: () => [] }
});

const isAllSelected = computed(() => {
  return props.posts.length > 0 && props.selectedPosts.length === props.posts.length;
});

const mapStatus = (status) => {
  return {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝'
  }[status] || '未知';
};

const mapTheme = (theme) => {
  return {
    tech: '技术',
    life: '生活',
    entertainment: '娱乐',
    other: '其他'
  }[theme] || '其他';
};

const getStatusClass = (status) => {
  return {
    pending: 'status-badge pending',
    approved: 'status-badge approved',
    rejected: 'status-badge rejected'
  }[status] || 'status-badge unknown';
};

const getThemeClass = (theme) => {
  return {
    tech: 'tech',
    life: 'life',
    entertainment: 'entertainment',
    other: 'other'
  }[theme] || 'other';
};

// 显示拒绝理由
const showRejectReason = (reason) => {
  showError(reason, { duration: 5000 }); // 显示5秒
};

defineEmits(['select', 'select-all', 'approve', 'reject', 'toggle-pin', 'delete', 'view-details']);
</script>

<style scoped>
.post-table-container {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  overflow-x: auto;
}

.post-table {
  width: 100%;
  min-width: 800px;
  border-collapse: collapse;
}

/* 表头样式 */
.table-header {
  padding: 12px 16px;
  background: #fafafa;
  border-bottom: 1px solid #e4e7ed;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
  text-align: left;
}

.table-header-right {
  text-align: right;
}

/* 表格行样式 */
.table-row {
  transition: background-color 0.2s ease;
}

.table-row:hover {
  background: #f5f7fa;
}

/* 表格单元格样式 */
.table-cell {
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
  color: #606266;
  font-size: 14px;
  vertical-align: middle;
}

.table-cell-right {
  text-align: right;
}

.empty-cell {
  text-align: center;
  color: #909399;
  font-style: italic;
}

/* 复选框样式 */
.table-checkbox {
  width: 16px;
  height: 16px;
  border: 1px solid #dcdfe6;
  border-radius: 2px;
  cursor: pointer;
  accent-color: #409eff;
}

/* 标题容器 */
.title-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-text {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pin-badge {
  padding: 2px 6px;
  background: #e1f3d8;
  color: #67c23a;
  font-size: 12px;
  border-radius: 4px;
  border: 1px solid #b3d8a4;
}

/* 作者容器 */
.author-container {
  display: flex;
  align-items: center;
}

.author-text {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 状态徽章 */
.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid;
}

.status-badge.pending {
  background: #fdf6ec;
  color: #e6a23c;
  border-color: #f5dab1;
}

.status-badge.approved {
  background: #f0f9ff;
  color: #67c23a;
  border-color: #b3d8a4;
}

.status-badge.rejected {
  background: #fef0f0;
  color: #f56c6c;
  border-color: #fbc4c4;
}

.status-badge.unknown {
  background: #f4f4f5;
  color: #909399;
  border-color: #d3d4d6;
}

.reject-reason-link {
  margin-left: 4px;
  color: #409eff;
  font-size: 11px;
  text-decoration: underline;
  cursor: pointer;
}

.reject-reason-link:hover {
  color: #66b1ff;
}

/* 主题徽章 */
.theme-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid;
}

.theme-badge.tech {
  background: #ecf5ff;
  color: #409eff;
  border-color: #b3d8ff;
}

.theme-badge.life {
  background: #f0f9ff;
  color: #67c23a;
  border-color: #b3d8a4;
}

.theme-badge.entertainment {
  background: #f4f4f5;
  color: #909399;
  border-color: #d3d4d6;
}

.theme-badge.other {
  background: #f4f4f5;
  color: #909399;
  border-color: #d3d4d6;
}

/* 置顶按钮 */
.pin-btn {
  padding: 6px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #ffffff;
  color: #606266;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pin-btn:hover {
  border-color: #409eff;
  color: #409eff;
}

.pin-btn.active {
  background: #f0f9ff;
  border-color: #67c23a;
  color: #67c23a;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
}

.action-btn {
  padding: 6px 12px;
  border: 1px solid;
  border-radius: 4px;
  font-size: 12px;
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

.reject-btn {
  color: #f56c6c;
  border-color: #f56c6c;
}

.reject-btn:hover {
  background: #f56c6c;
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

.view-btn {
  color: #409eff;
  border-color: #409eff;
}

.view-btn:hover {
  background: #409eff;
  color: #ffffff;
}

.status-text {
  color: #909399;
  font-size: 12px;
  margin-right: 8px;
}

.disabled-text {
  color: #c0c4cc;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .post-table-container {
    margin: 0 -16px;
    border-left: none;
    border-right: none;
  }

  .table-header,
  .table-cell {
    padding: 8px 12px;
  }

  .title-text {
    max-width: 120px;
  }

  .author-text {
    max-width: 80px;
  }

  .action-buttons {
    flex-direction: column;
    gap: 4px;
  }

  .action-btn {
    padding: 4px 8px;
    font-size: 11px;
  }
}
</style>