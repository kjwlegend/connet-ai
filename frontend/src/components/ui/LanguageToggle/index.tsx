'use client'

import { Button } from '@/components/ui/button'
import { Globe } from 'lucide-react'
import { useLocale, useTranslations, useSetLocale } from '@/lib/i18n/client'
import { localeInfo, type Locale } from '@/lib/i18n/config'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'

interface LanguageToggleProps {
  className?: string
  variant?: 'default' | 'ghost' | 'outline'
  size?: 'default' | 'sm' | 'lg' | 'icon'
}

export function LanguageToggle({
  className,
  variant = 'ghost',
  size = 'icon',
}: LanguageToggleProps) {
  const locale = useLocale()
  const t = useTranslations()
  const setLocale = useSetLocale()

  const currentLocaleInfo = localeInfo[locale] || localeInfo['en']

  const switchLocale = async (newLocale: Locale) => {
    if (newLocale === locale) return
    await setLocale(newLocale)
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant={variant}
          size={size}
          className={cn('transition-colors', className)}
          aria-label={t('language.toggle')}
        >
          {size === 'icon' ? (
            <Globe className="h-4 w-4" />
          ) : (
            <>
              <span className="mr-2">{currentLocaleInfo.flag}</span>
              <span className="hidden sm:inline">
                {currentLocaleInfo.nativeName}
              </span>
            </>
          )}
          <span className="sr-only">{t('language.toggle')}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48 bg-gray-50">
        {Object.values(localeInfo).map((localeItem) => (
          <DropdownMenuItem
            key={localeItem.code}
            onClick={() => switchLocale(localeItem.code)}
            className={cn(
              'flex items-center gap-3 cursor-pointer',
              locale === localeItem.code && 'bg-accent'
            )}
          >
            <span className="text-lg">{localeItem.flag}</span>
            <div className="flex flex-col">
              <span className="font-medium">{localeItem.nativeName}</span>
              <span className="text-xs text-muted-foreground">
                {localeItem.name}
              </span>
            </div>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

// 简单的语言切换按钮（只显示当前语言标志）
export function SimpleLanguageToggle({ className }: { className?: string }) {
  const locale = useLocale()
  const t = useTranslations()
  const setLocale = useSetLocale()

  const currentLocaleInfo = localeInfo[locale] || localeInfo['en']

  const toggleLanguage = async () => {
    // 在支持的语言之间切换
    const nextLocale: Locale = locale === 'en' ? 'zh' : 'en'
    await setLocale(nextLocale)
  }

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={toggleLanguage}
      className={cn('transition-colors ', className)}
      aria-label={t('language.toggle')}
    >
      <span className="text-sm">{currentLocaleInfo.flag}</span>
      <span className="sr-only">{t('language.toggle')}</span>
    </Button>
  )
}
