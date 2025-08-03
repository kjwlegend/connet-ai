"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Settings, Check, Crown, Sparkles } from "lucide-react"
import { useState } from "react"

const llmProviders = [
  {
    id: "openai",
    name: "OpenAI",
    logo: "🤖",
    models: ["gpt-4", "gpt-3.5-turbo", "text-embedding-ada-002"],
    configured: true,
  },
  {
    id: "anthropic",
    name: "Anthropic",
    logo: "🧠",
    models: ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
    configured: false,
  },
  {
    id: "google",
    name: "Google",
    logo: "🔍",
    models: ["gemini-pro", "gemini-pro-vision", "text-embedding-004"],
    configured: false,
  },
  {
    id: "azure",
    name: "Azure OpenAI",
    logo: "☁️",
    models: ["gpt-4", "gpt-35-turbo", "text-embedding-ada-002"],
    configured: false,
  },
]

const modelTypes = [
  { id: "chat", name: "对话模型", description: "用于日常对话和问答" },
  { id: "memory", name: "记忆模型", description: "用于上下文记忆和总结" },
  { id: "embedding", name: "向量模型", description: "用于文本向量化和搜索" },
]

export function SettingsLLM() {
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null)
  const [apiKey, setApiKey] = useState("")
  const [baseUrl, setBaseUrl] = useState("")
  const [selectedModels, setSelectedModels] = useState({
    chat: "gpt-4",
    memory: "gpt-3.5-turbo",
    embedding: "text-embedding-ada-002",
  })

  return (
    <div className="p-6 space-y-6">
      {/* Marketing Section */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-blue-100 rounded-full">
                <Crown className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">不想使用自己的 API Key？</h3>
                <p className="text-sm text-gray-600 mt-1">开通会员享受无限制 AI 对话，无需配置任何密钥</p>
              </div>
            </div>
            <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
              <Sparkles className="h-4 w-4 mr-2" />
              开通会员
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Model Selection - Moved to top */}
      <Card>
        <CardHeader>
          <CardTitle>模型选择</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {modelTypes.map((type) => (
            <div key={type.id} className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <h3 className="font-medium">{type.name}</h3>
                <p className="text-sm text-gray-600">{type.description}</p>
              </div>
              <div className="w-48">
                <Select
                  value={selectedModels[type.id as keyof typeof selectedModels]}
                  onValueChange={(value) => setSelectedModels((prev) => ({ ...prev, [type.id]: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="gpt-4">GPT-4</SelectItem>
                    <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                    <SelectItem value="text-embedding-ada-002">Text Embedding Ada 002</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* LLM Providers - Moved to bottom */}
      <Card>
        <CardHeader>
          <CardTitle>LLM 供应商配置</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {llmProviders.map((provider) => (
              <div
                key={provider.id}
                className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                  selectedProvider === provider.id
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-200 hover:border-gray-300"
                }`}
                onClick={() => setSelectedProvider(provider.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">{provider.logo}</div>
                    <div>
                      <h3 className="font-medium">{provider.name}</h3>
                      <p className="text-sm text-gray-600">{provider.models.length} 个模型</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {provider.configured && (
                      <Badge variant="secondary" className="text-xs">
                        <Check className="h-3 w-3 mr-1" />
                        已配置
                      </Badge>
                    )}
                    <Button variant="ghost" size="sm">
                      <Settings className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Provider Configuration */}
      {selectedProvider && (
        <Card>
          <CardHeader>
            <CardTitle>配置 {llmProviders.find((p) => p.id === selectedProvider)?.name}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="apiKey">API Key</Label>
                <Input
                  id="apiKey"
                  type="password"
                  placeholder="输入 API Key"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="baseUrl">Base URL (可选)</Label>
                <Input
                  id="baseUrl"
                  placeholder="https://api.openai.com/v1"
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                />
              </div>
            </div>
            <div className="flex space-x-2">
              <Button>保存配置</Button>
              <Button variant="outline">测试连接</Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default SettingsLLM