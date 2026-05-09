<template>
  <div class="cinema-search">
    <div class="search-header">
      <h3>影院搜索</h3>
    </div>

    <div class="search-controls">
      <div class="search-controls-wrapper">
        <!-- 城市选择 -->
        <div class="city-selector">
          <div class="custom-select" @click="toggleCityDropdown">
            <div class="select-display">
              {{ selectedCityName || '选择城市' }}
            </div>
            <div class="select-arrow" :class="{ 'open': cityDropdownOpen }">▼</div>
          </div>
          <div v-if="cityDropdownOpen" class="city-dropdown">
            <div
              v-for="city in cities"
              :key="city.id"
              class="city-option"
              @click="selectCity(city)"
            >
              {{ city.name }}
            </div>
          </div>
        </div>

        <el-input
          v-model="searchQuery"
          placeholder="搜索影院名称或地址"
          clearable
          @input="handleSearch"
          @clear="handleClear"
          @focus="searchFocused = true"
          @blur="searchFocused = false"
          class="search-input"
        />
        <el-button @click="handleSearch" :loading="searching" type="primary" class="search-button">
          搜索
        </el-button>
      </div>

      <!-- 搜索建议 -->
      <div v-if="suggestions.length > 0 && searchFocused" class="suggestions">
        <div
          v-for="suggestion in suggestions"
          :key="suggestion.id || suggestion.name"
          class="suggestion-item"
          @click="selectSuggestion(suggestion)"
        >
          {{ suggestion.name }}
          <span class="suggestion-address">{{ suggestion.address }}</span>
        </div>
      </div>
    </div>

    <!-- 影院列表 -->
    <div class="cinema-results">
      <div v-if="searching" class="loading">
        <el-skeleton :rows="3" animated />
      </div>

      <div v-else-if="cinemas.length === 0 && hasSearched" class="no-results">
        <el-empty description="未找到相关影院" />
      </div>

      <div v-else class="cinema-list">
        <div
          v-for="cinema in cinemas"
          :key="cinema.id"
          class="cinema-card"
          :class="{ active: selectedCinema?.id === cinema.id }"
          @click="selectCinema(cinema)"
        >
          <div class="cinema-info">
            <h4>{{ cinema.name }}</h4>
            <p class="address">{{ cinema.address }}</p>
            <div class="cinema-meta">
              <span v-if="cinema.distance" class="distance">
                {{ cinema.distance }}
              </span>
              <span v-if="cinema.phone" class="phone">
                {{ cinema.phone }}
              </span>
            </div>
          </div>

          <div class="cinema-actions">
            <el-button size="small" @click.stop="viewCinemaDetail(cinema)">
              详情
            </el-button>
            <el-button
              type="primary"
              size="small"
              @click.stop="selectCinema(cinema)"
            >
              选择
            </el-button>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="pagination">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="total"
          :page-size="pageSize"
          :current-page="currentPage"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import maoyanService from '@/api/maoyan'
import axios from 'axios'

export default {
  name: 'CinemaSearch',
  emits: ['cinema-selected'],
  setup(_, { emit }) {
    const useMaoyanApi = ref(true) // 默认使用猫眼数据
    const searchQuery = ref('')
    const searching = ref(false)
    const hasSearched = ref(false)
    const searchFocused = ref(false)
    const suggestions = ref([])
    const cinemas = ref([])
    const selectedCinema = ref(null)
    const cityDropdownOpen = ref(false)

    // 分页相关
    const currentPage = ref(1)
    const pageSize = ref(20)
    const total = ref(0)
    const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

    const selectedCityName = computed(() => {
      const city = cities.value.find(c => c.id === selectedCity.value)
      return city ? city.name : ''
    })

    // 城市数据
    const selectedCity = ref(1) // 默认北京
    const cities = ref([
      { id: 1, name: '北京' },
      { id: 2, name: '上海' },
      { id: 3, name: '广州' },
      { id: 4, name: '深圳' },
      { id: 5, name: '杭州' },
      { id: 6, name: '南京' },
      { id: 7, name: '武汉' },
      { id: 8, name: '成都' },
      { id: 9, name: '西安' },
      { id: 10, name: '重庆' }
    ])

    // 防抖搜索
    let searchTimeout = null
    const handleSearch = () => {
      if (searchTimeout) clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        performSearch()
      }, 500)
    }

    // 执行搜索
    const performSearch = async () => {
      if (!searchQuery.value.trim()) {
        suggestions.value = []
        return
      }

      searching.value = true
      hasSearched.value = true

      try {
        // 直接使用猫眼数据
        await searchWithMaoyan()
      } catch (error) {
        ElMessage.error('搜索失败，请稍后重试')
        console.error('搜索错误:', error)
      } finally {
        searching.value = false
      }
    }

    // 使用猫眼API搜索
    const searchWithMaoyan = async () => {
      try {
        console.log('开始猫眼API搜索:', searchQuery.value, selectedCity.value)

        // 获取搜索建议
        const suggestResult = await maoyanService.searchSuggest(
          searchQuery.value,
          selectedCity.value
        )
        console.log('搜索建议结果:', suggestResult)

        // 搜索影院
        const offset = (currentPage.value - 1) * pageSize.value
        const searchResult = await maoyanService.searchCinemas(
          searchQuery.value,
          selectedCity.value,
          offset,
          pageSize.value
        )
        console.log('影院搜索结果:', searchResult)

        // 处理搜索建议
        if (suggestResult && suggestResult.success && suggestResult.cinemas) {
          // 猫眼API返回的建议数据格式
          const cinemaList = suggestResult.cinemas.list || []
          suggestions.value = cinemaList.slice(0, 5).map(cinema => ({
            id: cinema.id,
            name: cinema.nm,
            address: cinema.addr
          }))
        }

        // 处理影院搜索结果
        if (searchResult) {
          if (Array.isArray(searchResult)) {
            // 直接返回数组格式
            cinemas.value = searchResult.map(cinema => ({
              id: cinema.id,
              name: cinema.nm || cinema.name,
              address: cinema.addr || cinema.address,
              distance: cinema.distance,
              phone: cinema.tel || cinema.phone
            }))
            total.value = searchResult.length
          } else if (searchResult.success && searchResult.cinemas) {
            // 对象格式，包含success字段
            const cinemaList = searchResult.cinemas.list || searchResult.cinemas
            if (Array.isArray(cinemaList)) {
              cinemas.value = cinemaList.map(cinema => ({
                id: cinema.id,
                name: cinema.nm || cinema.name,
                address: cinema.addr || cinema.address,
                distance: cinema.distance,
                phone: cinema.tel || cinema.phone
              }))
              total.value = cinemaList.length
            }
          } else {
            // 如果数据格式不符合预期，使用模拟数据
            console.log('猫眼API数据格式不符合预期，使用模拟数据')
            await useMockData()
          }
        } else {
          console.log('猫眼API无返回数据，使用模拟数据')
          await useMockData()
        }
      } catch (error) {
        console.error('猫眼API搜索失败:', error)
        ElMessage.warning('猫眼数据暂时不可用，已切换到本地数据')
        useMaoyanApi.value = false
        await searchLocal()
      }
    }

    // 使用模拟数据
    const useMockData = async () => {
      const mockCinemas = [
        {
          id: 'mock_1',
          name: '万达影城（' + cities.value.find(c => c.id === selectedCity.value)?.name + '店）',
          address: cities.value.find(c => c.id === selectedCity.value)?.name + '市中心商业区万达广场3楼',
          distance: '1.2km',
          phone: '400-677-5335'
        },
        {
          id: 'mock_2',
          name: '华谊兄弟影院（' + cities.value.find(c => c.id === selectedCity.value)?.name + '店）',
          address: cities.value.find(c => c.id === selectedCity.value)?.name + '市朝阳区建国路93号万达广场',
          distance: '2.1km',
          phone: '010-85806666'
        },
        {
          id: 'mock_3',
          name: '博纳国际影城（' + cities.value.find(c => c.id === selectedCity.value)?.name + '店）',
          address: cities.value.find(c => c.id === selectedCity.value)?.name + '市海淀区中关村大街1号',
          distance: '3.5km',
          phone: '010-82676767'
        }
      ].filter(cinema =>
        cinema.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        cinema.address.toLowerCase().includes(searchQuery.value.toLowerCase())
      )

      cinemas.value = mockCinemas
      total.value = mockCinemas.length

      // 生成搜索建议
      suggestions.value = mockCinemas.slice(0, 3).map(cinema => ({
        id: cinema.id,
        name: cinema.name,
        address: cinema.address
      }))
    }

    // 本地搜索
    const searchLocal = async () => {
      try {
        console.log('开始本地搜索:', searchQuery.value)
        const response = await axios.get('/api/cinemas/', {
          params: {
            search: searchQuery.value,
            page: currentPage.value,
            page_size: pageSize.value
          },
          headers: {
            'Authorization': `Token ${localStorage.getItem('authToken')}`
          }
        })

        console.log('本地搜索响应:', response.data)
        const data = response.data
        cinemas.value = Array.isArray(data) ? data : (data.results || [])
        total.value = data.count || cinemas.value.length

        // 生成本地搜索建议
        if (cinemas.value.length > 0) {
          suggestions.value = cinemas.value.slice(0, 3).map(cinema => ({
            id: cinema.id,
            name: cinema.name,
            address: cinema.address
          }))
        }

        console.log('本地搜索结果:', cinemas.value)
      } catch (error) {
        console.error('本地搜索失败:', error)
        ElMessage.warning('本地数据加载失败，使用模拟数据')

        // 如果本地API也失败，使用模拟数据
        const mockCinemas = [
          {
            id: 1,
            name: '万达影城（本地店）',
            address: '本地市中心商业区万达广场3楼',
            phone: '400-677-5335'
          },
          {
            id: 2,
            name: '华谊兄弟影院（本地店）',
            address: '本地市朝阳区建国路93号万达广场',
            phone: '010-85806666'
          },
          {
            id: 3,
            name: '博纳国际影城（本地店）',
            address: '本地市海淀区中关村大街1号',
            phone: '010-82676767'
          }
        ].filter(cinema =>
          !searchQuery.value ||
          cinema.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          cinema.address.toLowerCase().includes(searchQuery.value.toLowerCase())
        )

        cinemas.value = mockCinemas
        total.value = mockCinemas.length
        suggestions.value = []
      }
    }

    // 选择搜索建议
    const selectSuggestion = (suggestion) => {
      searchQuery.value = suggestion.name
      suggestions.value = []
      performSearch()
    }

    // 选择影院
    const selectCinema = (cinema) => {
      selectedCinema.value = cinema
      emit('cinema-selected', cinema)
    }

    // 查看影院详情
    const viewCinemaDetail = async (cinema) => {
      if (useMaoyanApi.value && cinema.id) {
        try {
          const detail = await maoyanService.getCinemaDetail(cinema.id)
          // 这里可以显示详情弹窗
          console.log('影院详情:', detail)
          ElMessage.info('影院详情功能开发中...')
        } catch (error) {
          ElMessage.error('获取影院详情失败')
        }
      } else {
        ElMessage.info('影院详情功能开发中...')
      }
    }

    // API切换
    const handleApiSwitch = () => {
      cinemas.value = []
      suggestions.value = []
      currentPage.value = 1

      if (searchQuery.value) {
        performSearch()
      } else {
        // 如果没有搜索词，加载默认数据
        loadDefaultCinemas()
      }
    }

    // 城市切换
    const handleCityChange = () => {
      currentPage.value = 1
      if (searchQuery.value) {
        performSearch()
      } else {
        // 如果没有搜索词，加载默认数据
        loadDefaultCinemas()
      }
    }

    // 分页切换
    const handlePageChange = (page) => {
      currentPage.value = page
      performSearch()
    }

    // 清空搜索
    const handleClear = () => {
      suggestions.value = []
      cinemas.value = []
      hasSearched.value = false
    }

    // 监听搜索输入
    watch(searchQuery, (newValue) => {
      if (!newValue.trim()) {
        suggestions.value = []
      }
    })

    // 初始化加载默认影院列表
    const loadDefaultCinemas = async () => {
      try {
        // 直接使用猫眼模拟数据作为默认显示
        await useMockData()
      } catch (error) {
        console.error('加载默认影院失败:', error)
        // 使用模拟数据作为后备
        await useMockData()
      }
    }

    // 组件挂载时加载默认数据
    onMounted(() => {
      loadDefaultCinemas()
    })

    // 城市选择方法
    const toggleCityDropdown = () => {
      cityDropdownOpen.value = !cityDropdownOpen.value
    }

    const selectCity = (city) => {
      selectedCity.value = city.id
      cityDropdownOpen.value = false
      console.log('城市变更:', city.id)
      // 重新搜索影院
      if (searchQuery.value) {
        handleSearch()
      }
    }

    return {
      useMaoyanApi,
      searchQuery,
      searching,
      hasSearched,
      searchFocused,
      suggestions,
      cinemas,
      selectedCinema,
      currentPage,
      pageSize,
      total,
      totalPages,
      selectedCity,
      selectedCityName,
      cities,
      cityDropdownOpen,
      handleSearch,
      handleClear,
      selectSuggestion,
      selectCinema,
      viewCinemaDetail,
      handleApiSwitch,
      handleCityChange,
      handlePageChange,
      toggleCityDropdown,
      selectCity
    }
  }
}
</script>

<style scoped>
.cinema-search {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-color);
}

.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-header h3 {
  margin: 0;
  color: var(--light-text);
}

.search-controls {
  position: relative;
  margin-bottom: 15px;
}

.search-controls-wrapper {
  display: flex;
  gap: 10px;
}

.search-input {
  flex: 1;
}

.search-button {
  flex-shrink: 0;
}

.city-selector {
  position: relative;
  width: 120px;
  flex-shrink: 0;
}

.custom-select {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.3s ease;
  height: 32px; /* 与 el-input 保持一致的高度 */
  box-sizing: border-box;
}

.custom-select:hover {
  border-color: var(--primary-color);
}

.select-display {
  color: var(--light-text);
  flex: 1;
}

.select-arrow {
  color: var(--gray-text);
  transition: transform 0.3s ease;
  font-size: 12px;
}

.select-arrow.open {
  transform: rotate(180deg);
}

.city-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-top: none;
  border-radius: 0 0 8px 8px;
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
}

.city-option {
  padding: 10px 12px;
  color: var(--light-text);
  cursor: pointer;
  transition: background-color 0.3s ease;
  border-bottom: 1px solid var(--border-color);
}

.city-option:hover {
  background: rgba(229, 9, 20, 0.1);
}

.city-option:last-child {
  border-bottom: none;
}

.suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-top: none;
  border-radius: 0 0 8px 8px;
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
}

.suggestion-item {
  padding: 10px 15px;
  cursor: pointer;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  color: var(--light-text);
  transition: background-color 0.3s ease;
}

.suggestion-item:hover {
  background: rgba(229, 9, 20, 0.1);
}

.suggestion-item i {
  margin-right: 8px;
  color: var(--gray-text);
}

.suggestion-address {
  margin-left: auto;
  color: var(--gray-text);
  font-size: 12px;
}

.city-selector {
  margin-bottom: 15px;
}

.cinema-results {
  min-height: 200px;
}

.loading {
  padding: 20px;
}

.no-results {
  text-align: center;
  padding: 40px 20px;
}

.cinema-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.cinema-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--darker-bg);
}

.cinema-card:hover {
  border-color: var(--primary-color);
  background: rgba(229, 9, 20, 0.05);
}

.cinema-card.active {
  border-color: var(--primary-color);
  background: rgba(229, 9, 20, 0.1);
}

.cinema-info h4 {
  margin: 0 0 5px 0;
  color: var(--light-text);
  font-size: 16px;
}

.cinema-info .address {
  margin: 0 0 8px 0;
  color: var(--gray-text);
  font-size: 14px;
}

.cinema-meta {
  display: flex;
  gap: 15px;
}

.cinema-meta span {
  display: flex;
  align-items: center;
  color: var(--gray-text);
  font-size: 12px;
}

.cinema-meta i {
  margin-right: 4px;
}

.cinema-actions {
  display: flex;
  gap: 8px;
}

.pagination {
  margin-top: 20px;
  text-align: center;
}

/* Element Plus 组件深色主题覆盖 */
:deep(.el-input__wrapper) {
  background-color: var(--card-bg);
  border-radius: 8px;
  box-shadow: 0 0 0 1px var(--border-color);
  height: 32px; /* 与城市下拉菜单保持一致的高度 */
  box-sizing: border-box;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--primary-color);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--primary-color);
}

:deep(.el-input__inner) {
  color: var(--light-text);
}

:deep(.el-button) {
  border-radius: 8px;
  background-color: var(--card-bg);
  border-color: var(--border-color);
  color: var(--light-text);
}

:deep(.el-button:hover) {
  border-color: var(--primary-color);
  color: var(--light-text);
  background-color: rgba(229, 9, 20, 0.1);
}

:deep(.el-button--primary) {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
  color: var(--light-text);
}

:deep(.el-button--primary:hover) {
  background-color: rgba(229, 9, 20, 0.8);
  border-color: rgba(229, 9, 20, 0.8);
  color: var(--light-text);
}

:deep(.el-switch__core) {
  background-color: var(--gray-text);
}

:deep(.el-switch.is-checked .el-switch__core) {
  background-color: var(--primary-color);
}

:deep(.el-select) {
  background-color: var(--card-bg);
}

:deep(.el-select .el-input__wrapper) {
  background-color: var(--card-bg);
  border-color: var(--border-color);
}

:deep(.el-select .el-input__wrapper:hover) {
  border-color: var(--primary-color);
}

:deep(.el-select .el-input__wrapper.is-focus) {
  border-color: var(--primary-color);
}

:deep(.el-select .el-input__inner) {
  color: var(--light-text);
}

:deep(.el-select-dropdown) {
  background-color: var(--card-bg) !important;
  border: 1px solid var(--border-color) !important;
  border-radius: 8px !important;
}

:deep(.el-select-dropdown .el-select-dropdown__item) {
  color: var(--light-text) !important;
  background-color: var(--card-bg) !important;
}

:deep(.el-select-dropdown .el-select-dropdown__item:hover) {
  background-color: rgba(229, 9, 20, 0.1) !important;
  color: var(--light-text) !important;
}

:deep(.el-select-dropdown .el-select-dropdown__item.selected) {
  background-color: var(--primary-color) !important;
  color: var(--light-text) !important;
}

:deep(.el-popper) {
  background-color: var(--card-bg) !important;
  border: 1px solid var(--border-color) !important;
}

:deep(.el-pagination) {
  color: var(--light-text);
}

:deep(.el-pagination .el-pager li) {
  background-color: var(--card-bg);
  color: var(--light-text);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  margin: 0 2px;
}

:deep(.el-pagination .el-pager li:hover) {
  color: var(--light-text);
  background-color: rgba(229, 9, 20, 0.1);
  border-color: var(--primary-color);
}

:deep(.el-pagination .el-pager li.is-active) {
  background-color: var(--primary-color);
  color: var(--light-text);
  border-color: var(--primary-color);
}

:deep(.el-pagination button) {
  background-color: var(--card-bg);
  color: var(--light-text);
  border: 1px solid var(--border-color);
  border-radius: 6px;
}

:deep(.el-pagination button:hover) {
  color: var(--light-text);
  background-color: rgba(229, 9, 20, 0.1);
  border-color: var(--primary-color);
}

:deep(.el-empty__description p) {
  color: var(--gray-text);
}
</style>