"use client"

import { useState } from "react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Send, Paperclip, Smile, MoreVertical } from "lucide-react"

interface Message {
  id: string
  sender: string
  content: string
  timestamp: string
  isUser: boolean
}

const mockMessages: Message[] = [
  {
    id: "1",
    sender: "AI 编程助手",
    content: "你好！我是你的AI编程助手，可以帮你解决各种编程问题。有什么我可以帮助你的吗？",
    timestamp: "10:30",
    isUser: false,
  },
  {
    id: "2",
    sender: "用户",
    content: "我想优化一下React组件的性能，有什么建议吗？",
    timestamp: "10:32",
    isUser: true,
  },
  {
    id: "3",
    sender: "AI 编程助手",
    content:
      "当然可以！React性能优化有几个关键点：\n\n1. 使用React.memo包装组件避免不必要的重渲染\n2. 使用useMemo和useCallback缓存计算结果和函数\n3. 合理使用useState和useEffect\n4. 避免在render中创建新对象\n\n你想了解哪个方面的详细实现？",
    timestamp: "10:33",
    isUser: false,
  },
]

interface ChatInterfaceProps {
  selectedItem: string
}

export function ChatInterface({ selectedItem }: ChatInterfaceProps) {
  const [message, setMessage] = useState("")
  const [messages, setMessages] = useState(mockMessages)

  const handleSendMessage = () => {
    if (!message.trim()) return

    const newMessage: Message = {
      id: Date.now().toString(),
      sender: "用户",
      content: message,
      timestamp: new Date().toLocaleTimeString("zh-CN", {
        hour: "2-digit",
        minute: "2-digit",
      }),
      isUser: true,
    }

    setMessages([...messages, newMessage])
    setMessage("")

    // 模拟AI回复
    setTimeout(() => {
      const aiReply: Message = {
        id: (Date.now() + 1).toString(),
        sender: "AI 编程助手",
        content: "我理解你的问题。让我为你提供一个详细的解决方案...",
        timestamp: new Date().toLocaleTimeString("zh-CN", {
          hour: "2-digit",
          minute: "2-digit",
        }),
        isUser: false,
      }
      setMessages((prev) => [...prev, aiReply])
    }, 1000)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Chat Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <Avatar className="h-10 w-10">
            <AvatarImage src="/placeholder.svg?height=40&width=40" />
            <AvatarFallback>AI</AvatarFallback>
          </Avatar>
          <div>
            <h2 className="font-semibold text-gray-900">AI 编程助手</h2>
            <p className="text-sm text-green-600">在线</p>
          </div>
        </div>
        <Button variant="ghost" size="sm">
          <MoreVertical className="h-5 w-5" />
        </Button>
      </div>

      {/* Messages Area */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.isUser ? "justify-end" : "justify-start"}`}>
              <div
                className={`flex items-start space-x-2 max-w-[70%] ${
                  msg.isUser ? "flex-row-reverse space-x-reverse" : ""
                }`}
              >
                {!msg.isUser && (
                  <Avatar className="h-8 w-8">
                    <AvatarImage src="/placeholder.svg?height=32&width=32" />
                    <AvatarFallback>AI</AvatarFallback>
                  </Avatar>
                )}
                <div
                  className={`rounded-lg p-3 ${msg.isUser ? "bg-blue-500 text-white" : "bg-gray-100 text-gray-900"}`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  <p className={`text-xs mt-1 ${msg.isUser ? "text-blue-100" : "text-gray-500"}`}>{msg.timestamp}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center space-x-2">
          <Button variant="ghost" size="sm">
            <Paperclip className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="sm">
            <Smile className="h-5 w-5" />
          </Button>
          <Input
            placeholder="输入消息..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
            className="flex-1"
          />
          <Button onClick={handleSendMessage} disabled={!message.trim()}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
