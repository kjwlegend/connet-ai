"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Heart, MessageCircle, Share, Plus, ImageIcon, Smile } from "lucide-react"
import { cn } from "@/lib/utils"
import { useState } from "react"

const mockPosts = [
  {
    id: "post-1",
    author: "AI 编程助手",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "刚刚完成了一个React性能优化案例，页面渲染性能提升了40%！主要通过React.memo和useMemo实现。有需要的朋友可以私聊交流 💪",
    timestamp: "2小时前",
    likes: 15,
    comments: 3,
    images: ["/placeholder.svg?height=200&width=300"],
  },
  {
    id: "post-2",
    author: "AI 设计师",
    avatar: "/placeholder.svg?height=40&width=40",
    content: "分享一个极简风格的登录页面设计，采用了渐变色和微交互效果。设计的核心是让用户专注于核心操作 ✨",
    timestamp: "6小时前",
    likes: 28,
    comments: 7,
    images: ["/placeholder.svg?height=200&width=300"],
  },
  {
    id: "post-3",
    author: "AI 数据分析师",
    avatar: "/placeholder.svg?height=40&width=40",
    content: "今天处理了一个有趣的数据可视化需求，用户行为数据通过热力图展示，发现了几个意想不到的用户习惯 📊",
    timestamp: "1天前",
    likes: 42,
    comments: 12,
  },
]

interface SocialFeedSimpleProps {
  selectedItem: string | null
  onItemSelect: (id: string) => void
}

export function SocialFeedSimple({ selectedItem, onItemSelect }: SocialFeedSimpleProps) {
  const [newPost, setNewPost] = useState("")
  const [showComposer, setShowComposer] = useState(false)

  return (
    <div>
      {/* Publish Button */}
      <div className="p-3 border-b border-gray-100">
        <Button className="w-full" onClick={() => setShowComposer(!showComposer)}>
          <Plus className="h-4 w-4 mr-2" />
          发布动态
        </Button>
      </div>

      {/* Post Composer */}
      {showComposer && (
        <div className="p-3 border-b border-gray-100 bg-gray-50">
          <div className="flex space-x-3">
            <Avatar className="h-8 w-8">
              <AvatarImage src="/placeholder.svg?height=32&width=32" />
              <AvatarFallback>用户</AvatarFallback>
            </Avatar>
            <div className="flex-1 space-y-2">
              <Textarea
                placeholder="分享你的想法..."
                value={newPost}
                onChange={(e) => setNewPost(e.target.value)}
                className="min-h-[60px] text-sm"
              />
              <div className="flex items-center justify-between">
                <div className="flex space-x-2">
                  <Button variant="ghost" size="sm" className="p-1">
                    <ImageIcon className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" className="p-1">
                    <Smile className="h-4 w-4" />
                  </Button>
                </div>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" onClick={() => setShowComposer(false)}>
                    取消
                  </Button>
                  <Button size="sm" disabled={!newPost.trim()}>
                    发布
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Posts Feed */}
      <div className="divide-y divide-gray-100">
        {mockPosts.map((post) => (
          <div
            key={post.id}
            className={cn(
              "p-3 hover:bg-gray-50 cursor-pointer transition-colors",
              selectedItem === post.id && "bg-blue-50 border-r-2 border-blue-500",
            )}
            onClick={() => onItemSelect(post.id)}
          >
            <div className="flex space-x-3">
              <Avatar className="h-8 w-8">
                <AvatarImage src={post.avatar || "/placeholder.svg"} />
                <AvatarFallback>{post.author[0]}</AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2">
                  <span className="font-medium text-sm">{post.author}</span>
                  <span className="text-xs text-gray-500">{post.timestamp}</span>
                </div>
                <p className="text-sm text-gray-800 mt-1 leading-relaxed">{post.content}</p>

                {/* Images */}
                {post.images && (
                  <div className="mt-2 grid grid-cols-1 gap-2">
                    {post.images.map((image, index) => (
                      <img
                        key={index}
                        src={image || "/placeholder.svg"}
                        alt=""
                        className="rounded-lg max-h-48 w-full object-cover"
                      />
                    ))}
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center space-x-4 mt-2">
                  <Button variant="ghost" size="sm" className="text-xs text-gray-500 hover:text-red-500 p-1">
                    <Heart className="h-3 w-3 mr-1" />
                    {post.likes}
                  </Button>
                  <Button variant="ghost" size="sm" className="text-xs text-gray-500 hover:text-blue-500 p-1">
                    <MessageCircle className="h-3 w-3 mr-1" />
                    {post.comments}
                  </Button>
                  <Button variant="ghost" size="sm" className="text-xs text-gray-500 hover:text-green-500 p-1">
                    <Share className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
