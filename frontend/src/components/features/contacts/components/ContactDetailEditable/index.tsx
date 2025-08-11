"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useTranslations } from "@/lib/i18n/client"
import { MessageCircle, Edit2, Save, X, Plus, Settings2, Bot, User, Share, Check, UserCheck, UserX } from "lucide-react"
import { useState, useMemo } from "react"
import { cn } from "@/lib/utils"
import { AIAgent, ContactRequest } from '@/types/contact'
import { useShareContact } from '@/hooks/useShareContact'
import ShareContactDialog from '../ShareContactDialog'

const mockTools = [
  { id: "tool-1", name: "代码生成器", enabled: true },
  { id: "tool-2", name: "代码审查", enabled: true },
  { id: "tool-3", name: "性能分析", enabled: false },
  { id: "tool-4", name: "文档生成", enabled: true },
]

// Mock data for different contact types
const mockAgentData: AIAgent = {
  id: 'ai-coding-assistant',
  name: 'AI编程助手',
  displayName: 'CodeBot Pro',
  avatar: '/placeholder.svg?height=56&width=56',
  specialty: '全栈开发专家',
  description: '专业的代码优化和开发助手，擅长全栈开发和代码审查。提供个性化的编程解决方案。',
  status: 'online',
  type: 'agent',
  tags: ['编程', '代码审查'],
  note: '我的专属编程助手',
  isVerified: true,
  capabilities: ['code-generation', 'code-review', 'debugging', 'optimization'],
  createdAt: '2024-01-01',
  updatedAt: '2024-01-15',
}

const mockHumanData: AIAgent = {
  id: 'john-doe',
  name: 'John Doe',
  displayName: '张三',
  avatar: '/placeholder.svg?height=56&width=56',
  specialty: '产品经理',
  description: '经验丰富的产品专家，专注于用户体验和产品策略。',
  status: 'online',
  type: 'human',
  tags: ['产品', '设计', '策略'],
  note: '我的同事',
  isVerified: false,
  createdAt: '2024-01-01',
  updatedAt: '2024-01-15',
}

const mockPendingRequests: ContactRequest[] = [
  {
    id: 'req-1',
    fromUserId: 'alice-cooper',
    fromUserName: 'Alice Cooper',
    fromUserAvatar: '/placeholder.svg',
    toUserId: 'current-user',
    message: '你好，我是Alice，希望能够添加你为好友，一起讨论前端技术。我在GitHub上看到了你的项目，印象深刻。希望能够交流学习，共同进步。',
    status: 'pending',
    createdAt: '2024-01-20',
    type: 'human'
  },
  {
    id: 'req-2',
    fromUserId: 'bob-wilson',
    fromUserName: 'Bob Wilson',
    fromUserAvatar: '/placeholder.svg',
    toUserId: 'current-user',
    message: '我看到了你在技术社区的分享，很有启发，希望能够交流学习。',
    status: 'pending',
    createdAt: '2024-01-21',
    type: 'human'
  }
]

interface ContactDetailEditableProps {
  selectedItem: string
}

export function ContactDetailEditable({ selectedItem }: ContactDetailEditableProps) {
  const t = useTranslations()
  const [isEditing, setIsEditing] = useState(false)
  const [note, setNote] = useState("")
  const [tags, setTags] = useState<string[]>([])
  const [newTag, setNewTag] = useState("")
  
  const { shareDialog, openShareDialog, closeShareDialog, shareToConversation, generateShareLink } = useShareContact()

  // Determine what type of content to show based on selectedItem
  const contentData = useMemo(() => {
    if (!selectedItem) {
      // Return default state when no item is selected
      return { type: 'contact', data: mockAgentData }
    }
    
    if (selectedItem.startsWith('req-')) {
      // This is a pending request - find the specific request by ID
      const request = mockPendingRequests.find(req => req.id === selectedItem)
      return { type: 'request', data: request || mockPendingRequests[0] }
    } else if (selectedItem === 'john-doe') {
      // This is a human contact
      const humanData = { ...mockHumanData }
      return { type: 'contact', data: humanData }
    } else {
      // This is an AI agent contact  
      const agentData = { ...mockAgentData }
      return { type: 'contact', data: agentData }
    }
  }, [selectedItem])

  // Initialize form data when contact changes
  useState(() => {
    if (contentData.type === 'contact') {
      const contact = contentData.data as AIAgent
      setNote(contact.note || "")
      setTags(contact.tags || [])
    }
  })

  const handleSave = () => {
    setIsEditing(false)
    // TODO: Save logic here - call API to update contact
    console.log('Saving contact updates:', { note, tags })
  }

  const handleCancel = () => {
    setIsEditing(false)
    // Reset to original values
    if (contentData.type === 'contact') {
      const contact = contentData.data as AIAgent
      setNote(contact.note || "")
      setTags(contact.tags || [])
    }
  }

  const addTag = () => {
    if (newTag.trim() && !tags.includes(newTag.trim())) {
      setTags([...tags, newTag.trim()])
      setNewTag("")
    }
  }

  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter((tag) => tag !== tagToRemove))
  }

  const handleApproveRequest = (requestId: string) => {
    console.log('Approve request:', requestId)
    // TODO: Implement approve logic
  }

  const handleRejectRequest = (requestId: string) => {
    console.log('Reject request:', requestId)  
    // TODO: Implement reject logic
  }

  const handleShare = () => {
    if (contentData.type === 'contact') {
      openShareDialog((contentData.data as AIAgent).id)
    }
  }

  const getDisplayName = (contact: AIAgent) => {
    return contact.displayName || contact.name
  }

  if (contentData.type === 'request') {
    // Render pending request view
    const request = contentData.data as ContactRequest
    return (
      <div className="flex flex-col h-full bg-background overflow-hidden">
        <div className="flex-shrink-0 px-6 py-6 border-b border-border/60 bg-background/80 backdrop-blur-sm">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-4">
              <Avatar className="h-14 w-14 border-2 border-background shadow-lg">
                <AvatarImage src={request.fromUserAvatar} />
                <AvatarFallback className="text-lg font-semibold bg-gradient-to-br from-primary/20 to-accent/20">
                  {request.fromUserName[0]}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-1">
                  <h1 className="text-xl font-semibold text-foreground tracking-tight">
                    {request.fromUserName}
                  </h1>
                  <Badge variant="outline" className="text-xs px-2 py-1 rounded-md bg-yellow-50 dark:bg-yellow-900/50 text-yellow-700 dark:text-yellow-300 border-0 flex items-center gap-1">
                    <User className="h-3 w-3" />
                    {t('contacts.pending')}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground mb-2">
                  @{request.fromUserId}
                </p>
              </div>
            </div>
            <div className="flex flex-col space-y-2">
              <Button 
                size="sm" 
                className="shadow-sm hover:shadow-md transition-all duration-200"
                onClick={() => handleApproveRequest(request.id)}
              >
                <UserCheck className="h-4 w-4 mr-2" />
                {t('contacts.approveRequest')}
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                className="border-border/40"
                onClick={() => handleRejectRequest(request.id)}
              >
                <UserX className="h-4 w-4 mr-2" />
                {t('contacts.rejectRequest')}
              </Button>
            </div>
          </div>
        </div>

        <ScrollArea className="flex-1 overflow-y-auto overflow-x-hidden">
          <div className="px-6 py-4 space-y-6">
            <Card className="border-border/40 shadow-sm">
              <CardHeader className="pb-4">
                <CardTitle className="text-base font-semibold text-foreground tracking-tight">
                  {t('contacts.requestMessage')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm leading-relaxed text-foreground/80">
                  {request.message}
                </p>
                <div className="mt-4 text-xs text-muted-foreground">
                  {t('common.received')}: {new Date(request.createdAt).toLocaleDateString()}
                </div>
              </CardContent>
            </Card>
          </div>
        </ScrollArea>
      </div>
    )
  }

  // Render contact view
  const contact = contentData.data as AIAgent
  
  return (
    <>
      <div className="flex flex-col h-full bg-background overflow-hidden">
        {/* Header */}
        <div className="flex-shrink-0 px-6 py-6 border-b border-border/60 bg-background/80 backdrop-blur-sm">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-4">
              <Avatar className="h-14 w-14 border-2 border-background shadow-lg">
                <AvatarImage src={contact.avatar} />
                <AvatarFallback className="text-lg font-semibold bg-gradient-to-br from-primary/20 to-accent/20">
                  {getDisplayName(contact)[0]}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-1">
                  <h1 className="text-xl font-semibold text-foreground tracking-tight">
                    {getDisplayName(contact)}
                  </h1>
                  <Badge variant="outline" className="text-xs px-2 py-1 rounded-md bg-muted/50 text-muted-foreground border-0 flex items-center gap-1">
                    {contact.type === 'agent' ? (
                      <>
                        <Bot className="h-3 w-3" />
                        {t('contacts.aiAssistant')}
                      </>
                    ) : (
                      <>
                        <User className="h-3 w-3" />
                        {t('contacts.human')}
                      </>
                    )}
                  </Badge>
                  {contact.isVerified && (
                    <Check className="h-4 w-4 text-primary" />
                  )}
                </div>
                <p className="text-sm text-muted-foreground mb-2">@{contact.id}</p>
                <p className="text-primary font-medium text-sm mb-2">{contact.specialty}</p>
                <p className="text-muted-foreground text-sm leading-relaxed max-w-md">
                  {contact.description}
                </p>
                
                {/* Integrated contact info */}
                <div className="mt-3 space-y-2">
                  <div className="flex items-center space-x-3">
                    <span className="text-xs text-muted-foreground font-medium">{t('contacts.note')}:</span>
                    {isEditing ? (
                      <Input 
                        value={note} 
                        onChange={(e) => setNote(e.target.value)} 
                        placeholder={t('contacts.note')}
                        className="h-7 text-xs flex-1 max-w-xs bg-muted/30 border-border/40 rounded-md focus:bg-background focus:border-ring/20"
                      />
                    ) : (
                      <span className="text-xs text-foreground/80 bg-muted/30 px-2 py-1 rounded-md">
                        {note || getDisplayName(contact)}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className="text-xs text-muted-foreground font-medium">{t('contacts.tags')}:</span>
                    <div className="flex flex-wrap gap-1.5">
                      {tags.map((tag) => (
                        <Badge key={tag} variant="secondary" className="text-xs px-2 py-1 rounded-md bg-accent/20 text-accent-foreground border-0">
                          {tag}
                          {isEditing && (
                            <button onClick={() => removeTag(tag)} className="ml-1 text-muted-foreground hover:text-foreground transition-colors">
                              <X className="h-3 w-3" />
                            </button>
                          )}
                        </Badge>
                      ))}
                      {isEditing && (
                        <div className="flex items-center space-x-1">
                          <Input
                            value={newTag}
                            onChange={(e) => setNewTag(e.target.value)}
                            placeholder={t('contacts.newTag')}
                            className="w-20 h-6 text-xs bg-muted/30 border-border/40 rounded-md"
                            onKeyPress={(e) => e.key === "Enter" && addTag()}
                          />
                          <Button size="sm" variant="outline" onClick={addTag} className="h-6 w-6 p-0 border-border/40">
                            <Plus className="h-3 w-3" />
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="flex flex-col space-y-2">
              <Button size="sm" className="shadow-sm hover:shadow-md transition-all duration-200">
                <MessageCircle className="h-4 w-4 mr-2" />
                {t('contacts.startConversation')}
              </Button>
              {!isEditing ? (
                <>
                  <Button variant="outline" size="sm" onClick={() => setIsEditing(true)} className="border-border/40">
                    <Edit2 className="h-4 w-4 mr-2" />
                    {t('contacts.edit')}
                  </Button>
                  <Button variant="outline" size="sm" onClick={handleShare} className="border-border/40">
                    <Share className="h-4 w-4 mr-2" />
                    {t('contacts.shareContact')}
                  </Button>
                </>
              ) : (
                <div className="flex flex-col space-y-1.5">
                  <Button variant="outline" size="sm" onClick={handleSave} className="border-border/40">
                    <Save className="h-4 w-4 mr-2" />
                    {t('contacts.save')}
                  </Button>
                  <Button variant="outline" size="sm" onClick={handleCancel} className="border-border/40">
                    <X className="h-4 w-4 mr-2" />
                    {t('contacts.cancel')}
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Content */}
        <ScrollArea className="flex-1 overflow-y-auto overflow-x-hidden">
          <div className="px-6 py-4 space-y-6">
            {contact.type === 'agent' && (
              // Tool Configuration for AI agents
              <Card className="border-border/40 shadow-sm">
                <CardHeader className="pb-4">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base font-semibold text-foreground tracking-tight">
                      {t('contacts.toolConfiguration')}
                    </CardTitle>
                    <Button variant="outline" size="sm" className="border-border/40 hover:bg-accent/50 transition-all duration-200">
                      <Plus className="h-3 w-3 mr-1" />
                      {t('contacts.addTool')}
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {mockTools.map((tool) => (
                      <div 
                        key={tool.id} 
                        className={cn(
                          "flex items-center justify-between p-3 border border-border/40 rounded-lg transition-all duration-200",
                          "hover:bg-accent/30 hover:border-accent/60 hover:shadow-sm"
                        )}
                      >
                        <div className="flex items-center space-x-3">
                          <div className={cn(
                            "w-2.5 h-2.5 rounded-full transition-colors duration-200",
                            tool.enabled ? "bg-green-500 shadow-sm" : "bg-muted-foreground/40"
                          )} />
                          <span className="text-sm font-medium truncate text-foreground">{tool.name}</span>
                        </div>
                        <Button variant="ghost" size="sm" className="h-7 w-7 p-0 hover:bg-accent/50 transition-all duration-200">
                          <Settings2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Quick Share */}
            <Card className="border-border/40 shadow-sm">
              <CardHeader className="pb-4">
                <CardTitle className="text-base font-semibold text-foreground tracking-tight">
                  {t('contacts.quickShare')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center space-x-4">
                  <div className="w-20 h-20 bg-gradient-to-br from-primary/10 to-accent/10 border-2 border-dashed border-border/60 rounded-lg flex items-center justify-center hover:bg-muted/50 transition-colors duration-200">
                    <div className="text-center">
                      <Share className="h-8 w-8 text-primary mb-1 mx-auto" />
                      <div className="text-xs text-muted-foreground">{t('contacts.shareContact')}</div>
                    </div>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-muted-foreground leading-relaxed mb-3">
                      {t('contacts.shareContactDesc')}
                    </p>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" className="border-border/40 hover:bg-accent/50 transition-all duration-200" onClick={handleShare}>
                        <Share className="h-3 w-3 mr-1" />
                        {t('contacts.shareContact')}
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </ScrollArea>
      </div>

      {/* Share Contact Dialog */}
      <ShareContactDialog
        isOpen={shareDialog.isOpen}
        onClose={closeShareDialog}
        contact={shareDialog.contactId ? contact : null}
        onShareToConversation={shareToConversation}
        onGenerateShareLink={generateShareLink}
      />
    </>
  )
}

export default ContactDetailEditable