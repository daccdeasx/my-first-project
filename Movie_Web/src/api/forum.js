import http from '@/utils/axios';

// 普通用户 API
export const fetchPosts = (theme, sort) => {
  let url = '/users/posts/';
  const params = {};
  
  if (theme) params.theme = theme;
  if (sort) params.sort = sort;
  
  return http.get(url, { params });
};

export const createPost = (data) => {
  const token = localStorage.getItem('token');
  
  return http.post('/users/posts/', data, {
    headers: {
      'Content-Type': 'multipart/form-data',
      ...(token && { Authorization: `Token ${token}` })
    }
  });
};

export const fetchPost = (pk) => {
  return http.get(`/users/posts/${pk}/`);
};

export const createReply = (postPk, data) => {
  const token = localStorage.getItem('token');
  
  return http.post(`/users/posts/${postPk}/replies/`, data, {
    headers: {
      ...(token && { Authorization: `Token ${token}` })
    }
  });
};

// 点赞与收藏
export const toggleLike = (postId) => {
  const token = localStorage.getItem('token');
  
  return http.post(`/users/posts/${postId}/like/`, null, {
    headers: {
      ...(token && { Authorization: `Token ${token}` })
    }
  });
};

export const toggleFavorite = (postId) => {
  const token = localStorage.getItem('token');
  
  return http.post(`/users/posts/${postId}/favorite/`, null, {
    headers: {
      ...(token && { Authorization: `Token ${token}` })
    }
  });
};

// 热门帖子
export const fetchHotPosts = () => {
  return http.get('/users/posts/hot/');
};

// 用户相关
export const fetchUserCollection = () => {
  const token = localStorage.getItem('token');
  
  return http.get('/users/collection/', {
    headers: {
      ...(token && { Authorization: `Token ${token}` })
    }
  });
};

export const fetchUserNotifications = () => {
  const token = localStorage.getItem('token');
  
  return http.get('/users/notifications/', {
    headers: {
      ...(token && { Authorization: `Token ${token}` })
    }
  });
};

export const markNotificationAsRead = (notificationId) => {
  const token = localStorage.getItem('token');
  
  return http.patch(`/users/notifications/${notificationId}/read/`, null, {
    headers: {
      ...(token && { Authorization: `Token ${token}` })
    }
  });
};

// 管理员 API
export const fetchPendingPosts = () => {
  const token = localStorage.getItem('token');
  
  return http.get('/users/admin/posts/pending/', {
    headers: {
      ...(token && { Authorization: `Token ${token}` })
    }
  });
};

export const approvePost = (postId) => {
  const token = localStorage.getItem('token');
  
  return http.put(`/users/admin/posts/${postId}/approve/`, null, {
    headers: {
      ...(token && { Authorization: `Token ${token}` })
    }
  });
};

export const rejectPost = (postId, reason) => {
  const token = localStorage.getItem('token');
  
  return http.put(`/users/admin/posts/${postId}/reject/`, { reason }, {
    headers: {
      ...(token && { Authorization: `Token ${token}` })
    }
  });
};

// 更新：支持分页查询和搜索
export const fetchAllPosts = (status, page = 1, search = '') => {
  const token = localStorage.getItem('token');
  let url = `/users/admin/posts/all/?page=${page}`;
  
  if (status && status !== 'all') {
    url += `&status=${status}`;
  }
  
  if (search && search.trim()) {
    url += `&search=${encodeURIComponent(search.trim())}`;
  }
  
  return http.get(url, {
    headers: {
      ...(token && { Authorization: `Token ${token}` })
    }
  });
};

// 系统管理 API
export const fetchAdminDashboard = () => {
  const token = localStorage.getItem('token');
  
  return http.get('/users/admin/dashboard/', {
    headers: {
      ...(token && { Authorization: `Token ${token}` })
    }
  });
};

export const fetchSystemHealth = () => {
  const token = localStorage.getItem('token');
  
  return http.get('/users/admin/system/health/', {
    headers: {
      ...(token && { Authorization: `Token ${token}` })
    }
  });
};

// 用户认证
export const login = (credentials) => {
  return http.post('/users/login/', credentials);
};

export const register = (userData) => {
  return http.post('/users/register/', userData);
};

export const fetchUserProfile = () => {
  const token = localStorage.getItem('token');
  
  return http.get('/users/profile/', {
    headers: {
      ...(token && { Authorization: `Token ${token}` })
    }
  });
};

export const updateUserSettings = (settingsData) => {
  const token = localStorage.getItem('token');
  
  return http.put('/users/settings/', settingsData, {
    headers: {
      ...(token && { Authorization: `Token ${token}` })
    }
  });
};

// 用户搜索API
export const fetchUserSuggestions = (keyword) => {
  const token = localStorage.getItem('token');
  return http.get(`/users/search/?keyword=${keyword}`, {
    headers: {
      ...(token && { Authorization: `Token ${token}` })
    }
  });
};

// 置顶帖子 API
export const togglePinPost = (postId) => {
  const token = localStorage.getItem('token');
  return http.put(`/users/admin/posts/${postId}/pin/`, null, {
    headers: {
      'Authorization': `Token ${token}`
    }
  });
};

// src/api/forum.js
export const deletePost = (postId) => {
  return http.delete(`/users/admin/posts/${postId}/`, {
    headers: {
      Authorization: `Token ${localStorage.getItem('token')}`
    }
  });
};

// 批量操作 API
export const batchApprovePosts = (postIds) => {
  const token = localStorage.getItem('token');
  
  return http.post('/users/admin/posts/batch-approve/', { post_ids: postIds }, {
    headers: {
      ...(token && { Authorization: `Token ${token}` })
    }
  });
};

export const batchDeletePosts = (postIds) => {
  const token = localStorage.getItem('token');
  
  return http.post('/users/admin/posts/batch-delete/', { post_ids: postIds }, {
    headers: {
      ...(token && { Authorization: `Token ${token}` })
    }
  });
};

// 获取帖子统计信息
export const fetchPostStats = () => {
  const token = localStorage.getItem('token');
  
  return http.get('/users/admin/posts/stats/', {
    headers: {
      ...(token && { Authorization: `Token ${token}` })
    }
  });
};