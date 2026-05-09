import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
    plugins: [vue()],
    define: {
      'process.env': {} // 添加空对象定义
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, ''),
        configure: (proxy, options) => {
          // 调试代理配置
          proxy.on('proxyReq', (proxyReq) => {
            console.log('代理请求至:', proxyReq.path)
          })
          return options
        }
      }
    }
  }
})