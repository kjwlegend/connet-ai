"use client"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { 
  Settings, 
  Check, 
  Crown, 
  Sparkles, 
  Bot, 
  Key, 
  Globe, 
  AlertCircle,
  TestTube,
  Brain,
  MessageSquare,
  Database
} from "lucide-react"
import { useState } from "react"
import { useTranslations } from "@/lib/i18n/client"
import { useTheme } from "next-themes"
import { cn } from "@/lib/utils"

const llmProviders = [
  {
    id: "openai",
    name: "OpenAI",
    icon: Bot,
    models: ["gpt-4", "gpt-3.5-turbo", "text-embedding-ada-002"],
    configured: true,
    color: "text-green-600",
    bgColor: "bg-green-50 dark:bg-green-900/20"
  },
  {
    id: "anthropic",
    name: "Anthropic",
    icon: Brain,
    models: ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
    configured: false,
    color: "text-purple-600",
    bgColor: "bg-purple-50 dark:bg-purple-900/20"
  },
  {
    id: "google",
    name: "Google",
    icon: Globe,
    models: ["gemini-pro", "gemini-pro-vision", "text-embedding-004"],
    configured: false,
    color: "text-blue-600",
    bgColor: "bg-blue-50 dark:bg-blue-900/20"
  },
  {
    id: "azure",
    name: "Azure OpenAI",
    icon: Database,
    models: ["gpt-4", "gpt-35-turbo", "text-embedding-ada-002"],
    configured: false,
    color: "text-indigo-600",
    bgColor: "bg-indigo-50 dark:bg-indigo-900/20"
  },
]

const modelTypes = [
  { 
    id: "chat", 
    name: "chat",
    icon: MessageSquare,
    color: "text-blue-600"
  },
  { 
    id: "memory", 
    name: "memory",
    icon: Brain,
    color: "text-purple-600"
  },
  { 
    id: "embedding", 
    name: "embedding",
    icon: Database,
    color: "text-green-600"
  },
]

export function SettingsLLM() {
  const t = useTranslations()
  const { theme } = useTheme()
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null)
  const [apiKey, setApiKey] = useState("")
  const [baseUrl, setBaseUrl] = useState("")
  const [isTesting, setIsTesting] = useState(false)
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null)
  const [selectedModels, setSelectedModels] = useState({
    chat: "gpt-4",
    memory: "gpt-3.5-turbo",
    embedding: "text-embedding-ada-002",
  })

  const handleTestConnection = async () => {
    setIsTesting(true)
    setTestResult(null)
    // Simulate API test
    await new Promise(resolve => setTimeout(resolve, 1500))
    setTestResult({
      success: true,
      message: t('settings.llm.testSuccess')
    })
    setIsTesting(false)
  }

  const handleSaveConfig = async () => {
    // Save configuration
    console.log('Saving configuration...')
  }

  return (
    <div className={cn(
      "flex-1 p-6 overflow-y-auto",
      theme === 'dark' ? 'bg-background' : 'bg-gray-50/50'
    )}>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold">{t('settings.llm.title')}</h1>
          <p className={cn(
            "text-sm mt-1",
            theme === 'dark' ? "text-gray-400" : "text-gray-600"
          )}>
            {t('settings.llm.description')}
          </p>
        </div>

        {/* Premium Banner */}
        <Card className={cn(
          "border-0",
          theme === 'dark' 
            ? "bg-gradient-to-r from-blue-900/50 to-purple-900/50" 
            : "bg-gradient-to-r from-blue-50 to-purple-50"
        )}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className={cn(
                  "p-3 rounded-full",
                  theme === 'dark' ? "bg-yellow-900/50" : "bg-yellow-100"
                )}>
                  <Crown className="h-6 w-6 text-yellow-600" />
                </div>
                <div>
                  <h3 className="font-semibold">{t('settings.llm.premiumTitle')}</h3>
                  <p className={cn(
                    "text-sm mt-1",
                    theme === 'dark' ? "text-gray-300" : "text-gray-600"
                  )}>
                    {t('settings.llm.premiumDesc')}
                  </p>
                </div>
              </div>
              <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white border-0">
                <Sparkles className="h-4 w-4 mr-2" />
                {t('settings.llm.upgradePro')}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Model Selection */}
        <Card className={cn(
          "border-border/40",
          theme === 'dark' ? "bg-card/50" : "bg-white"
        )}>
          <CardHeader>
            <CardTitle className="text-lg">{t('settings.llm.modelSelection')}</CardTitle>
            <CardDescription>{t('settings.llm.modelSelectionDesc')}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {modelTypes.map((type) => {
              const Icon = type.icon
              return (
                <div 
                  key={type.id} 
                  className={cn(
                    "flex items-center justify-between p-4 rounded-lg",
                    theme === 'dark' ? "bg-gray-800/50" : "bg-gray-50"
                  )}
                >
                  <div className="flex items-center gap-3">
                    <div className={cn(
                      "p-2 rounded-lg",
                      theme === 'dark' ? "bg-gray-700" : "bg-white"
                    )}>
                      <Icon className={cn("h-5 w-5", type.color)} />
                    </div>
                    <div>
                      <h3 className="font-medium">{t(`settings.llm.modelType.${type.name}`)}</h3>
                      <p className={cn(
                        "text-sm",
                        theme === 'dark' ? "text-gray-400" : "text-gray-600"
                      )}>
                        {t(`settings.llm.modelType.${type.name}Desc`)}
                      </p>
                    </div>
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
              )
            })}
          </CardContent>
        </Card>

        {/* LLM Providers */}
        <Card className={cn(
          "border-border/40",
          theme === 'dark' ? "bg-card/50" : "bg-white"
        )}>
          <CardHeader>
            <CardTitle className="text-lg">{t('settings.llm.providers')}</CardTitle>
            <CardDescription>{t('settings.llm.providersDesc')}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {llmProviders.map((provider) => {
                const Icon = provider.icon
                return (
                  <div
                    key={provider.id}
                    className={cn(
                      "relative border rounded-lg p-4 cursor-pointer transition-all",
                      "hover:shadow-md",
                      selectedProvider === provider.id 
                        ? "border-primary ring-2 ring-primary/20" 
                        : theme === 'dark'
                          ? "border-gray-700 hover:border-gray-600"
                          : "border-gray-200 hover:border-gray-300"
                    )}
                    onClick={() => setSelectedProvider(provider.id)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center space-x-3">
                        <div className={cn(
                          "p-2 rounded-lg",
                          provider.bgColor
                        )}>
                          <Icon className={cn("h-6 w-6", provider.color)} />
                        </div>
                        <div>
                          <h3 className="font-medium">{provider.name}</h3>
                          <p className={cn(
                            "text-sm",
                            theme === 'dark' ? "text-gray-400" : "text-gray-600"
                          )}>
                            {provider.models.length} {t('settings.llm.models')}
                          </p>
                        </div>
                      </div>
                      <div className="flex flex-col items-end gap-2">
                        {provider.configured ? (
                          <Badge variant="default" className="text-xs">
                            <Check className="h-3 w-3 mr-1" />
                            {t('settings.llm.configured')}
                          </Badge>
                        ) : (
                          <Badge variant="secondary" className="text-xs">
                            {t('settings.llm.notConfigured')}
                          </Badge>
                        )}
                      </div>
                    </div>
                    <p className={cn(
                      "text-xs mt-3",
                      theme === 'dark' ? "text-gray-500" : "text-gray-500"
                    )}>
                      {t('settings.llm.supportedModels')}: {provider.models.join(", ")}
                    </p>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>

        {/* Provider Configuration */}
        {selectedProvider && (
          <Card className={cn(
            "border-border/40",
            theme === 'dark' ? "bg-card/50" : "bg-white"
          )}>
            <CardHeader>
              <CardTitle className="text-lg">
                {t('settings.llm.configure')} {llmProviders.find((p) => p.id === selectedProvider)?.name}
              </CardTitle>
              <CardDescription>
                {t('settings.llm.configureDesc')}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="apiKey">
                    <Key className="h-4 w-4 inline mr-2" />
                    API Key
                  </Label>
                  <Input
                    id="apiKey"
                    type="password"
                    placeholder={t('settings.llm.enterApiKey')}
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="baseUrl">
                    <Globe className="h-4 w-4 inline mr-2" />
                    Base URL ({t('common.optional')})
                  </Label>
                  <Input
                    id="baseUrl"
                    placeholder="https://api.openai.com/v1"
                    value={baseUrl}
                    onChange={(e) => setBaseUrl(e.target.value)}
                  />
                </div>
              </div>

              {testResult && (
                <Alert className={testResult.success ? "border-green-500" : "border-red-500"}>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{testResult.message}</AlertDescription>
                </Alert>
              )}

              <div className={cn(
                "p-3 rounded-lg",
                theme === 'dark' ? "bg-blue-900/20" : "bg-blue-50"
              )}>
                <p className="text-sm flex items-start gap-2">
                  <AlertCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                  <span className={cn(
                    theme === 'dark' ? "text-gray-300" : "text-gray-700"
                  )}>
                    {t('settings.llm.securityNote')}
                  </span>
                </p>
              </div>

              <div className="flex gap-2">
                <Button onClick={handleSaveConfig}>
                  <Check className="h-4 w-4 mr-2" />
                  {t('common.save')}
                </Button>
                <Button 
                  variant="outline" 
                  onClick={handleTestConnection}
                  disabled={isTesting || !apiKey}
                >
                  <TestTube className="h-4 w-4 mr-2" />
                  {isTesting ? t('common.testing') : t('settings.llm.testConnection')}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

export default SettingsLLM