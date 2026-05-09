<template>
  <div class="order-detail-container">
    <el-card class="order-card">
      <template #header>
        <div class="card-header">
          <span>订单详情</span>
          <el-tag :type="getStatusType">{{ getStatusText }}</el-tag>
        </div>
      </template>

      <div class="order-info" v-if="order">
        <div class="movie-info">
          <h2>{{ order.movie_title }}</h2>
          <p>影院: {{ order.cinema_name }}</p>
          <p>场次: {{ formatDateTime(order.schedule_time) }}</p>
          <p>座位: {{ formatSeats(order.seats) }}</p>
          <p>总价: ¥{{ order.total_price }}</p>
          <p>订单号: {{ order.order_number }}</p>
          <p>创建时间: {{ formatDateTime(order.created_at) }}</p>
        </div>


      </div>
    </el-card>




  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import dayjs from 'dayjs'

export default {
  name: 'OrderDetailView',
  setup() {
    const route = useRoute()
    const order = ref(null)

    const getStatusType = computed(() => {
      const statusMap = {
        pending: 'info',
        paid: 'success',
        cancelled: 'danger',
        refunded: 'danger',
        changed: 'warning'
      }
      return statusMap[order.value?.status] || 'info'
    })

    const getStatusText = computed(() => {
      const statusMap = {
        pending: '待支付',
        paid: '已支付',
        cancelled: '已取消',
        refunded: '已退款',
        changed: '已改签'
      }
      return statusMap[order.value?.status] || '未知状态'
    })

    const loadOrder = async () => {
      try {
        const response = await axios.get(`/api/orders/${route.params.id}/`, {
          headers: {
            'Authorization': `Token ${localStorage.getItem('authToken')}`
          }
        })
        order.value = response.data
      } catch (error) {
        ElMessage.error('加载订单信息失败')
      }
    }



    const formatDateTime = (datetime) => {
      return dayjs(datetime).format('YYYY-MM-DD HH:mm')
    }

    const formatSeats = (seats) => {
      if (!seats) return '无座位信息'
      
      // 如果seats是对象（包含真实信息的增强格式）
      if (typeof seats === 'object' && !Array.isArray(seats)) {
        if (seats.seats && Array.isArray(seats.seats)) {
          return seats.seats.map(seat => `${seat.row + 1}排${seat.col + 1}号`).join('、')
        }
        return '无座位信息'
      }
      
      // 如果seats是数组（原始格式）
      if (Array.isArray(seats)) {
        if (seats.length === 0) return '无座位信息'
        return seats.map(seat => `${seat.row + 1}排${seat.col + 1}号`).join('、')
      }
      
      return '无座位信息'
    }

    onMounted(() => {
      loadOrder()
    })

    return {
      order,
      getStatusType,
      getStatusText,
      formatDateTime,
      formatSeats
    }
  }
}
</script>

<style scoped>
.order-detail-container {
  padding: 20px;
  padding-top: 100px; /* 为导航栏留出空间 */
  max-width: 800px;
  margin: 0 auto;
  background: var(--dark-bg);
  min-height: 100vh;
}

.order-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.movie-info {
  margin-bottom: 20px;
}

.movie-info h2 {
  margin-bottom: 15px;
  color: var(--light-text);
}

.movie-info p {
  margin: 10px 0;
  color: var(--gray-text);
}



/* Element Plus 组件深色主题覆盖 */
:deep(.el-card) {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

:deep(.el-card__header) {
  background-color: var(--darker-bg);
  border-bottom: 1px solid var(--border-color);
  color: var(--light-text);
}

:deep(.el-card__body) {
  background-color: var(--card-bg);
  color: var(--light-text);
}



:deep(.el-tag) {
  background-color: var(--darker-bg);
  border-color: var(--border-color);
  color: var(--light-text);
}



@media (max-width: 768px) {
  .order-detail-container {
    padding: 15px;
    padding-top: 90px;
  }
}
</style>