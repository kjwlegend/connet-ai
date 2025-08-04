"use client"

import { useEffect } from "react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils/cn"
import { useChat } from "@/store"
import { useTranslations, useLocale } from "@/lib/i18n/client"
import { formatDistanceToNow } from "date-fns"
import { zhCN, enUS } from "date-fns/locale"
import { MessageCircle, Users, Plus, Search } from "lucide-react"
import { Input } from "@/components/ui/input"

interface ConversationListProps {
  selectedItem?: string | null
  onItemSelect?: (id: string) => void
}

export function ConversationList({ selectedItem, onItemSelect }: ConversationListProps) {
  const t = useTranslations()
  const locale = useLocale()
  
  const {
    conversations,
    activeConversationId,
    isLoading,
    error,
    loadConversations,
    setActiveConversation,
  } = useChat()

  // Load conversations on mount
  useEffect(() => {
    loadConversations()
  }, [loadConversations])

  const formatLastMessageTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const dateLocale = locale === 'zh' ? zhCN : enUS
    
    return formatDistanceToNow(date, {
      addSuffix: true,
      locale: dateLocale
    })
  }

  const getAvatarFallback = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
  }

  const handleConversationSelect = (conversationId: string) => {
    setActiveConversation(conversationId)
    onItemSelect?.(conversationId)
  }

  const isGroupConversation = (participantCount: number) => participantCount > 2

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
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
      <div className="flex flex-col items-center justify-center h-64 px-4">
        <MessageCircle className="h-12 w-12 text-muted-foreground mb-4" />
        <h3 className="font-medium text-foreground mb-2">No conversations yet</h3>
        <p className="text-sm text-muted-foreground text-center mb-4">
          Start a new conversation with an AI agent to begin collaborating.
        </p>
        <Button size="sm" className="flex items-center space-x-2">
          <Plus className="h-4 w-4" />
          <span>New Conversation</span>
        </Button>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-foreground">Conversations</h2>
          <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
            <Plus className="h-4 w-4" />
          </Button>
        </div>
        
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search conversations..."
            className="pl-9 h-8"
          />
        </div>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto divide-y divide-border">
        {conversations.map((conversation) => {
          const isActive = activeConversationId === conversation.id || selectedItem === conversation.id
          const isGroup = isGroupConversation(conversation.participants.length)
          const lastMessageTime = conversation.lastMessage 
            ? formatLastMessageTime(conversation.lastMessage.timestamp)
            : formatLastMessageTime(conversation.updatedAt)

          return (
            <div
              key={conversation.id}
              className={cn(
                "p-4 hover:bg-muted/50 cursor-pointer transition-colors border-r-2 border-transparent",
                isActive && "bg-muted border-r-primary"
              )}
              onClick={() => handleConversationSelect(conversation.id)}
            >
              <div className="flex items-start space-x-3">
                {/* Avatar(s) */}
                <div className="relative flex-shrink-0">
                  {isGroup ? (
                    // Group avatar with overlapping circles
                    <div className="relative w-10 h-10">
                      {conversation.participants.slice(0, 2).map((participant, index) => (
                        <Avatar 
                          key={participant.id}
                          className={cn(
                            "h-8 w-8 border-2 border-background absolute",
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
                    <Avatar className="h-10 w-10">
                      <AvatarImage src={conversation.participants[1]?.avatar} />
                      <AvatarFallback>
                        {getAvatarFallback(conversation.participants[1]?.name || conversation.title)}
                      </AvatarFallback>
                    </Avatar>
                  )}
                  
                  {/* Online status indicator */}
                  {!isGroup && conversation.participants[1]?.status === 'online' && (
                    <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 border-2 border-background rounded-full"></div>
                  )}
                  
                  {/* Unread count badge */}
                  {conversation.unreadCount > 0 && (
                    <div className="absolute -top-1 -right-1 min-w-[1.25rem] h-5 bg-destructive text-destructive-foreground text-xs rounded-full flex items-center justify-center px-1">
                      {conversation.unreadCount > 99 ? "99+" : conversation.unreadCount}
                    </div>
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center space-x-2">
                      <h3 className="font-medium text-foreground truncate">
                        {conversation.title}
                      </h3>
                      {isGroup && (
                        <Badge variant="secondary" className="text-xs px-1.5 py-0.5">
                          <Users className="h-3 w-3 mr-1" />
                          {conversation.participants.length}
                        </Badge>
                      )}
                    </div>
                    <span className="text-xs text-muted-foreground flex-shrink-0">
                      {lastMessageTime}
                    </span>
                  </div>
                  
                  {/* Last message */}
                  <p className="text-sm text-muted-foreground truncate">
                    {conversation.lastMessage ? (
                      <>
                        {conversation.lastMessage.senderType !== 'user' && (
                          <span className="font-medium">
                            {conversation.lastMessage.senderName}: 
                          </span>
                        )}
                        <span className="ml-1">{conversation.lastMessage.content}</span>
                      </>
                    ) : (
                      <span className="italic">No messages yet</span>
                    )}
                  </p>
                  
                  {/* Participants (for groups) */}
                  {isGroup && (
                    <p className="text-xs text-muted-foreground mt-1 truncate">
                      {conversation.participants
                        .filter(p => p.type === 'agent')
                        .map(p => p.name)
                        .join(', ')}
                    </p>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default ConversationList