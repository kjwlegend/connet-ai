"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge" 
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { MessageCircle, Plus, Search, Filter, Users, Bot, User, ChevronDown } from "lucide-react"
import { cn } from "@/lib/utils"
import { useState, useMemo } from "react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel
} from "@/components/ui/dropdown-menu"

// Temporary mock data - will be replaced with actual types later
interface AIAgent {
  id: string
  name: string
  avatar: string
  specialty: string
  description: string
  status: 'online' | 'offline' | 'busy'
  type: 'agent' | 'human'
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
    type: "agent",
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
    type: "agent",
    tags: ["设计", "UI"],
    note: "UI设计专家",
  },
  {
    id: "human-1",
    name: "张三",
    avatar: "/placeholder.svg?height=40&width=40",
    specialty: "产品经理",
    description: "产品设计专家",
    status: "online",
    type: "human",
    tags: ["产品", "设计"],
    note: "产品设计专家",
  },
  {
    id: "agent-3",
    name: "AI 数据分析师", 
    avatar: "/placeholder.svg?height=40&width=40",
    specialty: "数据科学",
    description: "数据洞察专家",
    status: "busy",
    type: "agent",
    tags: ["数据", "分析"],
    note: "",
  },
  {
    id: "human-2",
    name: "李四",
    avatar: "/placeholder.svg?height=40&width=40", 
    specialty: "前端开发",
    description: "React专家",
    status: "offline",
    type: "human",
    tags: ["前端", "React"],
    note: "React技术专家",
  },
  {
    id: "agent-4",
    name: "AI 写作助手",
    avatar: "/placeholder.svg?height=40&width=40", 
    specialty: "内容创作",
    description: "文案写作助手",
    status: "offline",
    type: "agent",
    tags: ["写作", "文案"],
    note: "擅长各类文案创作",
  },
]

const typeFilters = [
  { id: "all", name: "全部", count: mockAgents.length },
  { id: "agent", name: "AI助手", count: mockAgents.filter(a => a.type === 'agent').length },
  { id: "human", name: "真人", count: mockAgents.filter(a => a.type === 'human').length },
]

const getAllTags = () => {
  const allTags = mockAgents.flatMap(agent => agent.tags)
  const uniqueTags = [...new Set(allTags)]
  return uniqueTags.map(tag => ({
    id: tag,
    name: tag,
    count: mockAgents.filter(agent => agent.tags.includes(tag)).length
  }))
}

interface ContactListProps {
  selectedItem: string | null
  onItemSelect: (id: string) => void
}

export function ContactList({ selectedItem, onItemSelect }: ContactListProps) {
  const [selectedTypeFilter, setSelectedTypeFilter] = useState("all")
  const [selectedTagFilter, setSelectedTagFilter] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')

  const filteredAgents = useMemo(() => {
    return mockAgents.filter(agent => {
      const typeMatch = selectedTypeFilter === "all" || agent.type === selectedTypeFilter
      const tagMatch = !selectedTagFilter || agent.tags.includes(selectedTagFilter)
      const searchMatch = !searchQuery.trim() || 
        agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        agent.specialty.toLowerCase().includes(searchQuery.toLowerCase()) ||
        agent.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (agent.note && agent.note.toLowerCase().includes(searchQuery.toLowerCase()))
      return typeMatch && tagMatch && searchMatch
    })
  }, [selectedTypeFilter, selectedTagFilter, searchQuery])

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
    <div className="h-full flex flex-col bg-background overflow-hidden">
      {/* Header */}
      <div className="flex-shrink-0 px-4 py-4 border-b border-border/60 bg-background/80 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-base font-semibold text-foreground tracking-tight">联系人</h2>
          <Button 
            size="sm" 
            variant="ghost" 
            className="h-8 w-8 p-0 rounded-lg hover:bg-accent/50 transition-all duration-200"
            title="添加联系人"
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>
        
        {/* Type Filter Tags */}
        <div className="flex gap-2 mb-3">
          {typeFilters.map((filter) => {
            const Icon = filter.id === 'agent' ? Bot : filter.id === 'human' ? User : Users
            return (
              <Button
                key={filter.id}
                variant="ghost"
                size="sm"
                className={cn(
                  "h-7 px-2 text-xs transition-all duration-200 flex items-center gap-1",
                  selectedTypeFilter === filter.id 
                    ? "bg-accent/40 text-accent-foreground font-medium" 
                    : "hover:bg-accent/40"
                )}
                onClick={() => setSelectedTypeFilter(filter.id === selectedTypeFilter ? 'all' : filter.id)}
              >
                <Icon className="h-3 w-3" />
                {filter.name} ({filter.count})
              </Button>
            )
          })}
          
          {/* Tag Filter Dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className={cn(
                  "h-7 px-2 text-xs transition-all duration-200 flex items-center gap-1",
                  selectedTagFilter
                    ? "bg-accent/40 text-accent-foreground font-medium"
                    : "hover:bg-accent/40"
                )}
              >
                <Filter className="h-3 w-3" />
                {selectedTagFilter || "标签"}
                <ChevronDown className="h-3 w-3" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-48">
              <DropdownMenuLabel>按标签筛选</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => setSelectedTagFilter(null)}>
                全部标签
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              {getAllTags().map((tag) => (
                <DropdownMenuItem
                  key={tag.id}
                  onClick={() => setSelectedTagFilter(tag.id)}
                  className={selectedTagFilter === tag.id ? "bg-accent" : ""}
                >
                  <Badge variant="outline" className="text-xs px-1 py-0 h-4 mr-2">
                    {tag.name}
                  </Badge>
                  ({tag.count})
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground/70" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="搜索联系人..."
            className="pl-9 h-8 text-sm bg-muted/30 border-border/40 rounded-lg focus:bg-background focus:border-ring/20 transition-all duration-200 placeholder:text-muted-foreground/60"
          />
        </div>
      </div>

      {/* Contact List */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden scrollbar-thin scrollbar-thumb-border/40 scrollbar-track-transparent">
        {filteredAgents.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-32 px-6">
            <p className="text-sm text-muted-foreground/80 text-center">
              {searchQuery.trim() ? (
                <>未找到匹配 "{searchQuery}" 的联系人</>
              ) : (
                <>暂无联系人</>
              )}
            </p>
          </div>
        ) : (
          filteredAgents.map((agent) => {
            const isActive = selectedItem === agent.id
            return (
              <div
                key={agent.id}
                className={cn(
                  "px-4 py-3 cursor-pointer transition-all duration-200 ease-out border-r-2 border-transparent relative group",
                  "hover:bg-accent/30 hover:border-r-primary/40",
                  isActive && "bg-accent/50 border-r-primary"
                )}
                onClick={() => onItemSelect(agent.id)}
              >
                <div className="flex items-start space-x-3">
                  {/* Avatar */}
                  <div className="relative flex-shrink-0">
                    <Avatar className="h-9 w-9">
                      <AvatarImage src={agent.avatar} />
                      <AvatarFallback className="text-xs">{agent.name[0]}</AvatarFallback>
                    </Avatar>
                    {/* Status indicator */}
                    <div className={cn(
                      "absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-background",
                      getStatusColor(agent.status)
                    )} />
                  </div>
                  
                  {/* Content */}
                  <div className="flex-1 min-w-0 overflow-hidden">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center space-x-2 flex-1 min-w-0 overflow-hidden">
                        <h3 className="font-medium text-foreground truncate text-sm leading-tight max-w-[120px]">
                          {agent.name}
                        </h3>
                        <Badge variant="outline" className="text-xs px-1.5 py-0.5 rounded bg-muted/50 text-muted-foreground border-0 flex items-center gap-1">
                          {agent.type === 'agent' ? (
                            <><Bot className="h-2.5 w-2.5" />AI</>
                          ) : (
                            <><User className="h-2.5 w-2.5" />人</>
                          )}
                        </Badge>
                      </div>
                      <span className="text-xs text-muted-foreground/60 flex-shrink-0">
                        {getStatusText(agent.status)}
                      </span>
                    </div>
                    
                    <p className="text-xs text-muted-foreground/90 truncate leading-relaxed max-w-[180px]">
                      {agent.specialty}
                    </p>
                    
                    {agent.note && (
                      <p className="text-xs text-muted-foreground/70 truncate mt-1 max-w-[180px]">
                        {agent.note}
                      </p>
                    )}
                    
                    {/* Tags */}
                    <div className="flex flex-wrap gap-1 mt-1">
                      {agent.tags.slice(0, 2).map((tag) => (
                        <Badge key={tag} variant="outline" className="text-xs px-1 py-0 h-4">
                          {tag}
                        </Badge>
                      ))}
                      {agent.tags.length > 2 && (
                        <Badge variant="outline" className="text-xs px-1 py-0 h-4">
                          +{agent.tags.length - 2}
                        </Badge>
                      )}
                    </div>
                  </div>
                  
                  {/* Action Button */}
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="h-7 w-7 p-0 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                  >
                    <MessageCircle className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}

export default ContactList