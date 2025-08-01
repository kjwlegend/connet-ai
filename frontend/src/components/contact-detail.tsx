"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { MessageCircle, Star, Settings } from "lucide-react"

interface ContactDetailProps {
  selectedItem: string
}

export function ContactDetail({ selectedItem }: ContactDetailProps) {
  return (
    <div className="p-6 space-y-6">
      {/* Agent Profile */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-4">
            <Avatar className="h-20 w-20">
              <AvatarImage src="/placeholder.svg?height=80&width=80" />
              <AvatarFallback>AI</AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <CardTitle className="text-2xl">AI 编程助手</CardTitle>
              <p className="text-lg text-blue-600 font-medium">全栈开发专家</p>
              <div className="flex items-center space-x-2 mt-2">
                <Badge variant="secondary">编程开发</Badge>
                <Badge variant="outline" className="text-green-600">
                  在线
                </Badge>
              </div>
            </div>
            <div className="flex space-x-2">
              <Button>
                <MessageCircle className="h-4 w-4 mr-2" />
                开始对话
              </Button>
              <Button variant="outline">
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">
            我是一个专业的AI编程助手，精通多种编程语言和开发框架。 可以帮助你解决代码问题、优化程序性能、设计系统架构，
            以及提供最佳实践建议。无论是前端、后端还是全栈开发， 我都能为你提供专业的技术支持。
          </p>
        </CardContent>
      </Card>

      {/* Capabilities */}
      <Card>
        <CardHeader>
          <CardTitle>专业能力</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <h4 className="font-medium">编程语言</h4>
              <div className="flex flex-wrap gap-2">
                {["JavaScript", "TypeScript", "Python", "Java", "Go"].map((lang) => (
                  <Badge key={lang} variant="outline">
                    {lang}
                  </Badge>
                ))}
              </div>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium">框架技术</h4>
              <div className="flex flex-wrap gap-2">
                {["React", "Next.js", "Node.js", "Express", "Django"].map((tech) => (
                  <Badge key={tech} variant="outline">
                    {tech}
                  </Badge>
                ))}
              </div>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium">数据库</h4>
              <div className="flex flex-wrap gap-2">
                {["MySQL", "PostgreSQL", "MongoDB", "Redis"].map((db) => (
                  <Badge key={db} variant="outline">
                    {db}
                  </Badge>
                ))}
              </div>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium">工具平台</h4>
              <div className="flex flex-wrap gap-2">
                {["Git", "Docker", "AWS", "Vercel"].map((tool) => (
                  <Badge key={tool} variant="outline">
                    {tool}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Statistics */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6 text-center">
            <div className="text-2xl font-bold text-blue-600">1,234</div>
            <p className="text-sm text-gray-600">解决问题</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 text-center">
            <div className="text-2xl font-bold text-green-600">4.9</div>
            <div className="flex items-center justify-center mt-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <Star key={star} className="h-4 w-4 text-yellow-400 fill-current" />
              ))}
            </div>
            <p className="text-sm text-gray-600">用户评分</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 text-center">
            <div className="text-2xl font-bold text-purple-600">567</div>
            <p className="text-sm text-gray-600">协作项目</p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>最近活动</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <p className="text-sm">帮助用户优化了React组件性能</p>
              <span className="text-xs text-gray-500">2小时前</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <p className="text-sm">参与了项目架构设计讨论</p>
              <span className="text-xs text-gray-500">6小时前</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <p className="text-sm">分享了代码优化最佳实践</p>
              <span className="text-xs text-gray-500">1天前</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
