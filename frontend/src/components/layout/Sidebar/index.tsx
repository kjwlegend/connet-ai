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
import { useTheme } from "next-themes"
import { useRouter, usePathname } from "next/navigation"

interface SidebarProps {
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

export function Sidebar({ currentMode, onModeChange }: SidebarProps) {
  const [isExpanded, setIsExpanded] = useState(true)
  const t = useTranslations()
  const { theme } = useTheme()
  const router = useRouter()
  const pathname = usePathname()

  const handleNavigation = (mode: NavigationMode) => {
    onModeChange(mode)
    router.push(`/${mode}`)
  }

  return (
    <div
      className={cn(
        "flex flex-col transition-all duration-300 shadow-soft-lg",
        theme === 'dark' 
          ? "bg-gray-900 text-white" 
          : "bg-white text-gray-900 border-r border-gray-200",
        isExpanded ? "w-48" : "w-12"
      )}
    >
      {/* Logo */}
      <div className={cn(
        "p-4 border-b",
        theme === 'dark' 
          ? "border-gray-700/50" 
          : "border-gray-200/50"
      )}>
        <div className="flex items-center justify-center">
          {isExpanded ? (
            <div className="text-lg font-bold bg-linear-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Connet.AI
            </div>
          ) : (
            <div className="w-8 h-8 bg-linear-to-br from-blue-500 to-purple-500 rounded-lg shadow-soft flex items-center justify-center">
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
                  "w-full justify-start transition-smooth rounded-lg",
                  theme === 'dark' 
                    ? "text-gray-300 hover:text-white hover:bg-gray-800/70" 
                    : "text-gray-600 hover:text-gray-900 hover:bg-gray-100/70",
                  isActive && (theme === 'dark' 
                    ? "bg-gray-800/90 text-white shadow-soft" 
                    : "bg-gray-100/90 text-gray-900 shadow-soft"),
                  !isExpanded && "justify-center px-2",
                )}
                onClick={() => handleNavigation(item.id as NavigationMode)}
              >
                <Icon className="h-5 w-5" />
                {isExpanded && <span className="ml-3">{t(item.translationKey)}</span>}
              </Button>
            )
          })}
        </div>
      </nav>

      {/* User Profile & Controls */}
      <div className={cn(
        "border-t",
        theme === 'dark' 
          ? "border-gray-700" 
          : "border-gray-200"
      )}>
        {isExpanded && (
          <div className="p-3">
            <div className={cn(
              "flex items-center space-x-3 mb-4 p-2 rounded-lg transition-smooth",
              theme === 'dark' 
                ? "bg-gray-800/50" 
                : "bg-gray-100/50"
            )}>
              <Avatar className="h-9 w-9 shadow-soft">
                <AvatarImage src="/placeholder.svg?height=36&width=36" />
                <AvatarFallback className={cn(
                  theme === 'dark' 
                    ? "bg-gray-700 text-gray-200" 
                    : "bg-gray-200 text-gray-700"
                )}>{t('ui.user')}</AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <div className={cn(
                  "text-sm font-medium truncate",
                  theme === 'dark' 
                    ? "text-gray-100" 
                    : "text-gray-800"
                )}>{t('ui.username')}</div>
                <div className={cn(
                  "text-xs flex items-center",
                  theme === 'dark' 
                    ? "text-gray-400" 
                    : "text-gray-500"
                )}>
                  <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                  {t('ui.online')}
                </div>
              </div>
            </div>
            
            {/* Theme and Language Toggle */}
            <div className="flex items-center justify-center space-x-2 mb-2">
              <ThemeToggle className={cn(
                "transition-smooth",
                theme === 'dark' 
                  ? "text-gray-400 hover:text-white" 
                  : "text-gray-500 hover:text-gray-900"
              )} />
              <LanguageToggle className={cn(
                "transition-smooth",
                theme === 'dark' 
                  ? "text-gray-400 hover:text-white" 
                  : "text-gray-500 hover:text-gray-900"
              )} />
            </div>
          </div>
        )}
        
        {/* Compact controls when collapsed */}
        {!isExpanded && (
          <div className="p-2 space-y-1">
            <ThemeToggle className={cn(
              "w-full",
              theme === 'dark' 
                ? "text-gray-400 hover:text-white" 
                : "text-gray-500 hover:text-gray-900"
            )} />
            <LanguageToggle className={cn(
              "w-full",
              theme === 'dark' 
                ? "text-gray-400 hover:text-white" 
                : "text-gray-500 hover:text-gray-900"
            )} />
          </div>
        )}
        
        <div className="p-2">
          <Button
            variant="ghost"
            size="sm"
            className={cn(
              "w-full",
              theme === 'dark' 
                ? "text-gray-400 hover:text-white" 
                : "text-gray-500 hover:text-gray-900"
            )}
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </Button>
        </div>
      </div>
    </div>
  )
}

export default Sidebar