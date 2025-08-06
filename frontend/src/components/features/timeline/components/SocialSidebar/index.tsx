'use client'

import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { useTheme } from 'next-themes'
import { useTranslations } from '@/lib/i18n/client'
import { Users, Globe, User, Star, Hash } from 'lucide-react'

interface SocialSidebarProps {
  selectedCategory: string
  onCategorySelect: (category: string) => void
}

export function SocialSidebar({
  selectedCategory,
  onCategorySelect,
}: SocialSidebarProps) {
  const { theme } = useTheme()
  const t = useTranslations()

  const socialCategories = [
    {
      id: 'friends-circle',
      name: t('social.categories.friendsCircle'),
      count: 15,
      icon: Users,
      description: t('social.categories.friendsCircleDesc'),
    },
    {
      id: 'square',
      name: t('social.categories.square'),
      count: 99,
      icon: Globe,
      description: t('social.categories.squareDesc'),
    },
    {
      id: 'my-circle',
      name: t('social.categories.myCircle'),
      count: 5,
      icon: User,
      description: t('social.categories.myCircleDesc'),
    },
    {
      id: 'my-favorites',
      name: t('social.categories.myFavorites'),
      count: 12,
      icon: Star,
      description: t('social.categories.myFavoritesDesc'),
    },
  ]

  return (
    <div className="h-full flex flex-col bg-background overflow-hidden">
      <div
        className={cn(
          'p-3 border-b border-border/40',
          theme === 'dark' ? 'bg-card/30' : 'bg-muted/20'
        )}
      >
        <div className="flex items-center space-x-2 mb-3">
          <Hash className="h-4 w-4 text-primary" />
          <h3 className="font-medium text-foreground">{t('social.title')}</h3>
        </div>
        <div className="space-y-1">
          {socialCategories.map((category) => {
            const Icon = category.icon
            const isActive = selectedCategory === category.id

            return (
              <Button
                key={category.id}
                variant="ghost"
                className={cn(
                  'w-full justify-between text-left p-3 h-auto transition-all duration-200',
                  'hover:bg-accent/60 hover:text-accent-foreground',
                  isActive &&
                    'bg-primary/10 text-primary hover:bg-primary/15 border-l-2 border-primary'
                )}
                onClick={() => onCategorySelect(category.id)}
              >
                <div className="flex items-center space-x-2">
                  <Icon
                    className={cn(
                      'h-4 w-4',
                      isActive ? 'text-primary' : 'text-muted-foreground'
                    )}
                  />
                  <div>
                    <div className="text-sm font-medium">{category.name}</div>
                    <div className="text-xs text-muted-foreground/80">
                      {category.description}
                    </div>
                  </div>
                </div>
                <Badge
                  variant={isActive ? 'default' : 'secondary'}
                  className={cn(
                    'text-xs h-5 px-1.5',
                    isActive
                      ? 'bg-primary/20 text-primary'
                      : 'bg-muted text-muted-foreground'
                  )}
                >
                  {category.count > 99 ? '99+' : category.count}
                </Badge>
              </Button>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default SocialSidebar
