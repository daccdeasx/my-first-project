<template>
  <div class="user-detail">
    <h3>用户详情</h3>
    <p>邮箱：{{ user.email }}</p>
    <p>用户名：{{ user.username }}</p>
    <p>状态：{{ user.is_active ? '激活' : '禁用' }}</p>
    <p>注册时间：{{ formatDate(user.date_joined) }}</p>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'
import { formatDate } from '@/utils/dateUtils' // 从公共工具文件导入

const props = defineProps({
  user: {
    type: Object,
    required: true
  }
})
</script>

<style scoped>
.user-detail {
  padding: 20px;
  line-height: 2.5;
}
</style>