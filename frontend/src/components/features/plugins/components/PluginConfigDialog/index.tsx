"use client"

import { useState } from "react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Settings, X, CheckCircle, AlertCircle, Info } from "lucide-react"
import { AdvancedConfigForm } from "../AdvancedConfigForm"
import type { Plugin } from "@/types/plugin"
import { cn } from "@/lib/utils"
import { useTheme } from "next-themes"

interface PluginConfigDialogProps {
  plugin: Plugin | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onSaveConfig: (pluginId: string, config: Record<string, any>) => Promise<void>
  onTestConnection?: (pluginId: string, config: Record<string, any>) => Promise<boolean>
}

export function PluginConfigDialog({
  plugin,
  open,
  onOpenChange,
  onSaveConfig,
  onTestConnection
}: PluginConfigDialogProps) {
  const [activeTab, setActiveTab] = useState("config")
  const [isSaving, setIsSaving] = useState(false)
  const [isTesting, setIsTesting] = useState(false)
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null)
  const { theme } = useTheme()

  const handleSave = async (config: Record<string, any>) => {
    if (!plugin) return
    
    setIsSaving(true)
    try {
      await onSaveConfig(plugin.id, config)
      onOpenChange(false)
    } catch (error) {
      console.error("Failed to save config:", error)
    } finally {
      setIsSaving(false)
    }
  }

  const handleTest = async (config: Record<string, any>) => {
    if (!plugin || !onTestConnection) return
    
    setIsTesting(true)
    setTestResult(null)
    
    try {
      const success = await onTestConnection(plugin.id, config)
      setTestResult({
        success,
        message: success ? "连接测试成功！" : "连接测试失败，请检查配置"
      })
    } catch (error) {
      setTestResult({
        success: false,
        message: "连接测试出错：" + (error as Error).message
      })
    } finally {
      setIsTesting(false)
    }
  }

  if (!plugin) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent 
        className={cn(
          "max-w-4xl max-h-[90vh] p-0",
          theme === 'dark' 
            ? "bg-card border-border" 
            : "bg-white border-gray-200"
        )}
      >
        {/* Header */}
        <DialogHeader className={cn(
          "p-6 border-b",
          theme === 'dark' ? "border-border" : "border-gray-200"
        )}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="text-4xl">{plugin.icon}</div>
              <div>
                <DialogTitle className="text-xl font-semibold">
                  {plugin.displayName || plugin.name}
                </DialogTitle>
                <DialogDescription className="flex items-center space-x-2 mt-1">
                  <span>v{plugin.version}</span>
                  <span className="text-gray-400">•</span>
                  <span>{plugin.author.name}</span>
                  {plugin.verified && (
                    <>
                      <span className="text-gray-400">•</span>
                      <Badge variant="secondary" className="text-xs">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        已验证
                      </Badge>
                    </>
                  )}
                </DialogDescription>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onOpenChange(false)}
              className="h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </DialogHeader>

        {/* Content */}
        <div className="flex-1 overflow-hidden">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
            <div className={cn(
              "px-6 pt-4 border-b",
              theme === 'dark' ? "border-border" : "border-gray-200"
            )}>
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="config" className="flex items-center space-x-2">
                  <Settings className="h-4 w-4" />
                  <span>配置</span>
                </TabsTrigger>
                <TabsTrigger value="info" className="flex items-center space-x-2">
                  <Info className="h-4 w-4" />
                  <span>信息</span>
                </TabsTrigger>
                <TabsTrigger value="test" className="flex items-center space-x-2">
                  <AlertCircle className="h-4 w-4" />
                  <span>测试</span>
                </TabsTrigger>
              </TabsList>
            </div>

            <div className="flex-1 overflow-hidden">
              <ScrollArea className="h-full">
                <TabsContent value="config" className="mt-0 p-6">
                  <AdvancedConfigForm
                    plugin={plugin}
                    onSave={handleSave}
                    onTest={handleTest}
                    isSaving={isSaving}
                    isTesting={isTesting}
                    testResult={testResult}
                  />
                </TabsContent>

                <TabsContent value="info" className="mt-0 p-6">
                  <div className="space-y-6">
                    <div>
                      <h3 className="font-medium text-lg mb-2">插件描述</h3>
                      <p className={cn(
                        "text-sm leading-relaxed",
                        theme === 'dark' ? "text-gray-300" : "text-gray-600"
                      )}>
                        {plugin.longDescription || plugin.description}
                      </p>
                    </div>

                    <div>
                      <h3 className="font-medium text-lg mb-3">主要功能</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                        {plugin.features.map((feature, index) => (
                          <div key={index} className="flex items-center space-x-2 text-sm">
                            <div className="w-1.5 h-1.5 bg-blue-500 rounded-full"></div>
                            <span>{feature}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {plugin.requirements && plugin.requirements.length > 0 && (
                      <div>
                        <h3 className="font-medium text-lg mb-3">系统要求</h3>
                        <div className="space-y-1">
                          {plugin.requirements.map((req, index) => (
                            <div key={index} className="flex items-center space-x-2 text-sm">
                              <AlertCircle className="h-4 w-4 text-amber-500" />
                              <span>{req}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className={cn(
                          "font-medium",
                          theme === 'dark' ? "text-gray-300" : "text-gray-600"
                        )}>
                          分类：
                        </span>
                        <span className="ml-1">{plugin.category}</span>
                      </div>
                      <div>
                        <span className={cn(
                          "font-medium",
                          theme === 'dark' ? "text-gray-300" : "text-gray-600"
                        )}>
                          下载量：
                        </span>
                        <span className="ml-1">{plugin.downloadCount.toLocaleString()}</span>
                      </div>
                      <div>
                        <span className={cn(
                          "font-medium",
                          theme === 'dark' ? "text-gray-300" : "text-gray-600"
                        )}>
                          更新时间：
                        </span>
                        <span className="ml-1">
                          {new Date(plugin.updatedAt).toLocaleDateString()}
                        </span>
                      </div>
                      <div>
                        <span className={cn(
                          "font-medium",
                          theme === 'dark' ? "text-gray-300" : "text-gray-600"
                        )}>
                          评分：
                        </span>
                        <span className="ml-1">{plugin.rating}/5.0</span>
                      </div>
                    </div>

                    {plugin.tags && plugin.tags.length > 0 && (
                      <div>
                        <h3 className="font-medium text-lg mb-3">标签</h3>
                        <div className="flex flex-wrap gap-2">
                          {plugin.tags.map((tag, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </TabsContent>

                <TabsContent value="test" className="mt-0 p-6">
                  <div className="space-y-4">
                    <div>
                      <h3 className="font-medium text-lg mb-2">连接测试</h3>
                      <p className={cn(
                        "text-sm mb-4",
                        theme === 'dark' ? "text-gray-300" : "text-gray-600"
                      )}>
                        测试插件配置是否正确，确保可以正常连接服务。
                      </p>
                    </div>

                    {testResult && (
                      <div className={cn(
                        "p-4 rounded-lg border",
                        testResult.success 
                          ? "bg-green-50 border-green-200 text-green-800 dark:bg-green-900/10 dark:border-green-800 dark:text-green-300"
                          : "bg-red-50 border-red-200 text-red-800 dark:bg-red-900/10 dark:border-red-800 dark:text-red-300"
                      )}>
                        <div className="flex items-center space-x-2">
                          {testResult.success ? (
                            <CheckCircle className="h-5 w-5" />
                          ) : (
                            <AlertCircle className="h-5 w-5" />
                          )}
                          <span className="font-medium">{testResult.message}</span>
                        </div>
                      </div>
                    )}

                    <Button
                      onClick={() => handleTest(plugin.currentConfig || {})}
                      disabled={isTesting}
                      className="w-full"
                    >
                      {isTesting ? "测试中..." : "开始测试"}
                    </Button>
                  </div>
                </TabsContent>
              </ScrollArea>
            </div>
          </Tabs>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default PluginConfigDialog