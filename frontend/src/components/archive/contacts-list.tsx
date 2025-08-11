"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { MessageCircle, Plus, ChevronDown, ChevronRight } from "lucide-react"
import { cn } from "@/lib/utils"
import { useState } from "react"
import type { Agent } from "@/types"

interface AIAgent {
  id: string
  name: string
  avatar?: string
  specialty: string
  description: string
  status: 'online' | 'busy' | 'offline'
  category: string
  tags: string[]
  note: string
}

const mockAgents: AIAgent[] = [
  {
    id: "agent-1",
    name: "AI 编程助手",
    avatar: "/placeholder.svg?height=40&width=40",
    specialty: "全栈开发",
    description: "代码优化专家",
    status: "online",
    category: "开发工具",
    tags: ["编程", "代码审查"],
    note: "主要负责代码优化",
  },
  {
    id: "agent-2",
    name: "AI 设计师",
    avatar: "/placeholder.svg?height=40&width=40",
    specialty: "UI/UX设计",
    description: "界面设计助手",
    status: "online",
    category: "设计工具",
    tags: ["设计", "UI"],
    note: "UI设计专家",
  },
  {
    id: "agent-3",
    name: "AI 数据分析师",
    avatar: "/placeholder.svg?height=40&width=40",
    specialty: "数据科学",
    description: "数据洞察专家",
    status: "busy",
    category: "数据工具",
    tags: ["数据", "分析"],
    note: "",
  },
  {
    id: "agent-4",
    name: "AI 写作助手",
    avatar: "/placeholder.svg?height=40&width=40",
    specialty: "内容创作",
    description: "文案写作助手",
    status: "offline",
    category: "内容工具",
    tags: ["写作", "文档"],
    note: "文档编写专家",
  },
]

const tagGroups = {
  编程: ["agent-1"],
  设计: ["agent-2"],
  数据: ["agent-3"],
  写作: ["agent-4"],
}

interface ContactsListProps {
  selectedItem: string | null
  onItemSelect: (id: string) => void
}

export function ContactsList({ selectedItem, onItemSelect }: ContactsListProps) {
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set(Object.keys(tagGroups)))

  const toggleGroup = (tag: string) => {
    const newExpanded = new Set(expandedGroups)
    if (newExpanded.has(tag)) {
      newExpanded.delete(tag)
    } else {
      newExpanded.add(tag)
    }
    setExpandedGroups(newExpanded)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "online":
        return "bg-green-500"
      case "busy":
        return "bg-yellow-500"
      case "offline":
        return "bg-gray-400"
      default:
        return "bg-gray-400"
    }
  }

  return (
    <div>
      {/* Add New Agent */}
      <div className="p-3 border-b border-gray-100">
        <Button className="w-full bg-transparent" variant="outline" size="sm">
          <Plus className="h-4 w-4 mr-2" />
          添加联系人
        </Button>
      </div>

      {/* Agents List by Tags */}
      <div>
        {Object.entries(tagGroups).map(([tag, agentIds]) => {
          const isExpanded = expandedGroups.has(tag)
          const agentsInGroup = mockAgents.filter((agent) => agentIds.includes(agent.id))

          return (
            <div key={tag}>
              <div
                className="px-3 py-2 text-xs font-medium text-gray-600 bg-gray-50 flex items-center justify-between cursor-pointer hover:bg-gray-100"
                onClick={() => toggleGroup(tag)}
              >
                <div className="flex items-center space-x-2">
                  {isExpanded ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
                  <span>{tag}</span>
                  <Badge variant="secondary" className="text-xs">
                    {agentsInGroup.length}
                  </Badge>
                </div>
              </div>

              {isExpanded && (
                <div className="divide-y divide-gray-100">
                  {agentsInGroup.map((agent) => (
                    <div
                      key={agent.id}
                      className={cn(
                        "p-3 hover:bg-gray-50 cursor-pointer transition-colors",
                        selectedItem === agent.id && "bg-blue-50 border-r-2 border-blue-500",
                      )}
                      onClick={() => onItemSelect(agent.id)}
                    >
                      <div className="flex items-center space-x-3">
                        <div className="relative">
                          <Avatar className="h-10 w-10">
                            <AvatarImage src={agent.avatar || "/placeholder.svg"} />
                            <AvatarFallback>{agent.name[0]}</AvatarFallback>
                          </Avatar>
                          <div
                            className={cn(
                              "absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white",
                              getStatusColor(agent.status),
                            )}
                          />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-medium text-gray-900 truncate text-sm">{agent.note || agent.name}</h3>
                          <p className="text-xs text-gray-500 truncate">{agent.description}</p>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {agent.tags?.map((tag) => (
                              <Badge key={tag} variant="secondary" className="text-xs px-1 py-0">
                                {tag}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        <Button size="sm" variant="ghost" className="p-1">
                          <MessageCircle className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
