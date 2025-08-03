import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'
import { ThemeProvider } from 'next-themes'
import { I18nProvider } from '@/lib/i18n/I18nProvider'
import { generateMetadata } from '@/lib/seo/metadata'
import { generateJSONLD } from '@/lib/seo/metadata'
import Script from 'next/script'

const inter = Inter({
  variable: '--font-inter',
  subsets: ['latin'],
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({
  variable: '--font-jetbrains-mono',
  subsets: ['latin'],
  display: 'swap',
})

export const metadata: Metadata = generateMetadata()

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* JSON-LD 结构化数据 */}
        <Script
          id="jsonld"
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: generateJSONLD()
          }}
        />
        
        {/* 预连接外部资源 */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        
        {/* PWA相关 */}
        <link rel="manifest" href="/manifest.json" />
        <link rel="apple-touch-icon" href="/icons/apple-touch-icon.png" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="format-detection" content="telephone=no" />
      </head>
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} antialiased font-sans`}
        style={{
          fontFamily: 'var(--font-inter), system-ui, sans-serif',
        }}
      >
        <ThemeProvider
          attribute="data-theme"
          defaultTheme="light"
          enableSystem
          themes={['light', 'dark']}
          storageKey="connet-theme"
        >
          <I18nProvider>
            <div className="min-h-screen bg-[--theme-background-primary] text-[--theme-text-primary] transition-colors">
              {children}
            </div>
          </I18nProvider>
        </ThemeProvider>
        
        {/* 主题初始化脚本 */}
        <Script id="theme-init" strategy="beforeInteractive">
          {`
            (function() {
              const savedTheme = localStorage.getItem('connet-theme');
              const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
              const theme = savedTheme || (prefersDark ? 'dark' : 'light');
              document.documentElement.setAttribute('data-theme', theme);
            })();
          `}
        </Script>
      </body>
    </html>
  )
}
