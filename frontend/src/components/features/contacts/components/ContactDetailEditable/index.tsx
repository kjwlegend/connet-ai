"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { MessageCircle, Edit2, Save, X, Plus, Settings2, Bot, User, QrCode, Share } from "lucide-react"
import { useState } from "react"
import { cn } from "@/lib/utils"

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
    // TODO: Save logic here
  }

  const handleCancel = () => {
    setIsEditing(false)
    // TODO: Reset to original values
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
    <div className="flex flex-col h-full bg-background overflow-hidden">
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-6 border-b border-border/60 bg-background/80 backdrop-blur-sm">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-4">
            <Avatar className="h-14 w-14 border-2 border-background shadow-lg">
              <AvatarImage src="/placeholder.svg?height=56&width=56" />
              <AvatarFallback className="text-lg font-semibold bg-gradient-to-br from-primary/20 to-accent/20">AI</AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-1">
                <h1 className="text-xl font-semibold text-foreground tracking-tight">AI 编程助手</h1>
                <Badge variant="outline" className="text-xs px-2 py-1 rounded-md bg-muted/50 text-muted-foreground border-0 flex items-center gap-1">
                  <Bot className="h-3 w-3" />
                  AI助手
                </Badge>
              </div>
              <p className="text-primary font-medium text-sm mb-2">全栈开发专家</p>
              <p className="text-muted-foreground text-sm leading-relaxed max-w-md">
                专业的代码优化和开发助手，擅长全栈开发和代码审查。提供个性化的编程解决方案。
              </p>
              
              {/* Integrated contact info */}
              <div className="mt-3 space-y-2">
                <div className="flex items-center space-x-3">
                  <span className="text-xs text-muted-foreground font-medium">备注:</span>
                  {isEditing ? (
                    <Input 
                      value={note} 
                      onChange={(e) => setNote(e.target.value)} 
                      placeholder="输入备注名" 
                      className="h-7 text-xs flex-1 max-w-xs bg-muted/30 border-border/40 rounded-md focus:bg-background focus:border-ring/20"
                    />
                  ) : (
                    <span className="text-xs text-foreground/80 bg-muted/30 px-2 py-1 rounded-md">{note || "AI 编程助手"}</span>
                  )}
                </div>
                <div className="flex items-center space-x-3">
                  <span className="text-xs text-muted-foreground font-medium">标签:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {tags.map((tag) => (
                      <Badge key={tag} variant="secondary" className="text-xs px-2 py-1 rounded-md bg-accent/20 text-accent-foreground border-0">
                        {tag}
                        {isEditing && (
                          <button onClick={() => removeTag(tag)} className="ml-1 text-muted-foreground hover:text-foreground transition-colors">
                            <X className="h-3 w-3" />
                          </button>
                        )}
                      </Badge>
                    ))}
                    {isEditing && (
                      <div className="flex items-center space-x-1">
                        <Input
                          value={newTag}
                          onChange={(e) => setNewTag(e.target.value)}
                          placeholder="新标签"
                          className="w-20 h-6 text-xs bg-muted/30 border-border/40 rounded-md"
                          onKeyPress={(e) => e.key === "Enter" && addTag()}
                        />
                        <Button size="sm" variant="outline" onClick={addTag} className="h-6 w-6 p-0 border-border/40">
                          <Plus className="h-3 w-3" />
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="flex flex-col space-y-2">
            <Button size="sm" className="shadow-sm hover:shadow-md transition-all duration-200">
              <MessageCircle className="h-4 w-4 mr-2" />
              开始对话
            </Button>
            {!isEditing ? (
              <Button variant="outline" size="sm" onClick={() => setIsEditing(true)} className="border-border/40">
                <Edit2 className="h-4 w-4 mr-2" />
                编辑
              </Button>
            ) : (
              <div className="flex flex-col space-y-1.5">
                <Button variant="outline" size="sm" onClick={handleSave} className="border-border/40">
                  <Save className="h-4 w-4 mr-2" />
                  保存
                </Button>
                <Button variant="outline" size="sm" onClick={handleCancel} className="border-border/40">
                  <X className="h-4 w-4 mr-2" />
                  取消
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>


      {/* Content */}
      <ScrollArea className="flex-1 overflow-y-auto overflow-x-hidden">
        <div className="px-6 py-4 space-y-6">
          {/* Tool Configuration - Optimized */}
          <Card className="border-border/40 shadow-sm">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base font-semibold text-foreground tracking-tight">工具配置</CardTitle>
                <Button variant="outline" size="sm" className="border-border/40 hover:bg-accent/50 transition-all duration-200">
                  <Plus className="h-3 w-3 mr-1" />
                  添加工具
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {mockTools.map((tool) => (
                  <div 
                    key={tool.id} 
                    className={cn(
                      "flex items-center justify-between p-3 border border-border/40 rounded-lg transition-all duration-200",
                      "hover:bg-accent/30 hover:border-accent/60 hover:shadow-sm"
                    )}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={cn(
                        "w-2.5 h-2.5 rounded-full transition-colors duration-200",
                        tool.enabled ? "bg-green-500 shadow-sm" : "bg-muted-foreground/40"
                      )} />
                      <span className="text-sm font-medium truncate text-foreground">{tool.name}</span>
                    </div>
                    <Button variant="ghost" size="sm" className="h-7 w-7 p-0 hover:bg-accent/50 transition-all duration-200">
                      <Settings2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* QR Code for Quick Adding */}
          <Card className="border-border/40 shadow-sm">
            <CardHeader className="pb-4">
              <CardTitle className="text-base font-semibold text-foreground tracking-tight">快速添加</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-4">
                <div className="w-20 h-20 bg-muted/30 border-2 border-dashed border-border/60 rounded-lg flex items-center justify-center hover:bg-muted/50 transition-colors duration-200">
                  <div className="text-center">
                    <QrCode className="h-8 w-8 text-muted-foreground mb-1 mx-auto" />
                    <div className="text-xs text-muted-foreground">二维码</div>
                  </div>
                </div>
                <div className="flex-1">
                  <p className="text-sm text-muted-foreground leading-relaxed mb-3">
                    扫描二维码快速添加此AI助手到您的联系人列表，或分享给他人使用。
                  </p>
                  <Button variant="outline" size="sm" className="border-border/40 hover:bg-accent/50 transition-all duration-200">
                    <Share className="h-3 w-3 mr-1" />
                    生成分享链接
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </ScrollArea>
    </div>
  )
}

export default ContactDetailEditable