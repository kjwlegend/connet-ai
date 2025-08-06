"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { MoreVertical } from "lucide-react"
import type { Conversation } from "@/store/slices/chatSlice"

interface ChatHeaderProps {
  conversation: Conversation
  onMenuClick?: () => void
}

export function ChatHeader({ conversation, onMenuClick }: ChatHeaderProps) {
  const getAvatarFallback = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
  }

  const onlineCount = conversation.participants.filter(p => p.status === 'online').length
  const totalParticipants = conversation.participants.length

  return (
    <div className="flex items-center justify-between p-4 border-b border-border bg-card">
      <div className="flex items-center space-x-3">
        {/* Show multiple avatars for group conversations */}
        <div className="relative">
          {conversation.participants.slice(0, 2).map((participant, index) => (
            <Avatar 
              key={participant.id} 
              className={`h-10 w-10 border-2 border-background ${
                index > 0 ? 'absolute -right-2 -top-1' : ''
              }`}
            >
              <AvatarImage src={participant.avatar} />
              <AvatarFallback className="text-xs">
                {getAvatarFallback(participant.name)}
              </AvatarFallback>
            </Avatar>
          ))}
        </div>
        <div className="flex-1 min-w-0">
          <h2 className="font-semibold text-foreground truncate">
            {conversation.title}
          </h2>
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <span className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>
                {onlineCount} online
              </span>
            </span>
            <span>•</span>
            <span>{totalParticipants} participants</span>
          </div>
        </div>
      </div>
      <Button 
        variant="ghost" 
        size="sm" 
        onClick={onMenuClick}
        type="button"
      >
        <MoreVertical className="h-5 w-5" />
      </Button>
    </div>
  )
}

export default ChatHeader