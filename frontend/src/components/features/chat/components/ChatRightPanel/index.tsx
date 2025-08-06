"use client"

import { useState } from "react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { 
  X, 
  Plus, 
  Users, 
  FileText, 
  ChevronDown, 
  ChevronRight, 
  Brain,
  Forward,
  Eye,
  Download,
  Share
} from "lucide-react"
import { useTranslations } from "@/lib/i18n/client"
import type { Conversation } from "@/store/slices/chatSlice"
import { AddContactDialog } from "./AddContactDialog"
import { ConversationSummaryDialog } from "./ConversationSummaryDialog"

interface ChatRightPanelProps {
  conversation: Conversation
  isOpen: boolean
  onClose: () => void
}

// Mock data for files
const mockFiles = [
  {
    id: '1',
    name: 'project-proposal.pdf',
    type: 'application/pdf',
    size: '2.3 MB',
    uploadedAt: new Date(Date.now() - 3600000).toISOString(),
    url: '#'
  },
  {
    id: '2',
    name: 'code-review.md',
    type: 'text/markdown',
    size: '15 KB',
    uploadedAt: new Date(Date.now() - 7200000).toISOString(),
    url: '#'
  },
  {
    id: '3',
    name: 'analysis-report.xlsx',
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    size: '890 KB',
    uploadedAt: new Date(Date.now() - 86400000).toISOString(),
    url: '#'
  },
  {
    id: '4',
    name: 'meeting-notes.docx',
    type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    size: '45 KB',
    uploadedAt: new Date(Date.now() - 172800000).toISOString(),
    url: '#'
  }
]

// Mock data for conversation summary
const mockSummary = {
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

export function ChatRightPanel({ conversation, isOpen, onClose }: ChatRightPanelProps) {
  const t = useTranslations()
  const [isFilesExpanded, setIsFilesExpanded] = useState(true)
  const [showAddContactDialog, setShowAddContactDialog] = useState(false)
  const [showSummaryDialog, setShowSummaryDialog] = useState(false)

  const getAvatarFallback = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
  }


  const handleForwardFile = (file: any) => {
    // TODO: Implement file forwarding functionality
    console.log('Forwarding file:', file.name)
  }

  const handleDownloadFile = (file: any) => {
    // TODO: Implement file download functionality
    console.log('Downloading file:', file.name)
    // Create a temporary link and trigger download
    const link = document.createElement('a')
    link.href = file.url || '#'
    link.download = file.name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleShareToConversation = (file: any) => {
    // TODO: Implement share to conversation functionality
    console.log('Sharing file to conversation:', file.name)
  }

  const formatFileSize = (size: string) => size

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
    <>
      {/* Overlay */}
      <div 
        className={`fixed inset-0 bg-black/20 z-40 lg:hidden transition-opacity duration-300 ${
          isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
        onClick={onClose}
      />
      
      {/* Right Panel */}
      <div className={`fixed right-0 top-0 h-full w-80 bg-card border-l border-border z-50 flex flex-col shadow-lg lg:relative lg:shadow-none transform transition-transform duration-300 ease-in-out ${
        isOpen 
          ? 'translate-x-0 lg:w-80' 
          : 'translate-x-full lg:w-0 lg:overflow-hidden'
      }`}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h3 className="font-semibold text-foreground">{t('chat.rightPanel.title')}</h3>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={onClose}
            type="button"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        <ScrollArea className="flex-1">
          <div className="p-4 space-y-6">
            {/* Participants Section */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <Users className="h-4 w-4 text-muted-foreground" />
                  <span className="font-medium text-sm">{t('chat.rightPanel.participants')} ({conversation.participants.length})</span>
                </div>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => setShowAddContactDialog(true)}
                  className="h-7 w-7 p-0"
                  title={t('chat.rightPanel.addParticipant')}
                >
                  <Plus className="h-3 w-3" />
                </Button>
              </div>
              
              <div className="space-y-2">
                {conversation.participants.map((participant) => (
                  <div key={participant.id} className="flex items-center space-x-3 p-2 rounded-lg hover:bg-accent/50 transition-colors">
                    <div className="relative">
                      <Avatar className="h-9 w-9">
                        <AvatarImage src={participant.avatar} />
                        <AvatarFallback className="text-xs">
                          {getAvatarFallback(participant.name)}
                        </AvatarFallback>
                      </Avatar>
                      {participant.status === 'online' && (
                        <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 border-2 border-card rounded-full" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-foreground truncate">
                        {participant.name}
                      </p>
                      <div className="flex items-center space-x-2">
                        <Badge 
                          variant={participant.type === 'user' ? 'default' : 'secondary'} 
                          className="text-xs px-1.5 py-0.5"
                        >
                          {t(`chat.rightPanel.${participant.type === 'user' ? 'user' : 'ai'}`)}
                        </Badge>
                        <span className={`text-xs ${
                          participant.status === 'online' ? 'text-green-600' : 'text-muted-foreground'
                        }`}>
                          {t(`chat.rightPanel.${participant.status === 'online' ? 'online' : 'offline'}`)}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <Separator />

            {/* Files Section */}
            <div>
              <div 
                className="flex items-center justify-between mb-3 cursor-pointer"
                onClick={() => setIsFilesExpanded(!isFilesExpanded)}
              >
                <div className="flex items-center space-x-2">
                  <FileText className="h-4 w-4 text-muted-foreground" />
                  <span className="font-medium text-sm">{t('chat.rightPanel.files')} ({mockFiles.length})</span>
                </div>
                {isFilesExpanded ? (
                  <ChevronDown className="h-4 w-4 text-muted-foreground" />
                ) : (
                  <ChevronRight className="h-4 w-4 text-muted-foreground" />
                )}
              </div>

              {isFilesExpanded && (
                <div className="space-y-2">
                  {mockFiles.map((file) => (
                    <div key={file.id} className="flex items-center space-x-3 p-2 rounded-lg hover:bg-accent/50 transition-colors">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground truncate">
                          {file.name}
                        </p>
                        <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                          <span>{formatFileSize(file.size)}</span>
                          <span>•</span>
                          <span>{formatTimeAgo(file.uploadedAt)}</span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="h-7 w-7 p-0"
                          onClick={() => handleDownloadFile(file)}
                          title={t('chat.rightPanel.downloadFile')}
                        >
                          <Download className="h-3 w-3" />
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="h-7 w-7 p-0"
                          onClick={() => handleShareToConversation(file)}
                          title={t('chat.rightPanel.shareToConversation')}
                        >
                          <Share className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <Separator />

            {/* Conversation Memory Section */}
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
                    {mockSummary.coreSummary}
                  </p>
                  <p className="text-xs text-muted-foreground mt-2">
                    {t('chat.rightPanel.lastUpdated')}: {formatTimeAgo(mockSummary.lastUpdated)}
                  </p>
                </div>

              </div>
            </div>
          </div>
        </ScrollArea>

        {/* Dialogs */}
        <AddContactDialog 
          open={showAddContactDialog}
          onOpenChange={setShowAddContactDialog}
        />
        
        <ConversationSummaryDialog
          open={showSummaryDialog}
          onOpenChange={setShowSummaryDialog}
          summary={mockSummary}
          conversationTitle={conversation.title}
        />
      </div>
    </>
  )
}

export default ChatRightPanel