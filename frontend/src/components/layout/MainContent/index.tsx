'use client'

import type { NavigationMode } from '@/types'
import { ChatInterface } from '@/components/features/chat/components/ChatInterface'
import { useState } from 'react'
import { useTheme } from 'next-themes'
import { cn } from '@/lib/utils'

import { FilesTable } from '@/components/features/files/components/FilesTable'
import { SocialContent } from '@/components/features/timeline/components/SocialContent'
import { PluginsMarketplace } from '@/components/features/plugins/components/PluginsMarketplace'
import { SettingsLLM } from '@/components/features/settings/components/SettingsLLM'
import { ContactDetailEditable } from '@/components/features/contacts/components/ContactDetailEditable'

interface MainContentProps {
  mode: NavigationMode
  selectedItem: string | null
  onItemSelect: (id: string) => void
}

export function MainContent({
  mode,
  selectedItem,
  onItemSelect,
}: MainContentProps) {
  const [fileCategory, setFileCategory] = useState('files')
  const [socialCategory, setSocialCategory] = useState('my-circle')
  const [selectedPlugin, setSelectedPlugin] = useState<string | null>(null)
  const { theme } = useTheme()

  // if (!selectedItem && mode !== 'settings' && mode !== 'plugins') {
  //   return (
  //     <div
  //       className={cn(
  //         'flex-1 flex items-center justify-center',
  //         theme === 'dark' ? 'bg-background' : 'bg-gray-50'
  //       )}
  //     >
  //       <div className="text-center">
  //         <div className="text-6xl mb-4">🤖</div>
  //         <h2
  //           className={cn(
  //             'text-2xl font-semibold mb-2',
  //             theme === 'dark' ? 'text-gray-100' : 'text-gray-900'
  //           )}
  //         >
  //           欢迎使用 AI 协作平台
  //         </h2>
  //         <p
  //           className={cn(theme === 'dark' ? 'text-gray-400' : 'text-gray-600')}
  //         >
  //           选择一个 AI 助手开始对话，或浏览其他功能
  //         </p>
  //       </div>
  //     </div>
  //   )
  // }

  const renderContent = () => {
    switch (mode) {
      case 'chat':
        return <ChatInterface selectedItem={selectedItem!} />
      case 'contacts':
        return <ContactDetailEditable selectedItem={selectedItem!} />
      case 'files':
        return <FilesTable category={fileCategory} />
      case 'social':
        return <SocialContent category={socialCategory} />
      case 'plugins':
        return (
          <PluginsMarketplace
            selectedPlugin={selectedPlugin}
            onPluginSelect={setSelectedPlugin}
          />
        )
      case 'settings':
        return <SettingsLLM />
      default:
        return (
          <div
            className={cn(
              'p-8',
              theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
            )}
          >
            功能开发中...
          </div>
        )
    }
  }

  return (
    <div
      className={cn(
        'flex-1 flex flex-col h-full',
        theme === 'dark' ? 'bg-background' : 'bg-white'
      )}
      style={{ minHeight: '100%' }}
    >
      {renderContent()}
    </div>
  )
}

export default MainContent
