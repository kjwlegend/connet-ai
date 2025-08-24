/**
 * Auth Business Hooks 入口文件
 * 统一导出所有认证相关的业务逻辑 hooks
 */

export { useAuthLogin } from './useAuthLogin'
export { useAuthRegister } from './useAuthRegister'
export { useAuthSession } from './useAuthSession'
export { useAuthOAuth } from './useAuthOAuth'
export { useAuthPassword } from './useAuthPassword'

// 类型导出
export type { User, UserPreferences } from '@/store/slices/auth/authSlice'