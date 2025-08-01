"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Settings, Star, ArrowLeft, Key, Globe, Database } from "lucide-react"
import { useState } from "react"

const pluginCategories = [
  {
    id: "development",
    name: "开发工具",
    plugins: [
      {
        id: "plugin-dev-1",
        name: "代码生成器",
        description: "基于需求自动生成高质量代码",
        icon: "🔧",
        rating: 4.8,
        configured: true,
        features: ["支持20+编程语言", "智能代码补全", "自动注释生成", "代码质量检查"],
        configFields: [
          { key: "apiKey", label: "API Key", type: "password", required: true },
          { key: "model", label: "模型选择", type: "select", options: ["gpt-4", "gpt-3.5-turbo"], required: true },
          { key: "temperature", label: "创造性", type: "number", min: 0, max: 1, step: 0.1 },
        ],
      },
      {
        id: "plugin-dev-2",
        name: "API测试工具",
        description: "快速测试和调试API接口",
        icon: "🔌",
        rating: 4.6,
        configured: false,
        features: ["RESTful API测试", "GraphQL支持", "自动化测试", "响应时间监控"],
        configFields: [
          { key: "baseUrl", label: "Base URL", type: "url", required: true },
          { key: "timeout", label: "超时时间(秒)", type: "number", min: 1, max: 300 },
          { key: "retries", label: "重试次数", type: "number", min: 0, max: 5 },
        ],
      },
      {
        id: "plugin-dev-3",
        name: "数据库工具",
        description: "数据库连接和管理工具",
        icon: "🗄️",
        rating: 4.7,
        configured: false,
        features: ["多数据库支持", "SQL查询优化", "数据迁移", "备份恢复"],
        configFields: [
          {
            key: "dbType",
            label: "数据库类型",
            type: "select",
            options: ["MySQL", "PostgreSQL", "MongoDB"],
            required: true,
          },
          { key: "host", label: "主机地址", type: "text", required: true },
          { key: "port", label: "端口", type: "number", min: 1, max: 65535 },
          { key: "username", label: "用户名", type: "text", required: true },
          { key: "password", label: "密码", type: "password", required: true },
        ],
      },
    ],
  },
  {
    id: "design",
    name: "设计工具",
    plugins: [
      {
        id: "plugin-design-1",
        name: "设计素材库",
        description: "海量设计素材和模板",
        icon: "🎨",
        rating: 4.7,
        configured: true,
        features: ["10万+设计素材", "AI图片生成", "品牌色彩管理", "字体推荐"],
        configFields: [
          { key: "apiKey", label: "API Key", type: "password", required: true },
          { key: "quality", label: "图片质量", type: "select", options: ["高", "中", "低"], required: true },
          { key: "watermark", label: "水印设置", type: "text" },
        ],
      },
      {
        id: "plugin-design-2",
        name: "颜色搭配助手",
        description: "智能颜色搭配建议",
        icon: "🌈",
        rating: 4.5,
        configured: false,
        features: ["色彩理论分析", "品牌色彩提取", "无障碍色彩检查", "色彩趋势预测"],
        configFields: [
          { key: "colorSpace", label: "色彩空间", type: "select", options: ["RGB", "HSL", "CMYK"], required: true },
          { key: "accessibility", label: "无障碍检查", type: "checkbox" },
        ],
      },
    ],
  },
  {
    id: "productivity",
    name: "效率工具",
    plugins: [
      {
        id: "plugin-prod-1",
        name: "项目管理",
        description: "任务分配和进度跟踪",
        icon: "📋",
        rating: 4.9,
        configured: true,
        features: ["甘特图管理", "团队协作", "时间追踪", "报告生成"],
        configFields: [
          { key: "webhookUrl", label: "Webhook URL", type: "url" },
          { key: "notifications", label: "通知设置", type: "checkbox" },
          { key: "timezone", label: "时区", type: "select", options: ["Asia/Shanghai", "UTC", "America/New_York"] },
        ],
      },
      {
        id: "plugin-prod-2",
        name: "时间追踪",
        description: "工作时间统计和分析",
        icon: "⏰",
        rating: 4.4,
        configured: false,
        features: ["自动时间记录", "项目时间分析", "效率报告", "团队统计"],
        configFields: [
          { key: "autoStart", label: "自动开始", type: "checkbox" },
          { key: "reminderInterval", label: "提醒间隔(分钟)", type: "number", min: 5, max: 60 },
        ],
      },
    ],
  },
]

interface PluginsMarketplaceProps {
  selectedPlugin: string | null
  onPluginSelect: (id: string) => void
}

export function PluginsMarketplace({ selectedPlugin, onPluginSelect }: PluginsMarketplaceProps) {
  const [configValues, setConfigValues] = useState<Record<string, any>>({})

  const selectedPluginData = pluginCategories
    .flatMap((cat) => cat.plugins)
    .find((plugin) => plugin.id === selectedPlugin)

  const handleConfigChange = (key: string, value: any) => {
    setConfigValues((prev) => ({ ...prev, [key]: value }))
  }

  const handleSaveConfig = () => {
    console.log("Saving config:", configValues)
    // Save configuration logic here
  }

  const renderConfigField = (field: any) => {
    const value = configValues[field.key] || ""

    switch (field.type) {
      case "password":
        return (
          <Input
            type="password"
            value={value}
            onChange={(e) => handleConfigChange(field.key, e.target.value)}
            placeholder={`请输入${field.label}`}
          />
        )
      case "url":
        return (
          <Input
            type="url"
            value={value}
            onChange={(e) => handleConfigChange(field.key, e.target.value)}
            placeholder={`请输入${field.label}`}
          />
        )
      case "number":
        return (
          <Input
            type="number"
            value={value}
            onChange={(e) => handleConfigChange(field.key, e.target.value)}
            min={field.min}
            max={field.max}
            step={field.step}
            placeholder={`请输入${field.label}`}
          />
        )
      case "select":
        return (
          <Select value={value} onValueChange={(val) => handleConfigChange(field.key, val)}>
            <SelectTrigger>
              <SelectValue placeholder={`选择${field.label}`} />
            </SelectTrigger>
            <SelectContent>
              {field.options?.map((option: string) => (
                <SelectItem key={option} value={option}>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )
      case "checkbox":
        return (
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={value}
              onChange={(e) => handleConfigChange(field.key, e.target.checked)}
              className="rounded"
            />
            <span className="text-sm">启用{field.label}</span>
          </div>
        )
      case "textarea":
        return (
          <Textarea
            value={value}
            onChange={(e) => handleConfigChange(field.key, e.target.value)}
            placeholder={`请输入${field.label}`}
            rows={3}
          />
        )
      default:
        return (
          <Input
            value={value}
            onChange={(e) => handleConfigChange(field.key, e.target.value)}
            placeholder={`请输入${field.label}`}
          />
        )
    }
  }

  return (
    <div className="p-6">
      {!selectedPlugin ? (
        <Card>
          <CardHeader>
            <CardTitle>插件市场</CardTitle>
            <p className="text-sm text-gray-600">发现和配置强大的AI工具插件</p>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="development">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="development">开发工具</TabsTrigger>
                <TabsTrigger value="design">设计工具</TabsTrigger>
                <TabsTrigger value="productivity">效率工具</TabsTrigger>
              </TabsList>

              {pluginCategories.map((category) => (
                <TabsContent key={category.id} value={category.id} className="mt-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {category.plugins.map((plugin) => (
                      <Card
                        key={plugin.id}
                        className="cursor-pointer hover:shadow-md transition-all duration-200 hover:scale-105"
                        onClick={() => onPluginSelect(plugin.id)}
                      >
                        <CardContent className="p-4">
                          <div className="flex items-start space-x-3">
                            <div className="text-3xl">{plugin.icon}</div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between mb-2">
                                <h3 className="font-medium text-sm">{plugin.name}</h3>
                                <div className="flex items-center space-x-1">
                                  <Star className="h-3 w-3 text-yellow-400 fill-current" />
                                  <span className="text-xs">{plugin.rating}</span>
                                </div>
                              </div>
                              <p className="text-xs text-gray-600 mb-3 line-clamp-2">{plugin.description}</p>
                              <div className="flex items-center justify-between">
                                <Badge variant={plugin.configured ? "secondary" : "outline"} className="text-xs">
                                  {plugin.configured ? "已配置" : "未配置"}
                                </Badge>
                                <Button size="sm" variant="ghost" className="text-xs p-1">
                                  查看详情
                                </Button>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </TabsContent>
              ))}
            </Tabs>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {/* Plugin Header */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <Button variant="ghost" size="sm" onClick={() => onPluginSelect("")} className="p-2">
                    <ArrowLeft className="h-4 w-4" />
                  </Button>
                  <div className="flex items-center space-x-3">
                    <div className="text-4xl">{selectedPluginData?.icon}</div>
                    <div>
                      <CardTitle className="flex items-center space-x-2">
                        {selectedPluginData?.name}
                        <Badge variant={selectedPluginData?.configured ? "secondary" : "outline"}>
                          {selectedPluginData?.configured ? "已配置" : "未配置"}
                        </Badge>
                      </CardTitle>
                      <div className="flex items-center space-x-2 mt-1">
                        <div className="flex items-center space-x-1">
                          <Star className="h-4 w-4 text-yellow-400 fill-current" />
                          <span className="text-sm">{selectedPluginData?.rating}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardHeader>
          </Card>

          {/* Plugin Overview */}
          <Card>
            <CardHeader>
              <CardTitle>插件概览</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h3 className="font-medium mb-2">插件描述</h3>
                  <p className="text-gray-600">{selectedPluginData?.description}</p>
                </div>

                <div>
                  <h3 className="font-medium mb-2">主要功能</h3>
                  <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {selectedPluginData?.features.map((feature, index) => (
                      <li key={index} className="flex items-center space-x-2 text-sm text-gray-600">
                        <div className="w-1.5 h-1.5 bg-blue-500 rounded-full"></div>
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Plugin Configuration */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Settings className="h-5 w-5" />
                <span>插件配置</span>
              </CardTitle>
              <p className="text-sm text-gray-600">配置插件所需的参数和密钥</p>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {selectedPluginData?.configFields.map((field) => (
                  <div key={field.key} className="space-y-2">
                    <Label htmlFor={field.key} className="flex items-center space-x-2">
                      <span>{field.label}</span>
                      {field.required && <span className="text-red-500">*</span>}
                      {field.type === "password" && <Key className="h-3 w-3 text-gray-400" />}
                      {field.type === "url" && <Globe className="h-3 w-3 text-gray-400" />}
                      {field.key.includes("db") && <Database className="h-3 w-3 text-gray-400" />}
                    </Label>
                    {renderConfigField(field)}
                  </div>
                ))}

                <div className="flex space-x-3 pt-4 border-t">
                  <Button onClick={handleSaveConfig} className="flex-1">
                    <Settings className="h-4 w-4 mr-2" />
                    保存配置
                  </Button>
                  <Button variant="outline" className="flex-1 bg-transparent">
                    测试连接
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
