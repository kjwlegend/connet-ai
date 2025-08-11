"use client"

import { useState } from "react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Users, Plus } from "lucide-react"
import { useTranslations } from "@/lib/i18n/client"
import type { Conversation } from "@/store/slices/chatSlice"
import { AddContactDialog } from "./AddContactDialog"

interface ParticipantsSectionProps {
  conversation: Conversation
  onAddParticipants?: (participantIds: string[]) => void
}

export function ParticipantsSection({ conversation, onAddParticipants }: ParticipantsSectionProps) {
  const t = useTranslations()
  const [showAddContactDialog, setShowAddContactDialog] = useState(false)

  const getAvatarFallback = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
  }

  const handleAddContacts = (contactIds: string[]) => {
    if (onAddParticipants) {
      onAddParticipants(contactIds)
    }
  }

  const participantCount = conversation.participants.length
  const isLargeGroup = participantCount > 5

  return (
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
      
      {/* Participants Display - Different layout based on count */}
      {isLargeGroup ? (
        // Grid layout for large groups (>5 participants) - 4 per row
        <div className="grid grid-cols-4 gap-2">
          {conversation.participants.map((participant) => (
            <div key={participant.id} className="flex flex-col items-center p-2 rounded-lg hover:bg-accent/50 transition-colors group">
              <div className="relative mb-1">
                <Avatar className="h-8 w-8">
                  <AvatarImage src={participant.avatar} />
                  <AvatarFallback className="text-xs">
                    {getAvatarFallback(participant.name)}
                  </AvatarFallback>
                </Avatar>
                {participant.status === 'online' && (
                  <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-green-500 border-2 border-card rounded-full" />
                )}
              </div>
              <div className="text-center min-w-0 w-full">
                <p className="text-xs font-medium text-foreground truncate">
                  {participant.name}
                </p>
                <Badge 
                  variant={participant.type === 'user' ? 'default' : 'secondary'} 
                  className="text-[10px] px-1 py-0 mt-0.5"
                >
                  {t(`chat.rightPanel.${participant.type === 'user' ? 'user' : 'ai'}`)}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      ) : (
        // List layout for small groups (≤5 participants)
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
      )}

      <AddContactDialog 
        open={showAddContactDialog}
        onOpenChange={setShowAddContactDialog}
        onAddContacts={handleAddContacts}
        existingContacts={conversation.participants.map(p => ({
          id: p.id,
          name: p.name,
          type: p.type,
          avatar: p.avatar,
          status: p.status,
          description: p.name // Placeholder
        }))}
      />
    </div>
  )
}

export default ParticipantsSection