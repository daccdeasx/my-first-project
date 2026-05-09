<template>
  <div class="forbidden-page">
    <!-- 左侧背景区域 -->
    <div class="forbidden-left"></div>

    <!-- 右侧内容区域 -->
    <div class="forbidden-right">
      <div class="content-container">
        <div class="error-header">
          <div class="error-code">403</div>
          <h2 class="error-title">访问被拒绝</h2>
          <p class="error-subtitle">抱歉，您没有权限访问此页面</p>
        </div>

        <div class="error-content">
          <div class="error-icon">
            <svg width="60" height="60" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L13.09 8.26L22 9L13.09 9.74L12 16L10.91 9.74L2 9L10.91 8.26L12 2Z" fill="#ffffff"/>
              <circle cx="12" cy="12" r="10" stroke="#e50914" stroke-width="2" fill="none"/>
              <path d="M15 9L9 15M9 9L15 15" stroke="#e50914" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>

          <div class="error-description">
            <p class="reason-title">可能的原因：</p>
            <div class="reason-list">
              <div class="reason-item">您的账户没有管理员权限</div>
              <div class="reason-item">会话已过期，请重新登录</div>
              <div class="reason-item">访问的页面需要特殊权限</div>
            </div>
          </div>
        </div>

        <div class="action-buttons">
          <button @click="goHome" class="primary-button">
            返回首页
          </button>
          <button @click="goLogin" class="secondary-button">
            重新登录
          </button>
        </div>

        <div class="help-text">
          <p>如果您认为这是一个错误，请联系管理员</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const goHome = () => {
  router.push('/')
}

const goLogin = () => {
  // 清除当前用户状态
  userStore.logout()
  localStorage.removeItem('authToken')
  router.push('/login')
}
</script>

<style scoped>
/* 主容器 - 左右分屏布局 */
.forbidden-page {
  display: flex;
  min-height: 100vh;
  overflow: hidden;
  background-color: #141414;
}

/* 左侧背景区域 */
.forbidden-left {
  flex: 1;
  background-image: url('/back.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  position: relative;
}

.forbidden-left::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 100px;
  background: linear-gradient(to right,
    rgba(26, 26, 26, 0) 0%,
    rgba(26, 26, 26, 0.3) 30%,
    rgba(26, 26, 26, 0.8) 70%,
    rgba(26, 26, 26, 1) 100%);
  z-index: 1;
}

/* 右侧内容区域 */
.forbidden-right {
  flex: 0 0 480px;
  background: #1a1a1a;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  position: relative;
  z-index: 2;
}

.content-container {
  width: 100%;
  max-width: 400px;
  text-align: center;
}

.error-header {
  margin-bottom: 24px;
}

.error-code {
  font-size: 3rem;
  font-weight: 900;
  color: #e50914;
  margin: 0 0 12px 0;
  text-shadow: 0 2px 4px rgba(229, 9, 20, 0.3);
}

.error-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 6px 0;
}

.error-subtitle {
  font-size: 0.9rem;
  color: #b3b3b3;
  margin: 0;
  font-weight: 400;
}

/* 错误内容 */
.error-content {
  margin-bottom: 24px;
}

.error-icon {
  margin-bottom: 16px;
  display: flex;
  justify-content: center;
}

.error-description {
  text-align: left;
  background: transparent;
  padding: 0;
  border-radius: 0;
  border: none;
}

.reason-title {
  color: #e5e5e5;
  margin: 0 0 12px 0;
  font-weight: 500;
  font-size: 14px;
}

.reason-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.reason-item {
  background: transparent;
  border: 1px solid #e50914;
  border-radius: 6px;
  padding: 10px 12px;
  color: #b3b3b3;
  font-size: 13px;
  transition: all 0.2s ease;
}

.reason-item:hover {
  background: rgba(229, 9, 20, 0.1);
  border-color: #f40612;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.primary-button {
  width: 100%;
  padding: 12px 20px;
  background: #e50914;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.primary-button:hover {
  background: #f40612;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(229, 9, 20, 0.3);
}

.secondary-button {
  width: 100%;
  padding: 12px 20px;
  background: transparent;
  color: #e5e5e5;
  border: 1px solid #333;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.secondary-button:hover {
  background: #333;
  border-color: #555;
  transform: translateY(-1px);
}

/* 帮助文本 */
.help-text {
  text-align: center;
}

.help-text p {
  font-size: 14px;
  color: #999;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .forbidden-right {
    flex: 0 0 400px;
  }
}

@media (max-width: 768px) {
  .forbidden-page {
    flex-direction: column;
  }

  .forbidden-left {
    flex: 0 0 300px;
  }

  .forbidden-right {
    flex: 1;
    padding: 20px;
    border-left: none;
    border-top: 1px solid #333;
  }

  .error-code {
    font-size: 3rem;
  }

  .error-title {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .forbidden-left {
    flex: 0 0 200px;
  }

  .content-container {
    padding: 0;
  }

  .error-code {
    font-size: 2.5rem;
  }

  .action-buttons {
    gap: 12px;
  }
}
</style>
