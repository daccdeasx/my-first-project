import request from '@/utils/request';

// 获取系统设置
export const fetchSettings = async () => {
  try {
    const response = await request({
      url: '/api/admin/settings',
      method: 'get'
    });
    return response;
  } catch (error) {
    console.error('获取系统设置失败:', error);
    throw error;
  }
};

// 更新系统设置
export const updateSettings = async (data) => {
  try {
    const response = await request({
      url: '/api/admin/settings',
      method: 'put',
      data
    });
    return response;
  } catch (error) {
    console.error('更新系统设置失败:', error);
    throw error;
  }
}; 