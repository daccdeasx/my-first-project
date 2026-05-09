// utils/request.js 完整配置
import axios from 'axios'
import router from '@/router'

const instance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
instance.interceptors.request.use(config => {
  const token = localStorage.getItem('authToken') // 使用正确的 token key
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  // 移除自动跳转逻辑，让路由守卫处理权限验证
  return config
})

// 响应拦截器
instance.interceptors.response.use(
  response => {
    return response
  },
  async error => {
    // 处理网络错误
    if (!error.response) {
      // 检查是否是超时错误
      if (error.code === 'ECONNABORTED') {
        error.message = '请求超时，请检查网络连接'
      } else if (error.message.includes('Network Error')) {
        error.message = '网络连接失败，请检查网络设置'
      } else {
        error.message = '请求失败，请稍后重试'
      }
      return Promise.reject(error)
    }

    const status = error.response.status
    const messageMap = {
      400: '请求参数错误',
      401: '登录已过期',
      403: '没有访问权限',
      404: '资源不存在',
      500: '服务器错误'
    }

    // 设置错误消息
    error.message = messageMap[status] || `请求失败 (${status})`

    // 处理401错误
    if (status === 401) {
      console.log('[Request] 401错误，清除token但不自动跳转')
      localStorage.removeItem('authToken') // 使用正确的 token key
      // 移除自动跳转，让组件自己处理
    }

    // 处理404错误
    if (status === 404) {
      console.error('请求的资源不存在:', error.config.url)
    }

    return Promise.reject(error)
  }
)

export default instance