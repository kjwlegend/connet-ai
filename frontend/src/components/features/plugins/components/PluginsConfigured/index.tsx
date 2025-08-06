"use client"

import { useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Settings, MoreVertical, Power, Trash2, Info } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from "@/components/ui/dropdown-menu"
import { PluginConfigDialog } from "../PluginConfigDialog"
import { cn } from "@/lib/utils"
import { useTheme } from "next-themes"
import type { Plugin } from "@/types/plugin"

// 临时数据 - 后续将从 pluginsData 中获取已配置的插件
const configuredPlugins = [
  {
    id: "plugin-dev-1",
    name: "代码生成器",
    icon: "🔧",
    status: "configured",
    description: "AI代码生成工具",
    enabled: true,
  },
  {
    id: "plugin-design-1", 
    name: "设计素材库",
    icon: "🎨",
    status: "configured",
    description: "设计资源管理",
    enabled: true,
  },
  {
    id: "plugin-prod-1",
    name: "项目管理",
    icon: "📋",
    status: "configured",
    description: "任务协作工具",
    enabled: false,
  },
]

interface PluginsConfiguredProps {
  selectedPlugin: string | null
  onPluginSelect: (id: string) => void
}

export function PluginsConfigured({ selectedPlugin, onPluginSelect }: PluginsConfiguredProps) {
  const [configDialogOpen, setConfigDialogOpen] = useState(false)
  const [selectedPluginForConfig, setSelectedPluginForConfig] = useState<Plugin | null>(null)
  const { theme } = useTheme()

  const handleConfigClick = (pluginId: string, event: React.MouseEvent) => {
    event.stopPropagation()
    
    // 这里应该从完整的插件数据中查找插件
    // 暂时使用模拟数据
    const mockPlugin: Plugin = {
      id: pluginId,
      name: "代码生成器",
      displayName: "AI 代码生成器",
      version: "1.2.0",
      description: "基于需求自动生成高质量代码",
      longDescription: "强大的AI代码生成工具，支持多种编程语言，提供智能代码补全、自动注释生成和代码质量检查功能。",
      icon: "🔧",
      author: {
        name: "Connet AI Team",
        email: "dev@connet.ai"
      },
      category: "development",
      tags: ["代码生成", "AI", "开发工具", "自动化"],
      rating: 4.8,
      downloadCount: 15420,
      configured: true,
      enabled: true,
      featured: true,
      verified: true,
      features: ["支持20+编程语言", "智能代码补全", "自动注释生成", "代码质量检查"],
      requirements: ["API Key", "网络连接"],
      configTemplate: {
        version: "1.0",
        sections: [
          {
            id: "basic",
            title: "基本配置",
            description: "配置基本的 API 连接信息",
            fields: [
              {
                key: "apiKey",
                type: "password",
                label: "API Key",
                description: "用于访问代码生成服务的密钥",
                placeholder: "请输入您的 API Key",
                required: true,
                validation: {
                  required: true,
                  minLength: 10
                }
              },
              {
                key: "model",
                type: "select",
                label: "AI 模型",
                description: "选择用于代码生成的AI模型",
                required: true,
                options: [
                  { label: "GPT-4 (推荐)", value: "gpt-4", description: "最强大的模型，适合复杂任务" },
                  { label: "GPT-3.5 Turbo", value: "gpt-3.5-turbo", description: "快速响应，适合简单任务" },
                  { label: "Claude-3", value: "claude-3", description: "优秀的代码理解能力" }
                ]
              }
            ]
          }
        ]
      },
      createdAt: "2024-01-15T08:30:00Z",
      updatedAt: "2024-03-10T14:22:00Z",
      supportUrl: "https://support.connet.ai/code-generator",
      documentationUrl: "https://docs.connet.ai/plugins/code-generator"
    }
    
    setSelectedPluginForConfig(mockPlugin)
    setConfigDialogOpen(true)
  }

  const handleSaveConfig = async (pluginId: string, config: Record<string, any>) => {
    console.log("Saving config for plugin:", pluginId, config)
    // TODO: 实现配置保存逻辑
  }

  const handleTestConnection = async (pluginId: string, config: Record<string, any>) => {
    console.log("Testing connection for plugin:", pluginId, config)
    // TODO: 实现连接测试逻辑
    return true
  }

  const handleTogglePlugin = (pluginId: string, enabled: boolean) => {
    console.log(`${enabled ? 'Enabling' : 'Disabling'} plugin:`, pluginId)
    // TODO: 实现插件启用/禁用逻辑
  }

  const handleDeletePlugin = (pluginId: string) => {
    console.log("Deleting plugin:", pluginId)
    // TODO: 实现插件删除逻辑
  }
  return (
    <>
      <div>
        <div className={cn(
          "p-3 border-b",
          theme === 'dark' ? "border-border" : "border-gray-100"
        )}>
          <h3 className={cn(
            "font-medium mb-1",
            theme === 'dark' ? "text-gray-100" : "text-gray-900"
          )}>
            已配置插件
          </h3>
          <p className={cn(
            "text-xs",
            theme === 'dark' ? "text-gray-400" : "text-gray-500"
          )}>
            点击插件进行配置或管理
          </p>
        </div>

        <div className={cn(
          "divide-y",
          theme === 'dark' ? "divide-border" : "divide-gray-100"
        )}>
          {configuredPlugins.map((plugin) => (
            <div
              key={plugin.id}
              className={cn(
                "p-3 cursor-pointer transition-colors group",
                theme === 'dark' 
                  ? "hover:bg-card/50" 
                  : "hover:bg-gray-50",
                selectedPlugin === plugin.id && (
                  theme === 'dark'
                    ? "bg-card border-r-2 border-accent-500"
                    : "bg-blue-50 border-r-2 border-blue-500"
                ),
              )}
              onClick={() => onPluginSelect(plugin.id)}
            >
              <div className="flex items-center space-x-3">
                <div className="text-xl">{plugin.icon}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <h3 className={cn(
                      "font-medium text-sm",
                      theme === 'dark' ? "text-gray-100" : "text-gray-900"
                    )}>
                      {plugin.name}
                    </h3>
                    <div className={cn(
                      "w-2 h-2 rounded-full",
                      plugin.enabled 
                        ? "bg-green-500" 
                        : "bg-gray-400"
                    )} />
                  </div>
                  <p className={cn(
                    "text-xs truncate",
                    theme === 'dark' ? "text-gray-400" : "text-gray-500"
                  )}>
                    {plugin.description}
                  </p>
                  <div className="flex items-center space-x-2 mt-2">
                    <Badge variant="secondary" className="text-xs">
                      已配置
                    </Badge>
                    <Badge 
                      variant={plugin.enabled ? "default" : "outline"} 
                      className="text-xs"
                    >
                      {plugin.enabled ? "运行中" : "已停用"}
                    </Badge>
                  </div>
                </div>
                
                <div className="flex items-center space-x-1">
                  <Button 
                    size="sm" 
                    variant="ghost" 
                    className="p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={(e) => handleConfigClick(plugin.id, e)}
                  >
                    <Settings className="h-4 w-4" />
                  </Button>
                  
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button 
                        size="sm" 
                        variant="ghost" 
                        className="p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-48">
                      <DropdownMenuItem onClick={() => handleConfigClick(plugin.id, {} as any)}>
                        <Settings className="h-4 w-4 mr-2" />
                        配置插件
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => handleTogglePlugin(plugin.id, !plugin.enabled)}>
                        <Power className="h-4 w-4 mr-2" />
                        {plugin.enabled ? "停用插件" : "启用插件"}
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem 
                        onClick={() => handleDeletePlugin(plugin.id)}
                        className="text-red-600 focus:text-red-600"
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        删除插件
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 配置对话框 */}
      <PluginConfigDialog
        plugin={selectedPluginForConfig}
        open={configDialogOpen}
        onOpenChange={setConfigDialogOpen}
        onSaveConfig={handleSaveConfig}
        onTestConnection={handleTestConnection}
      />
    </>
  )
}

export default PluginsConfigured