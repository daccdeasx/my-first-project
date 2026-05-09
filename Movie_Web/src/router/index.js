import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import MovieDetail from '../views/MovieDetail.vue';
import NotificationListView from '@/views/NotificationListView.vue'; // 新增导入
import YearlyReport from '@/views/YearlyReport.vue'
import MoviePlayer from '@/views/MoviePlayer.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/register',
      name: 'register',
      component: Register
    },
    {
      path: '/movie/:id(\\d+)',
      name: 'MovieDetail',
      component: MovieDetail,
      props: true
    },
    {
      path: '/movies',
      name: 'Movies',
      component: () => import('../views/MoviesView.vue')
    },
    {
      path: '/profile',
      name: 'Profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/library',
      name: 'Library',
      component: () => import('../views/LibraryView.vue')
    },
    {
      path: '/ranking',
      name: 'Ranking',
      component: () => import('@/views/RankingView.vue')
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/SettingsView.vue'),
    },
    {
      path: '/collection',
      name: 'Collection',
      component: () => import('../views/CollectionView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/recommend',
      name: 'Recommend',
      component: () => import('@/views/RecommendView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/search',
      name: 'Search',
      component: () => import('../views/SearchView.vue'),
    },
    // 论坛相关路由
    {
      path: '/forum',
      name: 'Forum',
      component: () => import('@/views/ForumView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/forum/create',
      name: 'CreatePost',
      component: () => import('@/views/forum/CreatePost.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/forum/post/:pk',
      name: 'PostDetail',
      component: () => import('@/views/forum/PostDetail.vue'),
      props: true,
      meta: { requiresAuth: true }
    },
      {
      path: '/notifications',
      name: 'Notifications',
      component: NotificationListView,
      meta: { requiresAuth: true }
    },
    // 新增管理员路由
    {
      path: '/admin',
      name: 'Admin',
      component: () => import('@/layouts/AdminLayout.vue'),
      meta: {
        requiresAuth: true,
        requiresAdmin: true,
        title: '管理员控制台'
      },
      redirect: { name: 'AdminDashboard' },
      children: [
        {
          path: 'dashboard',
          name: 'AdminDashboard',
          component: () => import('@/views/admin/Dashboard.vue'),
          meta: { title: '仪表盘', icon: 'Odometer' }
        },
        {
          path: 'users',
          name: 'UserManagement',
          component: () => import('@/views/admin/UserManagement.vue'),
          meta: { title: '用户管理', icon: 'User' }
        },
        {
          path: 'movies',
          name: 'MovieManagement',
          component: () => import('@/views/admin/MovieManagement.vue'),
          meta: { title: '电影管理', icon: 'VideoPlay' }
        },
        {
          path: 'reviews',
          name: 'ReviewManagement',
          component: () => import('@/views/admin/ReviewManagement.vue'),
          meta: { title: '评论管理', icon: 'ChatDotRound' }
        },
        {
          path: 'analytics',
          name: 'DataAnalytics',
          component: () => import('@/views/admin/DataAnalytics.vue'),
          meta: { title: '数据分析', icon: 'TrendCharts' }
        },
        {
          path: 'forum',
          name: 'AdminForum',
          component: () => import('@/views/admin/ForumManagement.vue'),
          meta: { title: '论坛管理', icon: 'ChatLineRound' }
        },
        {
          path: 'orders',
          name: 'AdminOrders',
          component: () => import('@/views/admin/AdminOrdersView.vue'),
          meta: { title: '订单管理', icon: 'Tickets' }
        }
      ]
    },
    {
      path: '/movie/:id/ticketing',
      name: 'Ticketing',
      component: () => import('../views/TicketingView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/orders',
      name: 'Orders',
      component: () => import('../views/OrdersView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/orders/:id',
      name: 'OrderDetail',
      component: () => import('../views/OrderDetailView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/yearly-report',
      name: 'YearlyReport',
      component: YearlyReport,
      meta: {
        requiresAuth: true
      }
    },
    // 403 禁止访问页面
    {
      path: '/403',
      name: 'Forbidden',
      component: () => import('../views/ForbiddenView.vue')
    },
    {
      path: '/movie/player',
      name: 'MoviePlayer',
      component: MoviePlayer
    }
  ]
});

// 路由守卫
router.beforeEach((to, from, next) => {
  console.log('[Router] 路由守卫触发', {
    to: to.path,
    from: from.path,
    toName: to.name,
    meta: to.meta
  })

  const token = localStorage.getItem('authToken')
  const isAuthenticated = !!token

  console.log('[Router] 认证状态:', { isAuthenticated, hasToken: !!token })

  // 检查路由是否需要认证
  if (to.matched.some(record => record.meta.requiresAuth)) {
    console.log('[Router] 路由需要认证')
    if (!isAuthenticated) {
      console.log('[Router] 用户未认证，跳转到登录页')
      // 未登录，跳转到登录页面，并保存原始路径
      next({
        name: 'login',
        query: { redirect: to.fullPath }
      })
      return
    }
  }

  // 检查是否需要管理员权限
  if (to.matched.some(record => record.meta.requiresAdmin)) {
    console.log('[Router] 路由需要管理员权限')
    if (!isAuthenticated) {
      console.log('[Router] 用户未认证，跳转到登录页')
      next({
        name: 'login',
        query: { redirect: to.fullPath }
      })
      return
    }
    // 管理员权限检查在 AdminLayout 组件中进行（包含角色越权拦截）
  }

  // 如果已登录用户访问登录或注册页面，重定向到首页
  if (isAuthenticated && (to.name === 'login' || to.name === 'register')) {
    console.log('[Router] 已登录用户访问登录/注册页，重定向到首页')
    next({ name: 'home' })
    return
  }

  console.log('[Router] 路由守卫通过，继续导航')
  next()
})

export default router