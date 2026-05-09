// src/api/user.js
import http from '@/utils/axios';

// 用户认证
export const login = (credentials) => {
  return http.post('/users/login/', credentials);
};

export const register = (userData) => {
  return http.post('/users/register/', userData);
};

// 用户资料
export const fetchUserProfile = () => {
  return http.get('/users/profile/', {
    headers: {
      Authorization: `Token ${localStorage.getItem('authToken')}`
    }
  });
};

export const updateUserProfile = (data) => {
  return http.patch('/users/profile/', data, {
    headers: {
      Authorization: `Token ${localStorage.getItem('authToken')}`,
      'Content-Type': 'multipart/form-data'
    }
  });
};

// 用户评论
export const fetchUserReviews = () => {
  return http.get('/users/reviews/', {
    headers: {
      Authorization: `Token ${localStorage.getItem('authToken')}`
    }
  });
};

export const updateReview = (tmdbId, reviewId, data) => {
  return http.put(`/movies/${tmdbId}/reviews/${reviewId}/`, data, {
    headers: {
      Authorization: `Token ${localStorage.getItem('authToken')}`
    }
  });
};

export const deleteReview = (reviewId) => {
  return http.delete(`/users/reviews/${reviewId}/`, {
    headers: {
      Authorization: `Token ${localStorage.getItem('authToken')}`
    }
  });
};

// 用户收藏
export const fetchUserCollections = () => {
  return http.get('/users/post-collections/', {
    headers: {
      Authorization: `Token ${localStorage.getItem('authToken')}`
    }
  });
};

// 通知
export const fetchUserNotifications = () => {
  return http.get('/users/notifications/', {
    headers: {
      Authorization: `Token ${localStorage.getItem('authToken')}`
    }
  });
};

export const markNotificationAsRead = (notificationId) => {
  return http.patch(`/users/notifications/${notificationId}/read/`, null, {
    headers: {
      Authorization: `Token ${localStorage.getItem('authToken')}`
    }
  });
};

// 设置
export const updateUserSettings = (settingsData) => {
  return http.put('/users/settings/', settingsData, {
    headers: {
      Authorization: `Token ${localStorage.getItem('authToken')}`
    }
  });
};

// 新增接口（修正为使用 http 而非 axios）
export const fetchUserPosts = () => {
  return http.get('/users/posts/', { // 此处应为 http.get
    headers: {
      Authorization: `Token ${localStorage.getItem('authToken')}`
    }
  });
};

export const deletePost = (postId) => {
  return http.delete(`/users/posts/${postId}/`, { // 此处应为 http.delete
    headers: {
      Authorization: `Token ${localStorage.getItem('authToken')}`
    }
  });
};