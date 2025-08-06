"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { useTranslations } from "@/lib/i18n/client"
import { useTheme } from "next-themes"
import { cn } from "@/lib/utils"
import { 
  MessageSquareQuote,
  Save,
  Plus,
  Trash2,
  Edit2,
  Copy,
  Check,
  Sparkles,
  AlertCircle,
  Globe,
  Lock,
  BookOpen,
  ExternalLink
} from "lucide-react"

interface Prompt {
  id: string
  title: string
  content: string
  category: string
  isActive: boolean
  isPublic: boolean
  usageCount: number
  createdAt: string
  updatedAt: string
}

export function SettingsPrompt() {
  const t = useTranslations()
  const { theme } = useTheme()
  const [editingPrompt, setEditingPrompt] = useState<string | null>(null)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  
  const [globalPrompt, setGlobalPrompt] = useState(
    "你是一个友好、专业的AI助手。请用简洁、准确的方式回答问题，并在需要时提供详细的解释。始终保持礼貌和耐心。"
  )
  
  const [prompts, setPrompts] = useState<Prompt[]>([
    {
      id: '1',
      title: '代码审查助手',
      content: '请作为一个经验丰富的代码审查专家，帮我审查以下代码。关注代码质量、性能优化、安全性和最佳实践。',
      category: 'development',
      isActive: true,
      isPublic: false,
      usageCount: 45,
      createdAt: '2024-03-01',
      updatedAt: '2024-03-15'
    },
    {
      id: '2',
      title: '学术写作助手',
      content: '请作为一个学术写作专家，帮助我改进文章的结构、逻辑和表达。确保引用准确，论述严谨。',
      category: 'writing',
      isActive: true,
      isPublic: true,
      usageCount: 23,
      createdAt: '2024-02-15',
      updatedAt: '2024-03-10'
    },
    {
      id: '3',
      title: '创意头脑风暴',
      content: '让我们进行创意头脑风暴。请提供独特、创新的想法，不要限制思维，越有创意越好。',
      category: 'creative',
      isActive: false,
      isPublic: false,
      usageCount: 12,
      createdAt: '2024-01-20',
      updatedAt: '2024-02-28'
    }
  ])

  const [newPrompt, setNewPrompt] = useState({
    title: '',
    content: '',
    category: 'general',
    isPublic: false
  })

  const handleSaveGlobalPrompt = () => {
    // Save global prompt
    console.log('Saving global prompt:', globalPrompt)
  }

  const handleCopyPrompt = (prompt: Prompt) => {
    navigator.clipboard.writeText(prompt.content)
    setCopiedId(prompt.id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const handleDeletePrompt = (id: string) => {
    setPrompts(prompts.filter(p => p.id !== id))
  }

  const handleToggleActive = (id: string) => {
    setPrompts(prompts.map(p => 
      p.id === id ? { ...p, isActive: !p.isActive } : p
    ))
  }

  const handleAddPrompt = () => {
    if (!newPrompt.title || !newPrompt.content) return
    
    const prompt: Prompt = {
      id: Date.now().toString(),
      ...newPrompt,
      isActive: true,
      usageCount: 0,
      createdAt: new Date().toISOString().split('T')[0],
      updatedAt: new Date().toISOString().split('T')[0]
    }
    
    setPrompts([prompt, ...prompts])
    setNewPrompt({ title: '', content: '', category: 'general', isPublic: false })
  }

  return (
    <div className={cn(
      "flex-1 p-6",
      theme === 'dark' ? 'bg-background' : 'bg-gray-50/50'
    )}>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">{t('settings.prompt.title')}</h1>
            <p className={cn(
              "text-sm mt-1",
              theme === 'dark' ? "text-gray-400" : "text-gray-600"
            )}>
              {t('settings.prompt.description')}
            </p>
          </div>
          <Button 
            variant="outline"
            onClick={() => window.open('/prompt-library', '_blank')}
            className="flex items-center gap-2"
          >
            <BookOpen className="h-4 w-4" />
            {t('settings.prompt.exploreLibrary')}
            <ExternalLink className="h-3 w-3" />
          </Button>
        </div>

        {/* Global Prompt */}
        <Card className={cn(
          "border-border/40",
          theme === 'dark' ? "bg-card/50" : "bg-white"
        )}>
          <CardHeader>
            <CardTitle className="text-lg">
              <Globe className="h-5 w-5 inline mr-2" />
              {t('settings.prompt.globalPrompt')}
            </CardTitle>
            <CardDescription>{t('settings.prompt.globalPromptDesc')}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Textarea
                value={globalPrompt}
                onChange={(e) => setGlobalPrompt(e.target.value)}
                placeholder={t('settings.prompt.globalPromptPlaceholder')}
                className="min-h-[120px]"
              />
              <div className={cn(
                "flex items-start gap-2 p-3 rounded-lg",
                theme === 'dark' ? "bg-blue-900/20" : "bg-blue-50"
              )}>
                <AlertCircle className="h-4 w-4 text-blue-600 mt-0.5" />
                <div className="text-sm">
                  <p className={cn(
                    theme === 'dark' ? "text-gray-300" : "text-gray-700"
                  )}>
                    {t('settings.prompt.globalPromptHint')}
                  </p>
                </div>
              </div>
              <div className="flex justify-end">
                <Button onClick={handleSaveGlobalPrompt}>
                  <Save className="h-4 w-4 mr-2" />
                  {t('common.save')}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Add New Prompt */}
        <Card className={cn(
          "border-border/40",
          theme === 'dark' ? "bg-card/50" : "bg-white"
        )}>
          <CardHeader>
            <CardTitle className="text-lg">
              <Plus className="h-5 w-5 inline mr-2" />
              {t('settings.prompt.addPrompt')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>{t('settings.prompt.promptTitle')}</Label>
                  <Input
                    value={newPrompt.title}
                    onChange={(e) => setNewPrompt({ ...newPrompt, title: e.target.value })}
                    placeholder={t('settings.prompt.promptTitlePlaceholder')}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{t('settings.prompt.category')}</Label>
                  <Input
                    value={newPrompt.category}
                    onChange={(e) => setNewPrompt({ ...newPrompt, category: e.target.value })}
                    placeholder={t('settings.prompt.categoryPlaceholder')}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label>{t('settings.prompt.promptContent')}</Label>
                <Textarea
                  value={newPrompt.content}
                  onChange={(e) => setNewPrompt({ ...newPrompt, content: e.target.value })}
                  placeholder={t('settings.prompt.promptContentPlaceholder')}
                  className="min-h-[100px]"
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={newPrompt.isPublic}
                    onCheckedChange={(checked) => setNewPrompt({ ...newPrompt, isPublic: checked })}
                  />
                  <Label className="text-sm cursor-pointer">
                    {t('settings.prompt.makePublic')}
                  </Label>
                </div>
                <Button 
                  onClick={handleAddPrompt}
                  disabled={!newPrompt.title || !newPrompt.content}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  {t('settings.prompt.addBtn')}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Prompt Library */}
        <Card className={cn(
          "border-border/40",
          theme === 'dark' ? "bg-card/50" : "bg-white"
        )}>
          <CardHeader>
            <CardTitle className="text-lg">
              <Sparkles className="h-5 w-5 inline mr-2" />
              {t('settings.prompt.library')}
            </CardTitle>
            <CardDescription>{t('settings.prompt.libraryDesc')}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {prompts.map((prompt) => (
                <div
                  key={prompt.id}
                  className={cn(
                    "p-4 rounded-lg border",
                    theme === 'dark' 
                      ? "bg-gray-800/50 border-gray-700" 
                      : "bg-gray-50 border-gray-200",
                    !prompt.isActive && "opacity-60"
                  )}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium">{prompt.title}</h4>
                      <Badge variant="secondary" className="text-xs">
                        {prompt.category}
                      </Badge>
                      {prompt.isPublic ? (
                        <Globe className="h-3 w-3 text-muted-foreground" />
                      ) : (
                        <Lock className="h-3 w-3 text-muted-foreground" />
                      )}
                    </div>
                    <div className="flex items-center gap-1">
                      <Switch
                        checked={prompt.isActive}
                        onCheckedChange={() => handleToggleActive(prompt.id)}
                      />
                    </div>
                  </div>
                  <p className={cn(
                    "text-sm mb-3",
                    theme === 'dark' ? "text-gray-400" : "text-gray-600"
                  )}>
                    {prompt.content}
                  </p>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>{t('settings.prompt.used')}: {prompt.usageCount}</span>
                      <span>{t('settings.prompt.updated')}: {prompt.updatedAt}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleCopyPrompt(prompt)}
                      >
                        {copiedId === prompt.id ? (
                          <Check className="h-4 w-4" />
                        ) : (
                          <Copy className="h-4 w-4" />
                        )}
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => setEditingPrompt(prompt.id)}
                      >
                        <Edit2 className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleDeletePrompt(prompt.id)}
                        className="text-destructive hover:text-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default SettingsPrompt