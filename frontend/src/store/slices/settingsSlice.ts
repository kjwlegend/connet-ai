import { StateCreator } from 'zustand'
import { StoreState } from '../types' // 假设 StoreState 包含了所有 slice 的类型
import { i18nConfig } from '@/lib/i18n/config'

export type Theme = 'light' | 'dark' | 'system'
export type Language = 'en' | 'zh' // 根据你的支持列表

export interface SettingsState {
  theme: Theme
  language: string
}

export interface SettingsActions {
  setTheme: (theme: Theme) => void
  setLanguage: (language: Language) => void
}

// 使用 StateCreator 来创建 slice，并确保类型正确
export const createSettingsSlice: StateCreator<
  StoreState, // 完整的 store 类型
  [], // 中间件类型 (如果不用中间件就是空数组)
  [], // 中间件类型 (如果不用中间件就是空数组)
  SettingsState & SettingsActions // 这个 slice 的类型
> = (set) => ({
  theme: 'system', // 默认主题
  language: i18nConfig.defaultLocale, // 默认语言
  setTheme: (theme) => set(() => ({ theme })),
  setLanguage: (language) => set(() => ({ language })),
})
