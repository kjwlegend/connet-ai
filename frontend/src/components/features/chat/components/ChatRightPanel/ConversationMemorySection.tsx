"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Brain, Eye } from "lucide-react"
import { useTranslations } from "@/lib/i18n/client"
import { ConversationSummaryDialog } from "./ConversationSummaryDialog"

interface ConversationSummary {
  coreSummary: string
  todos: Array<{
    id: string
    text: string
    completed: boolean
    assignee: string
    createdBy: string
    createdAt: string
  }>
  lastUpdated: string
}

interface ConversationMemorySectionProps {
  conversationTitle: string
  summary?: ConversationSummary
}

// Mock data for conversation summary
const mockSummary: ConversationSummary = {
  coreSummary: "本次对话主要围绕新产品的技术架构设计展开讨论。团队确定了使用微服务架构和容器化部署的技术方案，深入分析了React + Node.js技术栈的优势，并讨论了性能优化的关键要点。同时制定了详细的开发计划，包括技术方案文档编写、UI/UX设计和技术可行性分析等关键环节。整个讨论过程中，各AI助手从不同角度提供了专业建议，为项目的成功实施奠定了坚实基础。",
  todos: [
    {
      id: '1',
      text: '完成技术方案文档编写',
      completed: false,
      assignee: 'AI Programming Assistant',
      createdBy: 'ai',
      createdAt: new Date(Date.now() - 3600000).toISOString()
    },
    {
      id: '2', 
      text: '准备UI/UX设计原型方案',
      completed: true,
      assignee: 'Design Review Agent',
      createdBy: 'ai',
      createdAt: new Date(Date.now() - 7200000).toISOString()
    },
    {
      id: '3',
      text: '进行技术可行性分析报告',
      completed: false,
      assignee: 'Data Analysis Expert', 
      createdBy: 'ai',
      createdAt: new Date(Date.now() - 86400000).toISOString()
    },
    {
      id: '4',
      text: '确认服务器部署环境配置',
      completed: false,
      assignee: 'DevOps Specialist',
      createdBy: 'human',
      createdAt: new Date(Date.now() - 1800000).toISOString()
    }
  ],
  lastUpdated: new Date().toISOString()
}

export function ConversationMemorySection({ 
  conversationTitle, 
  summary = mockSummary 
}: ConversationMemorySectionProps) {
  const t = useTranslations()
  const [showSummaryDialog, setShowSummaryDialog] = useState(false)

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date()
    const time = new Date(timestamp)
    const diffMs = now.getTime() - time.getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffHours / 24)

    if (diffDays > 0) return `${diffDays}天前`
    if (diffHours > 0) return `${diffHours}小时前`
    return '刚刚'
  }

  return (
    <div>
      <div className="flex items-center space-x-2 mb-3">
        <Brain className="h-4 w-4 text-muted-foreground" />
        <span className="font-medium text-sm">{t('chat.rightPanel.summary')}</span>
      </div>

      <div className="space-y-4">
        {/* Core Summary */}
        <div className="bg-accent/30 rounded-lg p-3">
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs text-muted-foreground font-medium">{t('chat.rightPanel.coreSummary')}</p>
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => setShowSummaryDialog(true)}
              className="h-6 text-xs px-2"
            >
              <Eye className="h-3 w-3 mr-1" />
              {t('chat.rightPanel.viewDetails')}
            </Button>
          </div>
          <p className="text-sm text-foreground leading-relaxed">
            {summary.coreSummary}
          </p>
          <p className="text-xs text-muted-foreground mt-2">
            {t('chat.rightPanel.lastUpdated')}: {formatTimeAgo(summary.lastUpdated)}
          </p>
        </div>
      </div>

      <ConversationSummaryDialog
        open={showSummaryDialog}
        onOpenChange={setShowSummaryDialog}
        summary={summary}
        conversationTitle={conversationTitle}
      />
    </div>
  )
}

export default ConversationMemorySection