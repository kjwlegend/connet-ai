export const i18nConfig = {
  locales: ['en', 'zh'],
  defaultLocale: 'en',
  // prefixDefault: false, // 可选：是否给默认语言也加上路径前缀 (e.g., /en/about)
}

export type Locale = (typeof i18nConfig)['locales'][number]
