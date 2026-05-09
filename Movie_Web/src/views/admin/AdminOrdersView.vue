<template>
  <div class="admin-orders-container">
    <div class="page-header">
      <h1>订单管理</h1>
      <div class="filters">
        <el-input
          v-model="searchQuery"
          placeholder="搜索订单号/电影名/用户名"
          prefix-icon="el-icon-search"
          clearable
          @clear="handleSearch"
          @input="handleSearch"
        />
        <el-select v-model="statusFilter" placeholder="订单状态" clearable @change="handleSearch">
          <el-option
            v-for="item in statusOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          @change="handleSearch"
        />
      </div>
    </div>

    <el-table
      :data="orders"
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column prop="order_number" label="订单号" width="180" />
      <el-table-column prop="movie_title" label="电影" width="200" />
      <el-table-column prop="cinema_name" label="影院" width="200" />
      <el-table-column prop="schedule_time" label="场次" width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.schedule_time || scope.row.show_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="seats" label="座位" width="150">
        <template #default="scope">
          {{ formatSeats(scope.row.seats) }}
        </template>
      </el-table-column>
      <el-table-column prop="total_price" label="总价" width="100">
        <template #default="scope">
          ¥{{ scope.row.total_price }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ getStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <div class="action-buttons">
            <el-button
              v-if="scope.row.status === 'paid'"
              type="danger"
              size="small"
              @click="handleCancel(scope.row)"
            >
              退票
            </el-button>
            <el-button
              v-if="scope.row.status === 'paid'"
              type="warning"
              size="small"
              @click="handleChange(scope.row)"
            >
              改签
            </el-button>
            <el-button
              v-if="scope.row.status === 'pending'"
              type="success"
              size="small"
              @click="handleConfirmPayment(scope.row)"
            >
              确认支付
            </el-button>
            <el-button
              type="primary"
              size="small"
              @click="viewDetail(scope.row)"
            >
              详情
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
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
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import dayjs from 'dayjs'

export default {
  name: 'AdminOrdersView',
  setup() {
    const router = useRouter()
    const orders = ref([])
    const loading = ref(false)
    const total = ref(0)
    const pageSize = ref(10)
    const currentPage = ref(1)
    const searchQuery = ref('')
    const statusFilter = ref('')
    const dateRange = ref([])

    const statusOptions = [
      { value: 'pending', label: '待支付' },
      { value: 'paid', label: '已支付' },
      { value: 'cancelled', label: '已取消' },
      { value: 'refunded', label: '已退款' },
      { value: 'changed', label: '已改签' }
    ]

    const loadOrders = async () => {
      loading.value = true
      try {
        let finalOrders = []
        
        // 首先尝试从API获取订单
        try {
          const params = {
            page: currentPage.value,
            page_size: pageSize.value,
            search: searchQuery.value,
            status: statusFilter.value,
          }
          
          if (dateRange.value && dateRange.value.length === 2) {
            params.start_date = dayjs(dateRange.value[0]).format('YYYY-MM-DD')
            params.end_date = dayjs(dateRange.value[1]).format('YYYY-MM-DD')
          }
          
          const response = await axios.get('/api/orders/', { 
            params,
            headers: {
              'Authorization': `Token ${localStorage.getItem('authToken')}`
            }
          })
          finalOrders = response.data.results || response.data || []
          total.value = response.data.count || finalOrders.length
        } catch (apiError) {
          console.log('API获取订单失败，使用本地存储:', apiError)
          finalOrders = []
        }
        
        // 获取本地存储的订单（包含状态更新）
        const localOrders = JSON.parse(localStorage.getItem('localOrders') || '[]')
        
        // 合并API订单和本地订单，本地订单优先
        const mergedOrders = []
        
        // 首先添加所有API订单
        finalOrders.forEach(apiOrder => {
          // 检查本地存储中是否有相同订单的更新
          const localUpdate = localOrders.find(localOrder => 
            localOrder.id === apiOrder.id || 
            localOrder.order_number === apiOrder.order_number ||
            (localOrder.id && localOrder.id.toString() === apiOrder.id?.toString())
          )
          
          if (localUpdate) {
            // 如果本地有更新，使用本地数据覆盖API数据
            console.log(`管理员端订单 ${apiOrder.id} 使用本地更新数据:`, localUpdate)
            mergedOrders.push({
              ...apiOrder,
              ...localUpdate,
              // 确保保留API中的一些关键字段
              id: apiOrder.id,
              order_number: apiOrder.order_number || localUpdate.order_number
            })
          } else {
            // 没有本地更新，使用API数据
            mergedOrders.push(apiOrder)
          }
        })
        
        // 添加纯本地订单（不在API中的订单）
        localOrders.forEach(localOrder => {
          const existsInApi = finalOrders.some(apiOrder => 
            apiOrder.id === localOrder.id || 
            apiOrder.order_number === localOrder.order_number ||
            (apiOrder.id && apiOrder.id.toString() === localOrder.id?.toString())
          )
          
          if (!existsInApi) {
            mergedOrders.push(localOrder)
          }
        })
        
        // 应用搜索和状态过滤
        orders.value = mergedOrders.filter(order => {
          // 应用搜索过滤
          if (searchQuery.value) {
            const query = searchQuery.value.toLowerCase()
            const matchesSearch = order.order_number?.toLowerCase().includes(query) ||
                   order.movie_title?.toLowerCase().includes(query) ||
                   order.cinema_name?.toLowerCase().includes(query)
            if (!matchesSearch) return false
          }
          // 应用状态过滤
          if (statusFilter.value && order.status !== statusFilter.value) {
            return false
          }
          return true
        })
        
        total.value = orders.value.length
        console.log('管理员端最终合并后的订单数据:', orders.value)
        
      } catch (error) {
        console.error('加载订单列表失败:', error)
        ElMessage.error('加载订单列表失败')
        orders.value = []
        total.value = 0
      } finally {
        loading.value = false
      }
    }

    const handleSearch = () => {
      currentPage.value = 1
      loadOrders()
    }

    const handlePageChange = (page) => {
      currentPage.value = page
      loadOrders()
    }

    const handleCancel = async (order) => {
      try {
        await ElMessageBox.confirm(
          `确定要为订单 ${order.order_number} 退票吗？\n电影：${order.movie_title}\n总价：¥${order.total_price}`, 
          '管理员退票确认', 
          {
            confirmButtonText: '确定退票',
            cancelButtonText: '取消',
            type: 'warning',
            dangerouslyUseHTMLString: false
          }
        )
        
        // 先更新当前显示的订单状态
        const currentOrderIndex = orders.value.findIndex(o => o.id === order.id)
        if (currentOrderIndex !== -1) {
          orders.value[currentOrderIndex].status = 'refunded'
          orders.value[currentOrderIndex].refund_time = new Date().toISOString()
          orders.value[currentOrderIndex].refund_reason = '管理员操作退票'
        }
        
        try {
          // 尝试通过API退票 - 使用POST方法
          await axios.post(`/api/orders/${order.id}/refund/`, {
            admin_action: true,
            reason: '管理员操作退票'
          }, {
            headers: {
              'Authorization': `Token ${localStorage.getItem('authToken')}`
            }
          })
          ElMessage.success('退票成功')
        } catch (apiError) {
          console.log('API退票失败，更新本地存储:', apiError)
          // 如果API失败，更新本地存储
          const localOrders = JSON.parse(localStorage.getItem('localOrders') || '[]')
          const orderIndex = localOrders.findIndex(o => 
            o.id === order.id || 
            o.order_number === order.order_number ||
            (o.id && o.id.toString() === order.id?.toString())
          )
          if (orderIndex !== -1) {
            localOrders[orderIndex].status = 'refunded'
            localOrders[orderIndex].refund_time = new Date().toISOString()
            localOrders[orderIndex].refund_reason = '管理员操作退票'
            localStorage.setItem('localOrders', JSON.stringify(localOrders))
          } else {
            // 如果在localOrders中找不到，添加新的退票记录
            const refundedOrder = {
              ...order,
              status: 'refunded',
              refund_time: new Date().toISOString(),
              refund_reason: '管理员操作退票'
            }
            const existingOrders = JSON.parse(localStorage.getItem('localOrders') || '[]')
            existingOrders.push(refundedOrder)
            localStorage.setItem('localOrders', JSON.stringify(existingOrders))
          }
          ElMessage.success('退票成功（本地更新）')
        }
        
        // 不需要重新加载订单列表，因为已经更新了当前显示的状态
      } catch (error) {
        if (error !== 'cancel') {
          console.error('退票失败:', error)
          ElMessage.error('退票失败: ' + (error.message || '未知错误'))
          // 如果失败，恢复原状态
          const currentOrderIndex = orders.value.findIndex(o => o.id === order.id)
          if (currentOrderIndex !== -1) {
            orders.value[currentOrderIndex].status = order.status
            delete orders.value[currentOrderIndex].refund_time
            delete orders.value[currentOrderIndex].refund_reason
          }
        }
      }
    }

    const handleChange = async (order) => {
      try {
        // 创建一个更友好的时间选择对话框
        const createAdminTimePickerDialog = () => {
          return new Promise((resolve, reject) => {
            // 创建对话框HTML
            const dialogHTML = `
              <div id="adminTimePickerDialog" style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 10000;
              ">
                <div style="
                  background: white;
                  padding: 2rem;
                  border-radius: 12px;
                  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
                  max-width: 450px;
                  width: 90%;
                ">
                  <h3 style="margin: 0 0 1.5rem; text-align: center; color: #2c3e50;">管理员改签</h3>
                  <p style="margin-bottom: 1rem; color: #666; text-align: center;">
                    订单号：${order.order_number}<br>
                    当前场次：${formatDateTime(order.schedule_time || order.show_time)}
                  </p>
                  
                  <div style="margin-bottom: 1rem;">
                    <label style="display: block; margin-bottom: 0.5rem; color: #333; font-weight: 500;">选择日期：</label>
                    <input type="date" id="adminNewDate" style="
                      width: 100%;
                      padding: 0.75rem;
                      border: 2px solid #e0e0e0;
                      border-radius: 8px;
                      font-size: 1rem;
                      transition: border-color 0.3s;
                    " min="${new Date().toISOString().split('T')[0]}">
                  </div>
                  
                  <div style="margin-bottom: 1.5rem;">
                    <label style="display: block; margin-bottom: 0.5rem; color: #333; font-weight: 500;">选择时间：</label>
                    <select id="adminNewTime" style="
                      width: 100%;
                      padding: 0.75rem;
                      border: 2px solid #e0e0e0;
                      border-radius: 8px;
                      font-size: 1rem;
                      transition: border-color 0.3s;
                    ">
                      <option value="">请选择时间</option>
                      <option value="09:00">09:00 上午场</option>
                      <option value="10:30">10:30 上午场</option>
                      <option value="11:30">11:30 上午场</option>
                      <option value="13:00">13:00 下午场</option>
                      <option value="14:00">14:00 下午场</option>
                      <option value="15:30">15:30 下午场</option>
                      <option value="16:30">16:30 下午场</option>
                      <option value="18:00">18:00 晚上场</option>
                      <option value="19:00">19:00 晚上场</option>
                      <option value="20:30">20:30 晚上场</option>
                      <option value="21:30">21:30 晚上场</option>
                      <option value="22:30">22:30 深夜场</option>
                    </select>
                  </div>
                  
                  <div style="margin-bottom: 1.5rem;">
                    <label style="display: block; margin-bottom: 0.5rem; color: #333; font-weight: 500;">改签原因：</label>
                    <textarea id="adminChangeReason" placeholder="请输入改签原因..." style="
                      width: 100%;
                      height: 80px;
                      padding: 0.75rem;
                      border: 2px solid #e0e0e0;
                      border-radius: 8px;
                      font-size: 1rem;
                      resize: vertical;
                      transition: border-color 0.3s;
                    ">管理员操作改签</textarea>
                  </div>
                  
                  <div style="display: flex; gap: 1rem; justify-content: flex-end;">
                    <button id="adminCancelBtn" style="
                      padding: 0.75rem 1.5rem;
                      border: 2px solid #ddd;
                      background: #f8f9fa;
                      color: #666;
                      border-radius: 8px;
                      cursor: pointer;
                      font-weight: 500;
                      transition: all 0.3s;
                    ">取消</button>
                    <button id="adminConfirmBtn" style="
                      padding: 0.75rem 1.5rem;
                      border: none;
                      background: #e67e22;
                      color: white;
                      border-radius: 8px;
                      cursor: pointer;
                      font-weight: 500;
                      transition: all 0.3s;
                    ">确认改签</button>
                  </div>
                </div>
              </div>
            `
            
            // 添加到页面
            document.body.insertAdjacentHTML('beforeend', dialogHTML)
            
            const dialog = document.getElementById('adminTimePickerDialog')
            const dateInput = document.getElementById('adminNewDate')
            const timeSelect = document.getElementById('adminNewTime')
            const reasonTextarea = document.getElementById('adminChangeReason')
            const cancelBtn = document.getElementById('adminCancelBtn')
            const confirmBtn = document.getElementById('adminConfirmBtn')
            
            // 设置默认日期为今天
            dateInput.value = new Date().toISOString().split('T')[0]
            
            // 添加样式交互
            const inputs = [dateInput, timeSelect, reasonTextarea]
            inputs.forEach(input => {
              input.addEventListener('focus', () => {
                input.style.borderColor = '#3498db'
              })
              input.addEventListener('blur', () => {
                input.style.borderColor = '#e0e0e0'
              })
            })
            
            cancelBtn.addEventListener('mouseenter', () => {
              cancelBtn.style.background = '#e9ecef'
              cancelBtn.style.borderColor = '#adb5bd'
            })
            cancelBtn.addEventListener('mouseleave', () => {
              cancelBtn.style.background = '#f8f9fa'
              cancelBtn.style.borderColor = '#ddd'
            })
            
            confirmBtn.addEventListener('mouseenter', () => {
              confirmBtn.style.background = '#d35400'
              confirmBtn.style.transform = 'translateY(-1px)'
            })
            confirmBtn.addEventListener('mouseleave', () => {
              confirmBtn.style.background = '#e67e22'
              confirmBtn.style.transform = 'translateY(0)'
            })
            
            // 事件处理
            cancelBtn.onclick = () => {
              dialog.remove()
              reject('cancel')
            }
            
            confirmBtn.onclick = () => {
              const date = dateInput.value
              const time = timeSelect.value
              const reason = reasonTextarea.value.trim()
              
              if (!date || !time) {
                ElMessage.warning('请选择完整的日期和时间')
                return
              }
              
              if (!reason) {
                ElMessage.warning('请输入改签原因')
                return
              }
              
              const newDateTime = `${date} ${time}`
              dialog.remove()
              resolve({ newDateTime, reason })
            }
            
            // 点击背景关闭
            dialog.onclick = (e) => {
              if (e.target === dialog) {
                dialog.remove()
                reject('cancel')
              }
            }
          })
        }
        
        const result = await createAdminTimePickerDialog()
        const { newDateTime, reason } = result
        
        // 先更新当前显示的订单状态
        const currentOrderIndex = orders.value.findIndex(o => o.id === order.id)
        if (currentOrderIndex !== -1) {
          orders.value[currentOrderIndex].status = 'changed'
          orders.value[currentOrderIndex].original_schedule_time = orders.value[currentOrderIndex].schedule_time || orders.value[currentOrderIndex].show_time
          orders.value[currentOrderIndex].schedule_time = newDateTime
          orders.value[currentOrderIndex].show_time = newDateTime
          orders.value[currentOrderIndex].change_time = new Date().toISOString()
          orders.value[currentOrderIndex].change_reason = reason
        }
        
        try {
          // 尝试通过API改签 - 使用POST方法
          await axios.post(`/api/orders/${order.id}/change/`, {
            new_schedule_time: newDateTime,
            admin_action: true,
            reason: reason
          }, {
            headers: {
              'Authorization': `Token ${localStorage.getItem('authToken')}`
            }
          })
          ElMessage.success('改签成功')
        } catch (apiError) {
          console.log('API改签失败，更新本地存储:', apiError)
          // 如果API失败，更新本地存储
          const localOrders = JSON.parse(localStorage.getItem('localOrders') || '[]')
          const orderIndex = localOrders.findIndex(o => 
            o.id === order.id || 
            o.order_number === order.order_number ||
            (o.id && o.id.toString() === order.id?.toString())
          )
          if (orderIndex !== -1) {
            localOrders[orderIndex].status = 'changed'
            localOrders[orderIndex].original_schedule_time = localOrders[orderIndex].schedule_time || localOrders[orderIndex].show_time
            localOrders[orderIndex].schedule_time = newDateTime
            localOrders[orderIndex].show_time = newDateTime
            localOrders[orderIndex].change_time = new Date().toISOString()
            localOrders[orderIndex].change_reason = reason
            localStorage.setItem('localOrders', JSON.stringify(localOrders))
          } else {
            // 如果在localOrders中找不到，添加新的改签记录
            const changedOrder = {
              ...order,
              status: 'changed',
              original_schedule_time: order.schedule_time || order.show_time,
              schedule_time: newDateTime,
              show_time: newDateTime,
              change_time: new Date().toISOString(),
              change_reason: reason
            }
            const existingOrders = JSON.parse(localStorage.getItem('localOrders') || '[]')
            existingOrders.push(changedOrder)
            localStorage.setItem('localOrders', JSON.stringify(existingOrders))
          }
          ElMessage.success('改签成功（本地更新）')
        }
        
        // 不需要重新加载订单列表，因为已经更新了当前显示的状态
      } catch (error) {
        if (error !== 'cancel') {
          console.error('改签失败:', error)
          ElMessage.error('改签失败: ' + (error.message || '未知错误'))
          // 如果失败，恢复原状态
          const currentOrderIndex = orders.value.findIndex(o => o.id === order.id)
          if (currentOrderIndex !== -1) {
            orders.value[currentOrderIndex].status = order.status
            orders.value[currentOrderIndex].schedule_time = order.schedule_time
            orders.value[currentOrderIndex].show_time = order.show_time
            delete orders.value[currentOrderIndex].original_schedule_time
            delete orders.value[currentOrderIndex].change_time
            delete orders.value[currentOrderIndex].change_reason
          }
        }
      }
    }

    const viewDetail = (order) => {
      router.push({
        name: 'OrderDetail',
        params: { id: order.id }
      })
    }

    const handleConfirmPayment = async (order) => {
      try {
        await ElMessageBox.confirm(
          `确定要确认订单 ${order.order_number} 的支付状态吗？\n电影：${order.movie_title}\n总价：¥${order.total_price}`, 
          '管理员确认支付', 
          {
            confirmButtonText: '确认支付',
            cancelButtonText: '取消',
            type: 'info'
          }
        )
        
        try {
          // 尝试通过API确认支付
          await axios.patch(`/api/orders/${order.id}/confirm-payment/`, {
            admin_action: true,
            reason: '管理员确认支付'
          }, {
            headers: {
              'Authorization': `Token ${localStorage.getItem('authToken')}`
            }
          })
          ElMessage.success('支付确认成功')
        } catch (apiError) {
          console.log('API确认支付失败，更新本地存储:', apiError)
          // 如果API失败，更新本地存储
          const localOrders = JSON.parse(localStorage.getItem('localOrders') || '[]')
          const orderIndex = localOrders.findIndex(o => o.id === order.id || o.order_number === order.order_number)
          if (orderIndex !== -1) {
            localOrders[orderIndex].status = 'paid'
            localOrders[orderIndex].payment_confirmed_time = new Date().toISOString()
            localOrders[orderIndex].payment_confirmed_by = 'admin'
            localStorage.setItem('localOrders', JSON.stringify(localOrders))
            ElMessage.success('支付确认成功（本地更新）')
          } else {
            throw new Error('订单未找到')
          }
        }
        
        // 重新加载订单列表
        loadOrders()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('确认支付失败:', error)
          ElMessage.error('确认支付失败: ' + (error.message || '未知错误'))
        }
      }
    }

    const getStatusType = (status) => {
      const statusMap = {
        pending: 'info',
        paid: 'success',
        cancelled: 'danger',
        refunded: 'danger',
        changed: 'warning'
      }
      return statusMap[status] || 'info'
    }

    const getStatusText = (status) => {
      const statusMap = {
        pending: '待支付',
        paid: '已支付',
        cancelled: '已取消',
        refunded: '已退款',
        changed: '已改签'
      }
      return statusMap[status] || '未知状态'
    }

    const formatDateTime = (datetime) => {
      if (!datetime) return '未知时间'
      return dayjs(datetime).format('YYYY-MM-DD HH:mm')
    }

    const formatSeats = (seats) => {
      if (!seats) return '未知座位'
      
      // 如果是字符串数组（如 ["A1", "A2"]）
      if (Array.isArray(seats) && seats.length > 0 && typeof seats[0] === 'string') {
        return seats.join('、')
      }
      
      // 如果是对象数组（如 [{row: 0, col: 0}]）
      if (Array.isArray(seats) && seats.length > 0 && typeof seats[0] === 'object') {
        return seats.map(seat => `${String.fromCharCode(65 + seat.row)}${seat.col + 1}`).join('、')
      }
      
      // 如果是字符串（如 "A1,A2"）
      if (typeof seats === 'string') {
        return seats.replace(/,/g, '、')
      }
      
      return '未知座位'
    }

    onMounted(() => {
      loadOrders()
    })

    return {
      orders,
      loading,
      total,
      pageSize,
      currentPage,
      searchQuery,
      statusFilter,
      dateRange,
      statusOptions,
      handleSearch,
      handlePageChange,
      handleCancel,
      handleChange,
      viewDetail,
      handleConfirmPayment,
      getStatusType,
      getStatusText,
      formatDateTime,
      formatSeats
    }
  }
}
</script>

<style scoped>
.admin-orders-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin-bottom: 20px;
}

.filters {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.filters .el-input {
  width: 300px;
}

.filters .el-select {
  width: 150px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.action-buttons .el-button {
  margin: 0;
  font-size: 12px;
  padding: 5px 8px;
}

.action-buttons .el-button + .el-button {
  margin-left: 0;
}
</style> 