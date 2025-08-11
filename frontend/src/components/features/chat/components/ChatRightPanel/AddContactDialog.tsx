'use client'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useTranslations } from '@/lib/i18n/client'
import { Search, Bot, User, Plus, Check, UserPlus } from 'lucide-react'
import { useState, useEffect, useMemo } from 'react'
import { cn } from '@/lib/utils'

interface Contact {
  id: string
  name: string
  displayName?: string
  type: 'agent' | 'user'
  avatar: string
  status: 'online' | 'busy' | 'offline'
  capabilities?: string[]
  description: string
  specialty?: string
  tags?: string[]
  isVerified?: boolean
  isAlreadyContact?: boolean
}

interface AddContactDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onAddContacts?: (contactIds: string[]) => void
  existingContacts?: Contact[]
}

// Enhanced recommended AI agents (only agents, no humans)
const recommendedContacts: Contact[] = [
  {
    id: 'ai-coding-assistant',
    name: 'AI编程助手',
    displayName: 'CodeBot Pro',
    avatar: '/placeholder.svg',
    specialty: '全栈开发',
    description: '专业的代码优化和开发助手，支持多种编程语言',
    status: 'online',
    type: 'agent',
    tags: ['开发', '代码审查', '优化'],
    isVerified: true
  },
  {
    id: 'design-ai',
    name: 'AI设计师',
    displayName: 'DesignBot',
    avatar: '/placeholder.svg',
    specialty: 'UI/UX设计',
    description: '创意设计和界面优化专家，专注用户体验',
    status: 'online',
    type: 'agent',
    tags: ['设计', 'UI', 'UX'],
    isVerified: true
  },
  {
    id: 'data-analyst',
    name: '数据分析师',
    displayName: 'DataBot',
    avatar: '/placeholder.svg',
    specialty: '数据科学',
    description: '专业数据分析和洞察专家，支持多种数据源',
    status: 'busy',
    type: 'agent',
    tags: ['数据', '分析', '洞察'],
    isVerified: true
  },
  {
    id: 'marketing-ai',
    name: 'AI营销专家',
    displayName: 'MarketBot',
    avatar: '/placeholder.svg',
    specialty: '数字营销',
    description: '专业营销策略和推广方案专家',
    status: 'online',
    type: 'agent',
    tags: ['营销', '推广', '策略'],
    isVerified: true
  },
  {
    id: 'content-ai',
    name: 'AI内容创作',
    displayName: 'ContentBot',
    avatar: '/placeholder.svg',
    specialty: '内容创作',
    description: '专业文案写作和内容策划专家',
    status: 'online',
    type: 'agent',
    tags: ['写作', '内容', '创意'],
    isVerified: true
  }
]

export function AddContactDialog({ open, onOpenChange, onAddContacts, existingContacts = [] }: AddContactDialogProps) {
  const t = useTranslations()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedContacts, setSelectedContacts] = useState<string[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [searchResults, setSearchResults] = useState<Contact[]>([])

  // Category tags for filtering
  const categories = [
    { id: 'all', name: '全部联系人', tags: [] },
    { id: 'development', name: '开发', tags: ['开发', '代码审查', '优化'] },
    { id: 'design', name: '设计', tags: ['设计', 'UI', 'UX'] },
    { id: 'marketing', name: '营销', tags: ['营销', '推广', '策略'] },
    { id: 'productivity', name: '生产力', tags: ['生产力', '效率', '管理'] },
    { id: 'content', name: '内容', tags: ['写作', '内容', '创意'] },
    { id: 'data', name: '数据', tags: ['数据', '分析', '洞察'] }
  ]

  const getAvatarFallback = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
  }

  const getDisplayName = (contact: Contact) => {
    return contact.displayName || contact.name
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'bg-green-500'
      case 'busy': return 'bg-yellow-500' 
      case 'offline': return 'bg-gray-400'
      default: return 'bg-gray-400'
    }
  }

  const displayedContacts = useMemo(() => {
    const existingIds = new Set(existingContacts.map(c => c.id))
    const contactsToFilter = searchQuery.trim() ? searchResults : recommendedContacts
    
    // Filter by category
    let filteredContacts = contactsToFilter
    if (selectedCategory !== 'all') {
      const categoryData = categories.find(c => c.id === selectedCategory)
      if (categoryData) {
        filteredContacts = contactsToFilter.filter(contact => 
          contact.tags?.some(tag => categoryData.tags.includes(tag))
        )
      }
    }
    
    return filteredContacts
      .filter(contact => contact.type === 'agent') // Only show AI agents in recommendations
      .map(contact => ({
        ...contact,
        isAlreadyContact: existingIds.has(contact.id)
      }))
  }, [searchQuery, searchResults, recommendedContacts, existingContacts, selectedCategory, categories])

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    if (!query.trim()) {
      setSearchResults([])
      return
    }

    // Simulate search - in real implementation, this would call an API
    const results = recommendedContacts.filter(contact =>
      contact.name.toLowerCase().includes(query.toLowerCase()) ||
      contact.description.toLowerCase().includes(query.toLowerCase()) ||
      contact.tags?.some(tag => tag.toLowerCase().includes(query.toLowerCase()))
    )
    setSearchResults(results)
  }

  const handleContactToggle = (contactId: string) => {
    setSelectedContacts(prev => 
      prev.includes(contactId) 
        ? prev.filter(id => id !== contactId)
        : [...prev, contactId]
    )
  }

  const handleAddContacts = () => {
    if (onAddContacts) {
      onAddContacts(selectedContacts)
    }
    // Reset state and close dialog
    setSelectedContacts([])
    setSearchQuery('')
    setSearchResults([])
    onOpenChange(false)
  }

  const handleCancel = () => {
    setSelectedContacts([])
    setSearchQuery('')
    setSearchResults([])
    onOpenChange(false)
  }

  const ContactItem = ({ contact }: { contact: Contact }) => {
    const isSelected = selectedContacts.includes(contact.id)
    const isAlreadyContact = contact.isAlreadyContact
    
    return (
      <div
        className={cn(
          'group relative p-2 rounded-lg cursor-pointer transition-all duration-200 border',
          'hover:shadow-md hover:scale-[1.02] hover:border-primary/40',
          'w-[250px] h-[125px] flex flex-col justify-between',
          isSelected
            ? 'bg-primary/5 border-primary shadow-sm' 
            : 'bg-card border-border/40 hover:bg-accent/30'
        )}
        onClick={() => !isAlreadyContact && handleContactToggle(contact.id)}
      >
        {/* Status indicator & verification & selection */}
        <div className="absolute top-1.5 right-1.5 flex items-center space-x-1">
          <div className={cn(
            'w-1.5 h-1.5 rounded-full',
            getStatusColor(contact.status)
          )} />
          {contact.isVerified && (
            <Check className="h-2.5 w-2.5 text-primary" />
          )}
          {isSelected && (
            <div className="w-4 h-4 bg-primary text-primary-foreground rounded-full flex items-center justify-center">
              <Check className="h-2.5 w-2.5" />
            </div>
          )}
        </div>
        
        {/* Top Section: Avatar & Name */}
        <div className="flex items-start space-x-2 flex-1">
          <Avatar className="h-8 w-8 border border-background shadow-sm flex-shrink-0">
            <AvatarImage src={contact.avatar} />
            <AvatarFallback className="text-xs font-semibold">
              {getDisplayName(contact)[0]}
            </AvatarFallback>
          </Avatar>
          
          <div className="flex-1 min-w-0 space-y-1">
            <h4 className="font-medium text-xs truncate leading-tight">
              {getDisplayName(contact)}
            </h4>
            <div className="text-xs text-muted-foreground truncate">@{contact.id}</div>
            <div className="text-xs text-foreground/80 truncate font-medium">
              {contact.specialty}
            </div>
          </div>
        </div>
        
        {/* Bottom Section: Tags & Status */}
        <div className="space-y-1.5">
          {/* Tags */}
          <div className="flex flex-wrap gap-1">
            {contact.tags?.slice(0, 2).map((tag) => (
              <Badge
                key={tag}
                variant="secondary"
                className="text-xs px-1 py-0 bg-accent/20 text-accent-foreground h-4"
              >
                {tag}
              </Badge>
            ))}
            {(contact.tags?.length || 0) > 2 && (
              <Badge
                variant="secondary"
                className="text-xs px-1 py-0 bg-accent/20 text-accent-foreground h-4"
              >
                +{(contact.tags?.length || 0) - 2}
              </Badge>
            )}
          </div>
          
          {/* Status */}
          <div className="flex justify-end">
            {isAlreadyContact ? (
              <Badge variant="secondary" className="text-xs py-0.5 px-1.5 h-5">
                已添加
              </Badge>
            ) : isSelected ? (
              <Badge variant="default" className="text-xs py-0.5 px-1.5 h-5">
                已选择
              </Badge>
            ) : (
              <div className="h-5" />
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl md:max-w-4xl max-h-[90vh] w-[90vw]">
        <DialogHeader>
          <DialogTitle className="text-xl">添加参与者</DialogTitle>
          <DialogDescription>
            选择要添加到对话中的联系人或 AI 助手
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-6">
          {/* Search Input */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="搜索联系人或 AI 助手..."
              className="pl-10 h-12 text-base bg-muted/30 border-border/40 rounded-lg focus:bg-background focus:border-ring/20"
            />
          </div>

          {/* Category Filter Tags */}
          {!searchQuery.trim() && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-medium text-foreground">
                  分类
                </h4>
                <Badge variant="secondary" className="text-xs">
                  {displayedContacts.length} AI 助手
                </Badge>
              </div>
              <div className="flex flex-wrap gap-2">
                {categories.map((category) => (
                  <Button
                    key={category.id}
                    variant={selectedCategory === category.id ? "default" : "outline"}
                    size="sm"
                    className={cn(
                      "h-8 px-3 text-sm transition-all duration-200",
                      selectedCategory === category.id
                        ? "bg-primary text-primary-foreground shadow-sm"
                        : "hover:bg-accent/50 border-border/60"
                    )}
                    onClick={() => setSelectedCategory(category.id)}
                  >
                    {category.name}
                  </Button>
                ))}
              </div>
            </div>
          )}

          {/* Selected Count */}
          {selectedContacts.length > 0 && (
            <div className="text-sm text-muted-foreground">
              已选择 {selectedContacts.length} 个联系人
            </div>
          )}

          {/* Contact Grid */}
          <ScrollArea className="h-[400px]">
            <div className="space-y-4">
              {!searchQuery.trim() && (
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-medium text-muted-foreground">
                    {selectedCategory === 'all' ? '推荐联系人' : categories.find(c => c.id === selectedCategory)?.name}
                  </h4>
                </div>
              )}
              
              {displayedContacts.length === 0 && searchQuery.trim() ? (
                <div className="text-center py-12">
                  <div className="text-muted-foreground text-base">
                    没有找到匹配 "{searchQuery}" 的联系人
                  </div>
                </div>
              ) : displayedContacts.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-muted-foreground text-base">
                    没有找到联系人
                  </div>
                </div>
              ) : (
                <div className="flex flex-wrap justify-center gap-4">
                  {displayedContacts.map((contact) => (
                    <ContactItem key={contact.id} contact={contact} />
                  ))}
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
            <UserPlus className="h-4 w-4 mr-2" />
            添加 ({selectedContacts.length})
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}