"use client"

import type { NavigationMode } from "@/types"
import { ChatInterface } from "@/components/chat-interface"
import { ContactDetailEditable } from "@/components/contact-detail-editable"
import { FilesTable } from "@/components/files-table"
import { SocialContent } from "@/components/social-content"
import { PluginsMarketplace } from "@/components/plugins-marketplace"
import { SettingsLLM } from "@/components/settings-llm"
import { useState } from "react"

interface MainContentProps {
  mode: NavigationMode
  selectedItem: string | null
  onItemSelect: (id: string) => void
}

export function MainContent({ mode, selectedItem, onItemSelect }: MainContentProps) {
  const [fileCategory, setFileCategory] = useState("files")
  const [socialCategory, setSocialCategory] = useState("my-circle")

  if (!selectedItem && mode !== "settings" && mode !== "plugins") {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="text-6xl mb-4">🤖</div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">欢迎使用 AI 协作平台</h2>
          <p className="text-gray-600">选择一个 AI 助手开始对话，或浏览其他功能</p>
        </div>
      </div>
    )
  }

  const renderContent = () => {
    switch (mode) {
      case "chat":
        return <ChatInterface selectedItem={selectedItem!} />
      case "contacts":
        return <ContactDetailEditable selectedItem={selectedItem!} />
      case "files":
        return <FilesTable category={fileCategory} />
      case "social":
        return <SocialContent category={socialCategory} />
      case "plugins":
        return <PluginsMarketplace selectedPlugin={selectedItem} onPluginSelect={onItemSelect} />
      case "settings":
        return <SettingsLLM />
      default:
        return <div className="p-8 text-gray-500">功能开发中...</div>
    }
  }

  return <div className="flex-1 flex flex-col bg-white">{renderContent()}</div>
}
