"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, Star, Settings } from "lucide-react"
import { PluginConfigForm } from "../PluginConfigForm"
import type { Plugin } from "../PluginCard"

interface PluginDetailProps {
  plugin: Plugin
  onBack: () => void
  onSaveConfig: (config: Record<string, any>) => void
  onTestConnection?: () => void
}

export function PluginDetail({ plugin, onBack, onSaveConfig, onTestConnection }: PluginDetailProps) {
  return (
    <div className="space-y-6">
      {/* Plugin Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" onClick={onBack} className="p-2">
                <ArrowLeft className="h-4 w-4" />
              </Button>
              <div className="flex items-center space-x-3">
                <div className="text-4xl">{plugin.icon}</div>
                <div>
                  <CardTitle className="flex items-center space-x-2">
                    {plugin.name}
                    <Badge variant={plugin.configured ? "secondary" : "outline"}>
                      {plugin.configured ? "已配置" : "未配置"}
                    </Badge>
                  </CardTitle>
                  <div className="flex items-center space-x-2 mt-1">
                    <div className="flex items-center space-x-1">
                      <Star className="h-4 w-4 text-yellow-400 fill-current" />
                      <span className="text-sm">{plugin.rating}</span>
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
              <p className="text-gray-600">{plugin.description}</p>
            </div>

            <div>
              <h3 className="font-medium mb-2">主要功能</h3>
              <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {plugin.features.map((feature, index) => (
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
          <PluginConfigForm 
            plugin={plugin} 
            onSave={onSaveConfig}
            onTest={onTestConnection}
          />
        </CardContent>
      </Card>
    </div>
  )
}

export default PluginDetail