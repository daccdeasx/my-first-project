<template>
  <div class="login-page">
    <!-- 左侧背景区域 -->
    <div class="login-left"></div>

    <!-- 右侧表单区域 -->
    <div class="login-right">
      <div class="form-container">
        <div class="form-header">
          <h2 class="form-title">登录账户</h2>
          <p class="form-subtitle">继续您的电影之旅</p>
        </div>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="email" class="form-label">邮箱地址</label>
            <input
              id="email"
              type="email"
              v-model="credentials.email"
              required
              class="form-input"
              placeholder="请输入您的邮箱"
            >
          </div>

          <div class="form-group">
            <label for="password" class="form-label">密码</label>
            <input
              id="password"
              type="password"
              v-model="credentials.password"
              required
              class="form-input"
              placeholder="请输入您的密码"
            >
          </div>

          <div class="form-options">
            <label class="checkbox-wrapper">
              <input type="checkbox" class="checkbox">
              <span class="checkbox-text">记住我</span>
            </label>
            <a href="#" class="forgot-link">忘记密码？</a>
          </div>

          <button type="submit" class="login-button">
            立即登录
          </button>
        </form>

        <div class="form-footer">
          <div class="divider">
            <span>或</span>
          </div>
          <p class="signup-text">
            还没有账户？
            <router-link to="/register" class="signup-link">立即注册</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const credentials = reactive({
  email: '',
  password: ''
})

const handleLogin = async () => {
  try {
    // 确保发送字段与后端匹配
    const payload = {
      email: credentials.email,
      password: credentials.password
    }

    // 明确设置请求头
    const response = await axios.post(
      'http://localhost:8000/api/users/login/',
      payload,
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }
    )

    localStorage.setItem('authToken', response.data.token)

    // 新增：获取并存储用户信息
    await userStore.fetchUserProfile()

    router.push('/')
  } catch (error) {
    console.error('登录失败:', error.response?.data || error.message)
    alert(`登录失败: ${error.response?.data?.detail || '未知错误'}`)
  }
}
</script>

<style scoped>
/* 主容器 - 左右分屏布局 */
.login-page {
  display: flex;
  min-height: 100vh;
  overflow: hidden;
  background-color: #141414;
}

/* 左侧背景区域 */
.login-left {
  flex: 1;
  background-image: url('/back.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  position: relative;
}

.login-left::after {
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

/* 右侧表单区域 */
.login-right {
  flex: 0 0 480px;
  background: #1a1a1a;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  position: relative;
  z-index: 2;
}

.form-container {
  width: 100%;
  max-width: 400px;
}

.form-header {
  text-align: center;
  margin-bottom: 40px;
}

.form-title {
  font-size: 2rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 8px 0;
}

.form-subtitle {
  font-size: 1rem;
  color: #b3b3b3;
  margin: 0;
  font-weight: 400;
}

/* 表单样式 */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #e5e5e5;
  margin: 0;
}

.form-input {
  width: 100%;
  padding: 16px;
  border: 1px solid #333;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: #2a2a2a;
  color: #ffffff;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #e50914;
  background: #333;
  box-shadow: 0 0 0 2px rgba(229, 9, 20, 0.2);
}

.form-input::placeholder {
  color: #999;
}

/* 表单选项 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 8px 0;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox {
  width: 16px;
  height: 16px;
  accent-color: #e50914;
}

.checkbox-text {
  font-size: 14px;
  color: #b3b3b3;
}

.forgot-link {
  font-size: 14px;
  color: #e50914;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.forgot-link:hover {
  color: #f40612;
  text-decoration: underline;
}

/* 登录按钮 */
.login-button {
  width: 100%;
  padding: 16px 24px;
  background: #e50914;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 8px;
}

.login-button:hover {
  background: #f40612;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(229, 9, 20, 0.3);
}

.login-button:active {
  transform: translateY(0);
}

/* 表单底部 */
.form-footer {
  margin-top: 32px;
  text-align: center;
}

.divider {
  position: relative;
  margin: 24px 0;
  text-align: center;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #333;
}

.divider span {
  background: #1a1a1a;
  padding: 0 16px;
  color: #999;
  font-size: 14px;
  position: relative;
}

.signup-text {
  font-size: 14px;
  color: #b3b3b3;
  margin: 0;
}

.signup-link {
  color: #e50914;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s ease;
}

.signup-link:hover {
  color: #f40612;
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .login-right {
    flex: 0 0 400px;
  }
}

@media (max-width: 768px) {
  .login-page {
    flex-direction: column;
  }

  .login-left {
    flex: 0 0 300px;
  }

  .login-right {
    flex: 1;
    padding: 20px;
    border-left: none;
    border-top: 1px solid #333;
  }
}

@media (max-width: 480px) {
  .login-left {
    flex: 0 0 200px;
  }

  .form-container {
    padding: 0;
  }
}
</style>