"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Star } from "lucide-react"

export interface Plugin {
  id: string
  name: string
  description: string
  icon: string
  rating: number
  configured: boolean
  features: string[]
  configFields: Array<{
    key: string
    label: string
    type: string
    required?: boolean
    options?: string[]
    min?: number
    max?: number
    step?: number
  }>
}

interface PluginCardProps {
  plugin: Plugin
  onSelect: (id: string) => void
}

export function PluginCard({ plugin, onSelect }: PluginCardProps) {
  return (
    <Card
      className="cursor-pointer hover:shadow-md transition-all duration-200 hover:scale-105"
      onClick={() => onSelect(plugin.id)}
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
  )
}

export default PluginCard