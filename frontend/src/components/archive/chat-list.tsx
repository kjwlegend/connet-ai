"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { Conversation } from "@/types"

const mockConversations: Conversation[] = [
  {
    id: "agent-1",
    name: "AI 编程助手",
    avatar: "/placeholder.svg?height=40&width=40",
    lastMessage: "我可以帮你优化这段代码的性能",
    timestamp: "2分钟前",
    unreadCount: 2,
    isGroup: false,
  },
  {
    id: "agent-2",
    name: "AI 设计师",
    avatar: "/placeholder.svg?height=40&width=40",
    lastMessage: "这个UI设计方案怎么样？",
    timestamp: "10分钟前",
    unreadCount: 0,
    isGroup: false,
  },
  {
    id: "group-1",
    name: "项目协作群",
    avatar: "/placeholder.svg?height=40&width=40",
    lastMessage: "AI分析师: 数据分析报告已完成",
    timestamp: "1小时前",
    unreadCount: 5,
    isGroup: true,
    participants: ["AI编程助手", "AI设计师", "AI分析师"],
  },
  {
    id: "agent-3",
    name: "AI 写作助手",
    avatar: "/placeholder.svg?height=40&width=40",
    lastMessage: "文档草稿已经准备好了",
    timestamp: "2小时前",
    unreadCount: 1,
    isGroup: false,
  },
]

interface ChatListProps {
  selectedItem: string | null
  onItemSelect: (id: string) => void
}

export function ChatList({ selectedItem, onItemSelect }: ChatListProps) {
  return (
    <div className="divide-y divide-border">
      {mockConversations.map((conversation) => (
        <div
          key={conversation.id}
          className={cn(
            "p-4 hover:bg-accent/30 cursor-pointer transition-colors",
            selectedItem === conversation.id && "bg-accent/50 border-r-2 border-primary",
          )}
          onClick={() => onItemSelect(conversation.id)}
        >
          <div className="flex items-start space-x-3">
            <div className="relative">
              <Avatar className="h-10 w-10">
                <AvatarImage src={conversation.avatar || "/placeholder.svg"} />
                <AvatarFallback>{conversation.name[0]}</AvatarFallback>
              </Avatar>
              {conversation.unreadCount > 0 && (
                <div className="absolute -top-1 -right-1 w-5 h-5 bg-destructive text-destructive-foreground text-xs rounded-full flex items-center justify-center">
                  {conversation.unreadCount > 9 ? "9+" : conversation.unreadCount}
                </div>
              )}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <h3 className="font-medium text-foreground truncate">
                  {conversation.name}
                  {conversation.isGroup && (
                    <Badge variant="secondary" className="ml-2 text-xs">
                      群聊
                    </Badge>
                  )}
                </h3>
                <span className="text-xs text-muted-foreground">{conversation.timestamp}</span>
              </div>
              <p className="text-sm text-muted-foreground truncate mt-1">{conversation.lastMessage}</p>
              {conversation.isGroup && conversation.participants && (
                <p className="text-xs text-muted-foreground/70 mt-1">{conversation.participants.join(", ")}</p>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
