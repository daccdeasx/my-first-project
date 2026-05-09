<template>
  <el-card class="system-status-panel">
    <div class="flex justify-between items-center mb-4">
      <h3>系统状态</h3>
      <el-button 
        type="text" 
        size="small" 
        @click="refreshStatus"
        :loading="loading"
      >
        <el-icon><Refresh /></el-icon>刷新
      </el-button>
    </div>
    <div class="grid grid-cols-3 gap-4">
      <MetricCard 
        v-if="health.cpu !== undefined"
        title="CPU使用率" 
        :value="health.cpu" 
        unit="%"
        icon="microchip" 
        color="#409EFF"
        :trend="health.cpuTrend"
      />
      <MetricCard 
        v-if="health.memory !== undefined"
        title="内存使用" 
        :value="health.memory" 
        unit="GB"
        icon="memory" 
        color="#67C23A"
        :trend="health.memoryTrend"
      />
      <MetricCard 
        v-if="health.disk !== undefined"
        title="磁盘空间" 
        :value="health.disk" 
        unit="GB"
        icon="hdd-o" 
        color="#E6A23C"
        :trend="health.diskTrend"
      />
    </div>
    <div class="mt-4 text-sm text-gray-500">
      最后更新: {{ lastUpdated }}
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSystemHealth } from '@/api/admin'
import MetricCard from './MetricCard.vue'

const loading = ref(false)
const health = ref({
  cpu: 0,
  memory: 0,
  disk: 0,
  cpuTrend: 0,
  memoryTrend: 0,
  diskTrend: 0
})
const lastUpdated = ref('')

// 获取系统状态
const fetchSystemHealth = async () => {
  loading.value = true
  try {
    const response = await getSystemHealth()
    
    // 调试日志：查看实际返回的数据
    console.log('系统健康状态API响应:', response)
    
    // 检查响应是否有效
    if (!response) {
      throw new Error('API响应为空')
    }
    
    // 尝试从不同可能的位置提取数据
    let data = response
    if (response.data !== undefined) {
      data = response.data
    } else if (response.body !== undefined) {
      data = response.body
    }
    
    // 确保数据是一个对象
    if (typeof data !== 'object' || data === null) {
      throw new Error('系统状态数据格式不正确')
    }
    
    // 解构并验证数据结构，设置默认值
    const { 
      cpu = 0, 
      memory = 0, 
      disk = 0, 
      cpuTrend = 0, 
      memoryTrend = 0, 
      diskTrend = 0 
    } = data
    
    // 更新状态
    health.value = {
      cpu,
      memory,
      disk,
      cpuTrend,
      memoryTrend,
      diskTrend
    }
    
    // 更新最后更新时间
    const now = new Date()
    lastUpdated.value = now.toLocaleString()
    
    return health.value
  } catch (error) {
    console.error('获取系统状态失败:', error)
    ElMessage.error('获取系统状态失败: ' + error.message)
    
    // 保持默认值，避免UI崩溃
    health.value = {
      cpu: 0,
      memory: 0,
      disk: 0,
      cpuTrend: 0,
      memoryTrend: 0,
      diskTrend: 0
    }
    
    return null
  } finally {
    loading.value = false
  }
}

// 刷新系统状态
const refreshStatus = async () => {
  await fetchSystemHealth()
  ElMessage.success('系统状态已刷新')
}

// 初始化
onMounted(() => {
  fetchSystemHealth()
})
</script>

<style scoped>
.system-status-panel {
  margin-top: 20px;
}
</style>