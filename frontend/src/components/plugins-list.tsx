"use client"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Star, Download, Settings } from "lucide-react"
import { cn } from "@/lib/utils"
import type { Plugin } from "@/types"

const mockPlugins: Plugin[] = [
  {
    id: "plugin-1",
    name: "代码生成器",
    description: "基于需求自动生成高质量代码，支持多种编程语言",
    icon: "🔧",
    category: "开发工具",
    installed: true,
    rating: 4.8,
  },
  {
    id: "plugin-2",
    name: "设计素材库",
    description: "海量设计素材和模板，一键应用到你的项目中",
    icon: "🎨",
    category: "设计工具",
    installed: true,
    rating: 4.6,
  },
  {
    id: "plugin-3",
    name: "数据可视化",
    description: "将复杂数据转换为直观的图表和可视化界面",
    icon: "📊",
    category: "数据工具",
    installed: false,
    rating: 4.9,
  },
  {
    id: "plugin-4",
    name: "文档生成器",
    description: "自动生成技术文档、API文档和用户手册",
    icon: "📝",
    category: "文档工具",
    installed: false,
    rating: 4.7,
  },
  {
    id: "plugin-5",
    name: "项目管理",
    description: "任务分配、进度跟踪和团队协作的完整解决方案",
    icon: "📋",
    category: "效率工具",
    installed: true,
    rating: 4.5,
  },
]

const categories = ["全部", "已安装", "开发工具", "设计工具", "数据工具", "文档工具", "效率工具"]

interface PluginsListProps {
  selectedItem: string | null
  onItemSelect: (id: string) => void
}

export function PluginsList({ selectedItem, onItemSelect }: PluginsListProps) {
  return (
    <div>
      {/* Category Filter */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <Button key={category} variant="outline" size="sm" className="text-xs bg-transparent">
              {category}
            </Button>
          ))}
        </div>
      </div>

      {/* Plugins List */}
      <div className="divide-y divide-gray-100">
        {mockPlugins.map((plugin) => (
          <div
            key={plugin.id}
            className={cn(
              "p-4 hover:bg-gray-50 cursor-pointer transition-colors",
              selectedItem === plugin.id && "bg-blue-50 border-r-2 border-blue-500",
            )}
            onClick={() => onItemSelect(plugin.id)}
          >
            <div className="flex items-start space-x-3">
              <div className="shrink-0">
                <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center text-2xl">
                  {plugin.icon}
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium text-gray-900">{plugin.name}</h3>
                  <div className="flex items-center space-x-1">
                    <Star className="h-4 w-4 text-yellow-400 fill-current" />
                    <span className="text-sm text-gray-600">{plugin.rating}</span>
                  </div>
                </div>
                <p className="text-sm text-gray-600 mt-1 line-clamp-2">{plugin.description}</p>
                <div className="flex items-center justify-between mt-3">
                  <Badge variant="secondary" className="text-xs">
                    {plugin.category}
                  </Badge>
                  <div className="flex space-x-2">
                    {plugin.installed ? (
                      <Button size="sm" variant="outline">
                        <Settings className="h-4 w-4 mr-1" />
                        配置
                      </Button>
                    ) : (
                      <Button size="sm">
                        <Download className="h-4 w-4 mr-1" />
                        安装
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
