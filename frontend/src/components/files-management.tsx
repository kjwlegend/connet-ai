"use client"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

const fileCategories = [
  { id: "files", name: "文件管理", count: 24 },
  { id: "knowledge", name: "知识库管理", count: 12 },
]

interface FilesManagementProps {
  selectedCategory: string
  onCategorySelect: (category: string) => void
}

export function FilesManagement({ selectedCategory, onCategorySelect }: FilesManagementProps) {
  return (
    <div>
      <div className="p-3 border-b border-gray-100">
        <h3 className="font-medium text-gray-900 mb-3">文件分类</h3>
        <div className="space-y-1">
          {fileCategories.map((category) => (
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
              <span className="text-xs text-gray-500">{category.count}</span>
            </Button>
          ))}
        </div>
      </div>
    </div>
  )
}
