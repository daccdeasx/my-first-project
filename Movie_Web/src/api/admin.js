import http from '@/utils/axios'

//系统设置API
export const getSystemConfig = () => {
  return http.get('/users/admin/system/config/')
}

export const updateSystemConfig = (data) => {
  return http.put('/users/admin/system/config/', data)
}

export const systemBackup = () => {
  return http.get('/users/admin/system/backup/', {
    responseType: 'blob'
  })
}

export const getSystemLogs = (params) => {
  return http.get('/users/admin/system/logs/', { params })
}

export const clearSystemCache = () => {
  return http.delete('/users/admin/system/cache/')
}

// 新增获取配置版本的函数
export const getConfigVersions = () => {
  return http.get('/users/admin/config_versions/')
    .then(response => {
      // 成功获取版本列表
      return response.data;
    })
    .catch(error => {
      console.error('获取配置版本失败:', error);
      // 统一错误处理
      if (error.response) {
        throw new Error(`获取配置版本失败: ${error.response.data.message || error.response.statusText}`);
      } else if (error.request) {
        throw new Error('服务器未响应，请检查网络连接');
      } else {
        throw new Error(`请求配置版本时出错: ${error.message}`);
      }
    });
};

export const clearSystemLogs = () => {
  return http.delete('/users/admin/system/logs/clear/')
    .then(response => response.data)
    .catch(error => {
      console.error('清除日志失败:', error)
      throw error
    })
}


// 在 admin.js 中
export const getSystemHealth = () => {
  return http.get('/users/admin/system/health/')
    .then(response => {
      console.log('系统健康状态响应:', response)
      return response.data || response // 根据实际情况调整
    })
    .catch(error => {
      console.error('获取系统健康状态失败:', error)
      throw new Error('获取系统健康状态失败，请重试')
    })
}


//数据分析API
export const fetchDataAnalytics = () => {
  return http.get('/users/admin/analytics/')
}

// 导出报表API
export const exportAnalyticsReport = (params = {}) => {
  return http({
    url: '/users/admin/analytics/export/',
    method: 'get',
    responseType: 'blob', // 重要：指定响应类型为二进制流
    params
  })
}

// 用户评论管理API
export const getAdminReviews = (params) => {
  return http.get('/admin/reviews/', { params })
}

export const deleteReviewApi = (id) => {
  return http.delete(`/admin/reviews/${id}/`)
}

export const toggleReviewStatusApi = (id) => {
  return http.post(`/admin/reviews/${id}/toggle-status/`)
}

export const batchDeleteReviewsApi = (ids) => {
  return http.delete('/admin/reviews/batch/', { data: { ids } })
}

// 电影管理API
export const getAdminMovies = (params) => {
  return http.get('/admin/movies/', { params })
}

export const createMovie = (data) => {
  return http.post('/admin/movies/', data)
}

export const updateMovie = (tmdbId, data) => {
  return http.put(`/admin/movies/${tmdbId}/`, data)
}

export const deleteMovieApi = (tmdbId) => {
  return http.delete(`/admin/movies/${tmdbId}/`)
}

// 用户管理API
export const fetchUsers = (params) => {
  return http.get('/users/admin/users/', { params })
}

export const toggleUserStatusApi = (userId) => {
  return http.post(`/users/admin/users/${userId}/toggle-status/`)
}

export const deleteUserApi = (userId) => {
  return http.delete(`/users/admin/users/delete/${userId}/`)
}

export const updateUserRoleApi = (userId, admin_role) => {
  return http.patch(`/users/admin/users/${userId}/role/`, { admin_role })
}

// 仪表盘数据API
const useMockData = import.meta.env.VITE_USE_MOCK === 'true'

const mockDashboardData = {
  total_users: 1423,
  total_movies: 567,
  today_reviews: 23,
  user_growth: [
    { date: '09-01', value: 100 },
    { date: '09-02', value: 230 },
    { date: '09-03', value: 420 }
  ],
  genre_distribution: [
    { value: 335, name: '动作片' },
    { value: 280, name: '喜剧片' },
    { value: 190, name: '爱情片' }
  ],
  recent_activities: [
    {
      timestamp: '2023-09-20 14:30',
      title: '系统维护',
      content: '完成数据库优化'
    }
  ]
}

export const fetchDashboardData = async () => {
  if (useMockData) {
    return mockDashboardData
  }

  try {
    const response = await http.get('/users/admin/dashboard/')
    return response.data
  } catch (error) {
    console.error('仪表盘数据请求失败', error)
    throw new Error('仪表盘数据加载失败，请重试')
  }
}  