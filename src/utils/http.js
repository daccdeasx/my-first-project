import axios from 'axios';

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器
http.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
http.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.log('[HTTP] 响应拦截器捕获错误:', {
      status: error.response?.status,
      url: error.config?.url,
      method: error.config?.method
    })

    if (error.response) {
      // 只有在管理员页面时才自动跳转到登录页
      const isAdminPage = window.location.pathname.includes('/admin');
      if (error.response.status === 401 && isAdminPage) {
        console.log('[HTTP] 管理员页面401错误，跳转到登录页')
        localStorage.removeItem('authToken');
        window.location.href = '/login';
      } else if (error.response.status === 401) {
        console.log('[HTTP] 普通页面401错误，清除token但不跳转')
        localStorage.removeItem('authToken');
      }
      return Promise.reject(error.response.data);
    }
    return Promise.reject(error);
  }
);

export default http;