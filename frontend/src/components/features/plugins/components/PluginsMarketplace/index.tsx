"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { PluginCard } from "../PluginCard"
import { PluginDetail } from "../PluginDetail"
import { pluginCategories } from "../../data/pluginsData"

interface PluginsMarketplaceProps {
  selectedPlugin: string | null
  onPluginSelect: (id: string) => void
}

export function PluginsMarketplace({ selectedPlugin, onPluginSelect }: PluginsMarketplaceProps) {
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
    <div className="p-6">
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
                    <PluginCard
                      key={plugin.id}
                      plugin={plugin}
                      onSelect={onPluginSelect}
                    />
                  ))}
                </div>
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}

export default PluginsMarketplace