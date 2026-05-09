<template>
    <nav class="navbar">
      <div class="nav-brand">
        <router-link to="/" class="logo">
          <img src="@/assets/logo.png" alt="MovieFlix" class="logo-img" />
          <span class="logo-text">MovieFlix</span>
        </router-link>
      </div>

      <!-- 桌面导航菜单 -->
      <div class="nav-menu">
        <div class="nav-items">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="nav-link"
            :class="{ 'ai-link': item.isAI }"
            active-class="active-link"
          >
            <i :class="`icon ${item.icon}`"></i>
            <span class="link-text" :class="{ 'ai-text': item.isAI }">{{ item.name }}</span>
          </router-link>
        </div>

        <!-- 用户控制区 -->
        <div class="user-controls">
          <div
            class="user-profile"
            @mouseenter="showDropdown = true"
            @mouseleave="showDropdown = false"
          >
            <div class="avatar-wrapper">
              <img
                v-if="isLoggedIn"
                :src="userAvatar"
                class="user-avatar"
                alt="用户头像"
              />
              <div v-else class="login-btn" @click="navigateToLogin">
                <i class="icon fas fa-user"></i>
                <span>登录/注册</span>
              </div>
            </div>

            <!-- 用户下拉菜单 -->
            <transition name="slide-down">
              <div v-show="showDropdown && isLoggedIn" class="user-dropdown">
                <div class="dropdown-header">
                  <span class="user-email">{{ userEmail }}</span>
                </div>
                <div class="dropdown-list">
                  <router-link
                    v-for="item in userMenuItems"
                    :key="item.path"
                    :to="item.path"
                    class="dropdown-item"
                  >
                    <i :class="`icon ${item.icon}`"></i>
                    <span>{{ item.label }}</span>
                  </router-link>
                  <div class="dropdown-item" @click="handleLogout">
                    <i class="icon fas fa-sign-out-alt"></i>
                    <span>退出登录</span>
                  </div>
                </div>
              </div>
            </transition>
          </div>
        </div>
      </div>

      <!-- 移动端汉堡菜单 -->
      <button class="hamburger" @click="toggleMobileMenu">
        <i class="fas fa-bars"></i>
      </button>

      <!-- 移动端菜单 -->
      <transition name="slide-left">
        <div v-show="isMobileMenuOpen" class="mobile-menu">
          <div class="mobile-menu-header">
            <button class="close-btn" @click="toggleMobileMenu">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="mobile-nav-items">
            <router-link
              v-for="item in mobileNavItems"
              :key="item.path"
              :to="item.path"
              class="mobile-nav-link"
              @click="toggleMobileMenu"
            >
              <i :class="`icon ${item.icon}`"></i>
              <span>{{ item.name }}</span>
            </router-link>
            <div v-if="isLoggedIn" class="mobile-user-menu">
              <div
                v-for="item in userMenuItems"
                :key="item.path"
                class="mobile-menu-item"
                @click="toggleMobileMenu"
              >
                <router-link :to="item.path">
                  <i :class="`icon ${item.icon}`"></i>
                  <span>{{ item.label }}</span>
                </router-link>
              </div>
              <div class="mobile-menu-item" @click="handleLogout">
                <i class="icon fas fa-sign-out-alt"></i>
                <span>退出登录</span>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </nav>
  </template>

  <script setup>
  import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { useUserStore } from '@/stores/user'

  const router = useRouter()
  const route = useRoute()
  const userStore = useUserStore()

  // 响应式状态
  const showDropdown = ref(false)
  const isMobileMenuOpen = ref(false)
  const windowWidth = ref(window.innerWidth)

  // 导航配置项
  const navItems = ref([
    { path: '/', name: '首页', icon: 'fas fa-home' },
    { path: '/search', name: '✨智推', icon: 'fas fa-magic', isAI: true },
    { path: '/recommend', name: '推荐', icon: 'fas fa-star' },
    { path: '/library', name: '片库', icon: 'fas fa-film' },
    { path: '/ranking', name: '榜单', icon: 'fas fa-chart-line' }
  ])

  // 用户菜单项
  const userMenuItems = ref([
    { path: '/profile', label: '个人资料', icon: 'fas fa-user-cog' },
    { path: '/collection', label: '我的收藏', icon: 'fas fa-heart' },
    { path: '/settings', label: '账户设置', icon: 'fas fa-cog' },
    { path: '/history', label: '观看记录', icon: 'fas fa-history' }
  ])

  // 计算属性
  const isLoggedIn = computed(() => userStore.isAuthenticated)
  const userEmail = computed(() => userStore.email || '未知用户')
  const userAvatar = computed(() => userStore.avatar || '/default-avatar.jpg')

  // 移动端导航项（合并主导航和用户菜单）
  const mobileNavItems = computed(() => [
    ...navItems.value,
    ...(isLoggedIn.value ? userMenuItems.value : [])
  ])

  // 方法
  const toggleMobileMenu = () => {
    isMobileMenuOpen.value = !isMobileMenuOpen.value
  }

  const navigateToLogin = () => {
    router.push('/login')
  }

  const handleLogout = async () => {
    await userStore.logout()
    router.push('/login')
  }

  // 响应式处理
  const checkWindowWidth = () => {
    windowWidth.value = window.innerWidth
    if (windowWidth.value > 768 && isMobileMenuOpen.value) {
      isMobileMenuOpen.value = false
    }
  }

  // 生命周期
  onMounted(() => {
    window.addEventListener('resize', checkWindowWidth)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('resize', checkWindowWidth)
  })
  </script>

  <style scoped>
  .navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
    background: rgba(0, 0, 0, 0.95);
    backdrop-filter: blur(10px);
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .logo-img {
    height: 40px;
    width: auto;
  }

  .logo-text {
    font-size: 1.5rem;
    font-weight: bold;
    color: #fff;
    font-family: 'Arial Black', sans-serif;
  }

  .nav-menu {
    display: flex;
    align-items: center;
    gap: 2rem;
  }

  .nav-items {
    display: flex;
    gap: 1.5rem;
  }

  .nav-link {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: rgba(255, 255, 255, 0.8);
    padding: 0.5rem 1rem;
    border-radius: 8px;
    transition: all 0.3s ease;
  }

  .nav-link:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
  }

  .active-link {
    color: #00b4ff;
    background: rgba(0, 180, 255, 0.1);
  }

  /* AI智推菜单特殊样式 */
  .ai-link {
    position: relative;
  }

  .ai-text {
    background: linear-gradient(90deg, #ffd700, #e50914, #ff8c00);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 600;
  }

  @keyframes gradient-flow {
    0% {
      background-position: 0% 50%;
    }
    100% {
      background-position: 400% 50%;
    }
  }

  .ai-link:hover .ai-text {
    animation-duration: 0.8s;
  }

  .user-controls {
    position: relative;
  }

  .user-profile {
    position: relative;
  }

  .avatar-wrapper {
    cursor: pointer;
  }

  .user-avatar {
    width: 45px;
    height: 45px;
    border-radius: 50%;
    border: 2px solid #00b4ff;
  }

  .login-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #fff;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.1);
    transition: background 0.3s ease;
  }

  .login-btn:hover {
    background: rgba(255, 255, 255, 0.2);
  }

  .user-dropdown {
    position: absolute;
    right: 0;
    top: 100%;
    margin-top: 1rem;
    background: rgba(0, 0, 0, 0.9);
    border-radius: 8px;
    min-width: 220px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    overflow: hidden;
    backdrop-filter: blur(10px);
  }

  .dropdown-header {
    padding: 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .user-email {
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.8);
  }

  .dropdown-list {
    padding: 0.5rem 0;
  }

  .dropdown-item {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 0.8rem 1.5rem;
    color: rgba(255, 255, 255, 0.8);
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .dropdown-item:hover {
    background: rgba(255, 255, 255, 0.05);
    color: #00b4ff;
  }

  /* 移动端样式 */
  .hamburger {
    display: none;
    background: none;
    border: none;
    color: #fff;
    font-size: 1.5rem;
    cursor: pointer;
  }

  .mobile-menu {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    width: 280px;
    background: rgba(0, 0, 0, 0.95);
    backdrop-filter: blur(10px);
    padding: 1rem;
    z-index: 1001;
  }

  .mobile-menu-header {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 2rem;
  }

  .mobile-nav-items {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .mobile-nav-link {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    color: rgba(255, 255, 255, 0.8);
    border-radius: 8px;
  }

  .mobile-nav-link:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  /* 响应式处理 */
  @media (max-width: 768px) {
    .nav-menu {
      display: none;
    }

    .hamburger {
      display: block;
    }

    .nav-brand .logo-text {
      display: none;
    }
  }

  /* 过渡动画 */
  .slide-down-enter-active,
  .slide-down-leave-active {
    transition: all 0.3s ease;
    transform-origin: top center;
  }

  .slide-down-enter-from,
  .slide-down-leave-to {
    opacity: 0;
    transform: translateY(-10px);
  }

  .slide-left-enter-active,
  .slide-left-leave-active {
    transition: all 0.3s ease;
  }

  .slide-left-enter-from,
  .slide-left-leave-to {
    transform: translateX(100%);
  }
  </style>