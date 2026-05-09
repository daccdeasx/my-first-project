<template>
  <div class="movie-management">
    <!-- 操作栏 -->
    <div class="mb-4 flex justify-between items-center">
      <div class="flex gap-2">
        <el-button type="primary" @click="showDialog('create')">
          <el-icon><Plus /></el-icon>添加电影
        </el-button>
        <el-button @click="batchDelete" :disabled="selected.length === 0">
          批量删除 ({{ selected.length }})
        </el-button>
        <el-upload
          action="/api/admin/movies/import/"
          :show-file-list="false"
          :on-success="handleImportSuccess"
        >
          <el-button type="success">
            <el-icon><Upload /></el-icon>导入CSV
          </el-button>
        </el-upload>
      </div>

      <div class="flex gap-2">
        <el-input
          v-model="searchKey"
          placeholder="搜索电影..."
          clearable
          @clear="loadMovies"
          @keyup.enter="loadMovies"
          style="width: 300px"
        >
          <template #append>
            <el-button @click="loadMovies">
              <el-icon><Search /></el-icon>
            </el-button>
          </template>
        </el-input>

        <el-button @click="exportCSV" :loading="exporting">
          <el-icon><Download /></el-icon>导出
        </el-button>
      </div>
    </div>

    <!-- 数据表格 -->
    <el-table
      :data="movies"
      v-loading="loading"
      stripe
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="tmdb_id" label="TMDB ID" width="120" />
      <el-table-column prop="title" label="标题" min-width="200" />
      <el-table-column label="海报" width="120">
        <template #default="{row}">
          <el-image
            :src="getPosterUrl(row.poster_path)"
            fit="cover"
            class="w-20 h-28 rounded"
          />
        </template>
      </el-table-column>
      <el-table-column prop="release_date" label="上映日期" width="120" />
      <el-table-column prop="vote_average" label="评分" width="100">
        <template #default="{row}">
          <el-rate
            v-model="row.vote_average"
            :max="10"
            disabled
            show-score
            score-template="{value} 分"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{row}">
          <el-button size="small" @click="showDialog('edit', row)">
            编辑
          </el-button>
          <el-button
            size="small"
            type="danger"
            @click="deleteMovie(row.tmdb_id)"
          >
            删除
          </el-button>
          <!-- 移除详情按钮 -->
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="mt-4 flex justify-between items-center">
      <div class="text-gray-500">
        共 {{ pagination.total }} 条记录
      </div>
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadMovies"
        @current-change="loadMovies"
      />
    </div>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialog.visible"
      :title="dialog.mode === 'create' ? '添加电影' : '编辑电影'"
      width="600px"
    >
      <el-form
        :model="form"
        label-width="100px"
        label-position="left"
        :rules="rules"
        ref="formRef"
      >
        <el-form-item v-if="dialog.mode === 'create'" label="TMDB ID" prop="tmdb_id">
          <el-input v-model.number="form.tmdb_id" placeholder="例如：603（黑客帝国）" />
        </el-form-item>
        <el-form-item v-else label="TMDB ID">
          <el-input :model-value="form.tmdb_id" disabled />
        </el-form-item>

        <el-form-item label="电影标题" prop="title">
          <el-input v-model="form.title" />
        </el-form-item>

        <el-form-item label="上映日期" prop="release_date">
          <el-date-picker
            v-model="form.release_date"
            type="date"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <el-form-item label="时长（分钟）" prop="runtime">
          <el-input-number v-model="form.runtime" :min="1" />
        </el-form-item>

        <el-form-item label="推荐评分">
          <el-rate
            v-model="form.vote_average"
            :max="10"
            :allow-half="true"
            show-score
          />
        </el-form-item>

        <el-form-item label="是否推荐">
          <el-switch v-model="form.is_featured" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">
          确认
        </el-button>
      </template>
    </el-dialog>

    <!-- 移除详情侧边栏 -->
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAdminMovies, createMovie, updateMovie, deleteMovieApi } from '@/api/admin'
import axios from 'axios'

// 数据状态（移除详情相关状态）
const movies = ref([])
const loading = ref(false)
const exporting = ref(false)
const searchKey = ref('')
const selected = ref([])

// 分页配置
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0,
  total_pages: 0
})

// 对话框配置
const dialog = reactive({
  visible: false,
  mode: 'create'
})

// 表单配置
const form = reactive({
  tmdb_id: null,
  title: '',
  release_date: '',
  runtime: 90,
  vote_average: 7.5,
  is_featured: false
})

// 表单验证规则
const rules = reactive({
  tmdb_id: [{ required: true, message: '请输入TMDB ID（整数）', trigger: 'blur' }],
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  release_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  runtime: [{ type: 'number', min: 1, message: '时长需大于0', trigger: 'blur' }]
})

// 加载电影数据
const loadMovies = async (immediate = true) => {
  try {
    loading.value = true
    
    if (!immediate) {
      await new Promise(resolve => setTimeout(resolve, 300))
    }
    
    const params = {
      page: pagination.page,
      page_size: pagination.size,
      search: searchKey.value
    }
    
    const res = await getAdminMovies(params)
    
    movies.value = res.data.results || []
    pagination.total = res.data.count || 0
    pagination.total_pages = res.data.total_pages || 0
    
    if (pagination.page > pagination.total_pages && pagination.total_pages > 0) {
      pagination.page = pagination.total_pages
      loadMovies(false)
    }
  } catch (error) {
    ElMessage.error('数据加载失败')
  } finally {
    loading.value = false
  }
}

// 海报URL处理方法
const getPosterUrl = (path) => {
  if (!path) return 'https://picsum.photos/200/300' 
  return `https://image.tmdb.org/t/p/w300${path}` 
}

// 显示编辑对话框
const showDialog = (mode, data = null) => {
  dialog.mode = mode
  dialog.visible = true
  
  if (mode === 'edit' && data) {
    Object.assign(form, data)
  } else {
    resetForm()
  }
}

// 提交表单
const submitForm = async () => {
  try {
    if (dialog.mode === 'create') {
      await createMovie(form)
      ElMessage.success('电影添加成功')
    } else {
      await updateMovie(form.tmdb_id, form)
      ElMessage.success('更新成功')
    }
    dialog.visible = false
    loadMovies()
  } catch (error) {
    const detail = error?.response?.data
    ElMessage.error(typeof detail === 'string' ? detail : '操作失败（请检查表单字段）')
  }
}

// 删除电影
const deleteMovie = (tmdbId) => {
  ElMessageBox.confirm('确定删除该电影？所有关联数据将被清除', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await deleteMovieApi(tmdbId)
    ElMessage.success('删除成功')
    
    if (movies.value.length === 1 && pagination.page > 1) {
      pagination.page--
    }
    
    loadMovies()
  }).catch(() => null)
}

// 批量删除
const batchDelete = () => {
  if (selected.value.length === 0) return
  
  ElMessageBox.confirm(`确定删除选中的 ${selected.value.length} 部电影？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    const tmdbIds = selected.value.map(item => item.tmdb_id)
    
    for (const id of tmdbIds) {
      await deleteMovieApi(id)
    }
    
    ElMessage.success(`成功删除 ${selected.value.length} 部电影`)
    
    const expectedCount = pagination.total - selected.value.length
    const expectedPages = Math.ceil(expectedCount / pagination.size)
    
    if (pagination.page > expectedPages && pagination.page > 1) {
      pagination.page = expectedPages
    }
    
    loadMovies()
    selected.value = []
  }).catch(() => null)
}

// 处理导入成功
const handleImportSuccess = (response) => {
  if (response && response.success) {
    ElMessage.success(`成功导入 ${response.count} 条记录`)
    loadMovies()
  } else {
    ElMessage.error('导入失败')
  }
}

// 处理选择变化
const handleSelectionChange = (val) => {
  selected.value = val
}

// 移除详情相关函数 showMovieDetail

// 重置表单
const resetForm = () => {
  form.tmdb_id = null
  form.title = ''
  form.release_date = ''
  form.runtime = 90
  form.vote_average = 7.5
  form.is_featured = false
}

// 导出CSV
const exportCSV = async () => {
  try {
    exporting.value = true
    
    const response = await axios.get('/admin/movies/export/', {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'movies.csv')
    document.body.appendChild(link)
    link.click()
    
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
    console.error('导出CSV失败', error)
  } finally {
    exporting.value = false
  }
}

// 初始化加载
onMounted(() => {
  loadMovies()
})
</script>

<style scoped>
.movie-management {
  padding: 20px;
}

.el-table__row:hover {
  background-color: #f5f7fa !important;
}
</style>