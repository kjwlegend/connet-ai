'use client'

import { useEffect } from 'react'
import { useI18nStore } from './client'
import { defaultLocale } from './config'

interface I18nProviderProps {
  children: React.ReactNode
}

export function I18nProvider({ children }: I18nProviderProps) {
  const { setLocale, locale, messages } = useI18nStore()

  useEffect(() => {
    // 初始化加载默认语言的消息
    if (Object.keys(messages).length === 0) {
      setLocale(locale || defaultLocale)
    }
  }, [setLocale, locale, messages])

  return <>{children}</>
}