// src/composables/useLoading.js
import { ref } from 'vue'

export const useLoading = () => {
  const loading = ref(false)
  
  const startLoading = () => {
    loading.value = true
  }
  
  const endLoading = () => {
    loading.value = false
  }

  return {
    loading,
    startLoading,
    endLoading
  }
}