import React, { useRef, useEffect } from 'react'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Message } from '../types'
import MessageItem from './MessageItem'

interface MessageListProps {
  messages: Message[]
  currentUserAvatar?: string
  currentUserName: string
  onRetryMessage: (message: Message) => void
}
export default function MessageList({ messages, currentUserAvatar, currentUserName }: MessageListProps) {
  // const scrollAreaRef = useRef<HTMLDivElement>(null); // This ref is for the outer ScrollArea component
  const viewportRef = useRef<HTMLDivElement>(null); // Ref for the actual scrollable viewport

  useEffect(() => {
    if (viewportRef.current) {
      // console.log("Scrolling to bottom in MessageList, scrollHeight:", viewportRef.current.scrollHeight);
      viewportRef.current.scrollTop = viewportRef.current.scrollHeight;
    }
  }, [messages]); // Scroll whenever messages change

  return (
    // The ScrollArea itself should take up the available space using flex-1
    // And its parent needs to be a flex container with a defined height or also flex-1
    <ScrollArea className="flex-1 p-4 bg-gray-50 dark:bg-gray-850 overflow-y-auto">
      {/*
        The direct child of ScrollArea (from shadcn/ui) is usually the viewport.
        We give this viewport a ref.
        It needs to have a height that allows it to scroll, or its content will dictate its height.
        Typically, the viewport div should implicitly get height from its ScrollArea parent if the parent has flex:1
      */}
      <div ref={viewportRef} className="h-full w-full"> {/* This inner div might not be strictly necessary if ScrollArea's viewport can be reffed directly */}
        {messages.map((msg, index) => (
          <MessageItem
            key={`main-${msg.id}-${index}`}
            msg={msg}
            currentUserAvatar={currentUserAvatar}
            currentUserName={currentUserName}
            // Pass onRetry and onEdit if you implemented them
          />
        ))}
      </div>
    </ScrollArea>
  );
}