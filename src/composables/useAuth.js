// src/composables/useAuth.js
import { ref } from 'vue'

const authUser = ref(null)

export const useAuth = () => {
  const checkAuthStatus = async () => {
    try {
      const { data } = await axios.get('/api/auth/check/')
      authUser.value = data
    } catch {
      authUser.value = null
    }
  }

  return { authUser, checkAuthStatus }
}