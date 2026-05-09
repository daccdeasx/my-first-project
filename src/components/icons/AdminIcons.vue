<template>
  <svg 
    :width="size" 
    :height="size" 
    viewBox="0 0 24 24" 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
    :style="{ color: color }"
  >
    <!-- 仪表盘图标 -->
    <g v-if="name === 'dashboard'">
      <path 
        d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" 
        fill="currentColor"
      />
      <circle cx="12" cy="12" r="3" fill="currentColor"/>
      <path d="M12 1v6M23 12h-6M12 23v-6M1 12h6" stroke="currentColor" stroke-width="2"/>
    </g>

    <!-- 用户图标 -->
    <g v-else-if="name === 'user'">
      <path 
        d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" 
        fill="currentColor"
      />
    </g>

    <!-- 电影图标 -->
    <g v-else-if="name === 'movie'">
      <path 
        d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z" 
        fill="currentColor"
      />
    </g>

    <!-- 评论图标 -->
    <g v-else-if="name === 'comment'">
      <path 
        d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h4l4 4 4-4h4c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z" 
        fill="currentColor"
      />
      <circle cx="8" cy="10" r="1" fill="white"/>
      <circle cx="12" cy="10" r="1" fill="white"/>
      <circle cx="16" cy="10" r="1" fill="white"/>
    </g>

    <!-- 数据分析图标 -->
    <g v-else-if="name === 'analytics'">
      <path 
        d="M5 9.2h3V19H5zM10.6 5h2.8v14h-2.8zm5.6 8H19v6h-2.8z" 
        fill="currentColor"
      />
      <path 
        d="M2 20h20v2H2z" 
        fill="currentColor"
      />
    </g>

    <!-- 论坛图标 -->
    <g v-else-if="name === 'forum'">
      <path 
        d="M21 6h-2v9H6v2c0 .55.45 1 1 1h11l4 4V7c0-.55-.45-1-1-1zm-4 6V3c0-.55-.45-1-1-1H3c-.55 0-1 .45-1 1v14l4-4h11c.55 0 1-.45 1-1z" 
        fill="currentColor"
      />
    </g>

    <!-- 订单图标 -->
    <g v-else-if="name === 'orders'">
      <path 
        d="M22 10v6c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V8c0-1.1.9-2 2-2h2V4c0-1.1.9-2 2-2h8c1.1 0 2 .9 2 2v2h2c1.1 0 2 .9 2 2v2zm-8-6H10v2h4V4zm6 4H4v8h16v-8z" 
        fill="currentColor"
      />
      <path d="M9 10h6v2H9z" fill="white"/>
    </g>

    <!-- 设置图标 -->
    <g v-else-if="name === 'settings'">
      <path 
        d="M19.14,12.94c0.04-0.3,0.06-0.61,0.06-0.94c0-0.32-0.02-0.64-0.07-0.94l2.03-1.58c0.18-0.14,0.23-0.41,0.12-0.61 l-1.92-3.32c-0.12-0.22-0.37-0.29-0.59-0.22l-2.39,0.96c-0.5-0.38-1.03-0.7-1.62-0.94L14.4,2.81c-0.04-0.24-0.24-0.41-0.48-0.41 h-3.84c-0.24,0-0.43,0.17-0.47,0.41L9.25,5.35C8.66,5.59,8.12,5.92,7.63,6.29L5.24,5.33c-0.22-0.08-0.47,0-0.59,0.22L2.74,8.87 C2.62,9.08,2.66,9.34,2.86,9.48l2.03,1.58C4.84,11.36,4.8,11.69,4.8,12s0.02,0.64,0.07,0.94l-2.03,1.58 c-0.18,0.14-0.23,0.41-0.12,0.61l1.92,3.32c0.12,0.22,0.37,0.29,0.59,0.22l2.39-0.96c0.5,0.38,1.03,0.7,1.62,0.94l0.36,2.54 c0.05,0.24,0.24,0.41,0.48,0.41h3.84c0.24,0,0.44-0.17,0.47-0.41l0.36-2.54c0.59-0.24,1.13-0.56,1.62-0.94l2.39,0.96 c0.22,0.08,0.47,0,0.59-0.22l1.92-3.32c0.12-0.22,0.07-0.47-0.12-0.61L19.14,12.94z M12,15.6c-1.98,0-3.6-1.62-3.6-3.6 s1.62-3.6,3.6-3.6s3.6,1.62,3.6,3.6S13.98,15.6,12,15.6z" 
        fill="currentColor"
      />
    </g>

    <!-- 默认菜单图标 -->
    <g v-else>
      <path 
        d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z" 
        fill="currentColor"
      />
    </g>
  </svg>
</template>

<script setup>
defineProps({
  name: {
    type: String,
    required: true
  },
  size: {
    type: [String, Number],
    default: 18
  },
  color: {
    type: String,
    default: 'currentColor'
  }
})
</script>
