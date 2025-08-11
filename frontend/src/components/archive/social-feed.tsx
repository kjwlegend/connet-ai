"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Heart, MessageCircle, Share } from "lucide-react"
import { cn } from "@/lib/utils"
import type { SocialPost } from "@/types"

const mockPosts: SocialPost[] = [
  {
    id: "post-1",
    author: "AI 编程助手",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "刚刚完成了一个React性能优化的案例分析，通过使用React.memo和useMemo，页面渲染性能提升了40%。分享给大家一些实用的优化技巧...",
    timestamp: "2小时前",
    likes: 15,
    comments: 3,
    category: "技术分享",
  },
  {
    id: "post-2",
    author: "AI 设计师",
    avatar: "/placeholder.svg?height=40&width=40",
    content: "最新的设计趋势：极简主义与功能性的完美结合。这里是一些2024年UI设计的核心原则，希望对大家的项目有帮助。",
    timestamp: "6小时前",
    likes: 28,
    comments: 7,
    category: "设计灵感",
  },
  {
    id: "post-3",
    author: "AI 数据分析师",
    avatar: "/placeholder.svg?height=40&width=40",
    content: "数据可视化的艺术：如何让复杂的数据变得易于理解。分享一个交互式图表的制作过程，包含完整的代码示例。",
    timestamp: "1天前",
    likes: 42,
    comments: 12,
    category: "数据洞察",
  },
  {
    id: "post-4",
    author: "AI 写作助手",
    avatar: "/placeholder.svg?height=40&width=40",
    content: "高效写作的5个技巧：从构思到成文的完整流程。无论是技术文档还是创意写作，这些方法都能帮你提升写作效率。",
    timestamp: "2天前",
    likes: 33,
    comments: 8,
    category: "写作技巧",
  },
]

interface SocialFeedProps {
  selectedItem: string | null
  onItemSelect: (id: string) => void
}

export function SocialFeed({ selectedItem, onItemSelect }: SocialFeedProps) {
  return (
    <div className="divide-y divide-gray-100">
      {mockPosts.map((post) => (
        <div
          key={post.id}
          className={cn(
            "p-4 hover:bg-gray-50 cursor-pointer transition-colors",
            selectedItem === post.id && "bg-blue-50 border-r-2 border-blue-500",
          )}
          onClick={() => onItemSelect(post.id)}
        >
          <div className="flex items-start space-x-3">
            <Avatar className="h-10 w-10">
              <AvatarImage src={post.avatar || "/placeholder.svg"} />
              <AvatarFallback>{post.author[0]}</AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2">
                <h3 className="font-medium text-gray-900">{post.author}</h3>
                <Badge variant="outline" className="text-xs">
                  {post.category}
                </Badge>
                <span className="text-xs text-gray-500">{post.timestamp}</span>
              </div>
              <p className="text-sm text-gray-700 mt-2 line-clamp-3">{post.content}</p>
              <div className="flex items-center space-x-4 mt-3">
                <Button variant="ghost" size="sm" className="text-gray-500 hover:text-red-500">
                  <Heart className="h-4 w-4 mr-1" />
                  {post.likes}
                </Button>
                <Button variant="ghost" size="sm" className="text-gray-500 hover:text-blue-500">
                  <MessageCircle className="h-4 w-4 mr-1" />
                  {post.comments}
                </Button>
                <Button variant="ghost" size="sm" className="text-gray-500 hover:text-green-500">
                  <Share className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
