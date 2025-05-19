'use client'
import { createI18nClient } from 'next-international/client'
import { i18nConfig } from './config'

export const {
  useI18n,
  useScopedI18n,
  I18nProviderClient, // 提供给根布局
  useChangeLocale,
  useCurrentLocale,
} = createI18nClient({
  en: () => import('./locales/en.json'),
  zh: () => import('./locales/zh.json'),
})
