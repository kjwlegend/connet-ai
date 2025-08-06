"use client"

import { useEffect, useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Users, AlertCircle } from "lucide-react"
import { useChat } from "@/store"
import { useTranslations } from "@/lib/i18n/client"
import { formatDistanceToNow } from "date-fns"
import { zhCN, enUS } from "date-fns/locale"
import { useLocale } from "@/lib/i18n/client"
import { MessageBubble } from "@/components/features/chat/components/MessageBubble"
import { ChatInput } from "@/components/features/chat/components/ChatInput"
import { ChatHeader } from "@/components/features/chat/components/ChatHeader"
import { ChatRightPanel } from "@/components/features/chat/components/ChatRightPanel"

interface ChatInterfaceProps {
  selectedItem?: string
}

export function ChatInterface({ selectedItem }: ChatInterfaceProps) {
  const t = useTranslations()
  const locale = useLocale()
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const [isRightPanelOpen, setIsRightPanelOpen] = useState(false)
  
  const {
    activeConversationId,
    conversations,
    messages,
    draft,
    isSending,
    isLoading,
    error,
    setDraft,
    sendMessage,
    loadMessages,
    clearError,
  } = useChat()

  // Get current conversation
  const currentConversation = conversations.find(conv => conv.id === activeConversationId)
  const currentMessages = activeConversationId ? messages[activeConversationId] || [] : []

  // Load messages when conversation changes
  useEffect(() => {
    if (activeConversationId && !messages[activeConversationId]) {
      loadMessages(activeConversationId)
    }
  }, [activeConversationId, messages, loadMessages])

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollElement = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]')
      if (scrollElement) {
        scrollElement.scrollTop = scrollElement.scrollHeight
      }
    }
  }, [currentMessages])

  const handleSendMessage = async () => {
    if (!draft.trim() || !activeConversationId || isSending) return

    try {
      await sendMessage(activeConversationId, draft)
      setDraft('')
    } catch (error) {
      console.error('Failed to send message:', error)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Additional keyboard shortcuts can be added here
    // The basic Enter/Shift+Enter handling is done in ChatInput
  }

  const formatMessageTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const dateLocale = locale === 'zh' ? zhCN : enUS
    
    return formatDistanceToNow(date, {
      addSuffix: true,
      locale: dateLocale
    })
  }


  // Show empty state if no conversation is selected
  if (!activeConversationId || !currentConversation) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
        <Users className="h-16 w-16 mb-4 opacity-50" />
        <h3 className="text-lg font-medium mb-2">Welcome to Connet.AI</h3>
        <p className="text-sm text-center max-w-md">
          Select a conversation from the sidebar to start chatting with AI agents, 
          or create a new conversation to begin collaborating.
        </p>
      </div>
    )
  }

  return (
    <div className="flex h-screen max-h-screen bg-background overflow-hidden">
      {/* Main Chat Area */}
      <div className="flex flex-col flex-1 pb-[200px] overflow-hidden">
        {/* Chat Header */}
        <ChatHeader 
          conversation={currentConversation} 
          onMenuClick={() => setIsRightPanelOpen(!isRightPanelOpen)}
        />

        {/* Error Display */}
        {error && (
          <div className="mx-4 mt-4 p-3 bg-destructive/10 border border-destructive/20 rounded-lg flex items-center space-x-2">
            <AlertCircle className="h-4 w-4 text-destructive" />
            <span className="text-sm text-destructive">{error}</span>
            <Button variant="ghost" size="sm" onClick={clearError} className="ml-auto">
              ✕
            </Button>
          </div>
        )}

        {/* Messages Area */}
        <ScrollArea className="flex-1 px-4 overflow-y-auto" ref={scrollAreaRef}>
          {isLoading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : (
            <div className="py-6">
              {currentMessages.map((message) => (
                <MessageBubble
                  key={message.id}
                  message={message}
                  isUser={message.senderType === 'user'}
                  showAvatar={true}
                  showTimestamp={true}
                />
              ))}
              
              {/* Typing indicator */}
              {isSending && (
                <div className="flex items-start gap-3 mb-6">
                  <Avatar className="h-9 w-9 border-2 border-background shadow-sm">
                    <AvatarFallback className="text-xs font-medium bg-accent/50 text-accent-foreground">
                      AI
                    </AvatarFallback>
                  </Avatar>
                  <div className="bg-card border border-border/50 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-pulse"></div>
                      <div className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                      <div className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </ScrollArea>

        {/* Enhanced Input Area - Now rendered as fixed overlay */}
        <ChatInput
          value={draft}
          onChange={setDraft}
          onSend={handleSendMessage}
          onKeyDown={handleKeyDown}
          disabled={false}
          isSending={isSending}
          placeholder={t('chat.inputPlaceholder')}
        />
      </div>

      {/* Right Panel */}
      <ChatRightPanel
        conversation={currentConversation}
        isOpen={isRightPanelOpen}
        onClose={() => setIsRightPanelOpen(false)}
      />
    </div>
  )
}

export default ChatInterface