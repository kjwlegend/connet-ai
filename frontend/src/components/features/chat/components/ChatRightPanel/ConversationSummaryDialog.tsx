'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Brain,
  Target,
  Download,
  RefreshCw,
  Lightbulb,
  Users,
  Calendar,
  Bot,
  User,
  CheckSquare,
  Square,
  Plus,
  Check,
  X,
  Trash2,
  Circle
} from 'lucide-react'
import { useTranslations } from '@/lib/i18n/client'

interface ConversationSummary {
  coreSummary?: string
  todos?: {
    id: string
    text: string
    completed: boolean
    assignee: string
    createdBy: 'ai' | 'human'
    createdAt: string
  }[]
  lastUpdated?: string
}

interface ConversationSummaryDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  summary: ConversationSummary | null | undefined
  conversationTitle?: string
}

export function ConversationSummaryDialog({
  open,
  onOpenChange,
  summary,
  conversationTitle = '',
}: ConversationSummaryDialogProps) {
  const t = useTranslations()
  const [isRegenerating, setIsRegenerating] = useState(false)
  const [todos, setTodos] = useState(summary?.todos || [])
  const [newTodoText, setNewTodoText] = useState('')
  const [isAddingTodo, setIsAddingTodo] = useState(false)

  // Safe fallbacks for undefined data
  const safeSummary = summary || {}
  const safeCoreSummary = safeSummary.coreSummary || t('chat.rightPanel.noSummaryAvailable') || '暂无摘要内容'
  const safeLastUpdated = safeSummary.lastUpdated || new Date().toISOString()
  const safeConversationTitle = conversationTitle || t('chat.rightPanel.untitledConversation') || '未命名对话'

  // Sync todos with summary when it changes
  useState(() => {
    if (summary?.todos) {
      setTodos(summary.todos)
    }
  })

  const formatTimeAgo = (timestamp?: string) => {
    if (!timestamp) return t('ui.unknown') || '未知'
    
    try {
      const now = new Date()
      const time = new Date(timestamp)
      const diffMs = now.getTime() - time.getTime()
      
      // Check for invalid date
      if (isNaN(diffMs)) return t('ui.unknown') || '未知'
      
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
      const diffDays = Math.floor(diffHours / 24)

      if (diffDays > 0) return `${diffDays}天前`
      if (diffHours > 0) return `${diffHours}小时前`
      return '刚刚'
    } catch (error) {
      console.error('Error formatting time:', error)
      return t('ui.unknown') || '未知'
    }
  }

  const handleRegenerate = async () => {
    setIsRegenerating(true)
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 2000))
    } catch (error) {
      console.error('Error regenerating summary:', error)
    } finally {
      setIsRegenerating(false)
    }
  }

  const toggleTodo = (todoId: string) => {
    setTodos(prev => prev.map(todo => 
      todo.id === todoId ? { ...todo, completed: !todo.completed } : todo
    ))
  }

  const deleteTodo = (todoId: string) => {
    setTodos(prev => prev.filter(todo => todo.id !== todoId))
  }

  const addTodo = () => {
    if (!newTodoText.trim()) return
    
    const newTodo = {
      id: Date.now().toString(),
      text: newTodoText.trim(),
      completed: false,
      assignee: 'You',
      createdBy: 'human' as const,
      createdAt: new Date().toISOString()
    }
    
    setTodos(prev => [...prev, newTodo])
    setNewTodoText('')
    setIsAddingTodo(false)
  }

  const handleExport = () => {
    try {
      // Generate markdown content with null safety
      const todoSection = todos.length > 0 
        ? todos.map((todo) => `- [${todo.completed ? 'x' : ' '}] ${todo.text || 'Untitled task'} (${todo.assignee || 'Unassigned'})`).join('\n')
        : '暂无任务'

      const markdown = `# ${safeConversationTitle} - 对话摘要

## 📝 核心摘要

${safeCoreSummary}

## ✅ 任务清单

${todoSection}

---

*生成时间: ${new Date().toLocaleString('zh-CN')}*
*最后更新: ${formatTimeAgo(safeLastUpdated)}*
`

      // Download the file
      const blob = new Blob([markdown], { type: 'text/markdown' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${safeConversationTitle
        .replace(/[^a-z0-9\u4e00-\u9fa5]/gi, '_')
        .toLowerCase()}_summary.md`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error exporting summary:', error)
    }
  }

  // Don't render if no summary data at all
  if (!summary && !conversationTitle) {
    return null
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-primary" />
            {t('chat.rightPanel.summary') || '对话记忆'}
          </DialogTitle>
          <div className="flex items-center justify-between">
            <DialogDescription className="truncate">{safeConversationTitle}</DialogDescription>
            <span className="flex items-center gap-2 text-xs text-muted-foreground flex-shrink-0">
              <Calendar className="h-3 w-3" />
              {t('chat.rightPanel.lastUpdated') || '最后更新'}: {formatTimeAgo(safeLastUpdated)}
            </span>
          </div>
        </DialogHeader>

        <Tabs defaultValue="summary" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="summary" className="text-xs">
              <Lightbulb className="h-3 w-3 mr-1" />
              {t('chat.rightPanel.coreSummary') || '核心摘要'}
            </TabsTrigger>
            <TabsTrigger value="todos" className="text-xs">
              <Target className="h-3 w-3 mr-1" />
              {t('chat.rightPanel.todoList') || '任务清单'}
            </TabsTrigger>
          </TabsList>

          <ScrollArea className="h-96 mt-4">
            <TabsContent value="summary" className="mt-0">
              <div className="space-y-4">
                <div className="bg-accent/30 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Lightbulb className="h-4 w-4 text-primary" />
                    <h4 className="font-medium">{t('chat.rightPanel.coreSummary') || '核心摘要'}</h4>
                  </div>
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <p className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">
                      {safeCoreSummary}
                    </p>
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="todos" className="mt-0">
              <div className="space-y-3">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Target className="h-5 w-5 text-blue-600" />
                    <h4 className="font-medium">{t('chat.rightPanel.todoList') || '任务清单'}</h4>
                    <Badge variant="secondary" className="text-xs">
                      {todos.length} 项
                    </Badge>
                  </div>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => setIsAddingTodo(true)}
                    className="h-6 w-6 p-0"
                    title={t('chat.rightPanel.addTodo')}
                  >
                    <Plus className="h-3 w-3" />
                  </Button>
                </div>
                
                <div className="space-y-2">
                  {todos.map((todo) => {
                    const safeId = todo.id || `todo-${Math.random()}`
                    const safeText = todo.text || t('chat.rightPanel.untitledTask') || '未命名任务'
                    const safeAssignee = todo.assignee || t('ui.unassigned') || '未分配'
                    const safeCreatedBy = todo.createdBy || 'ai'
                    const safeCompleted = Boolean(todo.completed)
                    const safeCreatedAt = todo.createdAt || new Date().toISOString()

                    return (
                      <div key={safeId} className="flex items-start space-x-2 p-2 rounded-lg hover:bg-accent/50 transition-colors group">
                        <Checkbox 
                          checked={safeCompleted}
                          onCheckedChange={() => toggleTodo(safeId)}
                          className="mt-0.5"
                        />
                        <div className="flex-1 min-w-0">
                          <p className={`text-sm ${safeCompleted ? 'line-through text-muted-foreground' : 'text-foreground'}`}>
                            {safeText}
                          </p>
                          <div className="flex items-center space-x-2 text-xs text-muted-foreground mt-1">
                            <div className="flex items-center space-x-1">
                              {safeCreatedBy === 'ai' ? (
                                <Bot className="h-3 w-3" />
                              ) : (
                                <User className="h-3 w-3" />
                              )}
                              <span>{safeAssignee}</span>
                            </div>
                            <span>•</span>
                            <span>{formatTimeAgo(safeCreatedAt)}</span>
                          </div>
                        </div>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => deleteTodo(safeId)}
                          className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                          title={t('chat.rightPanel.deleteTodo')}
                        >
                          <Trash2 className="h-3 w-3 text-destructive" />
                        </Button>
                      </div>
                    )
                  })}
                  
                  {/* Add Todo Input */}
                  {isAddingTodo && (
                    <div className="flex items-center space-x-2 p-2 border border-border rounded-lg">
                      <Circle className="h-4 w-4 text-muted-foreground" />
                      <Input 
                        value={newTodoText}
                        onChange={(e) => setNewTodoText(e.target.value)}
                        placeholder={t('chat.rightPanel.addTodoPlaceholder')}
                        className="flex-1 h-7 text-sm border-none p-0 focus-visible:ring-0"
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault()
                            addTodo()
                          } else if (e.key === 'Escape') {
                            setIsAddingTodo(false)
                            setNewTodoText('')
                          }
                        }}
                        autoFocus
                      />
                      <div className="flex items-center space-x-1">
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={addTodo}
                          className="h-6 w-6 p-0 text-green-600 hover:text-green-700"
                          title={t('ui.save')}
                        >
                          <Check className="h-3 w-3" />
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => {
                            setIsAddingTodo(false)
                            setNewTodoText('')
                          }}
                          className="h-6 w-6 p-0 text-muted-foreground hover:text-foreground"
                          title={t('ui.cancel')}
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  )}
                  
                  {todos.length === 0 && !isAddingTodo && (
                    <div className="text-center py-8 text-muted-foreground">
                      <Target className="h-12 w-12 mx-auto mb-3 opacity-50" />
                      <p className="text-sm">{t('chat.rightPanel.noTodos') || '暂无任务'}</p>
                    </div>
                  )}
                </div>
              </div>
            </TabsContent>
          </ScrollArea>
        </Tabs>

        <Separator />

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-muted-foreground" />
            <span className="text-xs text-muted-foreground">
              {t('chat.rightPanel.autoGenerated') || '由 AI 助手自动生成和更新'}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRegenerate}
              disabled={isRegenerating}
            >
              {isRegenerating ? (
                <>
                  <RefreshCw className="h-3 w-3 mr-1 animate-spin" />
                  {t('chat.rightPanel.regenerating') || '重新生成中...'}
                </>
              ) : (
                <>
                  <RefreshCw className="h-3 w-3 mr-1" />
                  {t('chat.rightPanel.regenerate') || '重新生成'}
                </>
              )}
            </Button>

            <Button size="sm" onClick={handleExport}>
              <Download className="h-3 w-3 mr-1" />
              {t('chat.rightPanel.export') || '导出摘要'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}