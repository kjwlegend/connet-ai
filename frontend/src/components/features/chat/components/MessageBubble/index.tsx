"use client"

import { forwardRef } from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import remarkBreaks from "remark-breaks"
import rehypeHighlight from "rehype-highlight"
import rehypeRaw from "rehype-raw"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { Copy, Check } from "lucide-react"
import { useState } from "react"
import type { Message } from "@/store/slices/chatSlice"

interface MessageBubbleProps {
  message: Message
  isUser?: boolean
  showAvatar?: boolean
  showTimestamp?: boolean
  className?: string
}

export const MessageBubble = forwardRef<HTMLDivElement, MessageBubbleProps>(
  ({ message, isUser, showAvatar = true, showTimestamp = true, className }, ref) => {
    const [copiedCode, setCopiedCode] = useState<string | null>(null)

    const handleCopyCode = async (code: string) => {
      try {
        await navigator.clipboard.writeText(code)
        setCopiedCode(code)
        setTimeout(() => setCopiedCode(null), 2000)
      } catch (error) {
        console.error('Failed to copy code:', error)
      }
    }

    const getAvatarFallback = (name: string) => {
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    }

    return (
      <div
        ref={ref}
        className={cn(
          "group flex items-start gap-3 mb-6",
          isUser && "flex-row-reverse",
          className
        )}
      >
        {/* Avatar */}
        {showAvatar && (
          <div className="relative flex-shrink-0">
            <Avatar 
              className={cn(
                "h-9 w-9 border-2 border-background shadow-sm transition-all duration-200",
                "group-hover:shadow-md group-hover:scale-105"
              )}
            >
              <AvatarImage src={message.senderType === 'user' ? undefined : '/avatars/ai-agent.png'} />
              <AvatarFallback className={cn(
                "text-xs font-medium",
                isUser ? "bg-primary/10 text-primary" : "bg-accent/50 text-accent-foreground"
              )}>
                {getAvatarFallback(message.senderName)}
              </AvatarFallback>
            </Avatar>
            
            {/* Online indicator for agents */}
            {!isUser && (
              <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 border-2 border-background rounded-full"></div>
            )}
          </div>
        )}

        {/* Message Content */}
        <div className={cn(
          "flex flex-col max-w-[75%] min-w-0",
          isUser && "items-end"
        )}>
          {/* Sender Name */}
          {!isUser && message.senderName && (
            <div className="mb-1.5 px-1">
              <span className="text-xs font-medium text-muted-foreground/80">
                {message.senderName}
              </span>
            </div>
          )}

          {/* Message Bubble */}
          <div
            className={cn(
              "relative rounded-2xl px-4 py-3 shadow-sm transition-all duration-200",
              "group-hover:shadow-md",
              isUser ? [
                "bg-primary text-primary-foreground",
                "rounded-br-md", // Less rounded bottom right for user messages
              ] : [
                "bg-card border border-border/50 text-card-foreground",
                "rounded-bl-md", // Less rounded bottom left for agent messages
              ]
            )}
          >
            {/* Message Content with Markdown */}
            <div className={cn(
              "prose prose-sm max-w-none",
              isUser 
                ? "prose-invert prose-headings:text-primary-foreground prose-p:text-primary-foreground prose-strong:text-primary-foreground prose-em:text-primary-foreground prose-code:text-primary-foreground prose-pre:bg-primary-foreground/10 prose-pre:text-primary-foreground"
                : "prose-headings:text-foreground prose-p:text-foreground prose-strong:text-foreground prose-em:text-foreground prose-code:bg-muted prose-code:text-foreground prose-pre:bg-muted/50 prose-pre:border prose-pre:border-border/40"
            )}>
              <ReactMarkdown
                remarkPlugins={[remarkGfm, remarkBreaks]}
                rehypePlugins={[rehypeHighlight, rehypeRaw]}
                components={{
                  // Custom code block component with copy button
                  pre: ({ children, ...props }) => (
                    <div className="relative group/code">
                      <pre {...props} className={cn(
                        "rounded-lg p-4 overflow-x-auto text-sm font-mono leading-relaxed",
                        "bg-muted/50 border border-border/40",
                        isUser && "bg-primary-foreground/10 border-primary-foreground/20"
                      )}>
                        {children}
                      </pre>
                      <Button
                        size="sm"
                        variant="ghost"
                        className={cn(
                          "absolute top-2 right-2 h-8 w-8 p-0 opacity-0 group-hover/code:opacity-100 transition-opacity",
                          isUser 
                            ? "text-primary-foreground/70 hover:text-primary-foreground hover:bg-primary-foreground/10"
                            : "text-muted-foreground hover:text-foreground hover:bg-muted/80"
                        )}
                        onClick={() => {
                          const codeElement = children?.props?.children
                          if (typeof codeElement === 'string') {
                            handleCopyCode(codeElement)
                          }
                        }}
                      >
                        {copiedCode === children?.props?.children ? (
                          <Check className="h-4 w-4" />
                        ) : (
                          <Copy className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  ),
                  
                  // Custom inline code component 
                  code: ({ children, className, ...props }) => {
                    const inline = !className?.includes('language-')
                    if (inline) {
                      return (
                        <code 
                          {...props}
                          className={cn(
                            "px-1.5 py-0.5 rounded text-sm font-mono",
                            isUser 
                              ? "bg-primary-foreground/20 text-primary-foreground"
                              : "bg-muted text-foreground"
                          )}
                        >
                          {children}
                        </code>
                      )
                    }
                    return <code {...props} className={className}>{children}</code>
                  },

                  // Custom paragraph component
                  p: ({ children }) => (
                    <p className="leading-relaxed mb-3 last:mb-0">
                      {children}
                    </p>
                  ),

                  // Custom list components
                  ul: ({ children }) => (
                    <ul className="list-disc list-inside space-y-1 mb-3">
                      {children}
                    </ul>
                  ),
                  
                  ol: ({ children }) => (
                    <ol className="list-decimal list-inside space-y-1 mb-3">
                      {children}
                    </ol>
                  ),

                  // Custom blockquote component
                  blockquote: ({ children }) => (
                    <blockquote className={cn(
                      "border-l-4 pl-4 py-2 my-3 italic",
                      isUser 
                        ? "border-primary-foreground/30 text-primary-foreground/90"
                        : "border-primary/30 text-muted-foreground"
                    )}>
                      {children}
                    </blockquote>
                  ),

                  // Custom heading components
                  h1: ({ children }) => (
                    <h1 className="text-lg font-semibold mb-2 mt-4 first:mt-0">
                      {children}
                    </h1>
                  ),
                  h2: ({ children }) => (
                    <h2 className="text-base font-semibold mb-2 mt-3 first:mt-0">
                      {children}
                    </h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className="text-sm font-semibold mb-2 mt-3 first:mt-0">
                      {children}
                    </h3>
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>

            {/* Message reactions placeholder */}
            {message.metadata?.reactions && Object.keys(message.metadata.reactions).length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2 pt-2 border-t border-border/20">
                {Object.entries(message.metadata.reactions).map(([reaction, users]) => (
                  <Button
                    key={reaction}
                    variant="ghost"
                    size="sm"
                    className="h-6 px-2 text-xs rounded-full"
                  >
                    {reaction} {users.length}
                  </Button>
                ))}
              </div>
            )}
          </div>

          {/* Timestamp and status */}
          {showTimestamp && (
            <div className={cn(
              "mt-1.5 px-1 text-xs text-muted-foreground/60 transition-opacity",
              "opacity-0 group-hover:opacity-100",
              isUser && "text-right"
            )}>
              {new Date(message.timestamp).toLocaleTimeString('en-US', {
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
              })}
              {message.metadata?.mentions && message.metadata.mentions.length > 0 && (
                <span className="ml-2 text-primary text-xs">
                  @{message.metadata.mentions.length} mention{message.metadata.mentions.length > 1 ? 's' : ''}
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    )
  }
)

MessageBubble.displayName = 'MessageBubble'

export default MessageBubble