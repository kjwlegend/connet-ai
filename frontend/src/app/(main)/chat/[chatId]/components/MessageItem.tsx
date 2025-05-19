import React, { useState } from 'react'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Message } from '../types'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Button } from '@/components/ui/button'
import { Copy, RefreshCw, Edit, Trash2 } from 'lucide-react' // More icons

interface MessageItemProps {
  msg: Message
  currentUserAvatar?: string
  currentUserName: string
  onRetry?: (message: Message) => void // Callback for retry
  onEdit?: (message: Message) => void // Callback for edit
  // Add more action callbacks as needed
}

export default function MessageItem({
  msg,
  currentUserAvatar,
  currentUserName,
  onRetry,
  onEdit,
}: MessageItemProps) {
  const isCurrentUser = msg.sender === currentUserName
  const [showActions, setShowActions] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(msg.text)
    // Optional: Show a toast notification for "Copied!"
    alert('Copied to clipboard!')
  }

  return (
    <div
      className={`group flex mb-4 ${
        isCurrentUser ? 'justify-end' : 'justify-start'
      }`}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      {!isCurrentUser && (
        <Avatar className="w-8 h-8 mr-2 mt-1 flex-shrink-0">
          {' '}
          {/* Added mt-1 for alignment */}
          <AvatarImage
            src={msg.avatar || '/avatars/default-ai.png'}
            alt={msg.sender}
          />
          <AvatarFallback>
            {msg.sender.substring(0, 1).toUpperCase()}
          </AvatarFallback>
        </Avatar>
      )}

      <div className="flex flex-col">
        {' '}
        {/* Wrapper for message bubble and actions */}
        <div
          className={`p-3 rounded-lg max-w-xs sm:max-w-md md:max-w-lg lg:max-w-xl break-words relative ${
            // Increased max-width
            isCurrentUser
              ? 'bg-blue-500 text-white'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
          }`}
        >
          {/* Message Actions - show on hover or persistently on touch */}
          <div
            className={`absolute -top-2 ${
              isCurrentUser
                ? '-left-2 transform -translate-x-full'
                : '-right-2 transform translate-x-full'
            } opacity-0 group-hover:opacity-100 transition-opacity flex space-x-1 p-1 bg-white dark:bg-gray-800 rounded-md shadow-md`}
          >
            {/* Show actions based on message sender or type */}
            <Button variant="ghost" size="sm" onClick={handleCopy} title="Copy">
              <Copy className="h-3 w-3" />
            </Button>
            {!isCurrentUser &&
              onRetry && ( // Only show retry for AI messages
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onRetry(msg)}
                  title="Retry"
                >
                  <RefreshCw className="h-3 w-3" />
                </Button>
              )}
            {isCurrentUser &&
              onEdit && ( // Only show edit for user messages
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onEdit(msg)}
                  title="Edit"
                >
                  <Edit className="h-3 w-3" />
                </Button>
              )}
            {/* Add more actions like delete etc. */}
          </div>

          {msg.isDelegatedTask && msg.delegatedTo && (
            <p className="text-xs italic mb-1 opacity-80">
              Task delegated to {msg.delegatedTo}
            </p>
          )}
          {/* Markdown Rendering */}
          <article className="prose prose-sm dark:prose-invert max-w-none">
            {' '}
            {/* prose classes for styling */}
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {msg.text}
            </ReactMarkdown>
          </article>
          <p className="text-xs mt-1 opacity-60 text-right">
            {new Date(msg.timestamp).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </p>
        </div>
      </div>

      {isCurrentUser && (
        <Avatar className="w-8 h-8 ml-2 mt-1 flex-shrink-0">
          {' '}
          {/* Added mt-1 */}
          <AvatarImage
            src={currentUserAvatar || '/avatars/user.png'}
            alt={msg.sender}
          />
          <AvatarFallback>
            {msg.sender.substring(0, 1).toUpperCase()}
          </AvatarFallback>
        </Avatar>
      )}
    </div>
  )
}
