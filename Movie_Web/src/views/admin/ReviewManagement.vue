<template>
  <div class="review-management">
    <!-- 过滤工具栏 -->
    <div class="filter-bar mb-4 flex gap-4">
      <el-input
        v-model="searchKey"
        placeholder="搜索评论内容"
        clearable
        @clear="loadReviews"
        @keyup.enter="loadReviews"
        style="width: 300px"
      />

      <el-select
        v-model="filterStatus"
        placeholder="审核状态"
        @change="loadReviews"
      >
        <el-option label="全部" value="" />
        <el-option label="已审核" value="approved" />
        <el-option label="待审核" value="pending" />
        <el-option label="被举报" value="reported" />
      </el-select>

      <el-button type="danger" :disabled="selected.length === 0" @click="batchDelete">
        批量删除 ({{ selected.length }})
      </el-button>
    </div>

    <!-- 数据表格 -->
    <el-table
      :data="reviews"
      v-loading="loading"
      border
      stripe
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column label="评论内容" min-width="300">
        <template #default="{row}">
          <div class="content-preview">
            {{ formatContent(row.content) }}
          </div>
        </template>
      </el-table-column>

      <el-table-column label="用户/电影" width="220">
        <template #default="{row}">
          <div class="flex items-center gap-2">
            <div class="font-medium">
              {{ getUserName(row) }}
            </div>
            <div class="text-gray-500 text-sm">{{ row.movie_title || '未知电影' }}</div>
          </div>
        </template>
      </el-table-column>

      <el-table-column label="状态" width="120">
        <template #default="{row}">
          <el-tag :type="statusTagType(row)">
            {{ statusText(row) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="created_at" label="时间" width="180" />

      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{row}">
          <el-button
            size="small"
            :type="row.is_approved? 'danger' :'success'"
            @click="toggleStatus(row.id)"
          >
            {{ row.is_approved? '取消审核' : '通过审核' }}
          </el-button>
          <el-button
            size="small"
            type="danger"
            @click="deleteReview(row.id)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="mt-4 flex justify-end">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadReviews"
        @current-change="loadReviews"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getAdminReviews,
  deleteReviewApi,
  toggleReviewStatusApi,
  batchDeleteReviewsApi
} from '@/api/admin'

// 获取用户名
const getUserName = (row) => {
  if (!row.user) return '未知用户'
  return row.user.username || '无用户名'
}

// 格式化评论内容
const formatContent = (content) => {
  if (content === undefined) {
    return '暂无评论内容'
  }
  if (typeof content!=='string') {
    console.error('评论内容不是字符串类型:', content, '类型:', typeof content)
    return '[内容格式错误]'
  }
  const maxLength = 100
  if (content.length <= maxLength) {
    return content
  }
  return content.slice(0, maxLength) + '...'
}

// 数据状态
const reviews = ref([])
const loading = ref(false)
const searchKey = ref('')
const filterStatus = ref('')
const selected = ref([])

// 分页配置
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 状态显示处理
const statusTagType = (row) => {
  if (row.report_count > 0) return 'danger'
  return row.is_approved? 'success' : 'warning'
}

const statusText = (row) => {
  if (row.report_count > 0) return `被举报 (${row.report_count})`
  return row.is_approved? '已审核' : '待审核'
}

// 处理选择变化
const handleSelectionChange = (val) => {
  selected.value = val.map(item => item.id)
}

// API响应结构分析
const apiResponseStructure = computed(() => {
  if (!reviews.value.length) return '无数据'

  return JSON.stringify({
    responseKeys: Object.keys(reviews.value[0]),
    firstItem: Object.keys(reviews.value[0]).reduce((acc, key) => {
      acc[key] = typeof reviews.value[0][key]
      return acc
    }, {})
  }, null, 2)
})

// 第一条评论详情
const firstReviewDetails = computed(() => {
  if (!reviews.value.length) return '无数据'
  return JSON.stringify(reviews.value[0], null, 2)
})

// 字段统计
const fieldStats = computed(() => {
  if (!reviews.value.length) return '无数据'

  const allFields = {}

  reviews.value.forEach(item => {
    Object.keys(item).forEach(key => {
      if (!allFields[key]) {
        allFields[key] = {
          count: 1,
          types: new Set([typeof item[key]]),
          firstValue: item[key]
        }
      } else {
        allFields[key].count++
        allFields[key].types.add(typeof item[key])
      }
    })
  })

  return JSON.stringify(Object.keys(allFields).sort().reduce((acc, key) => {
    acc[key] = {
      count: allFields[key].count,
      types: Array.from(allFields[key].types),
      sampleValue: allFields[key].firstValue
    }
    return acc
  }, {}), null, 2)
})

// 加载数据
const loadReviews = async () => {
  try {
    loading.value = true

    // 构建请求参数
    const params = {
      page: pagination.page,
      page_size: pagination.size,
      search: searchKey.value,
      status: filterStatus.value
    }

    console.log('请求参数:', params) // 添加日志，打印请求参数

    // 发送请求
    const res = await getAdminReviews(params)

    console.log('后端返回的数据:', res.data.results)

    if (!res.data.results || res.data.results.length === 0) {
      console.error('没有获取到评论数据')
      return
    }

    reviews.value = res.data.results
    pagination.total = res.data.total
  } catch (error) {
    ElMessage.error('数据加载失败')
    console.error('加载评论失败:', error)
  } finally {
    loading.value = false
  }
}

// 单个删除
const deleteReview = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除该评论？', '警告')
    await deleteReviewApi(id)
    ElMessage.success('删除成功')
    loadReviews()
  } catch (error) {
    ElMessage.error('删除失败')
    console.error('删除评论失败:', error)
  }
}

// 批量删除
const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定删除选中的${selected.value.length}条评论？`, '警告')
    await batchDeleteReviewsApi(selected.value)
    ElMessage.success('批量删除成功')
    loadReviews()
  } catch (error) {
    ElMessage.error('批量删除失败')
    console.error('批量删除评论失败:', error)
  }
}

// 切换审核状态
const toggleStatus = async (id) => {
  try {
    console.log('切换审核状态，ID:', id) // 添加日志，打印切换的ID

    await toggleReviewStatusApi(id)
    ElMessage.success('状态更新成功')
    loadReviews()
  } catch (error) {
    ElMessage.error('操作失败')
    console.error('切换评论状态失败:', error)
  }
}

// 初始化加载
onMounted(() => {
  loadReviews()
})

// 监听评论数据变化
watch(reviews, (newVal) => {
  console.log('评论数据更新:', newVal) // 添加日志，打印更新后的数据
})
</script>

<style scoped>
.review-management {
  padding: 20px;
}
.content-preview {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>