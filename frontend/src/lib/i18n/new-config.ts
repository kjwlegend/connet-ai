import type { I18nConfig, LocaleInfo, I18nDesignTokens } from './types';

export const i18nConfig: I18nConfig = {
  defaultLocale: 'en',
  locales: ['en', 'zh-CN'],
};

export const localeInfo: Record<string, LocaleInfo> = {
  'en': {
    code: 'en',
    name: 'English',
    nativeName: 'English',
    direction: 'ltr',
    flag: '🇺🇸',
  },
  'zh-CN': {
    code: 'zh-CN',
    name: 'Chinese (Simplified)',
    nativeName: '简体中文',
    direction: 'ltr',
    flag: '🇨🇳',
  },
  'zh-TW': {
    code: 'zh-TW',
    name: 'Chinese (Traditional)',
    nativeName: '繁體中文',
    direction: 'ltr',
    flag: '🇹🇼',
  },
  'ja': {
    code: 'ja',
    name: 'Japanese',
    nativeName: '日本語',
    direction: 'ltr',
    flag: '🇯🇵',
  },
  'ko': {
    code: 'ko',
    name: 'Korean',
    nativeName: '한국어',
    direction: 'ltr',
    flag: '🇰🇷',
  },
};

export const i18nDesignTokens: I18nDesignTokens = {
  fontFamily: {
    'en': 'var(--font-family-primary)', // Inter
    'zh-CN': 'var(--font-family-chinese), var(--font-family-primary)', // PingFang SC, Inter
    'zh-TW': 'var(--font-family-chinese), var(--font-family-primary)',
    'ja': '"Hiragino Sans", "Yu Gothic", var(--font-family-primary)',
    'ko': '"Malgun Gothic", var(--font-family-primary)',
  },
  textDirection: {
    'en': 'ltr',
    'zh-CN': 'ltr',
    'zh-TW': 'ltr',
    'ja': 'ltr',
    'ko': 'ltr',
  },
  spacing: {
    'en': { text: 1, line: 1 },
    'zh-CN': { text: 1.05, line: 1.1 }, // 中文需要稍大的间距
    'zh-TW': { text: 1.05, line: 1.1 },
    'ja': { text: 1.02, line: 1.05 },
    'ko': { text: 1.02, line: 1.05 },
  },
};