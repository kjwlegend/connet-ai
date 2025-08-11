"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { MessageCircle, Edit2, Save, X, Plus, Settings2 } from "lucide-react"
import { useState } from "react"

const mockTools = [
  { id: "tool-1", name: "代码生成器", enabled: true },
  { id: "tool-2", name: "代码审查", enabled: true },
  { id: "tool-3", name: "性能分析", enabled: false },
  { id: "tool-4", name: "文档生成", enabled: true },
]

interface ContactDetailEditableProps {
  selectedItem: string
}

export function ContactDetailEditable({ selectedItem }: ContactDetailEditableProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [note, setNote] = useState("代码优化专家")
  const [tags, setTags] = useState(["编程", "代码审查"])
  const [newTag, setNewTag] = useState("")

  const handleSave = () => {
    setIsEditing(false)
    // Save logic here
  }

  const handleCancel = () => {
    setIsEditing(false)
    // Reset to original values
  }

  const addTag = () => {
    if (newTag.trim() && !tags.includes(newTag.trim())) {
      setTags([...tags, newTag.trim()])
      setNewTag("")
    }
  }

  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter((tag) => tag !== tagToRemove))
  }

  return (
    <div className="p-6 space-y-6">
      {/* Agent Profile - Editable */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Avatar className="h-16 w-16">
                <AvatarImage src="/placeholder.svg?height=64&width=64" />
                <AvatarFallback>AI</AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <CardTitle className="text-xl">AI 编程助手</CardTitle>
                <p className="text-blue-600 font-medium">全栈开发专家</p>
              </div>
            </div>
            <div className="flex space-x-2">
              <Button>
                <MessageCircle className="h-4 w-4 mr-2" />
                开始对话
              </Button>
              {!isEditing ? (
                <Button variant="outline" onClick={() => setIsEditing(true)}>
                  <Edit2 className="h-4 w-4 mr-2" />
                  编辑
                </Button>
              ) : (
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" onClick={handleSave}>
                    <Save className="h-4 w-4 mr-1" />
                    保存
                  </Button>
                  <Button variant="outline" size="sm" onClick={handleCancel}>
                    <X className="h-4 w-4 mr-1" />
                    取消
                  </Button>
                </div>
              )}
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Contact Info - Editable */}
      <Card>
        <CardHeader>
          <CardTitle>联系人信息</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="note">备注名</Label>
            {isEditing ? (
              <Input id="note" value={note} onChange={(e) => setNote(e.target.value)} placeholder="输入备注名" />
            ) : (
              <p className="text-sm text-gray-700">{note || "AI 编程助手"}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label>标签</Label>
            <div className="flex flex-wrap gap-2">
              {tags.map((tag) => (
                <Badge key={tag} variant="secondary" className="text-sm">
                  {tag}
                  {isEditing && (
                    <button onClick={() => removeTag(tag)} className="ml-1 text-gray-500 hover:text-gray-700">
                      <X className="h-3 w-3" />
                    </button>
                  )}
                </Badge>
              ))}
              {isEditing && (
                <div className="flex items-center space-x-2">
                  <Input
                    value={newTag}
                    onChange={(e) => setNewTag(e.target.value)}
                    placeholder="新标签"
                    className="w-20 h-6 text-xs"
                    onKeyPress={(e) => e.key === "Enter" && addTag()}
                  />
                  <Button size="sm" variant="outline" onClick={addTag} className="h-6 w-6 p-0 bg-transparent">
                    <Plus className="h-3 w-3" />
                  </Button>
                </div>
              )}
            </div>
          </div>
        </CardContent>
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
