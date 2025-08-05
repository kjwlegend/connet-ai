"use client"

import { useState, useRef, useCallback, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Send, Paperclip, Smile, Plus, Mic, FileImage, Calendar, Hash } from "lucide-react"
import { cn } from "@/lib/utils"
import dynamic from "next/dynamic"
import { useInputShortcuts } from "@/hooks/useKeyboardShortcuts"

// Dynamically import emoji picker to avoid SSR issues
const EmojiPicker = dynamic(
  () => import('@emoji-mart/react').then(mod => mod.default),
  { 
    ssr: false,
    loading: () => <div className="w-80 h-60 flex items-center justify-center">Loading...</div>
  }
)

interface ChatInputProps {
  value: string
  onChange: (value: string) => void
  onSend: () => void
  onKeyDown?: (e: React.KeyboardEvent) => void
  disabled?: boolean
  isSending?: boolean
  placeholder?: string
  className?: string
}

// Demo placeholder texts that rotate
const DEMO_PLACEHOLDERS = [
  "Ask me anything about coding, design, or project planning...",
  "Try: 'Help me optimize this React component' or 'Explain this code'...",
  "Need help? Just @ mention an AI agent to get started..."
]

export function ChatInput({
  value,
  onChange,
  onSend,
  onKeyDown,
  disabled = false,
  isSending = false,
  placeholder,
  className
}: ChatInputProps) {
  const [isEmojiOpen, setIsEmojiOpen] = useState(false)
  const [currentPlaceholder, setCurrentPlaceholder] = useState(0)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Text formatting functions
  const formatBold = useCallback(() => {
    const textarea = textareaRef.current
    if (!textarea) return

    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const selectedText = value.slice(start, end)
    const beforeText = value.slice(0, start)
    const afterText = value.slice(end)

    const newText = selectedText ? `**${selectedText}**` : '****'
    const newValue = beforeText + newText + afterText
    onChange(newValue)

    // Set cursor position
    setTimeout(() => {
      const newCursorPos = selectedText ? start + newText.length : start + 2
      textarea.setSelectionRange(newCursorPos, newCursorPos)
      textarea.focus()
    }, 0)
  }, [value, onChange])

  const formatItalic = useCallback(() => {
    const textarea = textareaRef.current
    if (!textarea) return

    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const selectedText = value.slice(start, end)
    const beforeText = value.slice(0, start)
    const afterText = value.slice(end)

    const newText = selectedText ? `*${selectedText}*` : '**'
    const newValue = beforeText + newText + afterText
    onChange(newValue)

    setTimeout(() => {
      const newCursorPos = selectedText ? start + newText.length : start + 1
      textarea.setSelectionRange(newCursorPos, newCursorPos)
      textarea.focus()
    }, 0)
  }, [value, onChange])

  const formatCode = useCallback(() => {
    const textarea = textareaRef.current
    if (!textarea) return

    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const selectedText = value.slice(start, end)
    const beforeText = value.slice(0, start)
    const afterText = value.slice(end)

    const newText = selectedText ? `\`${selectedText}\`` : '``'
    const newValue = beforeText + newText + afterText
    onChange(newValue)

    setTimeout(() => {
      const newCursorPos = selectedText ? start + newText.length : start + 1
      textarea.setSelectionRange(newCursorPos, newCursorPos)
      textarea.focus()
    }, 0)
  }, [value, onChange])

  const clearInput = useCallback(() => {
    onChange('')
    textareaRef.current?.focus()
  }, [onChange])

  const selectAll = useCallback(() => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.select()
    }
  }, [])

  // Setup input shortcuts
  useInputShortcuts({
    onSend: () => {
      if (value.trim() && !disabled && !isSending) {
        onSend()
      }
    },
    onClear: clearInput,
    onFormatBold: formatBold,
    onFormatItalic: formatItalic,
    onFormatCode: formatCode,
    onSelectAll: selectAll,
    enabled: !disabled
  })

  // Rotate placeholder text every 3 seconds
  useEffect(() => {
    if (!placeholder) {
      const interval = setInterval(() => {
        setCurrentPlaceholder(prev => (prev + 1) % DEMO_PLACEHOLDERS.length)
      }, 3000)

      return () => clearInterval(interval)
    }
  }, [placeholder])

  // Auto-resize textarea
  const adjustTextareaHeight = useCallback(() => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      const newHeight = Math.min(Math.max(textarea.scrollHeight, 44), 120) // Min 44px, max 120px
      textarea.style.height = `${newHeight}px`
    }
  }, [])

  useEffect(() => {
    adjustTextareaHeight()
  }, [value, adjustTextareaHeight])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Handle shortcuts
    if (e.key === 'Enter' && !e.shiftKey && !e.altKey && !e.ctrlKey && !e.metaKey) {
      e.preventDefault()
      if (value.trim() && !disabled && !isSending) {
        onSend()
      }
    }

    // Pass through to parent handler for additional shortcuts
    onKeyDown?.(e)
  }

  const handleEmojiSelect = (emoji: any) => {
    const cursor = textareaRef.current?.selectionStart || value.length
    const newValue = value.slice(0, cursor) + emoji.native + value.slice(cursor)
    onChange(newValue)
    setIsEmojiOpen(false)
    
    // Focus textarea and set cursor position
    setTimeout(() => {
      if (textareaRef.current) {
        textareaRef.current.focus()
        textareaRef.current.setSelectionRange(cursor + emoji.native.length, cursor + emoji.native.length)
      }
    }, 0)
  }

  const handleSend = () => {
    if (value.trim() && !disabled && !isSending) {
      onSend()
    }
  }

  const displayPlaceholder = placeholder || DEMO_PLACEHOLDERS[currentPlaceholder]

  return (
    <div className={cn(
      "border-t border-border/60 bg-background/80 backdrop-blur-sm",
      className
    )}>
      {/* Input Area */}
      <div className="px-6 py-4">
        <div className="flex items-end gap-3">
          {/* Attachment Button */}
          <Popover>
            <PopoverTrigger asChild>
              <Button 
                variant="ghost" 
                size="sm" 
                className="h-10 w-10 p-0 rounded-lg hover:bg-accent/50 transition-all duration-200 mb-1"
                disabled={disabled}
              >
                <Plus className="h-5 w-5" />
              </Button>
            </PopoverTrigger>
            <PopoverContent side="top" className="w-56 p-2">
              <div className="grid grid-cols-2 gap-1">
                <Button variant="ghost" size="sm" className="h-10 justify-start">
                  <Paperclip className="h-4 w-4 mr-2" />
                  File
                </Button>
                <Button variant="ghost" size="sm" className="h-10 justify-start">
                  <FileImage className="h-4 w-4 mr-2" />
                  Image
                </Button>
                <Button variant="ghost" size="sm" className="h-10 justify-start">
                  <Calendar className="h-4 w-4 mr-2" />
                  Schedule
                </Button>
                <Button variant="ghost" size="sm" className="h-10 justify-start">
                  <Hash className="h-4 w-4 mr-2" />
                  Snippet
                </Button>
              </div>
            </PopoverContent>
          </Popover>

          {/* Main Input Area */}
          <div className="flex-1 relative">
            <Textarea
              ref={textareaRef}
              value={value}
              onChange={(e) => onChange(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={displayPlaceholder}
              disabled={disabled}
              className={cn(
                "min-h-[44px] max-h-[120px] resize-none rounded-2xl border-border/40",
                "bg-muted/30 focus:bg-background transition-all duration-200",
                "placeholder:text-muted-foreground/60 placeholder:transition-all placeholder:duration-300",
                "scrollbar-thin scrollbar-thumb-border/40 scrollbar-track-transparent",
                "px-4 py-3 pr-12", // Space for emoji button
                isSending && "opacity-50"
              )}
              style={{ 
                paddingRight: '3rem', // Space for emoji button
                lineHeight: '1.4'
              }}
            />
            
            {/* Emoji Button inside textarea */}
            <Popover open={isEmojiOpen} onOpenChange={setIsEmojiOpen}>
              <PopoverTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="absolute right-2 top-2 h-8 w-8 p-0 rounded-lg hover:bg-accent/50 transition-all duration-200"
                  disabled={disabled}
                >
                  <Smile className="h-4 w-4" />
                </Button>
              </PopoverTrigger>
              <PopoverContent side="top" className="w-auto p-0 border-0 shadow-xl">
                <EmojiPicker
                  data={async () => {
                    const response = await import('@emoji-mart/data')
                    return response.default
                  }}
                  onEmojiSelect={handleEmojiSelect}
                  theme="light"
                  set="native"
                  showPreview={false}
                  showSkinTones={false}
                  emojiSize={20}
                  perLine={8}
                  maxFrequentRows={2}
                />
              </PopoverContent>
            </Popover>
          </div>

          {/* Voice Input Button */}
          <Button 
            variant="ghost" 
            size="sm" 
            className="h-10 w-10 p-0 rounded-lg hover:bg-accent/50 transition-all duration-200 mb-1"
            disabled={disabled}
          >
            <Mic className="h-5 w-5" />
          </Button>

          {/* Send Button */}
          <Button
            onClick={handleSend}
            disabled={!value.trim() || disabled || isSending}
            size="sm"
            className={cn(
              "h-10 w-10 p-0 rounded-lg transition-all duration-200 mb-1",
              "hover:scale-105 active:scale-95",
              "disabled:scale-100 disabled:opacity-50",
              value.trim() && !disabled && !isSending 
                ? "bg-primary text-primary-foreground shadow-md hover:shadow-lg" 
                : ""
            )}
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>

        {/* Input Help Text */}
        <div className="flex items-center justify-between mt-2 px-2">
          <div className="text-xs text-muted-foreground/60 transition-all duration-300">
            {isSending ? (
              <span className="flex items-center gap-1">
                <div className="w-1 h-1 bg-primary rounded-full animate-pulse" />
                <div className="w-1 h-1 bg-primary rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
                <div className="w-1 h-1 bg-primary rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
                <span className="ml-1">Sending...</span>
              </span>
            ) : (
              <span>
                <kbd className="px-1.5 py-0.5 bg-muted/50 rounded text-xs">Enter</kbd> to send, 
                <kbd className="px-1.5 py-0.5 bg-muted/50 rounded text-xs ml-1">Shift+Enter</kbd> for new line, 
                <kbd className="px-1.5 py-0.5 bg-muted/50 rounded text-xs ml-1">Ctrl+B</kbd> bold, 
                <kbd className="px-1.5 py-0.5 bg-muted/50 rounded text-xs ml-1">Ctrl+I</kbd> italic
              </span>
            )}
          </div>
          
          {/* Character count (optional) */}
          {value.length > 0 && (
            <div className="text-xs text-muted-foreground/60">
              {value.length}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ChatInput