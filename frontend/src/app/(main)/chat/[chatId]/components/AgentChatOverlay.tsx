import React from 'react'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import MessageItem from './MessageItem' // Re-use MessageItem
import { AIAgent, Message } from '../types'
// import { X } from 'lucide-react'; // If you have lucide-react

interface AgentChatOverlayProps {
  agent: AIAgent | null
  messages: Message[]
  onClose: () => void
  currentUserAvatar?: string
  currentUserName: string
}

export default function AgentChatOverlay({
  agent,
  messages,
  onClose,
  currentUserAvatar,
  currentUserName,
}: AgentChatOverlayProps) {
  if (!agent) return null

  return (
    <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-20 p-4">
      <div className="bg-white dark:bg-gray-800 w-full max-w-2xl h-[80vh] max-h-[700px] rounded-lg shadow-xl flex flex-col">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <div className="flex items-center">
            <Avatar className="w-8 h-8 mr-3">
              <AvatarImage src={agent.avatar} alt={agent.name} />
              <AvatarFallback>
                {agent.name.substring(0, 1).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
              Chat with {agent.name}
            </h2>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
            {/* <X className="h-5 w-5" /> */}
          </Button>
        </div>
        <ScrollArea className="flex-1 p-4">
          {messages.map((msg, index) => (
            <MessageItem
              key={`overlay-${msg.id}-${index}`}
              msg={msg}
              currentUserAvatar={currentUserAvatar}
              currentUserName={currentUserName}
            />
          ))}
        </ScrollArea>
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 text-sm text-gray-500 dark:text-gray-400">
          This is a dedicated chat with {agent.name}. (Input temporarily
          disabled)
        </div>
      </div>
    </div>
  )
}
