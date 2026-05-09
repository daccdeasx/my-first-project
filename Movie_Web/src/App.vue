<template>
  <div class="app">
    <!-- 全局导航栏 -->
    <nav class="navbar" v-if="showNav" :class="{ 'scrolled': hasScrolled }">
      <div class="nav-left">
        <router-link to="/" class="logo">
          <span class="logo-text">MovieFlix</span>
        </router-link>
        <template v-if="showNav">
          <router-link to="/">首页</router-link>
          <router-link to="/search" class="ai-nav-link">✨智推</router-link>
          <router-link to="/recommend">推荐</router-link>
          <router-link to="/ranking">排行</router-link>
          <router-link to="/forum">论坛</router-link>
          <router-link to="/library">搜索</router-link>
        </template>
      </div>
      <div class="nav-right">
        <!-- 消息通知 -->
        <div v-if="showNav && isLoggedIn" class="message-menu" @mouseover="showMessageMenu = true" @mouseleave="showMessageMenu = false">
          <div class="message-icon">
            <i class="fas fa-bell"></i>
            <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
          </div>
          <transition name="fade">
            <div v-show="showMessageMenu" class="message-dropdown">
              <NotificationDropdownList @update-count="updateUnreadCount" />
            </div>
          </transition>
        </div>

        <div v-if="showNav" class="user-menu" @mouseover="showMenu = true" @mouseleave="showMenu = false">
          <img v-if="isLoggedIn" :src="userAvatar" class="avatar" />
          <span v-else @click="goLogin" class="login-btn">登录</span>
          <transition name="fade">
            <div v-show="showMenu && isLoggedIn" class="dropdown-menu">
              <router-link to="/profile">个人信息</router-link>
              <router-link to="/collection">我的收藏</router-link>
              <router-link to="/settings">账户设置</router-link>
              <router-link to="/yearly-report">年度报告</router-link>
              <div @click="logout">退出登录</div>
            </div>
          </transition>
        </div>
      </div>
    </nav>

    <!-- 主要内容区域 -->
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>

    <!-- 回到顶部按钮 -->
    <transition name="fade">
      <button
        v-show="showBackToTop"
        @click="scrollToTop"
        class="back-to-top"
        title="回到顶部"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path d="M12 4L8 8H11V16H13V8H16L12 4Z" fill="currentColor"/>
        </svg>
      </button>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import NotificationDropdownList from '@/components/forum/NotificationDropdownList.vue'

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()
const showMenu = ref(false)
const showMessageMenu = ref(false)
const hasScrolled = ref(false)
const showBackToTop = ref(false)
const unreadCount = ref(0)

// 判断是否显示导航栏（登录/注册/admin/403页不显示）
const showNav = computed(() => {
  const excludedPaths = ['/login', '/register', '/403'];
  // 排除所有以 /admin 开头的路径
  return !excludedPaths.includes(route.path) && !route.path.startsWith('/admin');
});

// 用户登录状态
const isLoggedIn = computed(() => !!localStorage.getItem('authToken'))
const userAvatar = computed(() => {
  return userStore.avatar
   ? `${userStore.avatar}?ts=${userStore.avatarTimestamp}`
    : '/default-avatar.jpg'
})

// 检测滚动以改变导航栏样式和显示回到顶部按钮
const handleScroll = () => {
  const scrollY = window.scrollY;
  hasScrolled.value = scrollY > 50;
  showBackToTop.value = scrollY > 300; // 滚动超过300px时显示回到顶部按钮
}

const goLogin = () => {
  router.push('/login')
}

const logout = () => {
  localStorage.removeItem('authToken')
  userStore.clearUser()
  router.push('/login')
}

// 回到顶部功能
const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

// 更新未读消息数量
const updateUnreadCount = (count) => {
  unreadCount.value = count
}



// 添加滚动监听
onMounted(() => {
  window.addEventListener('scroll', handleScroll);
});

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style>
:root {
  --primary-color: #e50914;  /* 主色调红 */
  --dark-bg: #1a1a1a;       /* 深色背景 - 更柔和的深灰 */
  --darker-bg: #161616;     /* 更深色背景 - 柔和深灰 */
  --card-bg: #242424;       /* 卡片背景 - 中等灰色 */
  --light-text: #f5f5f5;    /* 浅色文字 - 柔和白色 */
  --gray-text: #b8b8b8;     /* 灰色文字 - 稍亮的灰色 */
  --border-color: rgba(255, 255, 255, 0.12); /* 边框颜色 */
}

body {
  margin: 0;
  padding: 0;
  font-family: 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont,
               'Helvetica Neue', Arial, sans-serif;
  background-color: var(--dark-bg);
  color: var(--light-text);
  overflow-x: hidden;
}

/* 全局隐藏滚动条但保持滚动功能 */
html {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

html::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

body {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

body::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

/* 确保所有元素都隐藏滚动条 */
* {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

*::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}
</style>

<style scoped>
.app {
  min-height: 100vh;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 4%;
  height: 68px;
  color: var(--light-text);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  transition: background-color 0.3s ease;
  background-color: transparent;
}

.navbar.scrolled {
  background-color: var(--dark-bg);
}

.logo {
  display: flex;
  align-items: center;
  height: 100%;
  margin-right: 25px;
}

.logo-text {
  font-size: 24px;
  font-weight: bold;
  color: var(--primary-color);
  letter-spacing: -0.5px;
}

.nav-left {
  display: flex;
  align-items: center;
  height: 100%;
}

.nav-left a {
  color: var(--gray-text);
  text-decoration: none;
  padding: 0 10px;
  margin: 0 5px;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.2s ease;
  letter-spacing: 0.1px;
}

.nav-left a:hover {
  color: var(--light-text);
}



/* AI智推导航链接特殊样式 */
.ai-nav-link {
  background: linear-gradient(90deg, #ffd700, #e50914, #ff8c00) !important;
  -webkit-background-clip: text !important;
  background-clip: text !important;
  -webkit-text-fill-color: transparent !important;
  font-weight: 600 !important;
}

@keyframes gradient-flow {
  0% {
    background-position: 0% 50%;
  }
  100% {
    background-position: 400% 50%;
  }
}

.ai-nav-link:hover {
  animation-duration: 0.8s !important;
}

.router-link-active {
  color: var(--light-text) !important;
  font-weight: 700 !important;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

/* 消息通知样式 */
.message-menu {
  position: relative;
  cursor: pointer;
}

.message-icon {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  color: var(--gray-text);
  transition: all 0.2s ease;
  border-radius: 6px;
}

.message-icon:hover {
  color: var(--light-text);
  background: rgba(255, 255, 255, 0.05);
}

.message-icon i {
  font-size: 16px;
}

.notification-badge {
  position: absolute;
  top: -1px;
  right: -1px;
  background: var(--primary-color);
  color: white;
  font-size: 9px;
  font-weight: bold;
  padding: 1px 4px;
  border-radius: 8px;
  min-width: 14px;
  text-align: center;
  line-height: 1.2;
  border: 1px solid rgba(20, 20, 20, 0.8);
}

.message-dropdown {
  position: absolute;
  right: 0;
  top: 120%;
  z-index: 1001;
}

.user-menu {
  position: relative;
  cursor: pointer;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.avatar:hover {
  transform: scale(1.05);
}

.login-btn {
  color: var(--light-text);
  padding: 7px 17px;
  background-color: var(--primary-color);
  border-radius: 3px;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.login-btn:hover {
  background-color: #f40612;
}

.dropdown-menu {
  position: absolute;
  right: 0;
  top: 120%;
  background: rgba(0, 0, 0, 0.9);
  color: var(--light-text);
  padding: 10px 0;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 2px;
  min-width: 180px;
  overflow: hidden;
}

.dropdown-menu a,
.dropdown-menu div {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  font-size: 13px;
  transition: all 0.2s ease;
  color: var(--light-text);
  text-decoration: none;
}

.dropdown-menu a:hover,
.dropdown-menu div:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* 回到顶部按钮 - 磨砂质感圆角正方形 */
.back-to-top {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 48px;
  height: 48px;
  background: rgba(45, 45, 45, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 999;
  font-size: 0;
}

.back-to-top:hover {
  background: rgba(55, 55, 55, 0.9);
  border-color: rgba(255, 255, 255, 0.25);
  color: rgba(255, 255, 255, 1);
  transform: translateY(-1px);
}

.back-to-top:active {
  transform: translateY(0);
  background: rgba(35, 35, 35, 0.8);
}

/* 全局过渡效果 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

@media (max-width: 768px) {
  .navbar {
    padding: 0 2%;
    height: 50px;
  }

  .logo-text {
    font-size: 20px;
  }

  .nav-left a {
    font-size: 12px;
    padding: 0 8px;
    margin: 0 2px;
  }

  .back-to-top {
    bottom: 20px;
    right: 20px;
    width: 44px;
    height: 44px;
    border-radius: 10px;
  }
}
</style>