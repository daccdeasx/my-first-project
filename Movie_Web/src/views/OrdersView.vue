<template>
  <div class="orders-container">
    <div class="orders-header">
      <h1>我的订单</h1>
      <el-button @click="refreshOrders" :loading="loading" icon="el-icon-refresh">
        刷新
      </el-button>
    </div>

    <div v-if="loading" class="loading">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="orders.length === 0" class="no-orders">
      <el-empty description="暂无订单">
        <el-button type="primary" @click="$router.push('/')">
          去看电影
        </el-button>
      </el-empty>
    </div>

    <div v-else class="orders-list">
      <div
        v-for="order in orders"
        :key="order.id"
        class="order-card"
      >
        <div class="order-header">
          <div class="order-info">
            <h3>
              <span class="order-status" :class="order.status">
                {{ getStatusText(order.status) }}
              </span>
              订单号: {{ order.order_number }}
            </h3>
          </div>
          <div class="order-price">
            ¥{{ order.total_price }}
          </div>
        </div>

        <div class="order-content">
          <div class="movie-info">
            <h4>{{ order.movie_title }}</h4>
            <p>{{ order.cinema_name }}</p>
            <p>场次时间: {{ formatDateTime(order.schedule_time) }}</p>
          </div>

          <div class="seat-info">
            <p>座位: {{ formatSeats(order.seats) }}</p>
            <p>数量: {{ order.seats.length }}张</p>
          </div>
        </div>

        <div class="order-footer">
          <div class="order-time">
            下单时间: {{ formatDateTime(order.created_at) }}
          </div>
          <div class="order-actions">
            <el-button
              v-if="order.status === 'paid'"
              size="small"
              @click="cancelOrder(order)"
            >
              申请退票
            </el-button>
            <el-button
              size="small"
              type="primary"
              @click="viewOrderDetail(order)"
            >
              查看详情
            </el-button>
          </div>
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
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import dayjs from 'dayjs'

export default {
  name: 'OrdersView',
  setup() {
    const router = useRouter()
    const orders = ref([])
    const loading = ref(false)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = ref(0)

    const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

    const loadOrders = async (page = 1) => {
      try {
        loading.value = true
        const response = await axios.get('/api/orders/', {
          params: {
            page,
            page_size: pageSize.value
          },
          headers: {
            'Authorization': `Token ${localStorage.getItem('authToken')}`
          }
        })

        if (response.data.results) {
          orders.value = response.data.results
          total.value = response.data.count
        } else {
          orders.value = Array.isArray(response.data) ? response.data : []
          total.value = orders.value.length
        }

        // 合并本地存储的订单（只显示当前用户的订单）
        const allLocalOrders = JSON.parse(localStorage.getItem('localOrders') || '[]')
        const currentUserId = JSON.parse(localStorage.getItem('user') || '{}')?.id
        const localOrders = currentUserId ? allLocalOrders.filter(order => 
          order.user_id === currentUserId || order.user === currentUserId
        ) : []
        if (localOrders.length > 0) {
          orders.value = [...localOrders, ...orders.value]
          total.value += localOrders.length
        }

        console.log('订单列表:', orders.value)
      } catch (error) {
        console.error('加载订单失败:', error)
        ElMessage.error('加载订单失败')

        // 如果API失败，只显示本地订单（只显示当前用户的订单）
        const allLocalOrders = JSON.parse(localStorage.getItem('localOrders') || '[]')
        const currentUserId = JSON.parse(localStorage.getItem('user') || '{}')?.id
        const localOrders = currentUserId ? allLocalOrders.filter(order => 
          order.user_id === currentUserId || order.user === currentUserId
        ) : []
        orders.value = localOrders
        total.value = localOrders.length
      } finally {
        loading.value = false
      }
    }

    const refreshOrders = () => {
      loadOrders(currentPage.value)
    }

    const handlePageChange = (page) => {
      currentPage.value = page
      loadOrders(page)
    }

    const getStatusText = (status) => {
      const statusMap = {
        'pending': '待支付',
        'paid': '已支付',
        'cancelled': '已取消',
        'refunded': '已退款'
      }
      return statusMap[status] || status
    }

    const formatDateTime = (datetime) => {
      if (!datetime) return '未知时间'
      return dayjs(datetime).format('YYYY-MM-DD HH:mm')
    }

    const formatSeats = (seats) => {
      if (!seats) return '无座位信息'
      
      // 如果seats是对象（包含真实信息的增强格式）
      if (typeof seats === 'object' && !Array.isArray(seats)) {
        if (seats.seats && Array.isArray(seats.seats)) {
          return seats.seats.join(', ')
        }
        return '无座位信息'
      }
      
      // 如果seats是数组（原始格式）
      if (Array.isArray(seats)) {
        if (seats.length === 0) return '无座位信息'
        return seats.join(', ')
      }
      
      return '无座位信息'
    }

    const cancelOrder = async (order) => {
      try {
        await ElMessageBox.confirm(
          '确定要申请退票吗？退票后将无法恢复。',
          '确认退票',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        // 如果是本地订单，直接更新本地存储
        if (order.id.toString().startsWith('local_')) {
          const localOrders = JSON.parse(localStorage.getItem('localOrders') || '[]')
          const orderIndex = localOrders.findIndex(o => o.id === order.id)
          if (orderIndex !== -1) {
            localOrders[orderIndex].status = 'cancelled'
            localStorage.setItem('localOrders', JSON.stringify(localOrders))
            ElMessage.success('退票申请成功')
            refreshOrders()
          }
          return
        }

        // 真实订单的退票处理
        await axios.post(`/api/orders/${order.id}/cancel/`, {}, {
          headers: {
            'Authorization': `Token ${localStorage.getItem('authToken')}`
          }
        })

        ElMessage.success('退票申请成功')
        refreshOrders()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('退票失败:', error)
          ElMessage.error('退票失败')
        }
      }
    }

    const viewOrderDetail = (order) => {
      // 显示订单详情对话框或跳转到详情页
      ElMessageBox.alert(
        `
        <div style="text-align: left; color: var(--light-text);">
          <p style="margin: 8px 0; color: var(--light-text);"><strong style="color: var(--light-text);">订单号:</strong> ${order.order_number}</p>
          <p style="margin: 8px 0; color: var(--light-text);"><strong style="color: var(--light-text);">电影:</strong> ${order.movie_title}</p>
          <p style="margin: 8px 0; color: var(--light-text);"><strong style="color: var(--light-text);">影院:</strong> ${order.cinema_name}</p>
          <p style="margin: 8px 0; color: var(--light-text);"><strong style="color: var(--light-text);">座位:</strong> ${formatSeats(order.seats)}</p>
          <p style="margin: 8px 0; color: var(--primary-color);"><strong style="color: var(--light-text);">总价:</strong> ¥${order.total_price}</p>
          <p style="margin: 8px 0; color: var(--light-text);"><strong style="color: var(--light-text);">状态:</strong> ${getStatusText(order.status)}</p>
          <p style="margin: 8px 0; color: var(--gray-text);"><strong style="color: var(--light-text);">下单时间:</strong> ${formatDateTime(order.created_at)}</p>
        </div>
        `,
        '订单详情',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '确定',
          customClass: 'dark-message-box'
        }
      )
    }

    onMounted(() => {
      loadOrders()
    })

    return {
      orders,
      loading,
      currentPage,
      pageSize,
      total,
      totalPages,
      loadOrders,
      refreshOrders,
      handlePageChange,
      getStatusText,
      formatDateTime,
      formatSeats,
      cancelOrder,
      viewOrderDetail
    }
  }
}
</script>

<style scoped>
.orders-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  padding-top: 100px; /* 为导航栏留出空间 */
  background: var(--dark-bg);
  min-height: 100vh;
}

.orders-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.orders-header h1 {
  margin: 0;
  color: var(--light-text);
  font-size: 24px;
}

.loading {
  padding: 20px;
}

.no-orders {
  text-align: center;
  padding: 60px 20px;
}

.orders-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.order-card {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.order-card:hover {
  border-color: var(--primary-color);
  background: rgba(229, 9, 20, 0.05);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
}

.order-info h3 {
  margin: 0;
  color: var(--light-text);
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.order-status {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}

.order-status.pending {
  background: rgba(230, 162, 60, 0.2);
  color: #e6a23c;
  border: 1px solid rgba(230, 162, 60, 0.3);
}

.order-status.paid {
  background: rgba(64, 158, 255, 0.2);
  color: #409eff;
  border: 1px solid rgba(64, 158, 255, 0.3);
}

.order-status.cancelled {
  background: rgba(245, 108, 108, 0.2);
  color: #f56c6c;
  border: 1px solid rgba(245, 108, 108, 0.3);
}

.order-status.refunded {
  background: rgba(144, 147, 153, 0.2);
  color: #909399;
  border: 1px solid rgba(144, 147, 153, 0.3);
}

.order-price {
  font-size: 16px;
  font-weight: bold;
  color: var(--primary-color);
}

.order-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 12px;
  margin-bottom: 10px;
}

.movie-info h4 {
  margin: 0 0 4px 0;
  color: var(--light-text);
  font-size: 14px;
  font-weight: 600;
}

.movie-info p {
  margin: 0 0 3px 0;
  color: var(--gray-text);
  font-size: 12px;
  line-height: 1.4;
}

.seat-info p {
  margin: 0 0 3px 0;
  color: var(--gray-text);
  font-size: 12px;
  line-height: 1.4;
}

.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 10px;
  border-top: 1px solid var(--border-color);
}

.order-time {
  color: var(--gray-text);
  font-size: 11px;
}

.order-actions {
  display: flex;
  gap: 6px;
}

.pagination {
  margin-top: 30px;
  text-align: center;
}

/* Element Plus 组件深色主题覆盖 */
:deep(.el-button) {
  border-radius: 6px;
  background-color: var(--card-bg);
  border-color: var(--border-color);
  color: var(--light-text);
  padding: 4px 8px;
  font-size: 12px;
  height: auto;
  min-height: 24px;
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

:deep(.el-empty__description p) {
  color: var(--gray-text);
}

:deep(.el-skeleton__item) {
  background: linear-gradient(90deg, var(--card-bg) 25%, var(--darker-bg) 50%, var(--card-bg) 75%) !important;
  background-size: 400% 100%;
  animation: loading 1.4s ease infinite;
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

/* MessageBox 深色主题 */
:deep(.dark-message-box) {
  background-color: var(--card-bg) !important;
  border: 1px solid var(--border-color) !important;
}

:deep(.dark-message-box .el-message-box__header) {
  background-color: var(--darker-bg) !important;
  border-bottom: 1px solid var(--border-color) !important;
}

:deep(.dark-message-box .el-message-box__title) {
  color: var(--light-text) !important;
}

:deep(.dark-message-box .el-message-box__content) {
  background-color: var(--card-bg) !important;
  color: var(--light-text) !important;
}

:deep(.dark-message-box .el-message-box__message) {
  color: var(--light-text) !important;
}

:deep(.dark-message-box .el-button--primary) {
  background-color: var(--primary-color) !important;
  border-color: var(--primary-color) !important;
}

@keyframes loading {
  0% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

@media (max-width: 768px) {
  .orders-container {
    padding: 15px;
    padding-top: 90px;
  }

  .order-content {
    grid-template-columns: 1fr;
  }

  .order-footer {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}
</style>