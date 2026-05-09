<template>
  <div class="settings-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">账户设置</h1>
      <p class="page-subtitle">管理您的账户信息和安全设置</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p>正在加载设置...</p>
      </div>
    </div>

    <!-- 设置内容 -->
    <div v-else class="settings-container">
      <form @submit.prevent="submitForm" class="settings-form">

        <!-- 基本信息卡片 -->
        <div class="settings-card">
          <div class="card-header">
            <h3 class="card-title">
              <i class="icon-user"></i>
              基本信息
            </h3>
          </div>
          <div class="card-content">
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">邮箱地址</label>
                <input
                  type="email"
                  v-model="formData.email"
                  :placeholder="user.email || '请输入邮箱'"
                  class="form-input"
                >
              </div>
              <div class="form-group">
                <label class="form-label">手机号码</label>
                <input
                  type="tel"
                  v-model="formData.phone"
                  :placeholder="user.phone || '请输入手机号'"
                  class="form-input"
                >
              </div>
            </div>
          </div>
        </div>

        <!-- 密码修改卡片 -->
        <div class="settings-card">
          <div class="card-header">
            <h3 class="card-title">
              <i class="icon-lock"></i>
              密码安全
            </h3>
            <p class="card-description">修改密码后需要重新登录</p>
          </div>
          <div class="card-content">
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">当前密码</label>
                <input
                  type="password"
                  v-model="formData.old_password"
                  placeholder="请输入当前密码"
                  class="form-input"
                >
              </div>
              <div class="form-group">
                <label class="form-label">新密码</label>
                <input
                  type="password"
                  v-model="formData.new_password"
                  placeholder="8-20位字符"
                  class="form-input"
                >
              </div>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="form-actions">
          <button type="button" @click="resetForm" class="btn-secondary">
            <i class="icon-refresh"></i>
            重置
          </button>
          <button type="submit" class="btn-primary" :disabled="!hasChanges">
            <i class="icon-save"></i>
            保存更改
          </button>
        </div>
      </form>

      <!-- 操作反馈 -->
      <div v-if="message" class="message-toast" :class="{'error': isError, 'show': !!message}">
        <div class="toast-content">
          <i :class="isError ? 'icon-error' : 'icon-success'"></i>
          <span>{{ message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

  <script>
  import axios from 'axios';

  export default {
    name: 'SettingsView',
    data() {
      return {
        user: {},
        formData: {
          email: '',
          old_password: '',
          new_password: '',
          phone: '',
          bio: '',
          avatar: null
        },
        originalData: {},
        message: '',
        isError: false,
        loading: true
      }
    },
    computed: {
      hasChanges() {
        return this.formData.email !== this.originalData.email ||
               this.formData.phone !== this.originalData.phone ||
               this.formData.old_password ||
               this.formData.new_password
      }
    },
    async created() {
      await this.fetchUserData();
    },
    methods: {
      async fetchUserData() {
        this.loading = true;
        try {
          const response = await axios.get('/api/users/settings/', {
            headers: {
              Authorization: `Token ${localStorage.getItem('authToken')}`
            }
          });
          this.user = response.data;
          // 保存原始数据用于比较
          this.originalData = {
            email: response.data.email || '',
            phone: response.data.phone || ''
          };
        } catch (error) {
          console.error('获取用户数据失败:', error);
          this.message = '加载用户信息失败，请刷新重试';
          this.isError = true;
        } finally {
          this.loading = false;
        }
      },
      handleAvatarUpload(event) {
        this.formData.avatar = event.target.files[0];
      },
      async submitForm() {
        const form = new FormData();
        for (const key in this.formData) {
          if (this.formData[key]) {
            form.append(key, this.formData[key]);
          }
        }

        try {
          await axios.patch('/api/users/settings/', form, {
            headers: {
              'Content-Type': 'multipart/form-data',
              Authorization: `Token ${localStorage.getItem('authToken')}`
            }
          });

          this.showMessage('设置已成功保存！', false);
          await this.fetchUserData(); // 刷新用户数据
          this.resetForm();

          // 如果修改了密码需要重新登录
          if (this.formData.new_password) {
            setTimeout(() => {
              this.$router.push('/logout');
            }, 1500);
          }

        } catch (error) {
          this.showMessage(error.response?.data?.message || '保存失败，请检查输入', true);
        }
      },
      resetForm() {
        this.formData = {
          email: '',
          old_password: '',
          new_password: '',
          phone: '',
          bio: '',
          avatar: null
        };
        this.clearMessage();
      },
      clearMessage() {
        this.message = '';
        this.isError = false;
      },
      showMessage(text, isError = false) {
        this.message = text;
        this.isError = isError;
        // 3秒后自动清除消息
        setTimeout(() => {
          this.clearMessage();
        }, 3000);
      }
    }
  }
  </script>

  <style scoped>
/* 页面容器 */
.settings-page {
  min-height: 100vh;
  background: #141414;
  color: #fff;
  padding: 70px 20px 30px;
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 6px;
  background: linear-gradient(45deg, #e50914, #ff6b6b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

/* 加载状态 */
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.loading-spinner {
  text-align: center;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 2px solid rgba(229, 9, 20, 0.3);
  border-top: 2px solid #e50914;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 12px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-spinner p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

/* 设置容器 */
.settings-container {
  max-width: 700px;
  margin: 0 auto;
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* 设置卡片 */
.settings-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  overflow: hidden;
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.1rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.card-title i {
  width: 16px;
  height: 16px;
  background: #e50914;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-title i::before {
  content: '';
  width: 6px;
  height: 6px;
  background: white;
  border-radius: 1px;
}

.card-description {
  margin: 6px 0 0 26px;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
}

.card-content {
  padding: 18px 20px;
}

/* 表单布局 */
.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 0.8rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-input {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 0.9rem;
  color: #fff;
  transition: all 0.3s ease;
  height: 32px;
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.form-input:focus {
  outline: none;
  border-color: #e50914;
  background: rgba(255, 255, 255, 0.12);
  box-shadow: 0 0 0 2px rgba(229, 9, 20, 0.1);
}

/* 操作按钮 */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 18px 0;
}

.btn-primary,
.btn-secondary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  height: 32px;
}

.btn-primary {
  background: #e50914;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #b8070f;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  background: rgba(229, 9, 20, 0.5);
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

/* 消息提示 */
.message-toast {
  position: fixed;
  top: 90px;
  right: 20px;
  background: rgba(0, 0, 0, 0.9);
  border-radius: 6px;
  padding: 12px 16px;
  border-left: 3px solid #4ade80;
  backdrop-filter: blur(10px);
  transform: translateX(100%);
  transition: transform 0.3s ease;
  z-index: 1000;
}

.message-toast.show {
  transform: translateX(0);
}

.message-toast.error {
  border-left-color: #e50914;
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #fff;
  font-size: 0.85rem;
}

.toast-content i {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-success {
  background: #4ade80;
}

.icon-error {
  background: #e50914;
}

.icon-success::before,
.icon-error::before {
  content: '';
  width: 6px;
  height: 6px;
  background: white;
  border-radius: 50%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-page {
    padding: 60px 16px 20px;
  }

  .page-title {
    font-size: 1.8rem;
  }

  .page-header {
    margin-bottom: 24px;
  }

  .settings-form {
    gap: 16px;
  }

  .card-header {
    padding: 14px 16px;
  }

  .card-content {
    padding: 16px;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .form-actions {
    flex-direction: column;
    padding: 16px 0;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
    justify-content: center;
  }

  .message-toast {
    right: 16px;
    left: 16px;
    transform: translateY(-100%);
  }

  .message-toast.show {
    transform: translateY(0);
  }
}
  </style>