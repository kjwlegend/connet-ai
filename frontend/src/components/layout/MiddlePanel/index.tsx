'use client'

import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Search } from 'lucide-react'
import type { NavigationMode } from '@/types'
import { ConversationList } from '@/components/features/chat/components/ConversationList'
import { ContactList } from '@/components/features/contacts/components/ContactList'
import { useState } from 'react'
import { useTheme } from 'next-themes'
import { cn } from '@/lib/utils'

import { FilesManagement } from '@/components/features/files/components/FilesManagement'
import { SocialSidebar } from '@/components/features/timeline/components/SocialSidebar'
import { PluginsConfigured } from '@/components/features/plugins/components/PluginsConfigured'
import { SettingsSidebar } from '@/components/features/settings/components/SettingsSidebar'

interface MiddlePanelProps {
  mode: NavigationMode
  selectedItem: string | null
  onItemSelect: (id: string) => void
}

export function MiddlePanel({
  mode,
  selectedItem,
  onItemSelect,
}: MiddlePanelProps) {
  const [fileCategory, setFileCategory] = useState('files')
  const [socialCategory, setSocialCategory] = useState('my-circle')
  const [searchQuery, setSearchQuery] = useState('')
  const { theme } = useTheme()

  const renderContent = () => {
    switch (mode) {
      case 'chat':
        return (
          <ConversationList
            selectedItem={selectedItem}
            onItemSelect={onItemSelect}
          />
        )
      case 'contacts':
        return (
          <ContactList
            selectedItem={selectedItem}
            onItemSelect={onItemSelect}
            searchQuery={searchQuery}
          />
        )
      case 'files':
        return (
          <FilesManagement
            selectedCategory={fileCategory}
            onCategorySelect={setFileCategory}
          />
        )
      case 'social':
        return (
          <SocialSidebar
            selectedCategory={socialCategory}
            onCategorySelect={setSocialCategory}
          />
        )
      case 'plugins':
        return (
          <PluginsConfigured
            selectedPlugin={selectedItem}
            onPluginSelect={onItemSelect}
          />
        )
      case 'settings':
        return (
          <SettingsSidebar
            selectedCategory={selectedItem || undefined}
            onCategorySelect={onItemSelect}
          />
        )
      default:
        return (
          <div
            className={cn(
              'p-4',
              theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
            )}
          >
            选择一个功能开始使用
          </div>
        )
    }
  }

  const getSearchPlaceholder = () => {
    switch (mode) {
      case 'chat':
        return '搜索对话...'
      case 'contacts':
        return '搜索联系人...'
      case 'files':
        return '搜索文件...'
      case 'social':
        return '搜索动态...'
      case 'plugins':
        return '搜索插件...'
      default:
        return '搜索...'
    }
  }

  return (
    <div
      className={cn(
        'w-64 border-r flex flex-col',
        theme === 'dark' ? 'bg-card border-border' : 'bg-white border-gray-200'
      )}
    >
      {/* Search Bar */}
      <div
        className={cn(
          'p-3 border-b',
          theme === 'dark' ? 'border-border' : 'border-gray-200'
        )}
      ></div>

      {/* Content List */}
      <ScrollArea className="flex-1">{renderContent()}</ScrollArea>
    </div>
  )
}

export default MiddlePanel
