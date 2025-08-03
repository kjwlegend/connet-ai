'use client'

import { useTranslations, useLocale } from '@/lib/i18n/client'
import { LanguageToggle } from '@/components/ui/LanguageToggle'

export default function TestI18nPage() {
  const t = useTranslations()
  const locale = useLocale()

  return (
    <div className="p-8 space-y-6">
      <h1 className="text-2xl font-bold">I18n Test Page (Client-side)</h1>
      
      <div className="space-y-2">
        <p><strong>Current Locale:</strong> {locale}</p>
        <p><strong>App Name:</strong> {t('app.name')}</p>
        <p><strong>App Tagline:</strong> {t('app.tagline')}</p>
        <p><strong>App Description:</strong> {t('app.description')}</p>
      </div>

      <div className="space-y-2">
        <h2 className="text-xl font-semibold">Navigation</h2>
        <ul className="space-y-1">
          <li>Chat: {t('navigation.chat')}</li>
          <li>Contacts: {t('navigation.contacts')}</li>
          <li>Files: {t('navigation.files')}</li>
          <li>Timeline: {t('navigation.social')}</li>
          <li>Plugins: {t('navigation.plugins')}</li>
          <li>Settings: {t('navigation.settings')}</li>
        </ul>
      </div>

      <div className="space-y-2">
        <h2 className="text-xl font-semibold">Language Toggle</h2>
        <LanguageToggle />
      </div>

      <div className="space-y-2">
        <h2 className="text-xl font-semibold">UI Elements</h2>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-blue-500 text-white rounded">
            {t('ui.save')}
          </button>
          <button className="px-4 py-2 bg-gray-500 text-white rounded">
            {t('ui.cancel')}
          </button>
        </div>
      </div>
      
      <div className="mt-8">
        <a href="/" className="text-blue-500 underline">
          Back to Home
        </a>
      </div>
    </div>
  )
}