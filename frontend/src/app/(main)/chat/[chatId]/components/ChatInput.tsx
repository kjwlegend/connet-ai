import React, { KeyboardEvent, useState, useEffect, useRef } from 'react'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Send, CornerDownLeft, Info } from 'lucide-react' // Added Info for tooltip
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip' // Add Tooltip via shadcn/ui

type SendMode = 'enter' | 'ctrlEnter'

interface ChatInputProps {
  inputValue: string
  onInputChange: (value: string) => void
  onSendMessage: () => void
  inputRef?: React.RefObject<HTMLTextAreaElement>
  isSending?: boolean
  onMaybeShowSelector: (value: string, caretPosition: number | null) => void // Pass caret position
}

export default function ChatInput({
  inputValue,
  onInputChange,
  onSendMessage,
  inputRef: parentInputRef, // Renamed to avoid conflict with local ref
  isSending,
  onMaybeShowSelector,
}: ChatInputProps) {
  const [sendMode, setSendMode] = useState<SendMode>('enter')
  const localTextareaRef = useRef<HTMLTextAreaElement>(null)
  const textareaRef = parentInputRef || localTextareaRef // Use parent ref if provided

  // Auto-resize textarea height
  useEffect(() => {
    if (textareaRef.current) {
      // Temporarily set height to auto to get the correct scrollHeight
      textareaRef.current.style.height = 'auto'
      // Set the height to the scrollHeight, but not exceeding max-height
      const newHeight = Math.min(textareaRef.current.scrollHeight, 200) // 200px max-height
      textareaRef.current.style.height = `${newHeight}px`
    }
  }, [inputValue, textareaRef]) // Added textareaRef dependency

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Pass current value and caret position to parent for @ detection
    const caretPosition = e.currentTarget.selectionStart
    onMaybeShowSelector(e.currentTarget.value, caretPosition)

    if (isSending) {
      e.preventDefault()
      return
    }

    if (sendMode === 'enter') {
      if (e.key === 'Enter' && !e.shiftKey && !e.metaKey && !e.ctrlKey) {
        e.preventDefault()
        onSendMessage()
      }
    } else if (sendMode === 'ctrlEnter') {
      if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        onSendMessage()
      }
    }
  }

  const toggleSendMode = () => {
    const newMode = sendMode === 'enter' ? 'ctrlEnter' : 'enter'
    setSendMode(newMode)
    // TODO: Persist this preference (e.g., localStorage or Zustand store)
    // For example: localStorage.setItem('chatSendMode', newMode);
  }

  // Load send mode preference from localStorage on mount (example)
  useEffect(() => {
    const savedMode = localStorage.getItem('chatSendMode') as SendMode | null
    if (savedMode && (savedMode === 'enter' || savedMode === 'ctrlEnter')) {
      setSendMode(savedMode)
    }
  }, [])

  return (
    <div className="bg-white dark:bg-gray-800 p-3 sm:p-4 border-t border-gray-200 dark:border-gray-700">
      {/* The main flex container for the input area */}
      <div className="flex items-end space-x-2">
        {/* Textarea wrapper to control its growth */}
        <div className="flex-1 min-w-0">
          {' '}
          {/* min-w-0 is important for flex-shrink */}
          <Textarea
            ref={textareaRef}
            placeholder="Type @ to mention an agent or your message... (Shift+Enter for new line)"
            value={inputValue}
            onChange={(e) => onInputChange(e.target.value)}
            onKeyDown={handleKeyDown}
            className="w-full resize-none overflow-y-auto min-h-[40px] max-h-[200px] py-2 leading-tight border-gray-300 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500"
            rows={1}
            disabled={isSending}
            style={{ scrollbarWidth: 'thin' }} // For Firefox, optional
          />
        </div>

        <div className="flex flex-col-reverse sm:flex-row items-center sm:items-end space-y-2 space-y-reverse sm:space-y-0 sm:space-x-2">
          {/* Send Mode Toggle Button - Improved */}
          <TooltipProvider delayDuration={300}>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={toggleSendMode}
                  className="h-10 w-10 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 flex-shrink-0"
                  aria-label={`Current send mode: ${
                    sendMode === 'enter'
                      ? 'Enter to send'
                      : 'Ctrl/Cmd + Enter to send'
                  }. Click to toggle.`}
                >
                  {sendMode === 'enter' ? (
                    <CornerDownLeft className="h-5 w-5" />
                  ) : (
                    <div className="flex items-center justify-center h-5 w-5">
                      <span className="text-xs font-semibold">^</span>
                      <CornerDownLeft className="h-4 w-4 ml-px" />
                    </div>
                  )}
                </Button>
              </TooltipTrigger>
              <TooltipContent side="top" className="text-xs">
                <p>
                  Send with:{' '}
                  <strong>
                    {sendMode === 'enter'
                      ? 'Enter'
                      : navigator.platform.toUpperCase().indexOf('MAC') >= 0
                      ? 'Cmd+Enter'
                      : 'Ctrl+Enter'}
                  </strong>
                </p>
                <p>Click to switch.</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          {/* Send Button */}
          <Button
            onClick={onSendMessage}
            disabled={isSending || !inputValue.trim()}
            size="default"
            className="h-10 px-4 flex-shrink-0"
          >
            <Send className="h-4 w-4 mr-0 sm:mr-2" />
            <span className="hidden sm:inline">Send</span>
          </Button>
        </div>
      </div>

      {/* Help text for send mode */}
      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1.5 pl-1">
        {sendMode === 'enter'
          ? 'Shift+Enter for new line. Enter to send.'
          : `Enter for new line. ${
              navigator.platform.toUpperCase().indexOf('MAC') >= 0
                ? 'Cmd+Enter'
                : 'Ctrl+Enter'
            } to send.`}
      </p>
    </div>
  )
}
