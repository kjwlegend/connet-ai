import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware' // 可选中间件
import createAuthSlice from './slices/authSlice'
import { createSettingsSlice } from './slices/settingsSlice'
import { StoreState } from './types'

// 使用类型 StoreState 来创建 store
const useAppStore = create<StoreState>()(
  devtools(
    // 可选：用于 Redux DevTools 浏览器扩展
    persist(
      // 可选：用于将状态持久化到 localStorage
      (...a) => ({
        ...createAuthSlice(...a),
        ...createSettingsSlice(...a),
        // ...其他 slices
      }),
      {
        name: 'xiaoguang-next-gen', // 持久化存储的 key
        partialize: (state) => ({
          // 选择性持久化某些状态
          theme: state.theme,
          language: state.language,
          // token: state.token, // 例如持久化 token
        }),
      }
    )
  )
)

export default useAppStore
