<template>
  <div v-if="loading" class="loading-overlay">
    <el-icon class="loading-icon" :size="32"><Loading /></el-icon>
  </div>
  <div v-else-if="showAdminContent" class="admin-layout" :class="{ 'sidebar-collapsed': isCollapse }">
    <!-- 侧边导航栏 -->
    <el-container>
      <el-aside
        :width="isCollapse? '64px' : '240px'"
        class="admin-sidebar"
      >
        <!-- 动态导航菜单 -->
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :collapse-transition="false"
          router
          class="admin-menu"
        >
          <el-sub-menu
            v-for="route in permissionRoutes.filter(r => r.children && r.children.length > 0)"
            :key="route.path"
            :index="route.path"
          >
            <template #title>
              <AdminIcons :name="getIconName(route.meta?.icon)" :size="18" />
              <span>{{ route.meta?.title }}</span>
            </template>

            <el-menu-item
              v-for="child in route.children"
              :key="child.path"
              :index="child.path"
            >
              <AdminIcons :name="getIconName(child.meta?.icon)" :size="16" />
              <template #title>{{ child.meta?.title }}</template>
            </el-menu-item>
          </el-sub-menu>

          <el-menu-item
            v-for="route in permissionRoutes.filter(r => !r.children || r.children.length === 0)"
            :key="route.path"
            :index="route.path"
          >
            <AdminIcons :name="getIconName(route.meta?.icon)" :size="18" />
            <template #title>{{ route.meta?.title }}</template>
          </el-menu-item>
        </el-menu>

        <!-- 侧边栏底部收起按钮 -->
        <div class="sidebar-footer">
          <el-button
            :icon="isCollapse? Expand : Fold"
            circle
            @click="toggleCollapse"
            class="collapse-btn"
            :title="isCollapse ? '展开侧边栏' : '收起侧边栏'"
          />
        </div>
      </el-aside>

      <el-container>
        <!-- 顶部导航栏 -->
        <el-header class="admin-header">
          <div class="header-left">
            <el-breadcrumb separator="/" class="breadcrumb">
              <el-breadcrumb-item
                v-for="item in breadcrumbs"
                :key="item.path"
              >
                {{ item.meta?.title }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>

          <!-- 用户操作菜单 -->
          <el-dropdown trigger="click">
            <div class="user-info">
              <el-avatar :src="userStore.avatar" />
              <span class="user-name">{{ userStore.username }}</span>
              <el-icon class="el-icon--right">
                <ArrowDown />
              </el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleProfile">
                  <el-icon><User /></el-icon> 个人中心
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon> 退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-header>

        <!-- 内容区域 -->
        <el-main class="admin-main">
          <router-view v-slot="{ Component }">
            <transition name="fade-transform" mode="out-in">
              <keep-alive :include="cachedViews">
                <component :is="Component" />
              </keep-alive>
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
  <div v-else class="unauthorized-message">
    <h1>401 未授权</h1>
    <p>您没有权限访问此页面</p>
    <el-button @click="goHome">返回首页</el-button>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox } from 'element-plus'
import AdminIcons from '@/components/icons/AdminIcons.vue'

import {
  Fold,
  Expand,
  User,
  SwitchButton,
  ArrowDown,
  Loading
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const loading = ref(true)
const showAdminContent = ref(false)

// 侧边栏折叠状态
const isCollapse = ref(localStorage.getItem('sidebarStatus')!== 'closed')

// 徽标路径
const miniLogo = '/path/to/mini-logo.png' // 替换为实际小图标路径
const fullLogo = '/path/to/full-logo.png' // 替换为实际完整图标路径

// 获取权限路由
const permissionRoutes = computed(() => {
  const routes = router.options.routes.find(r => r.path === '/admin')?.children || []
  // 超级管理员不过滤
  if (userStore.isSuperuser) return routes

  const role = userStore.adminRole || 'user'
  const allowNamesByRole = {
    movie_admin: new Set(['MovieManagement', 'ReviewManagement']),
    forum_admin: new Set(['AdminForum']),
    order_admin: new Set(['AdminOrders']),
    user: new Set([])
  }
  const allow = allowNamesByRole[role] || new Set([])
  return routes.filter(r => allow.has(r.name))
})

const isAdminRouteAllowed = (routeName) => {
  if (userStore.isSuperuser) return true
  const role = userStore.adminRole || 'user'
  const allowNamesByRole = {
    movie_admin: new Set(['MovieManagement', 'ReviewManagement']),
    forum_admin: new Set(['AdminForum']),
    order_admin: new Set(['AdminOrders']),
    user: new Set([])
  }
  return (allowNamesByRole[role] || new Set([])).has(routeName)
}

// 当前激活菜单
const activeMenu = computed(() => {
  const { meta, path } = route
  const active = meta.activeMenu || path
  return active
})

// 面包屑导航
const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta?.title)
  return matched
})

// 缓存页面列表
const cachedViews = computed(() => {
  return userStore.cachedViews
})

// 切换侧边栏折叠
const toggleCollapse = () => {
  isCollapse.value =!isCollapse.value
  localStorage.setItem('sidebarStatus', isCollapse.value? 'closed' : 'Document')
}

// 处理用户资料
const handleProfile = () => {
  router.push('/profile')
}

// 处理退出登录
const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logout()
    router.push('/login')
  }).catch(() => {
  })
}

// 返回首页
const goHome = () => {
  router.push('/')
}

// 初始化检查权限
onMounted(async () => {
  // 未登录用户直接跳转
  const hasAuthToken = localStorage.getItem('authToken');

  if (!userStore.isAuthenticated &&!hasAuthToken) {
    router.push({
      name: 'login',
      query: { redirect: router.currentRoute.value.fullPath }
    });
    return;
  }

  // 强制获取最新用户信息（即使 isAuthenticated 为 true）
  await userStore.fetchUserProfile();

  // 验证管理员权限
  if (userStore.isAdmin) {
    showAdminContent.value = true;
  } else {
    router.push('/403'); // 添加无权限页面
  }

  loading.value = false;

  // 确保DOM更新后执行
  nextTick(() => {
  });

  handleResize();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// 响应式处理
const handleResize = () => {
  const currentWidth = window.innerWidth
  const shouldCollapse = currentWidth < 768

  // 自动关闭移动端侧边栏
  if (shouldCollapse &&!isCollapse.value) {
    isCollapse.value = true
  }
}

// 图标名称映射
const getIconName = (iconName) => {
  const iconMap = {
    'Odometer': 'dashboard',
    'User': 'user',
    'VideoPlay': 'movie',
    'ChatDotRound': 'comment',
    'TrendCharts': 'analytics',
    'ChatLineRound': 'forum',
    'Tickets': 'orders',
    'Setting': 'settings'
  }
  return iconMap[iconName] || 'menu'
}

// 路由变化时处理
watch(
  () => route.path,
  () => {
    // 角色越权拦截：非超级管理员只能进入对应模块
    if (route.path.startsWith('/admin') && route.name && !isAdminRouteAllowed(route.name)) {
      router.push('/403')
      return
    }
    // 自动关闭移动端侧边栏
    if (window.innerWidth < 768) {
      isCollapse.value = true
    }
  }
)
</script>

<style lang="scss" scoped>
.admin-layout {
  height: 100vh;
  background: #f5f7fa;

  .admin-sidebar {
    background: #304156;
    transition: width 0.3s;
    display: flex;
    flex-direction: column;
    border-right: 1px solid #e4e7ed;
    height: 100vh;
    position: fixed;
    left: 0;
    top: 0;
    z-index: 1000;

    .admin-menu {
      border-right: none;
      background: transparent;
      flex: 1;
      padding-top: 16px;

      :deep(.el-menu-item),
      :deep(.el-sub-menu__title) {
        color: rgba(255, 255, 255, 0.7);
        border-radius: 6px;
        margin: 2px 8px;
        transition: all 0.2s ease;
        height: 48px;
        line-height: 48px;

        &:hover {
          background-color: #263445 !important;
          color: #ffffff;
        }

        &.is-active {
          color: #ffffff !important;
          background-color: #409eff !important;
        }
      }

      :deep(.el-sub-menu .el-menu-item) {
        margin: 2px 16px;
        border-radius: 4px;
        height: 40px;
        line-height: 40px;
      }

      :deep(.el-menu-item svg),
      :deep(.el-sub-menu__title svg) {
        color: inherit;
        width: 18px;
        height: 18px;
        margin-right: 8px;
      }

      :deep(.el-sub-menu .el-menu-item svg) {
        width: 16px;
        height: 16px;
        margin-right: 8px;
      }

      // 收起状态下的图标显示
      &.el-menu--collapse {
        :deep(.el-menu-item) {
          padding: 0 !important;
          display: flex !important;
          justify-content: center !important;
          align-items: center !important;
          width: 64px !important;
          height: 48px !important;
          margin: 2px 0 !important;

          svg {
            margin: 0 !important;
            width: 20px !important;
            height: 20px !important;
            flex-shrink: 0 !important;
          }

          span {
            display: none !important;
          }
        }

        :deep(.el-sub-menu__title) {
          padding: 0 !important;
          display: flex !important;
          justify-content: center !important;
          align-items: center !important;
          width: 64px !important;
          height: 48px !important;
          margin: 2px 0 !important;

          svg {
            margin: 0 !important;
            width: 20px !important;
            height: 20px !important;
            flex-shrink: 0 !important;
          }

          span {
            display: none !important;
          }
        }

        :deep(.el-sub-menu) {
          .el-sub-menu__icon-arrow {
            display: none !important;
          }
        }
      }
    }

    .sidebar-footer {
      padding: 16px;
      display: flex;
      justify-content: center;
      border-top: 1px solid rgba(255, 255, 255, 0.1);

      .collapse-btn {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: rgba(255, 255, 255, 0.7);
        transition: all 0.2s ease;

        &:hover {
          background: #409eff;
          border-color: #409eff;
          color: #ffffff;
        }
      }
    }
  }

  .admin-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #ffffff;
    border-bottom: 1px solid #e4e7ed;
    box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
    padding: 0 24px;
    height: 56px;
    position: fixed;
    top: 0;
    right: 0;
    left: 240px;
    z-index: 999;
    transition: left 0.3s;

    .header-left {
      display: flex;
      align-items: center;

      .breadcrumb {
        :deep(.el-breadcrumb__inner) {
          color: #606266;
          font-weight: 500;
        }

        :deep(.el-breadcrumb__inner.is-link) {
          color: #409eff;
        }

        :deep(.el-breadcrumb__separator) {
          color: #c0c4cc;
        }
      }
    }

    .user-info {
      display: flex;
      align-items: center;
      cursor: pointer;
      padding: 8px 12px;
      border-radius: 6px;
      transition: all 0.2s ease;

      &:hover {
        background: #f5f7fa;
      }

      .user-name {
        margin: 0 8px;
        color: #303133;
        font-weight: 500;
      }

      :deep(.el-icon) {
        color: #909399;
      }
    }
  }

  .admin-main {
    background: #f5f7fa;
    padding: 16px;
    margin-left: 240px;
    margin-top: 56px;
    min-height: calc(100vh - 56px);
    transition: margin-left 0.3s;

    :deep(.el-card) {
      background: #ffffff;
      border: 1px solid #e4e7ed;
      color: #303133;
      margin-bottom: 16px;
      box-shadow: none;

      .el-card__header {
        border-bottom: 1px solid #e4e7ed;
        background: #fafafa;
        padding: 12px 16px;
      }

      .el-card__body {
        padding: 16px;
      }
    }
  }

  // 收起状态下的布局调整
  &.sidebar-collapsed {
    .admin-header {
      left: 64px;
    }

    .admin-main {
      margin-left: 64px;
    }
  }
}

// 未授权消息样式
.unauthorized-message {
  text-align: center;
  padding: 2rem;
  background: #f5f7fa;
  color: #303133;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  h1 {
    color: #f56c6c;
    margin-bottom: 1rem;
  }

  p {
    color: #909399;
    margin-bottom: 2rem;
  }

  :deep(.el-button) {
    background: #409eff;
    border-color: #409eff;
    color: #ffffff;

    &:hover {
      background: #66b1ff;
      border-color: #66b1ff;
    }
  }
}

// 加载状态样式
.loading-overlay {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #f5f7fa;

  .loading-icon {
    color: #409eff;
  }
}

// 响应式处理
@media screen and (max-width: 768px) {
  .admin-layout {
    .admin-header {
      left: 64px !important;
    }

    .admin-main {
      margin-left: 64px !important;
    }

    &.sidebar-collapsed {
      .admin-header {
        left: 0 !important;
      }

      .admin-main {
        margin-left: 0 !important;
      }
    }
  }
}

// 过渡动画
.fade-transform-leave-active,
.fade-transform-enter-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>