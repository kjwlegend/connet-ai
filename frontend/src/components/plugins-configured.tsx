"use client"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Settings } from "lucide-react"
import { cn } from "@/lib/utils"

const configuredPlugins = [
  {
    id: "plugin-1",
    name: "代码生成器",
    icon: "🔧",
    status: "configured",
    description: "AI代码生成工具",
  },
  {
    id: "plugin-2",
    name: "设计素材库",
    icon: "🎨",
    status: "configured",
    description: "设计资源管理",
  },
  {
    id: "plugin-3",
    name: "项目管理",
    icon: "📋",
    status: "configured",
    description: "任务协作工具",
  },
  {
    id: "plugin-4",
    name: "数据分析",
    icon: "📊",
    status: "configured",
    description: "数据可视化工具",
  },
]

interface PluginsConfiguredProps {
  selectedPlugin: string | null
  onPluginSelect: (id: string) => void
}

export function PluginsConfigured({ selectedPlugin, onPluginSelect }: PluginsConfiguredProps) {
  return (
    <div>
      <div className="p-3 border-b border-gray-100">
        <h3 className="font-medium text-gray-900 mb-1">已配置插件</h3>
        <p className="text-xs text-gray-500">点击插件进行配置</p>
      </div>

      <div className="divide-y divide-gray-100">
        {configuredPlugins.map((plugin) => (
          <div
            key={plugin.id}
            className={cn(
              "p-3 hover:bg-gray-50 cursor-pointer transition-colors",
              selectedPlugin === plugin.id && "bg-blue-50 border-r-2 border-blue-500",
            )}
            onClick={() => onPluginSelect(plugin.id)}
          >
            <div className="flex items-center space-x-3">
              <div className="text-xl">{plugin.icon}</div>
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-sm">{plugin.name}</h3>
                <p className="text-xs text-gray-500 truncate">{plugin.description}</p>
                <Badge variant="secondary" className="text-xs mt-1">
                  已配置
                </Badge>
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
