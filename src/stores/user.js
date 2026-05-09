import { defineStore } from 'pinia'
import { ref } from 'vue'
import instance from '@/utils/axios' // 导入自定义 Axios 实例

export const useUserStore = defineStore('user', () => {
    // 状态
    const isAuthenticated = ref(false)
    const email = ref('')
    const avatar = ref(localStorage.getItem('avatar') || null)
    const avatarTimestamp = ref(Number(localStorage.getItem('avatarTs')) || Date.now())
    const profileData = ref(null)
    const isAdmin = ref(false) // 改为状态变量而非计算属性
    const adminRole = ref('user')
    const isSuperuser = ref(false)

    // 方法
    const logout = () => {
        isAuthenticated.value = false
        email.value = ''
        avatar.value = null
        avatarTimestamp.value = Date.now()
        profileData.value = null
        isAdmin.value = false // 登出时重置管理员状态
        adminRole.value = 'user'
        isSuperuser.value = false
        localStorage.removeItem('authToken')
        localStorage.removeItem('avatar')
        localStorage.removeItem('avatarTs')
    }

    const updateAvatar = (newAvatar) => {
        avatar.value = newAvatar
        avatarTimestamp.value = Date.now()
        localStorage.setItem('avatar', newAvatar)
        localStorage.setItem('avatarTs', avatarTimestamp.value)
    }

    const updateUserInfo = (userData) => {
        if (userData.email) email.value = userData.email
        if (userData.avatar) {
            avatar.value = userData.avatar
            avatarTimestamp.value = Date.now()
        }
        if (userData.is_admin!== undefined) { // 改为 is_admin 以匹配 API
            isAdmin.value = userData.is_admin
        }
        if (userData.admin_role) {
            adminRole.value = userData.admin_role
        }
        if (userData.is_superuser !== undefined) {
            isSuperuser.value = !!userData.is_superuser
        }
        isAuthenticated.value = true
    }

    const fetchUserProfile = async () => {
        try {
            // 使用自定义的 Axios 实例而非全局 axios
            const response = await instance.get('/users/profile/')
            
            profileData.value = response.data
            avatar.value = response.data.avatar
            avatarTimestamp.value = Date.now()
            localStorage.setItem('avatar', response.data.avatar)
            localStorage.setItem('avatarTs', avatarTimestamp.value)
            
            // 设置管理员状态和认证状态
            if (response.data.is_admin!== undefined) {
                isAdmin.value = response.data.is_admin  
            }
            if (response.data.admin_role) {
                adminRole.value = response.data.admin_role
            }
            if (response.data.is_superuser !== undefined) {
                isSuperuser.value = !!response.data.is_superuser
            }
            isAuthenticated.value = true
            
            return response.data
        } catch (error) {
            console.error('获取用户信息失败:', error)
            logout()
            throw error
        }
    }

    const clearUser = () => {
        avatar.value = null
        profileData.value = null
        avatarTimestamp.value = Date.now()
        localStorage.removeItem('avatar')
        localStorage.removeItem('avatarTs')
    }

    const verifyAdmin = async () => {
        try {
            if (!profileData.value) {
                await fetchUserProfile()
            }
            console.log('[UserStore] 验证管理员权限:', isAdmin.value)
            return isAdmin.value
        } catch (error) {
            logout()
            return false
        }
    }

    return {
        isAuthenticated,
        email,
        avatar,
        avatarTimestamp,
        profileData,
        isAdmin,
        adminRole,
        isSuperuser,
        logout,
        updateAvatar,
        updateUserInfo,
        fetchUserProfile,
        clearUser,
        verifyAdmin
    }
})