import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'
import { ThemeProvider } from 'next-themes'
import { I18nProvider } from '@/lib/i18n/I18nProvider'
import { AuthProvider } from '@/components/auth/AuthProvider'
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
          attribute="class"
          defaultTheme="system"
          enableSystem
          themes={['light', 'dark', 'system']}
          storageKey="connet-theme"
          disableTransitionOnChange={false}
        >
          <I18nProvider>
            <AuthProvider>
              <div className="min-h-screen bg-background text-foreground transition-colors">
                {children}
              </div>
            </AuthProvider>
          </I18nProvider>
        </ThemeProvider>
        
        {/* 主题初始化脚本 */}
        <Script id="theme-init" strategy="beforeInteractive">
          {`
            (function() {
              const savedTheme = localStorage.getItem('connet-theme');
              const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
              let theme = savedTheme || 'system';
              
              if (theme === 'system') {
                theme = prefersDark ? 'dark' : 'light';
              }
              
              document.documentElement.classList.toggle('dark', theme === 'dark');
            })();
          `}
        </Script>
      </body>
    </html>
  )
}
