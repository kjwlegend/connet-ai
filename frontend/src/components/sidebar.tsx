"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { MessageCircle, Users, FolderOpen, Star, Wrench, Settings, ChevronLeft, ChevronRight } from "lucide-react"
import type { NavigationMode } from "@/types"
import { cn } from "@/lib/utils"
import { useState } from "react"

interface SidebarProps {
  currentMode: NavigationMode
  onModeChange: (mode: NavigationMode) => void
}

const navigationItems = [
  { id: "chat", label: "对话", icon: MessageCircle },
  { id: "contacts", label: "联系人", icon: Users },
  { id: "files", label: "文件", icon: FolderOpen },
  { id: "social", label: "朋友圈", icon: Star },
  { id: "plugins", label: "工具插件", icon: Wrench },
  { id: "settings", label: "设置", icon: Settings },
] as const

export function Sidebar({ currentMode, onModeChange }: SidebarProps) {
  const [isExpanded, setIsExpanded] = useState(true)

  return (
    <div
      className={cn("bg-gray-900 text-white flex flex-col transition-all duration-300", isExpanded ? "w-48" : "w-12")}
    >
      {/* Logo */}
      <div className="p-3 border-b border-gray-700">
        <div className="flex items-center justify-center">
          {isExpanded ? (
            <div className="text-lg font-bold">AI Platform</div>
          ) : (
            <div className="w-6 h-6 bg-blue-500 rounded"></div>
          )}
        </div>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 p-2">
        <div className="space-y-1">
          {navigationItems.map((item) => {
            const Icon = item.icon
            const isActive = currentMode === item.id

            return (
              <Button
                key={item.id}
                variant="ghost"
                className={cn(
                  "w-full justify-start text-gray-300 hover:text-white hover:bg-gray-800",
                  isActive && "bg-gray-800 text-white",
                  !isExpanded && "justify-center px-2",
                )}
                onClick={() => onModeChange(item.id as NavigationMode)}
              >
                <Icon className="h-5 w-5" />
                {isExpanded && <span className="ml-3">{item.label}</span>}
              </Button>
            )
          })}
        </div>
      </nav>

      {/* User Profile & Collapse Button */}
      <div className="border-t border-gray-700">
        {isExpanded && (
          <div className="p-3">
            <div className="flex items-center space-x-3">
              <Avatar className="h-8 w-8">
                <AvatarImage src="/placeholder.svg?height=32&width=32" />
                <AvatarFallback>用户</AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate">用户名</div>
                <div className="text-xs text-gray-400">在线</div>
              </div>
            </div>
          </div>
        )}
        <div className="p-2">
          <Button
            variant="ghost"
            size="sm"
            className="w-full text-gray-400 hover:text-white"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </Button>
        </div>
      </div>
    </div>
  )
}
