<template>
  <div class="movies-page">
    <div class="page-header">
      <h1>电影列表</h1>
      <p>发现更多精彩电影</p>
    </div>
    
    <div class="movies-container">
      <!-- 搜索和筛选 -->
      <div class="search-filters">
        <el-input
          v-model="searchQuery"
          placeholder="搜索电影..."
          @input="handleSearch"
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select v-model="selectedGenre" placeholder="选择类型" @change="filterMovies">
          <el-option label="全部类型" value=""></el-option>
          <el-option label="动作" value="action"></el-option>
          <el-option label="喜剧" value="comedy"></el-option>
          <el-option label="剧情" value="drama"></el-option>
          <el-option label="科幻" value="sci-fi"></el-option>
          <el-option label="恐怖" value="horror"></el-option>
        </el-select>
      </div>
      
      <!-- 电影网格 -->
      <div v-if="loading" class="loading">
        <el-skeleton :rows="3" animated />
        <p>正在加载电影...</p>
      </div>
      
      <div v-else-if="filteredMovies.length > 0" class="movies-grid">
        <div 
          v-for="movie in filteredMovies" 
          :key="movie.id"
          class="movie-card"
          @click="goToMovie(movie.id)"
        >
          <div class="movie-poster">
            <img 
              :src="getMoviePoster(movie.poster_path)"
              :alt="movie.title"
              @error="handlePosterError"
            >
            <div class="movie-overlay">
              <el-button type="primary" size="small">查看详情</el-button>
            </div>
          </div>
          <div class="movie-info">
            <h3>{{ movie.title }}</h3>
            <p class="movie-rating">
              <el-rate 
                v-model="movie.rating" 
                disabled 
                show-score 
                text-color="#ff9900"
                score-template="{value}"
              />
            </p>
            <p class="movie-year">{{ getYear(movie.release_date) }}</p>
          </div>
        </div>
      </div>
      
      <div v-else class="no-movies">
        <el-empty description="没有找到相关电影">
          <el-button @click="resetFilters" type="primary">重置筛选</el-button>
        </el-empty>
      </div>
      
      <!-- 分页 -->
      <div v-if="totalPages > 1" class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="totalMovies"
          layout="prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  name: 'MoviesView',
  components: {
    Search
  },
  setup() {
    const router = useRouter()
    const movies = ref([])
    const loading = ref(false)
    const searchQuery = ref('')
    const selectedGenre = ref('')
    const currentPage = ref(1)
    const pageSize = ref(20)
    const totalMovies = ref(0)
    
    const filteredMovies = computed(() => {
      let result = movies.value
      
      if (searchQuery.value) {
        result = result.filter(movie => 
          movie.title.toLowerCase().includes(searchQuery.value.toLowerCase())
        )
      }
      
      if (selectedGenre.value) {
        result = result.filter(movie => 
          movie.genres && movie.genres.some(genre => 
            genre.toLowerCase().includes(selectedGenre.value)
          )
        )
      }
      
      return result
    })
    
    const totalPages = computed(() => {
      return Math.ceil(filteredMovies.value.length / pageSize.value)
    })
    
    const loadMovies = async () => {
      loading.value = true
      try {
        const response = await axios.get('/api/movies/', {
          params: {
            page: currentPage.value,
            page_size: pageSize.value
          }
        })
        
        movies.value = response.data.results || response.data || []
        totalMovies.value = response.data.count || movies.value.length
        
        // 如果API返回的数据不够，添加一些模拟数据
        if (movies.value.length === 0) {
          movies.value = generateMockMovies()
          totalMovies.value = movies.value.length
        }
      } catch (error) {
        console.error('加载电影失败:', error)
        ElMessage.error('加载电影失败')
        // 使用模拟数据
        movies.value = generateMockMovies()
        totalMovies.value = movies.value.length
      } finally {
        loading.value = false
      }
    }
    
    const generateMockMovies = () => {
      return [
        {
          id: 1,
          title: '阿凡达：水之道',
          poster_path: '/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg',
          release_date: '2022-12-16',
          rating: 4.2,
          genres: ['科幻', '动作', '冒险']
        },
        {
          id: 2,
          title: '黑豹2：瓦坎达万岁',
          poster_path: '/sv1xJUazXeYqALzczSZ3O6nkH75.jpg',
          release_date: '2022-11-11',
          rating: 4.0,
          genres: ['动作', '科幻', '剧情']
        },
        {
          id: 3,
          title: '壮志凌云：独行侠',
          poster_path: '/62HCnUTziyWcpDaBO2i1DX17ljH.jpg',
          release_date: '2022-05-27',
          rating: 4.5,
          genres: ['动作', '剧情']
        },
        {
          id: 4,
          title: '奇异博士2：疯狂多元宇宙',
          poster_path: '/9Gtg2DzBhmYamXBS1hKAhiwbBKS.jpg',
          release_date: '2022-05-06',
          rating: 3.8,
          genres: ['科幻', '动作', '奇幻']
        },
        {
          id: 5,
          title: '雷神4：爱与雷电',
          poster_path: '/pIkRyD18kl4FhoCNQuWxWu5cBLM.jpg',
          release_date: '2022-07-08',
          rating: 3.6,
          genres: ['动作', '科幻', '喜剧']
        }
      ]
    }
    
    const getMoviePoster = (posterPath) => {
      if (!posterPath) return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjQ1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+CiAgPHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxOCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPueUteW9seaWt+aKpTwvdGV4dD4KPC9zdmc+'
      if (posterPath.startsWith('http')) return posterPath
      return `https://image.tmdb.org/t/p/w300${posterPath}`
    }
    
    const handlePosterError = (event) => {
      event.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjQ1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+CiAgPHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxOCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPueUteW9seaWt+aKpTwvdGV4dD4KPC9zdmc+'
      event.target.onerror = null
    }
    
    const getYear = (dateString) => {
      if (!dateString) return '未知'
      return new Date(dateString).getFullYear()
    }
    
    const goToMovie = (movieId) => {
      router.push(`/movie/${movieId}`)
    }
    
    const handleSearch = () => {
      // 搜索逻辑已在computed中处理
    }
    
    const filterMovies = () => {
      // 筛选逻辑已在computed中处理
    }
    
    const resetFilters = () => {
      searchQuery.value = ''
      selectedGenre.value = ''
    }
    
    const handlePageChange = (page) => {
      currentPage.value = page
      loadMovies()
    }
    
    onMounted(() => {
      loadMovies()
    })
    
    return {
      movies,
      loading,
      searchQuery,
      selectedGenre,
      currentPage,
      pageSize,
      totalMovies,
      filteredMovies,
      totalPages,
      getMoviePoster,
      handlePosterError,
      getYear,
      goToMovie,
      handleSearch,
      filterMovies,
      resetFilters,
      handlePageChange
    }
  }
}
</script>

<style scoped>
.movies-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.page-header p {
  color: #7f8c8d;
  font-size: 16px;
}

.search-filters {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  align-items: center;
}

.search-input {
  flex: 1;
  max-width: 400px;
}

.loading {
  text-align: center;
  padding: 40px;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.movie-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
}

.movie-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.movie-poster {
  position: relative;
  width: 100%;
  height: 300px;
  overflow: hidden;
}

.movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.movie-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.movie-card:hover .movie-overlay {
  opacity: 1;
}

.movie-info {
  padding: 15px;
}

.movie-info h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 16px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.movie-rating {
  margin: 5px 0;
}

.movie-year {
  margin: 5px 0 0 0;
  color: #95a5a6;
  font-size: 14px;
}

.no-movies {
  text-align: center;
  padding: 60px 20px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}

@media (max-width: 768px) {
  .search-filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .movies-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 15px;
  }
  
  .movie-poster {
    height: 225px;
  }
}
</style> 