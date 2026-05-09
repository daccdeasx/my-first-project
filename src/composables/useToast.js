// src/composables/useToast.js
import { ref } from 'vue'

export const useToast = () => {
  const toast = ref(null)
  
  const showSuccess = (message, duration = 3000) => {
    // 这里需要你实际的Toast组件实现
    console.log(`[SUCCESS] ${message}`)
  }
  
  const showError = (message, duration = 5000) => {
    // 这里需要你实际的Toast组件实现
    console.error(`[ERROR] ${message}`)
  }

  return {
    toast,
    showSuccess,
    showError
  }
}