"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Star, Download, Shield, CheckCircle, Plus } from "lucide-react"
import { cn } from "@/lib/utils"
import { useTheme } from "next-themes"
import type { Plugin } from "@/types/plugin"

interface PluginCardProps {
  plugin: Plugin
  onSelect: (id: string) => void
  viewMode?: "grid" | "list"
}

export function PluginCard({ plugin, onSelect, viewMode = "grid" }: PluginCardProps) {
  const { theme } = useTheme()

  if (viewMode === "list") {
    return (
      <Card
        className={cn(
          "cursor-pointer transition-all duration-200 hover:shadow-md",
          theme === 'dark' 
            ? "bg-card border-border hover:bg-card/80" 
            : "bg-white border-gray-200 hover:bg-gray-50"
        )}
        onClick={() => onSelect(plugin.id)}
      >
        <CardContent className="p-4">
          <div className="flex items-center space-x-4">
            <div className="text-3xl flex-shrink-0">{plugin.icon}</div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-3 mb-2">
                <h3 className={cn(
                  "font-semibold text-base",
                  theme === 'dark' ? "text-gray-100" : "text-gray-900"
                )}>
                  {plugin.displayName || plugin.name}
                </h3>
                
                <div className="flex items-center space-x-2">
                  {plugin.verified && (
                    <Badge variant="secondary" className="text-xs">
                      <Shield className="h-3 w-3 mr-1" />
                      已验证
                    </Badge>
                  )}
                  {plugin.featured && (
                    <Badge variant="default" className="text-xs">
                      精选
                    </Badge>
                  )}
                  <Badge 
                    variant={plugin.configured ? "default" : "outline"} 
                    className="text-xs"
                  >
                    {plugin.configured ? "已安装" : "未安装"}
                  </Badge>
                </div>
              </div>
              
              <p className={cn(
                "text-sm mb-3 line-clamp-2",
                theme === 'dark' ? "text-gray-300" : "text-gray-600"
              )}>
                {plugin.description}
              </p>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4 text-xs text-gray-500">
                  <div className="flex items-center space-x-1">
                    <Star className="h-3 w-3 text-yellow-400 fill-current" />
                    <span>{plugin.rating}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Download className="h-3 w-3" />
                    <span>{plugin.downloadCount?.toLocaleString()}</span>
                  </div>
                  <span>v{plugin.version}</span>
                </div>
                
                <Button size="sm" variant="ghost" className="text-xs">
                  {plugin.configured ? "配置" : "安装"}
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Grid view (default)
  return (
    <Card
      className={cn(
        "cursor-pointer transition-all duration-200 hover:shadow-lg group",
        theme === 'dark' 
          ? "bg-card border-border hover:bg-card/80 hover:border-accent-500/50" 
          : "bg-white border-gray-200 hover:bg-gray-50 hover:border-blue-300",
        "hover:scale-[1.02]"
      )}
      onClick={() => onSelect(plugin.id)}
    >
      <CardContent className="p-5">
        <div className="space-y-4">
          {/* Header */}
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-3xl">{plugin.icon}</div>
              <div className="min-w-0 flex-1">
                <h3 className={cn(
                  "font-semibold text-sm truncate",
                  theme === 'dark' ? "text-gray-100" : "text-gray-900"
                )}>
                  {plugin.displayName || plugin.name}
                </h3>
                <p className={cn(
                  "text-xs mt-1",
                  theme === 'dark' ? "text-gray-400" : "text-gray-500"
                )}>
                  v{plugin.version}
                </p>
              </div>
            </div>
            
            {plugin.featured && (
              <Badge variant="default" className="text-xs">
                精选
              </Badge>
            )}
          </div>

          {/* Description */}
          <p className={cn(
            "text-xs line-clamp-3 min-h-[3rem]",
            theme === 'dark' ? "text-gray-300" : "text-gray-600"
          )}>
            {plugin.description}
          </p>

          {/* Tags */}
          {plugin.tags && plugin.tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {plugin.tags.slice(0, 3).map((tag, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {tag}
                </Badge>
              ))}
              {plugin.tags.length > 3 && (
                <Badge variant="outline" className="text-xs">
                  +{plugin.tags.length - 3}
                </Badge>
              )}
            </div>
          )}

          {/* Stats */}
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-1">
                <Star className="h-3 w-3 text-yellow-400 fill-current" />
                <span>{plugin.rating}</span>
              </div>
              <div className="flex items-center space-x-1">
                <Download className="h-3 w-3 text-gray-400" />
                <span className={cn(
                  theme === 'dark' ? "text-gray-400" : "text-gray-500"
                )}>
                  {plugin.downloadCount?.toLocaleString()}
                </span>
              </div>
            </div>
            
            {plugin.verified && (
              <div className="flex items-center space-x-1 text-green-600">
                <Shield className="h-3 w-3" />
                <span className="text-xs">已验证</span>
              </div>
            )}
          </div>

          {/* Action Button */}
          <div className="pt-2 border-t">
            <Button 
              size="sm" 
              className="w-full text-xs"
              variant={plugin.configured ? "outline" : "default"}
              onClick={(e) => {
                e.stopPropagation()
                onSelect(plugin.id)
              }}
            >
              {plugin.configured ? (
                <>
                  <CheckCircle className="h-3 w-3 mr-2" />
                  已安装
                </>
              ) : (
                <>
                  <Plus className="h-3 w-3 mr-2" />
                  安装插件
                </>
              )}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default PluginCard