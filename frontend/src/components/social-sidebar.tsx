"use client"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

const socialCategories = [
  { id: "my-circle", name: "我的圈子", count: 5 },
  { id: "my-friends", name: "我的好友", count: 12 },
  { id: "plaza", name: "广场", count: 99 },
]

interface SocialSidebarProps {
  selectedCategory: string
  onCategorySelect: (category: string) => void
}

export function SocialSidebar({ selectedCategory, onCategorySelect }: SocialSidebarProps) {
  return (
    <div>
      <div className="p-3 border-b border-gray-100">
        <h3 className="font-medium text-gray-900 mb-3">朋友圈</h3>
        <div className="space-y-1">
          {socialCategories.map((category) => (
            <Button
              key={category.id}
              variant="ghost"
              className={cn(
                "w-full justify-between text-left",
                selectedCategory === category.id && "bg-blue-50 text-blue-600",
              )}
              onClick={() => onCategorySelect(category.id)}
            >
              <span>{category.name}</span>
              <Badge variant="secondary" className="text-xs">
                {category.count > 99 ? "99+" : category.count}
              </Badge>
            </Button>
          ))}
        </div>
      </div>
    </div>
  )
}
