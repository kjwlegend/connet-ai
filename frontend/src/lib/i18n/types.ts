export type Locale = 'en' | 'zh-CN' | 'zh-TW' | 'ja' | 'ko';

export interface I18nConfig {
  defaultLocale: Locale;
  locales: Locale[];
}

export interface LocaleInfo {
  code: Locale;
  name: string;
  nativeName: string;
  direction: 'ltr' | 'rtl';
  flag: string;
}

export interface I18nDesignTokens {
  fontFamily: {
    [locale: string]: string;
  };
  textDirection: {
    [locale: string]: 'ltr' | 'rtl';
  };
  spacing: {
    [locale: string]: {
      text: number; // 文字间距调整
      line: number; // 行间距调整
    };
  };
}