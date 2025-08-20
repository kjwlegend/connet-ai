"use client"

import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { X, LogOut } from "lucide-react"
import { useTranslations } from "@/lib/i18n/client"
import type { Conversation } from "@/store/types/chat"
import { ParticipantsSection } from "./ParticipantsSection"
import { FilesSection } from "./FilesSection"
import { ConversationMemorySection } from "./ConversationMemorySection"

interface ChatRightPanelProps {
  conversation: Conversation
  isOpen: boolean
  onClose: () => void
  onAddParticipants?: (participantIds: string[]) => void
  onLeaveGroup?: (conversationId: string) => void
}


export function ChatRightPanel({ conversation, isOpen, onClose, onAddParticipants, onLeaveGroup }: ChatRightPanelProps) {
  const t = useTranslations()

  const handleLeaveGroup = () => {
    if (onLeaveGroup) {
      onLeaveGroup(conversation.id)
    }
  }

  // Check if it's a group conversation (more than 2 participants)
  const isGroupConversation = conversation.participants.length > 2

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
            <ParticipantsSection 
              conversation={conversation}
              onAddParticipants={onAddParticipants}
            />

            <Separator />

            {/* Files Section */}
            <FilesSection />

            <Separator />

            {/* Conversation Memory Section */}
            <ConversationMemorySection 
              conversationTitle={conversation.title}
            />
          </div>
        </ScrollArea>

        {/* Footer with Leave Group Button */}
        {isGroupConversation && (
          <div className="p-4 border-t border-border">
            <Button 
              variant="outline"
              size="sm"
              onClick={handleLeaveGroup}
              className="w-full text-destructive hover:text-destructive hover:bg-destructive/10 border-destructive/20"
            >
              <LogOut className="h-4 w-4 mr-2" />
              退出群组
            </Button>
          </div>
        )}

      </div>
    </>
  )
}

export default ChatRightPanel