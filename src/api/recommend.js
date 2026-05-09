// api/recommend.js
import http from '@/utils/request';

export const getRecommendations = () => {
  return http.get('/recommend/')
    .then(response => {
      // 直接返回后端的响应数据
      return {
        data: response.data
      }
    })
    .catch(error => {
      console.error('获取推荐失败:', error);
      return { 
        data: { 
          status: 'error',
          recommendations: [] 
        } 
      };
    });
};