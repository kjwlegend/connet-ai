"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { MessageCircle, Settings2 } from "lucide-react"

const mockTools = [
  { id: "tool-1", name: "代码生成器", enabled: true },
  { id: "tool-2", name: "代码审查", enabled: true },
  { id: "tool-3", name: "性能分析", enabled: false },
  { id: "tool-4", name: "文档生成", enabled: true },
]

interface ContactDetailSimpleProps {
  selectedItem: string
}

export function ContactDetailSimple({ selectedItem }: ContactDetailSimpleProps) {
  return (
    <div className="p-6 space-y-6">
      {/* Agent Profile - Simplified */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-4">
            <Avatar className="h-16 w-16">
              <AvatarImage src="/placeholder.svg?height=64&width=64" />
              <AvatarFallback>AI</AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <CardTitle className="text-xl">AI 编程助手</CardTitle>
              <p className="text-blue-600 font-medium">全栈开发专家</p>
            </div>
            <Button>
              <MessageCircle className="h-4 w-4 mr-2" />
              开始对话
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Tool Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>工具配置</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {mockTools.map((tool) => (
              <div key={tool.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-2 h-2 rounded-full ${tool.enabled ? "bg-green-500" : "bg-gray-300"}`} />
                  <span className="font-medium">{tool.name}</span>
                </div>
                <Button variant="ghost" size="sm">
                  <Settings2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
