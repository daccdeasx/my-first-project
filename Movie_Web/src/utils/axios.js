import axios from 'axios';

const instance = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 30000,
  // 移除这里的Authorization头，改为在拦截器中动态设置
});

// 只保留一个请求拦截器
instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');

    // 如果有token，添加到请求头
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }

    // 移除自动拦截逻辑，让路由守卫和后端处理权限验证
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 添加响应拦截器处理401错误
instance.interceptors.response.use(
  (response) => response,
  (error) => {
    console.log('[Axios] 响应拦截器捕获错误:', {
      status: error.response?.status,
      url: error.config?.url,
      method: error.config?.method
    })

    if (error.response && error.response.status === 401) {
      console.log('[Axios] 401错误，清除token但不自动跳转')
      // 认证失败，清除token但不自动跳转，让组件自己处理
      localStorage.removeItem('authToken');
      // 移除自动跳转，让各个组件根据需要自行处理
    }
    return Promise.reject(error);
  }
);

export default instance;