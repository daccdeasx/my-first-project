import axios from 'axios'

const MAOYAN_BASE_URL = 'https://apis.netstart.cn/maoyan'

// 创建猫眼API实例
const maoyanApi = axios.create({
  baseURL: MAOYAN_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
maoyanApi.interceptors.request.use(
  config => {
    console.log('猫眼API请求:', config.url, config.params)
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
maoyanApi.interceptors.response.use(
  response => {
    console.log('猫眼API响应:', response.data)
    return response.data
  },
  error => {
    console.error('猫眼API错误:', error)
    // 如果是网络错误或API不可用，返回模拟数据
    if (error.code === 'NETWORK_ERROR' || error.response?.status >= 500) {
      console.log('猫眼API不可用，返回模拟数据')
      return Promise.resolve({
        status: 'mock',
        message: '使用模拟数据',
        data: null
      })
    }
    return Promise.reject(error)
  }
)

export const maoyanService = {
  // 搜索建议
  searchSuggest(kw, cityId = 1) {
    return maoyanApi.get('/search/suggest', {
      params: { kw, cityId }
    })
  },

  // 电影搜索
  searchMovies(keyword, ci = 1, offset = 0, limit = 20) {
    const params = { keyword, ci }
    if (offset > 0) {
      params.offset = offset
      params.limit = limit
    }
    return maoyanApi.get('/search/movies', { params })
  },

  // 影院搜索
  searchCinemas(keyword, ci = 1, offset = 0, limit = 20) {
    const params = { keyword, ci }
    if (offset > 0) {
      params.offset = offset
      params.limit = limit
    }
    return maoyanApi.get('/search/cinemas', { params })
  },

  // 影院详情
  getCinemaDetail(cinemaId) {
    return maoyanApi.get('/cinema/detail', {
      params: { cinemaId }
    })
  },

  // 影院正在上映电影列表
  getCinemaShows(cinemaId, ci, channelId = 4) {
    return maoyanApi.get('/cinema/shows', {
      params: { cinemaId, ci, channelId }
    })
  },

  // 影院座位信息
  getCinemaSeats(size = 'small') {
    const url = size === 'medium' ? '/cinema/seat-m.json' : '/cinema/seat.json'
    return maoyanApi.get(url)
  },

  // 视频Feed列表
  getVideoFeed(offset = 0, feedChannelId = 4) {
    return maoyanApi.get(`/video/${offset}`, {
      params: { feedChannelId }
    })
  },

  // 小视频Feed列表
  getShortVideoFeed(offset = 0) {
    return maoyanApi.get(`/video/short/${offset}`)
  },

  // 影片详情（猫眼版本）
  getMaoyanMovieDetail(movieId) {
    return maoyanApi.get('/movie/detail', {
      params: { movieId }
    })
  },

  // 影片介绍（购票页面简介）
  getMaoyanMovieIntro(movieId) {
    return maoyanApi.get('/movie/intro', {
      params: { movieId }
    })
  },

  // 影片上映日期
  getMaoyanMovieShowDays(movieId, cityId = 20) {
    return maoyanApi.get('/movie/showdays', {
      params: { movieId, cityId }
    })
  },

  // 影院超值套餐
  getCinemaDeals() {
    return maoyanApi.get('/cinema/queryDealList.json')
  },

  // 电影简介
  getMovieIntro(movieId) {
    return maoyanApi.get('/movie/intro', {
      params: { movieId }
    })
  },

  // 电影上映日期
  getMovieShowDays(movieId, cityId = 20) {
    return maoyanApi.get('/movie/showdays', {
      params: { movieId, cityId }
    })
  },

  // 电影上映影院筛选条件
  getSelectItems(movieId, cityId = 20, showDate) {
    return maoyanApi.get('/movie/select/items', {
      params: { movieId, cityId, showDate }
    })
  },

  // 电影上映影院筛选结果
  getSelectCinemas(params) {
    const defaultParams = {
      limit: 20,
      offset: 0,
      sort: 'distance',
      cityId: 20,
      districtId: -1,
      lineId: -1,
      areaId: -1,
      stationId: -1,
      brandIds: '[-1]',
      serviceIds: '[-1]',
      hallTypeIds: '["all"]',
      languageIds: '["all"]',
      dimIds: '["all"]'
    }
    
    return maoyanApi.get('/movie/select/cinemas', {
      params: { ...defaultParams, ...params }
    })
  }
}

export default maoyanService 