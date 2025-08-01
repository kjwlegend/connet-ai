"use client"

import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Search } from "lucide-react"
import type { NavigationMode } from "@/types"
import { ChatList } from "@/components/chat-list"
import { ContactsList } from "@/components/contacts-list"
import { FilesManagement } from "@/components/files-management"
import { SocialSidebar } from "@/components/social-sidebar"
import { PluginsConfigured } from "@/components/plugins-configured"
import { useState } from "react"

interface MiddlePanelProps {
  mode: NavigationMode
  selectedItem: string | null
  onItemSelect: (id: string) => void
}

export function MiddlePanel({ mode, selectedItem, onItemSelect }: MiddlePanelProps) {
  const [fileCategory, setFileCategory] = useState("files")
  const [socialCategory, setSocialCategory] = useState("my-circle")

  const renderContent = () => {
    switch (mode) {
      case "chat":
        return <ChatList selectedItem={selectedItem} onItemSelect={onItemSelect} />
      case "contacts":
        return <ContactsList selectedItem={selectedItem} onItemSelect={onItemSelect} />
      case "files":
        return <FilesManagement selectedCategory={fileCategory} onCategorySelect={setFileCategory} />
      case "social":
        return <SocialSidebar selectedCategory={socialCategory} onCategorySelect={setSocialCategory} />
      case "plugins":
        return <PluginsConfigured selectedPlugin={selectedItem} onPluginSelect={onItemSelect} />
      case "settings":
        return <div className="p-4 text-gray-500 text-center">选择设置选项</div>
      default:
        return <div className="p-4 text-gray-500">选择一个功能开始使用</div>
    }
  }

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Search Bar */}
      <div className="p-3 border-b border-gray-200">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input placeholder="搜索..." className="pl-10" />
        </div>
      </div>

      {/* Content List */}
      <ScrollArea className="flex-1">{renderContent()}</ScrollArea>
    </div>
  )
}
