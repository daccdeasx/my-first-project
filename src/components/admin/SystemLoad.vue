<template>
  <div>
    <h3 class="chart-title mb-4"></h3>
    <div v-if="performance">
      <div class="grid grid-cols-2 gap-4">
        <RadialProgress 
          :percentage="performance.server_load?.cpu || 0"
          label="CPU使用率"
          color="#F56C6C"
        />
        <RadialProgress 
          :percentage="performance.server_load?.memory || 0"
          label="内存使用率"
          color="#67C23A"
        />
      </div>
      <div class="mt-6 grid grid-cols-2 gap-4 text-sm">
        <div class="bg-gray-50 p-4 rounded-lg">
          <div class="text-gray-500 mb-2">响应时间</div>
          <div class="space-y-1">
            <div class="flex justify-between">
              <span class="text-gray-600">最小:</span>
              <span>{{ performance.response_time?.min || 0 }}ms</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">平均:</span>
              <span>{{ performance.response_time?.avg || 0 }}ms</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">最大:</span>
              <span>{{ performance.response_time?.max || 0 }}ms</span>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 p-4 rounded-lg">
          <div class="text-gray-500 mb-2">数据库</div>
          <div class="space-y-1">
            <div class="flex justify-between">
              <span class="text-gray-600">查询:</span>
              <span>{{ performance.database?.queries || 0 }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">连接:</span>
              <span>{{ performance.database?.connections || 0 }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="p-4 flex items-center justify-center">
      <el-skeleton count="1" animated />
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'
import { ElSkeleton } from 'element-plus'

defineProps({
  performance: {
    type: Object,
    default: () => ({
      server_load: { cpu: 0, memory: 0 },
      response_time: { min: 0, avg: 0, max: 0 },
      database: { queries: 0, connections: 0 }
    })
  }
})
</script>