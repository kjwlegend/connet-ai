'use client'

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { defaultLocale, type Locale } from './config'

// 动态导入语言文件
const loadMessages = async (locale: Locale) => {
  try {
    const messages = await import(`./messages/${locale}.json`)
    return messages.default
  } catch (error) {
    console.warn(`Failed to load messages for locale: ${locale}, falling back to default`)
    const fallbackMessages = await import(`./messages/${defaultLocale}.json`)
    return fallbackMessages.default
  }
}

// Zustand store for i18n state
interface I18nStore {
  locale: Locale
  messages: Record<string, any>
  isLoading: boolean
  setLocale: (locale: Locale) => Promise<void>
  t: (key: string, params?: Record<string, string | number>) => string
}

export const useI18nStore = create<I18nStore>()(
  persist(
    (set, get) => ({
      locale: defaultLocale,
      messages: {},
      isLoading: false,
      
      setLocale: async (locale: Locale) => {
        set({ isLoading: true })
        try {
          const messages = await loadMessages(locale)
          set({ locale, messages, isLoading: false })
        } catch (error) {
          console.error('Failed to set locale:', error)
          set({ isLoading: false })
        }
      },
      
      t: (key: string, params?: Record<string, string | number>) => {
        const { messages } = get()
        const keys = key.split('.')
        let value: any = messages
        
        for (const k of keys) {
          if (value && typeof value === 'object' && k in value) {
            value = value[k]
          } else {
            return key // 返回 key 作为fallback
          }
        }
        
        if (typeof value !== 'string') {
          return key
        }
        
        // 简单的参数替换
        if (params) {
          return value.replace(/\{(\w+)\}/g, (match, paramKey) => {
            return params[paramKey]?.toString() || match
          })
        }
        
        return value
      },
    }),
    {
      name: 'i18n-storage',
      partialize: (state) => ({ locale: state.locale }),
    }
  )
)

// 便捷的 hooks
export const useLocale = () => useI18nStore((state) => state.locale)
export const useTranslations = () => useI18nStore((state) => state.t)
export const useSetLocale = () => useI18nStore((state) => state.setLocale)
export const useI18nLoading = () => useI18nStore((state) => state.isLoading)