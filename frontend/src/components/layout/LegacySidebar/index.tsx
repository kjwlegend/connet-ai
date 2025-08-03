"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { MessageCircle, Users, FolderOpen, Star, Wrench, Settings, ChevronLeft, ChevronRight } from "lucide-react"
import type { NavigationMode } from "@/types"
import { cn } from "@/lib/utils"
import { useState } from "react"
import { ThemeToggle } from "@/components/ui/ThemeToggle"
import { LanguageToggle } from "@/components/ui/LanguageToggle"
import { useTranslations } from "@/lib/i18n/client"

interface LegacySidebarProps {
  currentMode: NavigationMode
  onModeChange: (mode: NavigationMode) => void
}

const navigationItems = [
  { id: "chat", translationKey: "navigation.chat", icon: MessageCircle },
  { id: "contacts", translationKey: "navigation.contacts", icon: Users },
  { id: "files", translationKey: "navigation.files", icon: FolderOpen },
  { id: "social", translationKey: "navigation.social", icon: Star },
  { id: "plugins", translationKey: "navigation.plugins", icon: Wrench },
  { id: "settings", translationKey: "navigation.settings", icon: Settings },
] as const

export function LegacySidebar({ currentMode, onModeChange }: LegacySidebarProps) {
  const [isExpanded, setIsExpanded] = useState(true)
  const t = useTranslations()

  return (
    <div
      className={cn("bg-gray-900 text-white flex flex-col transition-all duration-300 shadow-soft-lg", isExpanded ? "w-48" : "w-12")}
    >
      {/* Logo */}
      <div className="p-4 border-b border-gray-700/50">
        <div className="flex items-center justify-center">
          {isExpanded ? (
            <div className="text-lg font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Connet.AI
            </div>
          ) : (
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg shadow-soft flex items-center justify-center">
              <span className="text-white font-bold text-sm">C</span>
            </div>
          )}
        </div>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 p-3">
        <div className="space-y-2">
          {navigationItems.map((item) => {
            const Icon = item.icon
            const isActive = currentMode === item.id

            return (
              <Button
                key={item.id}
                variant="ghost"
                className={cn(
                  "w-full justify-start text-gray-300 hover:text-white hover:bg-gray-800/70 transition-smooth rounded-lg",
                  isActive && "bg-gray-800/90 text-white shadow-soft",
                  !isExpanded && "justify-center px-2",
                )}
                onClick={() => onModeChange(item.id as NavigationMode)}
              >
                <Icon className="h-5 w-5" />
                {isExpanded && <span className="ml-3">{t(item.translationKey)}</span>}
              </Button>
            )
          })}
        </div>
      </nav>

      {/* User Profile & Controls */}
      <div className="border-t border-gray-700">
        {isExpanded && (
          <div className="p-3">
            <div className="flex items-center space-x-3 mb-4 p-2 rounded-lg bg-gray-800/50 transition-smooth">
              <Avatar className="h-9 w-9 shadow-soft">
                <AvatarImage src="/placeholder.svg?height=36&width=36" />
                <AvatarFallback className="bg-gray-700 text-gray-200">{t('ui.user')}</AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate text-gray-100">{t('ui.username')}</div>
                <div className="text-xs text-gray-400 flex items-center">
                  <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                  {t('ui.online')}
                </div>
              </div>
            </div>
            
            {/* Theme and Language Toggle */}
            <div className="flex items-center justify-center space-x-2 mb-2">
              <ThemeToggle className="text-gray-400 hover:text-white transition-smooth" />
              <LanguageToggle className="text-gray-400 hover:text-white transition-smooth" />
            </div>
          </div>
        )}
        
        {/* Compact controls when collapsed */}
        {!isExpanded && (
          <div className="p-2 space-y-1">
            <ThemeToggle className="w-full text-gray-400 hover:text-white" />
            <LanguageToggle className="w-full text-gray-400 hover:text-white" />
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

export default LegacySidebar