'use client'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useTranslations } from '@/lib/i18n/client'
import { Search, Bot, User, Plus, Check, UserPlus } from 'lucide-react'
import { useState, useEffect, useMemo } from 'react'
import { cn } from '@/lib/utils'
import { AIAgent, AddContactSearchResult } from '@/types/contact'

interface AddContactDialogProps {
  isOpen: boolean
  onClose: () => void
  onSearchContacts: (query: string) => Promise<AddContactSearchResult[]>
  onAddContact: (contactId: string) => void
  onSendContactRequest: (contactId: string, message: string) => void
  existingContacts: AIAgent[]
}

export function AddContactDialog({
  isOpen,
  onClose,
  onSearchContacts,
  onAddContact,
  onSendContactRequest,
  existingContacts
}: AddContactDialogProps) {
  const t = useTranslations()
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<AddContactSearchResult[]>([])
  const [selectedContact, setSelectedContact] = useState<AddContactSearchResult | null>(null)
  const [requestMessage, setRequestMessage] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  // Category tags for filtering
  const categories = [
    { id: 'all', name: t('contacts.allContacts'), tags: [] },
    { id: 'development', name: t('contacts.development'), tags: ['开发', '代码审查', '优化'] },
    { id: 'design', name: t('contacts.design'), tags: ['设计', 'UI', 'UX'] },
    { id: 'marketing', name: t('contacts.marketing'), tags: ['营销', '推广', '策略'] },
    { id: 'productivity', name: t('contacts.productivity'), tags: ['生产力', '效率', '管理'] },
    { id: 'education', name: t('contacts.education'), tags: ['教育', '课程', '学习'] },
    { id: 'entertainment', name: t('contacts.entertainment'), tags: ['娱乐', '游戏', '创意'] }
  ]

  // Enhanced recommended AI agents (only agents, no humans)
  const recommendedContacts: AddContactSearchResult[] = [
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
      isVerified: true,
      createdAt: '2024-01-01',
      updatedAt: '2024-01-15'
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
      isVerified: true,
      createdAt: '2024-01-01',
      updatedAt: '2024-01-15'
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
      isVerified: true,
      createdAt: '2024-01-01',
      updatedAt: '2024-01-15'
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
      isVerified: true,
      createdAt: '2024-01-01',
      updatedAt: '2024-01-15'
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
      isVerified: true,
      createdAt: '2024-01-01',
      updatedAt: '2024-01-15'
    },
    {
      id: 'education-ai',
      name: 'AI教育助手',
      displayName: 'EduBot',
      avatar: '/placeholder.svg',
      specialty: '在线教育',
      description: '专业课程设计和教学方法专家',
      status: 'online',
      type: 'agent',
      tags: ['教育', '课程', '学习'],
      isVerified: true,
      createdAt: '2024-01-01',
      updatedAt: '2024-01-15'
    },
    {
      id: 'productivity-ai',
      name: 'AI效率助手',
      displayName: 'ProductivityBot',
      avatar: '/placeholder.svg',
      specialty: '工作效率',
      description: '专业时间管理和工作流程优化专家',
      status: 'online',
      type: 'agent',
      tags: ['生产力', '效率', '管理'],
      isVerified: true,
      createdAt: '2024-01-01',
      updatedAt: '2024-01-15'
    },
    {
      id: 'entertainment-ai',
      name: 'AI娱乐助手',
      displayName: 'FunBot',
      avatar: '/placeholder.svg',
      specialty: '娱乐内容',
      description: '专业游戏和娱乐内容策划专家',
      status: 'online',
      type: 'agent',
      tags: ['娱乐', '游戏', '创意'],
      isVerified: true,
      createdAt: '2024-01-01',
      updatedAt: '2024-01-15'
    }
  ]

  const displayedContacts = useMemo(() => {
    const existingIds = new Set(existingContacts.map(c => c.id))
    const contactsToFilter = searchQuery.trim() ? searchResults : recommendedContacts
    
    // Filter by category
    let filteredContacts = contactsToFilter
    if (selectedCategory !== 'all') {
      const categoryData = categories.find(c => c.id === selectedCategory)
      if (categoryData) {
        filteredContacts = contactsToFilter.filter(contact => 
          contact.tags.some(tag => categoryData.tags.includes(tag))
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

  const handleSearch = async (query: string) => {
    setSearchQuery(query)
    if (!query.trim()) {
      setSearchResults([])
      return
    }

    setIsSearching(true)
    try {
      const results = await onSearchContacts(query)
      setSearchResults(results)
    } catch (error) {
      console.error('Search failed:', error)
      setSearchResults([])
    } finally {
      setIsSearching(false)
    }
  }

  const handleContactSelect = (contact: AddContactSearchResult) => {
    setSelectedContact(contact)
  }

  const handleAddContact = () => {
    if (!selectedContact) return
    
    if (selectedContact.type === 'human') {
      // For humans, show request form
      return
    }

    // For agents, add directly
    onAddContact(selectedContact.id)
    handleClose()
  }

  const handleSendRequest = async () => {
    if (!selectedContact || !requestMessage.trim()) return

    setIsSubmitting(true)
    try {
      await onSendContactRequest(selectedContact.id, requestMessage.trim())
      handleClose()
    } catch (error) {
      console.error('Failed to send request:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleClose = () => {
    setSearchQuery('')
    setSearchResults([])
    setSelectedContact(null)
    setRequestMessage('')
    setIsSubmitting(false)
    onClose()
  }

  const getDisplayName = (contact: AddContactSearchResult) => {
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

  const ContactItem = ({ contact }: { contact: AddContactSearchResult }) => (
    <div
      className={cn(
        'group relative p-2 rounded-lg cursor-pointer transition-all duration-200 border',
        'hover:shadow-md hover:scale-[1.02] hover:border-primary/40',
        'w-[250px] h-[125px] flex flex-col justify-between',
        selectedContact?.id === contact.id 
          ? 'bg-primary/5 border-primary shadow-sm' 
          : 'bg-card border-border/40 hover:bg-accent/30'
      )}
      onClick={() => handleContactSelect(contact)}
    >
      {/* Status indicator & verification */}
      <div className="absolute top-1.5 right-1.5 flex items-center space-x-1">
        <div className={cn(
          'w-1.5 h-1.5 rounded-full',
          getStatusColor(contact.status)
        )} />
        {contact.isVerified && (
          <Check className="h-2.5 w-2.5 text-primary" />
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
      
      {/* Bottom Section: Tags & Action */}
      <div className="space-y-1.5">
        {/* Tags */}
        <div className="flex flex-wrap gap-1">
          {contact.tags.slice(0, 2).map((tag) => (
            <Badge
              key={tag}
              variant="secondary"
              className="text-xs px-1 py-0 bg-accent/20 text-accent-foreground h-4"
            >
              {tag}
            </Badge>
          ))}
          {contact.tags.length > 2 && (
            <Badge
              variant="secondary"
              className="text-xs px-1 py-0 bg-accent/20 text-accent-foreground h-4"
            >
              +{contact.tags.length - 2}
            </Badge>
          )}
        </div>
        
        {/* Action Button or Status */}
        <div className="flex justify-end">
          {contact.isAlreadyContact ? (
            <Badge variant="secondary" className="text-xs py-0.5 px-1.5 h-5">
              {t('contacts.alreadyConnected')}
            </Badge>
          ) : (
            <Button
              size="sm"
              variant={selectedContact?.id === contact.id ? "default" : "outline"}
              className="h-5 px-2 text-xs transition-all duration-200"
              onClick={(e) => {
                e.stopPropagation()
                handleContactSelect(contact)
              }}
            >
              <UserPlus className="h-2.5 w-2.5 mr-1" />
              {t('ui.add')}
            </Button>
          )}
        </div>
      </div>
    </div>
  )

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-6xl max-h-[90vh] w-[95vw]">
        <DialogHeader>
          <DialogTitle className="text-xl">{t('contacts.addContact')}</DialogTitle>
          <DialogDescription>
            {selectedContact && selectedContact.type === 'human' 
              ? t('contacts.requestNote')
              : t('contacts.searchByName')
            }
          </DialogDescription>
        </DialogHeader>
        
        {!selectedContact || selectedContact.type === 'agent' ? (
          <div className="space-y-6">
            {/* Search Input */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                placeholder={t('contacts.searchByName')}
                className="pl-10 h-12 text-base bg-muted/30 border-border/40 rounded-lg focus:bg-background focus:border-ring/20"
              />
            </div>

            {/* Category Filter Tags */}
            {!searchQuery.trim() && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-medium text-foreground">
                    {t('contacts.categories')}
                  </h4>
                  <Badge variant="secondary" className="text-xs">
                    {displayedContacts.length} {t('contacts.aiAgents')}
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

            {/* Contact Grid */}
            <ScrollArea className="h-[400px]">
              <div className="space-y-4">
                {!searchQuery.trim() && (
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-medium text-muted-foreground">
                      {selectedCategory === 'all' ? t('contacts.recommended') : categories.find(c => c.id === selectedCategory)?.name}
                    </h4>
                  </div>
                )}
                
                {displayedContacts.length === 0 && searchQuery.trim() ? (
                  <div className="text-center py-12">
                    <div className="text-muted-foreground text-base">
                      {t('contacts.noResultsFor')} "{searchQuery}"
                    </div>
                  </div>
                ) : displayedContacts.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-muted-foreground text-base">
                      {t('contacts.noResults')}
                    </div>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {displayedContacts.map((contact) => (
                      <ContactItem key={contact.id} contact={contact} />
                    ))}
                  </div>
                )}
              </div>
            </ScrollArea>

            {/* Actions */}
            {selectedContact && !selectedContact.isAlreadyContact && (
              <div className="flex justify-end space-x-3 pt-4 border-t border-border/40">
                <Button variant="outline" onClick={handleClose} size="lg">
                  {t('common.cancel')}
                </Button>
                <Button onClick={handleAddContact} size="lg">
                  <UserPlus className="h-4 w-4 mr-2" />
                  {selectedContact.type === 'human' ? t('contacts.sendRequest') : t('contacts.addToContacts')}
                </Button>
              </div>
            )}
          </div>
        ) : (
          // Contact Request Form (for humans)
          <div className="space-y-4">
            {/* Selected Contact Info */}
            <div className="flex items-center space-x-3 p-4 bg-muted/30 rounded-lg">
              <Avatar className="h-12 w-12">
                <AvatarImage src={selectedContact.avatar} />
                <AvatarFallback>{getDisplayName(selectedContact)[0]}</AvatarFallback>
              </Avatar>
              <div>
                <div className="font-medium">{getDisplayName(selectedContact)}</div>
                <div className="text-sm text-muted-foreground">@{selectedContact.id}</div>
                <div className="text-sm text-muted-foreground">{selectedContact.specialty}</div>
              </div>
            </div>

            {/* Request Message */}
            <div className="space-y-2">
              <Label htmlFor="request-message">
                {t('contacts.requestMessage')}
              </Label>
              <Textarea
                id="request-message"
                value={requestMessage}
                onChange={(e) => setRequestMessage(e.target.value)}
                placeholder={t('contacts.requestNote')}
                className="min-h-20"
              />
            </div>

            {/* Actions */}
            <div className="flex justify-end space-x-2 pt-4 border-t">
              <Button variant="outline" onClick={() => setSelectedContact(null)}>
                {t('common.back')}
              </Button>
              <Button 
                onClick={handleSendRequest}
                disabled={!requestMessage.trim() || isSubmitting}
              >
                {isSubmitting ? t('common.sending') : t('contacts.sendRequest')}
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}

export default AddContactDialog