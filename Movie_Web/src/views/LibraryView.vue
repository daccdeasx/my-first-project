<template>
    <div class="library-container">
        <!-- 搜索框 -->
        <div class="search-section">
            <div class="search-box">
                <input
                    type="text"
                    v-model="searchQuery"
                    placeholder="搜索电影名称、演员、导演..."
                    @keyup.enter="handleSearch"
                    class="search-input"
                >
                <button @click="handleSearch" class="search-button">搜索</button>
            </div>
        </div>

        <!-- 新增加载状态 -->
        <div v-if="loading" class="loading-overlay">
            <div class="loader"></div>
            <p>正在加载电影...</p>
        </div>

        <!-- 新增空状态 -->
        <div v-if="!loading && movies.length === 0" class="empty-state">
            <img src="https://www.svgrepo.com/show/452030/empty.svg" alt="没有找到电影">
            <p>没有找到符合条件的电影</p>
            <button @click="resetFilters">重置筛选条件</button>
        </div>



        <!-- 紧凑筛选器 -->
        <div class="filters-container">
            <!-- 类型筛选 -->
            <div class="filter-section">
                <span class="filter-label">类型：</span>
                <div class="genre-tags">
                    <button
                        v-for="genre in genres"
                        :key="genre.id"
                        :class="['genre-tag', { active: selectedGenres.includes(genre.id) }]"
                        @click="toggleGenre(genre.id)"
                    >
                        {{ genre.name }}
                    </button>
                </div>
            </div>

            <!-- 年份和地区筛选 -->
            <div class="filter-section">
                <span class="filter-label">年份：</span>
                <div class="year-tags">
                    <button
                        v-for="year in years"
                        :key="year"
                        :class="['year-tag', { active: selectedYear === year.toString() }]"
                        @click="selectYear(year)"
                    >
                        {{ year }}
                    </button>
                </div>
            </div>

            <div class="filter-section">
                <span class="filter-label">地区：</span>
                <div class="region-tags">
                    <button
                        v-for="region in regions"
                        :key="region.value"
                        :class="['region-tag', { active: selectedRegion === region.value }]"
                        @click="selectRegion(region.value)"
                    >
                        {{ region.label }}
                    </button>
                </div>
            </div>
        </div>

        <!-- 影片列表 -->
        <div class="movie-list">
            <div
                v-for="movie in movies"
                :key="movie.id"
                class="movie-card"
                @click="goToDetail(movie.id)"
            >
                <img
                    :src="`https://image.tmdb.org/t/p/w300${movie.poster_path}`"
                    :alt="movie.title"
                    class="poster"
                >
                <div class="movie-info">
                    <h3>{{ movie.title }}</h3>
                    <div class="rating">
                        <span>★</span>
                        {{ movie.vote_average }}
                    </div>
                    <div class="meta">
                        <span>{{ movie.release_date.slice(0,4) }}</span>

                    </div>
                    <!-- 新增类型标签显示 -->
                    <div class="genres">
                        {{ movie.genres.join(', ') }}
                    </div>
                </div>
            </div>
        </div>

        <!-- 分页 -->
        <div class="pagination">
            <button
                :disabled="currentPage === 1"
                @click="changePage(currentPage - 1)"
            >
                上一页
            </button>
            <input
                type="number"
                v-model.number="inputPage"
                min="1"
                :max="totalPages"
                @keyup.enter="goToPage"
            >
            <span> / {{ totalPages }}</span>
            <button
                :disabled="currentPage === totalPages"
                @click="changePage(currentPage + 1)"
            >
                下一页
            </button>
        </div>
    </div>
</template>

<script>
import axios from 'axios'
import { debounce } from 'lodash-es' // 需要安装 lodash-es

export default {
    data() {
        return {
            movies: [],
            genres: [],
            selectedGenres: [],
            selectedYear: '',
            selectedRegion: '',
            currentPage: 1,
            totalPages: 1,
            years: Array.from({ length: 50 }, (_, i) => new Date().getFullYear() - i),
            loading: false,
            error: null,
            // 缓存最近请求参数避免重复请求
            lastRequestParams: null,
            inputPage: 1,
            regions: [
                { value: 'CN', label: '中国大陆' },
                { value: 'US', label: '北美' },
                { value: 'KR', label: '韩国' },
                { value: 'JP', label: '日本' },
                { value: 'HK', label: '香港' },
                { value: 'TW', label: '台湾' }
            ],
            // 新增搜索关键词
            searchQuery: ''
        }
    },
    watch: {
        // 使用深度监听和防抖
        selectedGenres: {
            handler: debounce(function () {
                this.validateAndFetch()
            }, 3000),
            deep: true
        },
        selectedYear: {
            handler: debounce(function () {
                this.validateAndFetch()
            }, 3000)
        },
        selectedRegion: {
            handler: debounce(function () {
                this.validateAndFetch()
            }, 3000)
        },
        currentPage() {
            this.inputPage = this.currentPage
            this.validateAndFetch()
        },
        // 新增搜索关键词监听
        searchQuery: {
            handler: debounce(function (newVal) {
                if (newVal) {
                    this.currentPage = 1
                    this.validateAndFetch()
                } else {
                    this.resetFilters()
                }
            }, 5000)
        },
        // 监听路由变化
        '$route.query.q': {
            handler(newQuery) {
                if (newQuery && newQuery !== this.searchQuery) {
                    this.searchQuery = newQuery
                    this.currentPage = 1
                    this.validateAndFetch()
                }
            },
            immediate: true
        }
    },
    async created() {
        // 检查URL参数中的搜索查询
        if (this.$route.query.q) {
            this.searchQuery = this.$route.query.q
        }
        await this.initializeData()
    },

    methods: {
        isParamsEqual(a, b) {
        const normalize = obj => JSON.stringify(
            Object.entries(obj).sort(([k1], [k2]) => k1.localeCompare(k2))
        );
        return normalize(a || {}) === normalize(b || {});
    },
        // 初始化数据
        async initializeData() {
            try {
                await Promise.all([
                    this.fetchGenres(),
                    this.loadSavedFilters() // 加载本地保存的筛选条件
                ])
                this.validateAndFetch()
            } catch (error) {
                this.handleError(error, '初始化失败')
            }
        },

        // 获取电影类型
        async fetchGenres() {
            try {
                const cacheKey = 'tmdb_genres'
                const cached = sessionStorage.getItem(cacheKey)
                if (cached) {
                    this.genres = JSON.parse(cached)
                    return
                }

                const response = await axios.get('/api/movies/tmdb/', {
                    params: { type: 'genre' },
                    timeout: 5000
                })


                if (response.data?.genres) {
                    this.genres = response.data.genres
                       .filter(g => g.id && g.name)
                       .slice(0, 15) // 限制最多显示15个类型
                    sessionStorage.setItem(cacheKey, JSON.stringify(this.genres))
                }
            } catch (error) {
                this.handleError(error, '获取类型失败')
            }
        },

        async fetchMovies() {
    try {
        this.loading = true;
        this.error = null;

        // 参数生成策略
        const isSearch = !!this.searchQuery;
        const baseParams = {
            type: isSearch ? 'search' : 'discover',
            page: this.currentPage,
            language: 'zh-CN'
        };

        // 条件化参数构造
        const specificParams = isSearch ? {
            query: this.searchQuery.trim()  // 清理搜索关键词
        } : {
            region: this.selectedRegion?.toUpperCase(),
            primary_release_year: this.selectedYear,
            with_genres: this.selectedGenres.join(','),
            sort_by: 'popularity.desc'
        };

        // 合并并清理参数
        const params = {
            ...baseParams,
            ...specificParams,
            // 强制转换数值类型
            ...(specificParams.page && { page: Number(specificParams.page) })
        };

        // 参数清理优化
        Object.keys(params).forEach(key => {
            const val = params[key]
            // 过滤 falsy 值但保留 0 和 false
            if (val === null || val === undefined || val === '') {
                delete params[key]
            }
        });

        // 请求防重检查（深度比较）
        if (this.isParamsEqual(params, this.lastRequestParams)) {
            return;
        }

        // API 请求
        const response = await axios.get('/api/movies/tmdb/', {
            params,
            timeout: 10000,
            // 添加请求取消令牌
            cancelToken: new axios.CancelToken(c => this.cancelRequest = c)
        });

        // 响应验证
        if (!response.data?.results) {
            throw new Error('无效的API响应结构');
        }

        // 处理数据
        this.processMovieData(response.data);
        this.lastRequestParams = params;
        this.saveFilters();

        // 调试日志
        console.log('请求成功:', {
            params,
            count: response.data.results.length
        });

    } catch (error) {
        if (!axios.isCancel(error)) {
            this.handleError(error, '获取电影失败');
        }
    } finally {
        this.loading = false;
        this.cancelRequest = null;
    }
},

        // 处理电影数据
        processMovieData(data) {
            this.movies = data.results
               .filter(movie => movie.poster_path)
               .map(movie => ({
                    ...movie,
                    runtime: movie.runtime > 0 ?
                        `${Math.floor(movie.runtime / 60)}h ${String(movie.runtime % 60).padStart(2, '0')}m` :
                        '时长未知',
                    // 添加类型名称处理
                    genres: this.getMovieGenres(movie.genre_ids),
                    // 修复年份显示
                    release_date: movie.release_date?.slice(0, 4) || '未知年份'
                }))

            // 限制总页数（TMDB API限制）
            this.totalPages = Math.min(data.total_pages, 300)
        },

        // 参数验证
        validateAndFetch() {
            // 重置无效页码
            if (this.currentPage < 1 || this.currentPage > this.totalPages) {
                this.currentPage = 1
            }

            // 类型ID有效性检查
            this.selectedGenres = this.selectedGenres.filter(genreId =>
                this.genres.some(g => g.id === genreId)
            )

            this.fetchMovies()
        },

        // 错误处理
        handleError(error, message = '发生错误') {
            console.error(error)
            this.error = `${message}: ${error.response?.data?.error || error.message}`
            this.movies = []

            // 自动重试机制
            if (!error.response || error.response.status >= 500) {
                setTimeout(() => this.fetchMovies(), 3000)
            }
        },

        // 本地存储筛选条件
        saveFilters() {
            const filters = {
                genres: this.selectedGenres,
                year: this.selectedYear,
                region: this.selectedRegion,
                page: this.currentPage,
                searchQuery: this.searchQuery
            }
            localStorage.setItem('movieFilters', JSON.stringify(filters))
        },

        // 加载本地筛选条件
        loadSavedFilters() {
            const saved = localStorage.getItem('movieFilters')
            if (saved) {
                try {
                    const filters = JSON.parse(saved)
                    this.selectedGenres = filters.genres || []
                    this.selectedYear = filters.year || ''
                    this.selectedRegion = filters.region || ''
                    this.currentPage = filters.page || 1
                    this.inputPage = this.currentPage
                    this.searchQuery = filters.searchQuery || ''
                } catch (e) {
                    localStorage.removeItem('movieFilters')
                }
            }
        },

        // 类型切换
        toggleGenre(genreId) {
            const index = this.selectedGenres.indexOf(genreId)
            index === -1
               ? this.selectedGenres.push(genreId)
                : this.selectedGenres.splice(index, 1)

            // 自动滚动到顶部
            if (this.currentPage !== 1) {
                this.currentPage = 1
            }
        },

        // 年份选择
        selectYear(year) {
            this.selectedYear = this.selectedYear === year.toString() ? '' : year.toString()
            this.currentPage = 1
        },

        // 地区选择
        selectRegion(regionValue) {
            this.selectedRegion = this.selectedRegion === regionValue ? '' : regionValue
            this.currentPage = 1
        },

        // 分页控制
        changePage(page) {
            this.currentPage = Math.max(1, Math.min(page, this.totalPages))
            window.scrollTo({ top: 0, behavior: 'smooth' })
        },

        // 输入页码跳转
        goToPage() {
            if (this.inputPage >= 1 && this.inputPage <= this.totalPages) {
                this.currentPage = this.inputPage
                window.scrollTo({ top: 0, behavior: 'smooth' })
            } else {
                this.inputPage = this.currentPage
            }
        },

        // 重置筛选条件
        resetFilters() {
            this.searchQuery = ''
            this.selectedGenres = []
            this.selectedYear = ''
            this.selectedRegion = ''
            this.currentPage = 1
            this.inputPage = 1
            localStorage.removeItem('movieFilters')
        },

        // 新增搜索处理方法
        handleSearch() {
            this.currentPage = 1
            this.validateAndFetch()
        },

        goToDetail(movieId) {
            this.$router.push({
                name: 'MovieDetail',
                params: { id: movieId },
                query: {
                    from: 'library',
                    filters: JSON.stringify({
                        genres: this.selectedGenres,
                        year: this.selectedYear,
                        region: this.selectedRegion,
                        searchQuery: this.searchQuery
                    })
                }
            })
        },

        // 获取电影的类型名称
        getMovieGenres(genreIds) {
            return genreIds.map(id => {
                const genre = this.genres.find(g => g.id === id);
                return genre ? genre.name : '';
            }).filter(name => name);
        }
    }
}
</script>
<style scoped>
.library-container {
  padding: 6rem 2rem 2rem;
  background: var(--dark-bg);
  color: var(--light-text);
  min-height: 100vh;
}

/* 搜索框样式 */
.search-section {
  margin-bottom: 2rem;
}

.search-box {
  display: flex;
  gap: 1rem;
  max-width: 600px;
  margin: 0 auto;
}

.search-input {
  flex: 1;
  padding: 0.8rem 1.2rem;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--light-text);
  font-size: 1rem;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(229, 9, 20, 0.1);
}

.search-input::placeholder {
  color: var(--gray-text);
}

.search-button {
  padding: 0.8rem 1.5rem;
  background: var(--primary-color);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.search-button:hover {
  background: #c8070f;
  transform: translateY(-1px);
}

/* 加载和空状态 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(26, 26, 26, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loader {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--gray-text);
}

.empty-state button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* 紧凑筛选器样式 */
.filters-container {
  margin-bottom: 2rem;
  padding: 1rem;
  background: var(--card-bg);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.filter-section {
  display: flex;
  align-items: flex-start;
  margin-bottom: 1rem;
  gap: 0.5rem;
}

.filter-section:last-child {
  margin-bottom: 0;
}

.filter-label {
  font-weight: 600;
  color: var(--light-text);
  min-width: 60px;
  margin-right: 1rem;
  flex-shrink: 0;
  padding-top: 0.4rem;
}

.genre-tags, .year-tags, .region-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.genre-tag, .year-tag, .region-tag {
  padding: 0.4rem 0.8rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--gray-text);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.genre-tag:hover, .year-tag:hover, .region-tag:hover {
  background: rgba(255, 255, 255, 0.15);
  color: var(--light-text);
}

.genre-tag.active, .year-tag.active, .region-tag.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

/* 电影列表 - 7列布局 */
.movie-list {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.movie-card {
  background: var(--card-bg);
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
  border: 1px solid var(--border-color);
}

.movie-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
  border-color: var(--primary-color);
}

.poster {
  width: 100%;
  height: 240px;
  object-fit: cover;
}

.movie-info {
  padding: 1rem;
}

.movie-info h3 {
  font-size: 0.9rem;
  margin: 0 0 0.5rem 0;
  color: var(--light-text);
  font-weight: 600;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.rating {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  margin-bottom: 0.5rem;
  font-size: 0.8rem;
  color: #ffd700;
}

.meta {
  font-size: 0.75rem;
  color: var(--gray-text);
  margin-bottom: 0.5rem;
}

.genres {
  font-size: 0.7rem;
  color: var(--gray-text);
  line-height: 1.2;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.pagination button {
  padding: 0.5rem 1rem;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--light-text);
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination button:hover:not(:disabled) {
  background: var(--primary-color);
  border-color: var(--primary-color);
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination input {
  width: 60px;
  padding: 0.5rem;
  background: var(--dark-bg);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--light-text);
  text-align: center;
}

.pagination span {
  color: var(--gray-text);
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .movie-list {
    grid-template-columns: repeat(6, 1fr);
  }
}

@media (max-width: 1200px) {
  .movie-list {
    grid-template-columns: repeat(5, 1fr);
  }
}

@media (max-width: 900px) {
  .movie-list {
    grid-template-columns: repeat(4, 1fr);
  }

  .filter-section {
    flex-direction: column;
    align-items: flex-start;
  }

  .filter-label {
    margin-bottom: 0.5rem;
  }
}

@media (max-width: 600px) {
  .movie-list {
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
  }

  .library-container {
    padding: 6rem 1rem 2rem;
  }
}
</style>