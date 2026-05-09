<template>
  <div class="register-page">
    <!-- 左侧背景区域 -->
    <div class="register-left"></div>

    <!-- 右侧表单区域 -->
    <div class="register-right">
      <div class="form-container">
        <div class="form-header">
          <h2 class="form-title">创建账户</h2>
          <p class="form-subtitle">填写信息，立即开始</p>
        </div>

        <form @submit.prevent="handleSubmit" class="register-form">
          <div class="form-group">
            <label for="email" class="form-label">邮箱地址</label>
            <input
              id="email"
              type="email"
              v-model="form.email"
              required
              class="form-input"
              placeholder="请输入您的邮箱地址"
            >
          </div>

          <div class="form-group">
            <label for="password" class="form-label">设置密码</label>
            <input
              id="password"
              type="password"
              v-model="form.password"
              required
              class="form-input"
              placeholder="请设置您的登录密码"
            >
          </div>

          <div class="form-row">
            <div class="form-group half-width">
              <label for="birthday" class="form-label">出生日期</label>
              <input
                id="birthday"
                type="date"
                v-model="form.birthday"
                required
                class="form-input"
                min="1900-01-01"
                :max="new Date().toISOString().split('T')[0]"
              >
            </div>

            <div class="form-group half-width">
              <label for="age" class="form-label">年龄</label>
              <input
                id="age"
                type="number"
                v-model="form.age"
                required
                class="form-input"
                placeholder="年龄"
                min="1"
                max="120"
              >
            </div>
          </div>

          <div class="form-group">
            <label for="phone" class="form-label">手机号码</label>
            <input
              id="phone"
              type="tel"
              v-model="form.phone"
              required
              class="form-input"
              placeholder="请输入您的手机号码"
              pattern="[0-9]{11}"
            >
          </div>

          <div class="terms-section">
            <label class="checkbox-wrapper">
              <input type="checkbox" class="checkbox" required>
              <span class="checkbox-text">
                我已阅读并同意 <a href="#" class="terms-link">用户协议</a> 和 <a href="#" class="terms-link">隐私政策</a>
              </span>
            </label>
          </div>

          <button type="submit" class="register-button">
            立即注册
          </button>
        </form>

        <div class="form-footer">
          <div class="divider">
            <span>或</span>
          </div>
          <p class="login-text">
            已有账户？
            <router-link to="/login" class="login-link">立即登录</router-link>
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

  const router = useRouter()
  const form = reactive({
    email: '',
    password: '',
    birthday: '',
    age: null,
    phone: ''
  })

  const handleSubmit = async () => {
    try {
      await axios.post('http://localhost:8000/api/users/register/', form)
      router.push('/login')
    } catch (error) {
      console.error('注册失败:', error.response.data)
    }
  }
  </script>

<style scoped>
/* 主容器 - 左右分屏布局 */
.register-page {
  display: flex;
  min-height: 100vh;
  overflow: hidden;
  background-color: #141414;
}

/* 左侧背景区域 */
.register-left {
  flex: 1;
  background-image: url('/back.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  position: relative;
}

.register-left::after {
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
.register-right {
  flex: 0 0 480px;
  background: #1a1a1a;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 30px;
  position: relative;
  z-index: 2;
}

.form-container {
  width: 100%;
  max-width: 400px;
}

.form-header {
  text-align: center;
  margin-bottom: 24px;
}

.form-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 6px 0;
}

.form-subtitle {
  font-size: 0.9rem;
  color: #b3b3b3;
  margin: 0;
  font-weight: 400;
}

/* 表单样式 */
.register-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: flex;
  gap: 12px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.form-group.half-width {
  flex: 1;
}

.form-label {
  font-size: 13px;
  font-weight: 500;
  color: #e5e5e5;
  margin: 0;
}

.form-input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #333;
  border-radius: 6px;
  font-size: 15px;
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

/* 条款同意 */
.terms-section {
  margin: 12px 0;
}

.checkbox-wrapper {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  cursor: pointer;
  line-height: 1.4;
}

.checkbox {
  width: 16px;
  height: 16px;
  accent-color: #e50914;
  margin-top: 1px;
  flex-shrink: 0;
}

.checkbox-text {
  font-size: 13px;
  color: #b3b3b3;
}

.terms-link {
  color: #e50914;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.terms-link:hover {
  color: #f40612;
  text-decoration: underline;
}

/* 注册按钮 */
.register-button {
  width: 100%;
  padding: 14px 20px;
  background: #e50914;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 6px;
}

.register-button:hover {
  background: #f40612;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(229, 9, 20, 0.3);
}

.register-button:active {
  transform: translateY(0);
}

/* 表单底部 */
.form-footer {
  margin-top: 24px;
  text-align: center;
}

.divider {
  position: relative;
  margin: 18px 0;
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

.login-text {
  font-size: 14px;
  color: #b3b3b3;
  margin: 0;
}

.login-link {
  color: #e50914;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s ease;
}

.login-link:hover {
  color: #f40612;
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .register-right {
    flex: 0 0 450px;
  }
}

@media (max-width: 768px) {
  .register-page {
    flex-direction: column;
  }

  .register-left {
    flex: 0 0 300px;
  }

  .register-right {
    flex: 1;
    padding: 20px;
    border-left: none;
    border-top: 1px solid #333;
  }

  .form-row {
    flex-direction: column;
    gap: 20px;
  }

  .form-group.half-width {
    flex: none;
  }
}

@media (max-width: 480px) {
  .register-left {
    flex: 0 0 200px;
  }

  .form-container {
    padding: 0;
  }
}
</style>