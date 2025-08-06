"use client"

import { useState } from "react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Search, Users, Plus } from "lucide-react"
import { useTranslations } from "@/lib/i18n/client"

interface AddContactDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

// Mock contacts data - this would come from the contacts store later
const mockContacts = [
  {
    id: 'agent-5',
    name: 'Content Writing Assistant',
    type: 'agent' as const,
    avatar: '/placeholder.svg?height=40&width=40',
    status: 'online' as const,
    capabilities: ['写作', '编辑', '翻译'],
    description: '专业的内容写作助手，擅长各类文档创作'
  },
  {
    id: 'agent-6',
    name: 'Marketing Specialist',
    type: 'agent' as const,
    avatar: '/placeholder.svg?height=40&width=40',
    status: 'online' as const,
    capabilities: ['营销策略', '市场分析', '广告创意'],
    description: '营销专家，提供全方位的市场营销解决方案'
  },
  {
    id: 'agent-7',
    name: 'Project Manager AI',
    type: 'agent' as const,
    avatar: '/placeholder.svg?height=40&width=40',
    status: 'busy' as const,
    capabilities: ['项目管理', '团队协调', '进度跟踪'],
    description: '智能项目管理助手，帮助团队高效协作'
  },
  {
    id: 'agent-8',
    name: 'Finance Advisor',
    type: 'agent' as const,
    avatar: '/placeholder.svg?height=40&width=40',
    status: 'offline' as const,
    capabilities: ['财务分析', '投资建议', '风险评估'],
    description: '专业的财务顾问，提供投资和理财建议'
  },
  {
    id: 'user-2',
    name: 'Alice Johnson',
    type: 'user' as const,
    avatar: '/placeholder.svg?height=40&width=40',
    status: 'online' as const,
    capabilities: [],
    description: '产品经理'
  },
  {
    id: 'user-3',
    name: 'Bob Smith',
    type: 'user' as const,
    avatar: '/placeholder.svg?height=40&width=40',
    status: 'offline' as const,
    capabilities: [],
    description: '高级开发工程师'
  }
]

export function AddContactDialog({ open, onOpenChange }: AddContactDialogProps) {
  const t = useTranslations()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedContacts, setSelectedContacts] = useState<string[]>([])

  const getAvatarFallback = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
  }

  const filteredContacts = mockContacts.filter(contact =>
    contact.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    contact.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    contact.capabilities.some(cap => cap.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  const handleContactToggle = (contactId: string) => {
    setSelectedContacts(prev => 
      prev.includes(contactId) 
        ? prev.filter(id => id !== contactId)
        : [...prev, contactId]
    )
  }

  const handleAddContacts = () => {
    // TODO: Implement actual add contacts functionality
    console.log('Adding contacts:', selectedContacts)
    // Reset state and close dialog
    setSelectedContacts([])
    setSearchQuery('')
    onOpenChange(false)
  }

  const handleCancel = () => {
    setSelectedContacts([])
    setSearchQuery('')
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            添加参与者
          </DialogTitle>
          <DialogDescription>
            选择要添加到对话中的联系人或 AI 助手
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="搜索联系人或 AI 助手..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>

          {/* Selected Count */}
          {selectedContacts.length > 0 && (
            <div className="text-sm text-muted-foreground">
              已选择 {selectedContacts.length} 个联系人
            </div>
          )}

          {/* Contact List */}
          <ScrollArea className="h-64">
            <div className="space-y-2">
              {filteredContacts.map((contact) => {
                const isSelected = selectedContacts.includes(contact.id)
                
                return (
                  <div
                    key={contact.id}
                    className={`flex items-center space-x-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                      isSelected 
                        ? 'bg-primary/10 border-primary/50' 
                        : 'hover:bg-accent/50 border-transparent'
                    }`}
                    onClick={() => handleContactToggle(contact.id)}
                  >
                    <div className="relative">
                      <Avatar className="h-10 w-10">
                        <AvatarImage src={contact.avatar} />
                        <AvatarFallback className="text-xs">
                          {getAvatarFallback(contact.name)}
                        </AvatarFallback>
                      </Avatar>
                      {contact.status === 'online' && (
                        <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 border-2 border-background rounded-full" />
                      )}
                      {isSelected && (
                        <div className="absolute -top-1 -right-1 w-5 h-5 bg-primary text-primary-foreground rounded-full flex items-center justify-center">
                          <Plus className="h-3 w-3" />
                        </div>
                      )}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <p className="font-medium text-sm text-foreground truncate">
                          {contact.name}
                        </p>
                        <Badge 
                          variant={contact.type === 'user' ? 'default' : 'secondary'} 
                          className="text-xs px-1.5 py-0.5 flex-shrink-0"
                        >
                          {contact.type === 'user' ? '用户' : 'AI'}
                        </Badge>
                      </div>
                      
                      <p className="text-xs text-muted-foreground mb-1 truncate">
                        {contact.description}
                      </p>
                      
                      {contact.capabilities.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {contact.capabilities.slice(0, 3).map((capability, index) => (
                            <Badge key={index} variant="outline" className="text-xs px-1 py-0">
                              {capability}
                            </Badge>
                          ))}
                          {contact.capabilities.length > 3 && (
                            <span className="text-xs text-muted-foreground">
                              +{contact.capabilities.length - 3}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
              
              {filteredContacts.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <Users className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">没有找到匹配的联系人</p>
                </div>
              )}
            </div>
          </ScrollArea>
        </div>

        <DialogFooter className="gap-2 sm:gap-0">
          <Button variant="outline" onClick={handleCancel}>
            取消
          </Button>
          <Button 
            onClick={handleAddContacts}
            disabled={selectedContacts.length === 0}
          >
            添加 ({selectedContacts.length})
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}