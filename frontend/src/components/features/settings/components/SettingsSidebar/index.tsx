"use client"

import { cn } from "@/lib/utils"
import { useTheme } from "next-themes"
import { useTranslations } from "@/lib/i18n/client"
import { useRouter, usePathname } from "next/navigation"
import {
  Bot,
  User,
  Ticket,
  ShoppingBag,
  MessageSquareQuote,
  ChevronRight,
  Crown,
} from "lucide-react"

interface SettingsSidebarProps {
  selectedCategory?: string
  onCategorySelect?: (category: string) => void
}

export function SettingsSidebar({ selectedCategory, onCategorySelect }: SettingsSidebarProps) {
  const { theme } = useTheme()
  const t = useTranslations()
  const router = useRouter()
  const pathname = usePathname()

  // Extract category from pathname
  const currentCategory = pathname.split('/').pop() || 'llm'

  const settingsCategories = [
    {
      id: 'membership',
      name: t('settings.categories.membership'),
      icon: Crown,
      description: t('settings.categories.membershipDesc'),
      path: '/settings/membership'
    },
    {
      id: 'llm',
      name: t('settings.categories.llm'),
      icon: Bot,
      description: t('settings.categories.llmDesc'),
      path: '/settings/llm'
    },
    {
      id: 'account',
      name: t('settings.categories.account'),
      icon: User,
      description: t('settings.categories.accountDesc'),
      path: '/settings/account'
    },
    {
      id: 'invitation',
      name: t('settings.categories.invitation'),
      icon: Ticket,
      description: t('settings.categories.invitationDesc'),
      path: '/settings/invitation'
    },
    {
      id: 'orders',
      name: t('settings.categories.orders'),
      icon: ShoppingBag,
      description: t('settings.categories.ordersDesc'),
      path: '/settings/orders'
    },
    {
      id: 'prompt',
      name: t('settings.categories.prompt'),
      icon: MessageSquareQuote,
      description: t('settings.categories.promptDesc'),
      path: '/settings/prompt'
    },
  ]

  const handleCategoryClick = (category: typeof settingsCategories[0]) => {
    router.push(category.path)
    onCategorySelect?.(category.id)
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className={cn(
        "px-4 py-3 border-b",
        theme === 'dark' ? "border-gray-800" : "border-gray-200"
      )}>
        <h2 className={cn(
          "text-sm font-semibold",
          theme === 'dark' ? "text-gray-300" : "text-gray-700"
        )}>
          {t('settings.title')}
        </h2>
      </div>

      {/* Categories List */}
      <div className="flex-1 overflow-y-auto p-2">
        {settingsCategories.map((category) => {
          const Icon = category.icon
          const isSelected = currentCategory === category.id || selectedCategory === category.id

          return (
            <button
              key={category.id}
              onClick={() => handleCategoryClick(category)}
              className={cn(
                "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg mb-1",
                "transition-all duration-200",
                "group hover:bg-accent/50",
                isSelected 
                  ? theme === 'dark' 
                    ? "bg-gray-800 text-white" 
                    : "bg-gray-100 text-gray-900"
                  : theme === 'dark'
                    ? "text-gray-400 hover:text-gray-200"
                    : "text-gray-600 hover:text-gray-900"
              )}
            >
              <Icon className={cn(
                "h-5 w-5 flex-shrink-0",
                isSelected && "text-primary"
              )} />
              <div className="flex-1 text-left">
                <div className={cn(
                  "text-sm font-medium",
                  isSelected && "font-semibold"
                )}>
                  {category.name}
                </div>
                <div className={cn(
                  "text-xs mt-0.5",
                  theme === 'dark' ? "text-gray-500" : "text-gray-500"
                )}>
                  {category.description}
                </div>
              </div>
              <ChevronRight className={cn(
                "h-4 w-4 opacity-0 group-hover:opacity-100 transition-opacity",
                isSelected && "opacity-100"
              )} />
            </button>
          )
        })}
      </div>

      {/* Footer */}
      <div className={cn(
        "px-4 py-3 border-t",
        theme === 'dark' ? "border-gray-800" : "border-gray-200"
      )}>
        <div className={cn(
          "text-xs",
          theme === 'dark' ? "text-gray-500" : "text-gray-400"
        )}>
          {t('settings.version')}: 1.0.0
        </div>
      </div>
    </div>
  )
}

export default SettingsSidebar