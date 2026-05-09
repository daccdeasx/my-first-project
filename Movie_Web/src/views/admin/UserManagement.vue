<template>
  <div class="user-management">
    <!-- 搜索和过滤 -->
    <div class="mb-4 flex items-center gap-4">
      <el-input
        v-model="searchKey"
        placeholder="搜索用户（邮箱/用户名）"
        clearable
        @clear="handleSearch"
        @keyup.enter="handleSearch"
        style="max-width: 300px"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-button type="primary" @click="handleSearch">
        搜索
      </el-button>
    </div>

    <!-- 用户表格 -->
    <el-table
      v-loading="loading"
      :data="users"
      stripe
      style="width: 100%"
      empty-text="暂无用户数据"
      @row-click="handleRowClick"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="email" label="邮箱" min-width="150" /> <!-- 调整列宽 -->
      <el-table-column prop="username" label="用户名" width="150" />
      <el-table-column label="角色" width="160">
        <template #default="{ row }">
          <el-select
            v-model="row.admin_role"
            size="small"
            style="width: 140px"
            :disabled="row.is_superuser"
            @change="(val) => handleRoleChange(row, val)"
          >
            <el-option label="普通用户" value="user" />
            <el-option label="电影管理员" value="movie_admin" />
            <el-option label="论坛管理员" value="forum_admin" />
            <el-option label="订单管理员" value="order_admin" />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" effect="plain">
            {{ row.is_active ? '激活' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="date_joined" label="注册时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.date_joined) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button
            size="small"
            :type="row.is_active ? 'danger' : 'success'"
            @click="toggleUserStatus(row)"
          >
            {{ row.is_active ? '禁用' : '激活' }}
          </el-button>
          <el-popconfirm
            title="确认删除该用户？"
            @confirm="deleteUser(row.id)"
          >
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页组件 -->
    <div class="mt-4 flex justify-end">
      <el-pagination
        v-model:current-page="pagination.current"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadUsers"
        @current-change="loadUsers"
      />
    </div>

    <!-- 用户详情对话框 -->
    <el-dialog v-model="detailVisible" title="用户详情">
      <UserDetail :user="selectedUser" />
    </el-dialog>

    <!-- 全选和批量删除 -->
    <el-row class="mb-4">
      <el-col :span="6">
        <el-checkbox v-model="selectAll">全选</el-checkbox>
      </el-col>
      <el-col :span="6" :offset="12">
        <el-button v-if="selectedUsers.length" type="danger" @click="batchDelete">
          批量删除 ({{ selectedUsers.length }})
        </el-button>
      </el-col>
    </el-row>

    <!-- 导出Excel -->
    <el-button type="primary" @click="exportUsers">
      <el-icon><Download /></el-icon>
      导出Excel
    </el-button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Download } from '@element-plus/icons-vue'
import UserDetail from '@/components/users/UserDetail.vue'

// 导入API函数
import { fetchUsers, toggleUserStatusApi, deleteUserApi, updateUserRoleApi } from '@/api/admin'

// 导入公共工具函数
import { formatDate } from '@/utils/dateUtils'

// 修复：导入Excel导出所需的库
import * as XLSX from 'xlsx'
import FileSaver from 'file-saver'

// 数据状态
const users = ref([])
const searchKey = ref('')
const loading = ref(false)

// 分页配置
const pagination = ref({
  current: 1,
  size: 20,
  total: 0
})

// 用户详情相关
const detailVisible = ref(false)
const selectedUser = ref(null)

// 全选和批量删除相关
const selectAll = ref(false)
const selectedUsers = ref([])

// 加载用户数据（添加调试日志）
const loadUsers = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.value.current,
      page_size: pagination.value.size,
      search: searchKey.value
    }
    
    const response = await fetchUsers(params)
    
    // 适配分页结构
    users.value = response.data.results
    pagination.value.total = response.data.count
  } catch (error) {
    ElMessage.error('用户数据加载失败')
  } finally {
    loading.value = false
  }
}

const handleRoleChange = async (user, role) => {
  try {
    await updateUserRoleApi(user.id, role)
    ElMessage.success('角色已更新')
  } catch (error) {
    ElMessage.error('角色更新失败（仅超级管理员可操作）')
    // 回滚：重新拉取
    loadUsers()
  }
}

// 搜索处理
const handleSearch = () => {
  console.log('执行搜索，关键词:', searchKey.value)
  pagination.value.current = 1
  loadUsers()
}

// 切换用户状态（添加调试日志）
const toggleUserStatus = async (user) => {
  console.group('toggleUserStatus 调用')
  console.log('用户ID:', user.id, '当前状态:', user.is_active)
  
  try {
    await toggleUserStatusApi(user.id)
    user.is_active = !user.is_active
    ElMessage.success(`已${user.is_active ? '激活' : '禁用'}用户`)
    console.log('状态更新成功，新状态:', user.is_active)
  } catch (error) {
    console.error('状态更新失败:', error)
    ElMessage.error('状态修改失败')
  } finally {
    console.groupEnd()
  }
}

// 删除用户（添加调试日志）
const deleteUser = async (userId) => {
  console.group('deleteUser 调用')
  console.log('待删除用户ID:', userId)
  
  try {
    await deleteUserApi(userId)
    users.value = users.value.filter(u => u.id !== userId)
    ElMessage.success('用户删除成功')
    console.log('用户删除成功，剩余用户数:', users.value.length)
  } catch (error) {
    console.error('删除用户失败:', error)
    ElMessage.error('删除用户失败')
  } finally {
    console.groupEnd()
  }
}

// 批量删除用户（添加调试日志）
const batchDelete = async () => {
  console.group('batchDelete 调用')
  const ids = selectedUsers.value.map(user => user.id)
  console.log('待批量删除用户ID:', ids)
  
  try {
    const confirm = await ElMessageBox.confirm('确认批量删除选中用户？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    if (confirm === 'confirm') {
      console.log('用户确认批量删除')
      await Promise.all(ids.map(id => deleteUserApi(id)))
      users.value = users.value.filter(user => !ids.includes(user.id))
      selectedUsers.value = []
      selectAll.value = false
      ElMessage.success('批量删除成功')
      console.log('批量删除完成，剩余用户数:', users.value.length)
    } else {
      console.log('用户取消批量删除')
    }
  } catch (error) {
    console.error('批量删除失败:', error)
    ElMessage.error('批量删除失败')
  } finally {
    console.groupEnd()
  }
}

// 导出Excel（修复XLSX未定义问题）
const exportUsers = () => {
  console.group('exportUsers 调用')
  console.log('导出用户数据，当前数量:', users.value.length)
  
  try {
    // 确保用户数据存在
    if (!users.value || users.value.length === 0) {
      throw new Error('没有可导出的用户数据')
    }
    
    const wb = XLSX.utils.book_new()
    // 提取需要导出的字段
    const exportData = users.value.map(user => ({
      邮箱: user.email,
      用户名: user.username,
      状态: user.is_active ? '激活' : '禁用',
      注册时间: formatDate(user.date_joined)
    }))
    
    const ws = XLSX.utils.json_to_sheet(exportData)
    XLSX.utils.book_append_sheet(wb, ws, '用户列表')
    const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
    
    console.log('Excel数据生成成功')
    
    FileSaver.saveAs(
      new Blob([wbout], { type: 'application/octet-stream' }), 
      `用户列表_${new Date().toISOString().slice(0, 10)}.xlsx`
    )
    
    ElMessage.success('导出成功')
  } catch (e) {
    console.error('导出失败:', e)
    ElMessage.error(`导出失败: ${e.message}`)
  } finally {
    console.groupEnd()
  }
}

const handleRowClick = (row, column) => {
  // 👇 关键：如果点的是“角色”列，不弹出详情
  if (column.label === '角色') {
    return
  }
  
  console.log('点击行数据:', row)
  selectedUser.value = row
  detailVisible.value = true
}

const handleSelectionChange = (rows) => {
  console.log('表格选择变化，选中数量:', rows.length)
  selectedUsers.value = rows
  selectAll.value = rows.length === users.value.length
}

// 初始化加载
onMounted(() => {
  console.log('组件挂载完成，初始化加载用户数据')
  loadUsers()
})
</script>

<style scoped>
.user-management {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  min-height: 100vh;
  box-sizing: border-box;
}

:deep(.el-table .cell) {
  white-space: nowrap;
}

</style>  