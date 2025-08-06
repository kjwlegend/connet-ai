"use client"

import { useEffect, useState, useMemo } from "react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils/cn"
import { useChat } from "@/store"
import { useTranslations, useLocale } from "@/lib/i18n/client"
import { formatDistanceToNow } from "date-fns"
import { zhCN, enUS } from "date-fns/locale"
import { MessageCircle, Users, Plus, Search, Pin, Download, Trash2 } from "lucide-react"
import { Input } from "@/components/ui/input"
import { ContextMenu, ContextMenuItem, ContextMenuSeparator } from "@/components/ui/context-menu"
import { DeleteConversationDialog } from "./DeleteConversationDialog"

interface ConversationListProps {
  selectedItem?: string | null
  onItemSelect?: (id: string) => void
}

type FilterType = 'all' | 'contacts' | 'unread' | 'groups'

export function ConversationList({ selectedItem, onItemSelect }: ConversationListProps) {
  const t = useTranslations()
  const locale = useLocale()
  const [activeFilter, setActiveFilter] = useState<FilterType>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [conversationToDelete, setConversationToDelete] = useState<string | null>(null)
  
  const {
    conversations,
    activeConversationId,
    isLoading,
    error,
    loadConversations,
    setActiveConversation,
    createNewConversation,
    pinConversation,
    unpinConversation,
    exportConversation,
    deleteConversation,
  } = useChat()

  // Load conversations on mount
  useEffect(() => {
    loadConversations()
  }, []) // Remove loadConversations from dependencies to prevent infinite loop
  
  // eslint-disable-next-line react-hooks/exhaustive-deps

  const formatLastMessageTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const dateLocale = locale === 'zh' ? zhCN : enUS
    
    return formatDistanceToNow(date, {
      addSuffix: true,
      locale: dateLocale
    })
  }

  const formatConversationDate = (timestamp: string) => {
    const date = new Date(timestamp)
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    return `${month}/${day}`
  }

  const getAvatarFallback = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
  }

  const handleConversationSelect = (conversationId: string) => {
    setActiveConversation(conversationId)
    onItemSelect?.(conversationId)
  }

  const handleCreateNewConversation = async () => {
    try {
      // Create a conversation with a random available agent
      const availableAgents = [
        { id: 'agent-new-1', name: 'AI助手' },
        { id: 'agent-new-2', name: '编程助手' },
        { id: 'agent-new-3', name: '写作助手' },
        { id: 'agent-new-4', name: '设计顾问' },
        { id: 'agent-new-5', name: '数据分析师' }
      ]
      
      const randomAgent = availableAgents[Math.floor(Math.random() * availableAgents.length)]
      const conversationId = await createNewConversation(randomAgent.id, randomAgent.name)
      
      // Select the new conversation
      onItemSelect?.(conversationId)
    } catch (error) {
      console.error('Failed to create new conversation:', error)
    }
  }

  const isGroupConversation = (participantCount: number) => participantCount > 2

  // Filter conversations based on active filter and search query
  const filteredConversations = useMemo(() => {
    let filtered = conversations

    // Apply filter
    switch (activeFilter) {
      case 'contacts':
        // Filter for direct conversations with agents (not groups)
        filtered = conversations.filter(conv => !isGroupConversation(conv.participants.length))
        break
      case 'unread':
        // Filter for conversations with unread messages
        filtered = conversations.filter(conv => conv.unreadCount > 0)
        break
      case 'groups':
        // Filter for group conversations
        filtered = conversations.filter(conv => isGroupConversation(conv.participants.length))
        break
      default:
        filtered = conversations
    }

    // Apply search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase().trim()
      filtered = filtered.filter(conv => 
        conv.title.toLowerCase().includes(query) ||
        conv.lastMessage?.content.toLowerCase().includes(query) ||
        conv.participants.some(p => p.name.toLowerCase().includes(query))
      )
    }

    // Sort conversations: pinned conversations first, then by update time
    return filtered.sort((a, b) => {
      // First sort by pinned status
      if (a.isPinned && !b.isPinned) return -1
      if (!a.isPinned && b.isPinned) return 1
      
      // Then sort by update time (most recent first)
      return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    })
  }, [conversations, activeFilter, searchQuery])

  const handleFilterChange = (filter: FilterType) => {
    setActiveFilter(filter)
  }

  const handlePinConversation = (conversationId: string, isPinned?: boolean) => {
    if (isPinned) {
      unpinConversation(conversationId)
    } else {
      pinConversation(conversationId)
    }
  }

  const handleExportConversation = async (conversationId: string) => {
    try {
      await exportConversation(conversationId)
      // You could add a toast notification here
    } catch (error) {
      console.error('Failed to export conversation:', error)
    }
  }

  const handleDeleteConversation = (conversationId: string) => {
    setConversationToDelete(conversationId)
    setDeleteDialogOpen(true)
  }

  const confirmDeleteConversation = () => {
    if (conversationToDelete) {
      deleteConversation(conversationToDelete)
      setConversationToDelete(null)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-32">
        <div className="flex flex-col items-center space-y-3">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary/20 border-t-primary"></div>
          <p className="text-sm text-muted-foreground">Loading conversations...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 text-center">
        <p className="text-sm text-destructive">{error}</p>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={() => loadConversations()}
          className="mt-2"
        >
          Retry
        </Button>
      </div>
    )
  }

  if (conversations.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 px-6">
        <div className="rounded-full bg-muted/30 p-4 mb-4">
          <MessageCircle className="h-8 w-8 text-muted-foreground/60" />
        </div>
        <h3 className="font-semibold text-foreground mb-2 text-base">{t('chat.emptyStates.emptyTitle')}</h3>
        <p className="text-sm text-muted-foreground/80 text-center mb-6 leading-relaxed max-w-xs">
          {t('chat.emptyStates.emptyDescription')}
        </p>
        <Button 
          size="sm" 
          className="flex items-center space-x-2 rounded-lg shadow-sm hover:shadow-md transition-all duration-200"
          onClick={handleCreateNewConversation}
        >
          <Plus className="h-4 w-4" />
          <span>{t('chat.newConversation')}</span>
        </Button>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-background overflow-hidden">
      {/* Header */}
      <div className="flex-shrink-0 px-4 py-4 border-b border-border/60 bg-background/80 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-base font-semibold text-foreground tracking-tight">{t('chat.conversations')}</h2>
          <Button 
            size="sm" 
            variant="ghost" 
            className="h-8 w-8 p-0 rounded-lg hover:bg-accent/50 transition-all duration-200"
            onClick={handleCreateNewConversation}
            title={t('chat.newConversation')}
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>
        
        {/* Filter Tags */}
        <div className="flex gap-2 mb-3">
          <Button 
            variant="ghost" 
            size="sm" 
            className={cn(
              "h-7 px-2 text-xs transition-all duration-200",
              activeFilter === 'contacts' 
                ? "bg-accent/40 text-accent-foreground font-medium" 
                : "hover:bg-accent/40"
            )}
            onClick={() => handleFilterChange(activeFilter === 'contacts' ? 'all' : 'contacts')}
          >
            {t('chat.filters.contacts')}
          </Button>
          <Button 
            variant="ghost" 
            size="sm" 
            className={cn(
              "h-7 px-2 text-xs transition-all duration-200",
              activeFilter === 'unread' 
                ? "bg-accent/40 text-accent-foreground font-medium" 
                : "hover:bg-accent/40"
            )}
            onClick={() => handleFilterChange(activeFilter === 'unread' ? 'all' : 'unread')}
          >
            {t('chat.filters.unread')}
          </Button>
          <Button 
            variant="ghost" 
            size="sm" 
            className={cn(
              "h-7 px-2 text-xs transition-all duration-200",
              activeFilter === 'groups' 
                ? "bg-accent/40 text-accent-foreground font-medium" 
                : "hover:bg-accent/40"
            )}
            onClick={() => handleFilterChange(activeFilter === 'groups' ? 'all' : 'groups')}
          >
            {t('chat.filters.groups')}
          </Button>
        </div>
        
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground/70" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t('chat.searchPlaceholder')}
            className="pl-9 h-8 text-sm bg-muted/30 border-border/40 rounded-lg focus:bg-background focus:border-ring/20 transition-all duration-200 placeholder:text-muted-foreground/60"
          />
        </div>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden scrollbar-thin scrollbar-thumb-border/40 scrollbar-track-transparent">
        {filteredConversations.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-32 px-6">
            <p className="text-sm text-muted-foreground/80 text-center">
              {searchQuery.trim() ? (
                t('chat.emptyStates.noSearchResults', { query: searchQuery })
              ) : (
                <>
                  {activeFilter === 'contacts' && t('chat.emptyStates.noContacts')}
                  {activeFilter === 'unread' && t('chat.emptyStates.noUnread')}  
                  {activeFilter === 'groups' && t('chat.emptyStates.noGroups')}
                  {activeFilter === 'all' && t('chat.emptyStates.noConversations')}
                </>
              )}
            </p>
          </div>
        ) : (
          filteredConversations.map((conversation) => {
          const isActive = activeConversationId === conversation.id || selectedItem === conversation.id
          const isGroup = isGroupConversation(conversation.participants.length)
          const lastMessageTime = conversation.lastMessage 
            ? formatLastMessageTime(conversation.lastMessage.timestamp)
            : formatLastMessageTime(conversation.updatedAt)

          return (
            <ContextMenu
              key={conversation.id}
              trigger={
                <div
                  className={cn(
                    "px-4 py-3 cursor-pointer transition-all duration-200 ease-out border-r-2 border-transparent relative group",
                    "hover:bg-accent/30 hover:border-r-primary/40",
                    isActive && "bg-accent/50 border-r-primary",
                    conversation.isPinned && "bg-accent/20 border-l-4 border-l-primary/60",
                  )}
                  onClick={() => handleConversationSelect(conversation.id)}
                >
              <div className="flex items-start space-x-3">
                {/* Avatar(s) */}
                <div className="relative flex-shrink-0">
                  {isGroup ? (
                    // Group avatar with overlapping circles
                    <div className="relative w-9 h-9">
                      {conversation.participants.slice(0, 2).map((participant, index) => (
                        <Avatar 
                          key={participant.id}
                          className={cn(
                            "h-7 w-7 border-2 border-background absolute",
                            index === 0 ? "top-0 left-0" : "bottom-0 right-0"
                          )}
                        >
                          <AvatarImage src={participant.avatar} />
                          <AvatarFallback className="text-xs">
                            {getAvatarFallback(participant.name)}
                          </AvatarFallback>
                        </Avatar>
                      ))}
                    </div>
                  ) : (
                    // Single avatar
                    <Avatar className="h-9 w-9">
                      <AvatarImage src={conversation.participants[1]?.avatar} />
                      <AvatarFallback className="text-xs">
                        {getAvatarFallback(conversation.participants[1]?.name || conversation.title)}
                      </AvatarFallback>
                    </Avatar>
                  )}
                  
                  {/* Online status indicator */}
                  {!isGroup && conversation.participants[1]?.status === 'online' && (
                    <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-green-500 border-2 border-background rounded-full"></div>
                  )}
                  
                  {/* Unread count badge */}
                  {conversation.unreadCount > 0 && (
                    <div className="absolute -top-1 -right-1 min-w-[1rem] h-4 bg-primary text-primary-foreground text-xs rounded-full flex items-center justify-center px-1 font-medium shadow-lg border border-background">
                      {conversation.unreadCount > 99 ? "99+" : conversation.unreadCount}
                    </div>
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0 overflow-hidden">
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center space-x-2 flex-1 min-w-0 overflow-hidden">
                      <h3 className="font-medium text-foreground truncate text-sm leading-tight max-w-[120px]">
                        {conversation.title}
                      </h3>
                      {isGroup && (
                        <Badge variant="secondary" className="text-xs px-1.5 py-0.5 rounded bg-muted/50 text-muted-foreground border-0">
                          <Users className="h-2.5 w-2.5 mr-0.5" />
                          {conversation.participants.length}
                        </Badge>
                      )}
                      <span className="text-xs text-muted-foreground/60 flex-shrink-0">
                        {formatConversationDate(conversation.updatedAt)}
                      </span>
                    </div>
                    <span className="text-xs text-muted-foreground/80 flex-shrink-0 group-hover:text-muted-foreground transition-colors">
                      {lastMessageTime}
                    </span>
                  </div>
                  
                  {/* Last message */}
                  <p className="text-xs text-muted-foreground/90 truncate leading-relaxed max-w-[180px]">
                    {conversation.lastMessage ? (
                      <>
                        {conversation.lastMessage.senderType !== 'user' && (
                          <span className="font-medium text-muted-foreground">
                            {conversation.lastMessage.senderName}: 
                          </span>
                        )}
                        <span className="ml-0.5">
                          {conversation.lastMessage.content.length > 30 
                            ? `${conversation.lastMessage.content.substring(0, 30)}...`
                            : conversation.lastMessage.content
                          }
                        </span>
                      </>
                    ) : (
                      <span className="italic text-muted-foreground/60">{t('chat.emptyStates.noMessages')}</span>
                    )}
                  </p>
                  
                  {/* Participants (for groups) */}
                  {isGroup && (
                    <p className="text-xs text-muted-foreground/70 mt-1 truncate">
                      {conversation.participants
                        .filter(p => p.type === 'agent')
                        .map(p => p.name)
                        .join(', ')}
                    </p>
                  )}
                </div>
              </div>
                </div>
              }
            >
              <ContextMenuItem
                onClick={() => handlePinConversation(conversation.id, conversation.isPinned)}
              >
                {conversation.isPinned ? (
                  <>
                    <Pin className="h-4 w-4 mr-2 fill-current" />
                    {t('chat.contextMenu.unpin')}
                  </>
                ) : (
                  <>
                    <Pin className="h-4 w-4 mr-2" />
                    {t('chat.contextMenu.pin')}
                  </>
                )}
              </ContextMenuItem>
              
              <ContextMenuSeparator />
              
              <ContextMenuItem
                onClick={() => handleExportConversation(conversation.id)}
              >
                <Download className="h-4 w-4 mr-2" />
                {t('chat.contextMenu.export')}
              </ContextMenuItem>
              
              <ContextMenuSeparator />
              
              <ContextMenuItem
                onClick={() => handleDeleteConversation(conversation.id)}
                destructive
              >
                <Trash2 className="h-4 w-4 mr-2" />
                {t('chat.contextMenu.delete')}
              </ContextMenuItem>
            </ContextMenu>
          )
          })
        )}
      </div>

      {/* Delete Confirmation Dialog */}
      <DeleteConversationDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        conversationTitle={
          conversationToDelete 
            ? conversations.find(c => c.id === conversationToDelete)?.title || '' 
            : ''
        }
        onConfirm={confirmDeleteConversation}
      />
    </div>
  )
}

export default ConversationList