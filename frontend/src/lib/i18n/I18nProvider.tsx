'use client'

import { useEffect, useState } from 'react'
import { useI18nStore } from './client'
import { defaultLocale } from './config'

interface I18nProviderProps {
  children: React.ReactNode
}

export function I18nProvider({ children }: I18nProviderProps) {
  const { setLocale, locale, messages } = useI18nStore()
  const [forceRender, setForceRender] = useState(0)

  useEffect(() => {
    // 初始化加载默认语言的消息
    if (Object.keys(messages).length === 0) {
      setLocale(locale || defaultLocale)
    }
  }, [setLocale, locale, messages])

  useEffect(() => {
    // 监听语言变化事件，强制重新渲染
    const handleLanguageChange = () => {
      setForceRender(prev => prev + 1)
    }

    window.addEventListener('languageChanged', handleLanguageChange)
    return () => {
      window.removeEventListener('languageChanged', handleLanguageChange)
    }
  }, [])

  return <div key={forceRender}>{children}</div>
}