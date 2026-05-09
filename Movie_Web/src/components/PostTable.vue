<template>
  <table class="post-table">
    <thead>
      <tr>
        <th>ID</th>
        <th>标题</th>
        <th>作者</th>
        <th>状态</th>
        <th>创建时间</th>
        <th v-if="isEditable">操作</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="post in posts" :key="post.id">
        <td>{{ post.id }}</td>
        <td>{{ post.title }}</td>
        <td>{{ post.author || post.user.username }}</td>
        <td :class="statusClass(post.status)">{{ statusText(post.status) }}</td>
        <td>{{ formatDate(post.created_at) }}</td>
        <td v-if="isEditable">
          <!-- 只在待审核状态显示审核按钮 -->
          <div v-if="post.status === 'pending'" class="action-buttons">
            <button @click="handleApprove(post.id)">通过</button>
            <button @click="handleReject(post.id)">拒绝</button>
          </div>
          <!-- 已审核状态显示查看详情 -->
          <div v-else>
            <router-link :to="`/posts/${post.id}`">查看详情</router-link>
          </div>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup>
import { computed, defineEmits } from 'vue'

defineProps({
  posts: {
    type: Array,
    required: true
  },
  isEditable: {
    type: Boolean,
    default: false
  }
})

// 定义事件
const emit = defineEmits(['approve','reject'])

// 状态文本映射
const statusText = (status) => {
  return {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝'
  }[status] || status
}

// 状态样式映射
const statusClass = (status) => {
  return {
    pending: 'status-pending',
    approved: 'status-approved',
    rejected: 'status-rejected'
  }[status]
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}

// 处理审核事件（传递到父组件）
const handleApprove = (postId) => {
  emit('approve', postId)
}

const handleReject = (postId) => {
  emit('reject', postId)
}
</script>

<style scoped>
.post-table {
  width: 100%;
  border-collapse: collapse;
}

.post-table th,.post-table td {
  padding: 8px;
  border: 1px solid #ddd;
  text-align: left;
}

.post-table th {
  background-color: #f2f2f2;
}

.status-pending { color: orange; }
.status-approved { color: green; }
.status-rejected { color: red; }

.action-buttons button {
  margin-right: 5px;
  padding: 4px 8px;
  cursor: pointer;
}
</style>