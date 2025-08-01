"use client"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Settings } from "lucide-react"
import { cn } from "@/lib/utils"
import type { Plugin } from "@/types"

const mockPlugins: Plugin[] = [
  {
    id: "plugin-1",
    name: "代码生成器",
    description: "基于需求自动生成高质量代码",
    icon: "🔧",
    category: "开发工具",
    installed: true,
    rating: 4.8,
  },
  {
    id: "plugin-2",
    name: "设计素材库",
    description: "海量设计素材和模板",
    icon: "🎨",
    category: "设计工具",
    installed: true,
    rating: 4.6,
  },
  {
    id: "plugin-3",
    name: "数据可视化",
    description: "将数据转换为直观图表",
    icon: "📊",
    category: "数据工具",
    installed: false,
    rating: 4.9,
  },
  {
    id: "plugin-4",
    name: "文档生成器",
    description: "自动生成技术文档",
    icon: "📝",
    category: "文档工具",
    installed: false,
    rating: 4.7,
  },
]

interface PluginsListSimpleProps {
  selectedItem: string | null
  onItemSelect: (id: string) => void
}

export function PluginsListSimple({ selectedItem, onItemSelect }: PluginsListSimpleProps) {
  return (
    <div>
      {/* Filter */}
      <div className="p-3 border-b border-gray-100">
        <div className="flex space-x-2">
          <Button variant="outline" size="sm" className="text-xs bg-transparent">
            全部
          </Button>
          <Button variant="outline" size="sm" className="text-xs bg-transparent">
            已安装
          </Button>
        </div>
      </div>

      {/* Plugins List */}
      <div className="divide-y divide-gray-100">
        {mockPlugins.map((plugin) => (
          <div
            key={plugin.id}
            className={cn(
              "p-3 hover:bg-gray-50 cursor-pointer transition-colors",
              selectedItem === plugin.id && "bg-blue-50 border-r-2 border-blue-500",
            )}
            onClick={() => onItemSelect(plugin.id)}
          >
            <div className="flex items-center space-x-3">
              <div className="text-2xl">{plugin.icon}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2">
                  <h3 className="font-medium text-sm">{plugin.name}</h3>
                  {plugin.installed && (
                    <Badge variant="secondary" className="text-xs">
                      已安装
                    </Badge>
                  )}
                </div>
                <p className="text-xs text-gray-600 truncate">{plugin.description}</p>
              </div>
              <Button size="sm" variant="ghost" className="p-1">
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
