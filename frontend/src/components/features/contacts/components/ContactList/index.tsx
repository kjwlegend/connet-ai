"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge" 
import { Button } from "@/components/ui/button"
import { MessageCircle, Plus, ChevronDown, ChevronRight } from "lucide-react"
import { cn } from "@/lib/utils"
import { useState } from "react"

// Temporary mock data - will be replaced with actual types later
interface AIAgent {
  id: string
  name: string
  avatar: string
  specialty: string
  description: string
  status: 'online' | 'offline' | 'busy'
  category: string
  tags: string[]
  note?: string
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
    tags: ["写作", "文案"],
    note: "擅长各类文案创作",
  },
]

const categories = [
  { id: "all", name: "全部联系人", count: mockAgents.length },
  { id: "开发工具", name: "开发工具", count: 1 },
  { id: "设计工具", name: "设计工具", count: 1 },
  { id: "数据工具", name: "数据工具", count: 1 },
  { id: "内容工具", name: "内容工具", count: 1 },
]

interface ContactListProps {
  selectedItem: string | null
  onItemSelect: (id: string) => void
}

export function ContactList({ selectedItem, onItemSelect }: ContactListProps) {
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [expandedCategories, setExpandedCategories] = useState<string[]>(["all"])

  const toggleCategory = (categoryId: string) => {
    setExpandedCategories(prev =>
      prev.includes(categoryId)
        ? prev.filter(id => id !== categoryId)
        : [...prev, categoryId]
    )
  }

  const filteredAgents = selectedCategory === "all" 
    ? mockAgents 
    : mockAgents.filter(agent => agent.category === selectedCategory)

  const getStatusColor = (status: string) => {
    switch (status) {
      case "online": return "bg-green-500"
      case "busy": return "bg-yellow-500"
      case "offline": return "bg-gray-400"
      default: return "bg-gray-400"
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case "online": return "在线"
      case "busy": return "忙碌"
      case "offline": return "离线"
      default: return "未知"
    }
  }

  return (
    <div className="h-full">
      {/* Category List */}
      <div className="divide-y divide-gray-100">
        {categories.map((category) => (
          <div key={category.id}>
            <div
              className={cn(
                "flex items-center justify-between p-3 hover:bg-gray-50 cursor-pointer",
                selectedCategory === category.id && "bg-blue-50"
              )}
              onClick={() => {
                setSelectedCategory(category.id)
                toggleCategory(category.id)
              }}
            >
              <div className="flex items-center space-x-2">
                {category.id !== "all" && (
                  <button onClick={(e) => {
                    e.stopPropagation()
                    toggleCategory(category.id)
                  }}>
                    {expandedCategories.includes(category.id) ? (
                      <ChevronDown className="h-4 w-4" />
                    ) : (
                      <ChevronRight className="h-4 w-4" />
                    )}
                  </button>
                )}
                <span className="font-medium text-gray-900">{category.name}</span>
                <Badge variant="secondary" className="text-xs">
                  {category.count}
                </Badge>
              </div>
              {category.id === "all" && (
                <Button variant="ghost" size="sm">
                  <Plus className="h-4 w-4" />
                </Button>
              )}
            </div>

            {/* Agent List */}
            {expandedCategories.includes(category.id) && selectedCategory === category.id && (
              <div className="bg-gray-50">
                {filteredAgents.map((agent) => (
                  <div
                    key={agent.id}
                    className={cn(
                      "flex items-center space-x-3 p-3 hover:bg-white cursor-pointer transition-colors ml-6",
                      selectedItem === agent.id && "bg-blue-50 border-r-2 border-blue-500"
                    )}
                    onClick={() => onItemSelect(agent.id)}
                  >
                    <div className="relative">
                      <Avatar className="h-10 w-10">
                        <AvatarImage src={agent.avatar} />
                        <AvatarFallback>{agent.name[0]}</AvatarFallback>
                      </Avatar>
                      <div className={cn(
                        "absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white",
                        getStatusColor(agent.status)
                      )} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h3 className="font-medium text-gray-900 truncate">{agent.name}</h3>
                        <span className="text-xs text-gray-500">{getStatusText(agent.status)}</span>
                      </div>
                      <p className="text-sm text-gray-600 truncate">{agent.description}</p>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {agent.tags.map((tag) => (
                          <Badge key={tag} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <Button variant="ghost" size="sm">
                      <MessageCircle className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default ContactList