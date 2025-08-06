"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  Search, 
  Star, 
  Download, 
  Shield, 
  TrendingUp, 
  Filter,
  Grid3X3,
  List,
  SortAsc
} from "lucide-react"
import { PluginCard } from "../PluginCard"
import { PluginDetail } from "../PluginDetail"
import { pluginCategories } from "../../data/pluginsData"
import { cn } from "@/lib/utils"
import { useTheme } from "next-themes"

interface PluginsMarketplaceProps {
  selectedPlugin: string | null
  onPluginSelect: (id: string) => void
}

export function PluginsMarketplace({ selectedPlugin, onPluginSelect }: PluginsMarketplaceProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const [sortBy, setSortBy] = useState<"rating" | "downloads" | "updated">("rating")
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid")
  const { theme } = useTheme()
  
  const selectedPluginData = pluginCategories
    .flatMap((cat) => cat.plugins)
    .find((plugin) => plugin.id === selectedPlugin)

  const handleSaveConfig = (config: Record<string, any>) => {
    console.log("Saving config:", config)
    // TODO: 实现配置保存逻辑
  }

  const handleTestConnection = () => {
    console.log("Testing connection...")
    // TODO: 实现连接测试逻辑
  }

  const filterAndSortPlugins = (plugins: any[]) => {
    let filtered = plugins
    
    if (searchQuery) {
      filtered = plugins.filter(plugin =>
        plugin.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        plugin.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        plugin.tags?.some((tag: string) => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    }
    
    return filtered.sort((a, b) => {
      switch (sortBy) {
        case "rating":
          return (b.rating || 0) - (a.rating || 0)
        case "downloads":
          return (b.downloadCount || 0) - (a.downloadCount || 0)
        case "updated":
          return new Date(b.updatedAt || 0).getTime() - new Date(a.updatedAt || 0).getTime()
        default:
          return 0
      }
    })
  }

  if (selectedPlugin && selectedPluginData) {
    return (
      <div className="p-6">
        <PluginDetail
          plugin={selectedPluginData}
          onBack={() => onPluginSelect("")}
          onSaveConfig={handleSaveConfig}
          onTestConnection={handleTestConnection}
        />
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className={cn(
        "p-6 border-b",
        theme === 'dark' ? "border-border" : "border-gray-200"
      )}>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className={cn(
              "text-2xl font-bold",
              theme === 'dark' ? "text-gray-100" : "text-gray-900"
            )}>
              插件市场
            </h1>
            <p className={cn(
              "text-sm mt-1",
              theme === 'dark' ? "text-gray-400" : "text-gray-600"
            )}>
              发现和安装强大的AI工具插件，扩展平台能力
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Badge variant="outline" className="text-xs">
              <TrendingUp className="h-3 w-3 mr-1" />
              {pluginCategories.reduce((total, cat) => total + cat.plugins.length, 0)} 个插件
            </Badge>
          </div>
        </div>

        {/* Search and Controls */}
        <div className="flex items-center space-x-4">
          <div className="relative flex-1 max-w-md">
            <Search className={cn(
              "absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4",
              theme === 'dark' ? "text-gray-500" : "text-gray-400"
            )} />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索插件名称、描述或标签..."
              className="pl-10"
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setViewMode(viewMode === "grid" ? "list" : "grid")}
            >
              {viewMode === "grid" ? <List className="h-4 w-4" /> : <Grid3X3 className="h-4 w-4" />}
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                const sortOptions: Array<typeof sortBy> = ["rating", "downloads", "updated"]
                const currentIndex = sortOptions.indexOf(sortBy)
                setSortBy(sortOptions[(currentIndex + 1) % sortOptions.length])
              }}
            >
              <SortAsc className="h-4 w-4 mr-2" />
              {sortBy === "rating" ? "评分" : sortBy === "downloads" ? "下载量" : "更新时间"}
            </Button>
          </div>
        </div>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1">
        <div className="p-6">
          <Tabs defaultValue="all" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="all">全部</TabsTrigger>
              <TabsTrigger value="development">开发工具</TabsTrigger>
              <TabsTrigger value="design">设计工具</TabsTrigger>
              <TabsTrigger value="productivity">效率工具</TabsTrigger>
            </TabsList>

            {/* All plugins tab */}
            <TabsContent value="all" className="mt-6">
              <div className="space-y-6">
                {/* Featured Section */}
                <div>
                  <h3 className={cn(
                    "text-lg font-semibold mb-4 flex items-center",
                    theme === 'dark' ? "text-gray-100" : "text-gray-900"
                  )}>
                    <Star className="h-5 w-5 mr-2 text-yellow-500" />
                    精选插件
                  </h3>
                  <div className={cn(
                    "grid gap-4",
                    viewMode === "grid" 
                      ? "grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
                      : "grid-cols-1"
                  )}>
                    {filterAndSortPlugins(
                      pluginCategories.flatMap(cat => cat.plugins.filter(p => p.featured))
                    ).map((plugin) => (
                      <PluginCard
                        key={plugin.id}
                        plugin={plugin}
                        onSelect={onPluginSelect}
                        viewMode={viewMode}
                      />
                    ))}
                  </div>
                </div>

                {/* All Plugins */}
                <div>
                  <h3 className={cn(
                    "text-lg font-semibold mb-4",
                    theme === 'dark' ? "text-gray-100" : "text-gray-900"
                  )}>
                    所有插件
                  </h3>
                  <div className={cn(
                    "grid gap-4",
                    viewMode === "grid" 
                      ? "grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
                      : "grid-cols-1"
                  )}>
                    {filterAndSortPlugins(
                      pluginCategories.flatMap(cat => cat.plugins)
                    ).map((plugin) => (
                      <PluginCard
                        key={plugin.id}
                        plugin={plugin}
                        onSelect={onPluginSelect}
                        viewMode={viewMode}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </TabsContent>

            {/* Category tabs */}
            {pluginCategories.map((category) => (
              <TabsContent key={category.id} value={category.id} className="mt-6">
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <div className="text-2xl">{category.icon}</div>
                    <div>
                      <h3 className={cn(
                        "text-lg font-semibold",
                        theme === 'dark' ? "text-gray-100" : "text-gray-900"
                      )}>
                        {category.name}
                      </h3>
                      {category.description && (
                        <p className={cn(
                          "text-sm",
                          theme === 'dark' ? "text-gray-400" : "text-gray-600"
                        )}>
                          {category.description}
                        </p>
                      )}
                    </div>
                  </div>
                  
                  <div className={cn(
                    "grid gap-4",
                    viewMode === "grid" 
                      ? "grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
                      : "grid-cols-1"
                  )}>
                    {filterAndSortPlugins(category.plugins).map((plugin) => (
                      <PluginCard
                        key={plugin.id}
                        plugin={plugin}
                        onSelect={onPluginSelect}
                        viewMode={viewMode}
                      />
                    ))}
                  </div>
                </div>
              </TabsContent>
            ))}
          </Tabs>
        </div>
      </ScrollArea>
    </div>
  )
}

export default PluginsMarketplace