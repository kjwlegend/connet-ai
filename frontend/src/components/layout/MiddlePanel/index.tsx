"use client"

import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Search } from "lucide-react"
import type { NavigationMode } from "@/types"
import { ConversationList } from "@/components/features/chat/components/ConversationList"
import { ContactList } from "@/components/features/contacts/components/ContactList"
import { useState } from "react"
import { useTheme } from "next-themes"
import { cn } from "@/lib/utils"

import { FilesManagement } from "@/components/features/files/components/FilesManagement"
import { SocialSidebar } from "@/components/features/timeline/components/SocialSidebar"
import { PluginsConfigured } from "@/components/features/plugins/components/PluginsConfigured"

interface MiddlePanelProps {
  mode: NavigationMode
  selectedItem: string | null
  onItemSelect: (id: string) => void
}

export function MiddlePanel({ mode, selectedItem, onItemSelect }: MiddlePanelProps) {
  const [fileCategory, setFileCategory] = useState("files")
  const [socialCategory, setSocialCategory] = useState("my-circle")
  const { theme } = useTheme()

  const renderContent = () => {
    switch (mode) {
      case "chat":
        return <ConversationList selectedItem={selectedItem} onItemSelect={onItemSelect} />
      case "contacts":
        return <ContactList selectedItem={selectedItem} onItemSelect={onItemSelect} />
      case "files":
        return <FilesManagement selectedCategory={fileCategory} onCategorySelect={setFileCategory} />
      case "social":
        return <SocialSidebar selectedCategory={socialCategory} onCategorySelect={setSocialCategory} />
      case "plugins":
        return <PluginsConfigured selectedPlugin={selectedItem} onPluginSelect={onItemSelect} />
      case "settings":
        return <div className={cn(
          "p-4 text-center",
          theme === 'dark' ? "text-gray-400" : "text-gray-500"
        )}>选择设置选项</div>
      default:
        return <div className={cn(
          "p-4",
          theme === 'dark' ? "text-gray-400" : "text-gray-500"
        )}>选择一个功能开始使用</div>
    }
  }

  return (
    <div className={cn(
      "w-64 border-r flex flex-col",
      theme === 'dark' 
        ? "bg-card border-border" 
        : "bg-white border-gray-200"
    )}>
      {/* Search Bar */}
      <div className={cn(
        "p-3 border-b",
        theme === 'dark' ? "border-border" : "border-gray-200"
      )}>
        <div className="relative">
          <Search className={cn(
            "absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4",
            theme === 'dark' ? "text-gray-500" : "text-gray-400"
          )} />
          <Input placeholder="搜索..." className="pl-10" />
        </div>
      </div>

      {/* Content List */}
      <ScrollArea className="flex-1">{renderContent()}</ScrollArea>
    </div>
  )
}

export default MiddlePanel