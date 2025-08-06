'use client'

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  MessageCircle,
  Plus,
  Search,
  Filter,
  Users,
  Bot,
  User,
  ChevronDown,
  Trash2,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useState, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { useChat } from '@/store'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from '@/components/ui/dropdown-menu'
import { ContextMenu, ContextMenuItem } from '@/components/ui/context-menu'

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
    id: 'agent-1',
    name: 'AI 编程助手',
    avatar: '/placeholder.svg?height=40&width=40',
    specialty: '全栈开发',
    description: '代码优化专家',
    status: 'online',
    type: 'agent',
    tags: ['编程', '代码审查'],
    note: '主要负责代码优化',
  },
  {
    id: 'agent-2',
    name: 'AI 设计师',
    avatar: '/placeholder.svg?height=40&width=40',
    specialty: 'UI/UX设计',
    description: '界面设计助手',
    status: 'online',
    type: 'agent',
    tags: ['设计', 'UI'],
    note: 'UI设计专家',
  },
  {
    id: 'human-1',
    name: '张三',
    avatar: '/placeholder.svg?height=40&width=40',
    specialty: '产品经理',
    description: '产品设计专家',
    status: 'online',
    type: 'human',
    tags: ['产品', '设计'],
    note: '产品设计专家',
  },
  {
    id: 'agent-3',
    name: 'AI 数据分析师',
    avatar: '/placeholder.svg?height=40&width=40',
    specialty: '数据科学',
    description: '数据洞察专家',
    status: 'busy',
    type: 'agent',
    tags: ['数据', '分析'],
    note: '',
  },
  {
    id: 'human-2',
    name: '李四',
    avatar: '/placeholder.svg?height=40&width=40',
    specialty: '前端开发',
    description: 'React专家',
    status: 'offline',
    type: 'human',
    tags: ['前端', 'React'],
    note: 'React技术专家',
  },
  {
    id: 'agent-4',
    name: 'AI 写作助手',
    avatar: '/placeholder.svg?height=40&width=40',
    specialty: '内容创作',
    description: '文案写作助手',
    status: 'offline',
    type: 'agent',
    tags: ['写作', '文案'],
    note: '擅长各类文案创作',
  },
]

const typeFilters = [
  { id: 'all', name: '全部', count: mockAgents.length },
  {
    id: 'agent',
    name: 'AI助手',
    count: mockAgents.filter((a) => a.type === 'agent').length,
  },
  {
    id: 'human',
    name: '真人',
    count: mockAgents.filter((a) => a.type === 'human').length,
  },
]

const getAllTags = () => {
  const allTags = mockAgents.flatMap((agent) => agent.tags)
  const uniqueTags = [...new Set(allTags)]
  return uniqueTags.map((tag) => ({
    id: tag,
    name: tag,
    count: mockAgents.filter((agent) => agent.tags.includes(tag)).length,
  }))
}

interface ContactListProps {
  selectedItem: string | null
  onItemSelect: (id: string) => void
  searchQuery?: string
}

export function ContactList({
  selectedItem,
  onItemSelect,
  searchQuery = '',
}: ContactListProps) {
  const [selectedTypeFilter, setSelectedTypeFilter] = useState('all')
  const [selectedTagFilter, setSelectedTagFilter] = useState<string | null>(
    null
  )
  const [localSearchQuery, setLocalSearchQuery] = useState('')
  const router = useRouter()
  const { createNewConversation, conversations } = useChat()

  const filteredAgents = useMemo(() => {
    return mockAgents.filter((agent) => {
      const typeMatch =
        selectedTypeFilter === 'all' || agent.type === selectedTypeFilter
      const tagMatch =
        !selectedTagFilter || agent.tags.includes(selectedTagFilter)
      // 同时支持来自 MiddlePanel 的搜索和本地搜索
      const globalSearchMatch =
        !searchQuery.trim() ||
        agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        agent.specialty.toLowerCase().includes(searchQuery.toLowerCase()) ||
        agent.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (agent.note &&
          agent.note.toLowerCase().includes(searchQuery.toLowerCase()))
      const localSearchMatch =
        !localSearchQuery.trim() ||
        agent.name.toLowerCase().includes(localSearchQuery.toLowerCase()) ||
        agent.specialty
          .toLowerCase()
          .includes(localSearchQuery.toLowerCase()) ||
        agent.description
          .toLowerCase()
          .includes(localSearchQuery.toLowerCase()) ||
        (agent.note &&
          agent.note.toLowerCase().includes(localSearchQuery.toLowerCase()))
      return typeMatch && tagMatch && globalSearchMatch && localSearchMatch
    })
  }, [selectedTypeFilter, selectedTagFilter, searchQuery, localSearchQuery])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'bg-green-500'
      case 'busy':
        return 'bg-yellow-500'
      case 'offline':
        return 'bg-gray-400'
      default:
        return 'bg-gray-400'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'online':
        return '在线'
      case 'busy':
        return '忙碌'
      case 'offline':
        return '离线'
      default:
        return '未知'
    }
  }

  // 处理开始对话
  const handleStartConversation = async (agent: AIAgent) => {
    try {
      // 检查是否已经存在与该联系人的对话
      const existingConversation = conversations.find(
        (conv) =>
          conv.participants.length === 2 &&
          conv.participants.some((p) => p.id === agent.id)
      )

      if (existingConversation) {
        // 跳转到已存在的对话
        router.push(`/chat/${existingConversation.id}`)
      } else {
        // 创建新的对话
        const conversationId = await createNewConversation(agent.id, agent.name)
        router.push(`/chat/${conversationId}`)
      }
    } catch (error) {
      console.error('Failed to start conversation:', error)
    }
  }

  // 处理删除联系人
  const handleDeleteContact = (agent: AIAgent) => {
    // TODO: 实现删除联系人逻辑
    console.log('Delete contact:', agent.id, agent.name)
    // 这里应该调用删除联系人的 API
  }

  return (
    <div className="h-full flex flex-col bg-background overflow-hidden">
      {/* Compact Header with Filters */}
      <div className="flex-shrink-0 px-3 py-2 border-b border-border/40">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-foreground">联系人</h3>
          <Button
            size="sm"
            variant="ghost"
            className="h-6 w-6 p-0 rounded hover:bg-accent/50"
            title="添加联系人"
          >
            <Plus className="h-3 w-3" />
          </Button>
        </div>

        {/* Compact Type Filter Tags */}
        <div className="flex gap-1 flex-wrap">
          {typeFilters.map((filter) => {
            const Icon =
              filter.id === 'agent' ? Bot : filter.id === 'human' ? User : Users
            return (
              <Button
                key={filter.id}
                variant="ghost"
                size="sm"
                className={cn(
                  'h-6 px-1.5 text-xs transition-all duration-200 flex items-center gap-1',
                  selectedTypeFilter === filter.id
                    ? 'bg-accent/60 text-accent-foreground font-medium'
                    : 'hover:bg-accent/40'
                )}
                onClick={() =>
                  setSelectedTypeFilter(
                    filter.id === selectedTypeFilter ? 'all' : filter.id
                  )
                }
              >
                <Icon className="h-2.5 w-2.5" />
                {filter.name.length > 2 ? filter.name.slice(0, 2) : filter.name}
              </Button>
            )
          })}

          {/* Compact Tag Filter */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className={cn(
                  'h-6 px-1.5 text-xs flex items-center gap-1',
                  selectedTagFilter
                    ? 'bg-accent/60 text-accent-foreground font-medium'
                    : 'hover:bg-accent/40'
                )}
              >
                <Filter className="h-2.5 w-2.5" />
                <ChevronDown className="h-2.5 w-2.5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              align="start"
              className="w-40 bg-popover/95 backdrop-blur-sm border-border/60"
            >
              <DropdownMenuLabel className="text-xs text-muted-foreground">
                标签筛选
              </DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-border/40" />
              <DropdownMenuItem
                onClick={() => setSelectedTagFilter(null)}
                className="text-xs hover:bg-accent/60 focus:bg-accent/60"
              >
                全部
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-border/40" />
              {getAllTags().map((tag) => (
                <DropdownMenuItem
                  key={tag.id}
                  onClick={() => setSelectedTagFilter(tag.id)}
                  className={cn(
                    'text-xs hover:bg-accent/60 focus:bg-accent/60 transition-colors',
                    selectedTagFilter === tag.id
                      ? 'bg-accent/80 text-accent-foreground font-medium'
                      : ''
                  )}
                >
                  {tag.name} ({tag.count})
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Local Search */}
        <div className="relative mt-2">
          <Search className="absolute left-2.5 top-1/2 transform -translate-y-1/2 h-3 w-3 text-muted-foreground/70" />
          <Input
            value={localSearchQuery}
            onChange={(e) => setLocalSearchQuery(e.target.value)}
            placeholder="本地搜索..."
            className="pl-8 h-7 text-xs bg-muted/30 border-border/40 rounded focus:bg-background focus:border-ring/20 transition-all duration-200 placeholder:text-muted-foreground/60"
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
              <ContextMenu
                key={agent.id}
                trigger={
                  <div
                    className={cn(
                      'px-3 py-2.5 cursor-pointer transition-all duration-200 ease-out border-r-2 border-transparent relative group',
                      'hover:bg-accent/30 hover:border-r-primary/40',
                      isActive && 'bg-accent/50 border-r-primary'
                    )}
                    onClick={() => onItemSelect(agent.id)}
                  >
                    <div className="flex items-start space-x-2.5 w-full">
                      {/* Avatar */}
                      <div className="relative flex-shrink-0">
                        <Avatar className="h-8 w-8">
                          <AvatarImage src={agent.avatar} />
                          <AvatarFallback className="text-xs">
                            {agent.name[0]}
                          </AvatarFallback>
                        </Avatar>
                        {/* Status indicator */}
                        <div
                          className={cn(
                            'absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full border border-background',
                            getStatusColor(agent.status)
                          )}
                        />
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0 overflow-hidden">
                        <div className="flex items-center justify-between mb-0.5">
                          <div className="flex items-center space-x-1 flex-1 min-w-0 overflow-hidden">
                            <h3 className="font-medium text-foreground truncate text-sm leading-tight">
                              {agent.name}
                            </h3>
                            <Badge
                              variant="outline"
                              className="text-xs px-1 py-0 rounded bg-muted/50 text-muted-foreground border-0 flex items-center gap-0.5 flex-shrink-0"
                            >
                              {agent.type === 'agent' ? (
                                <>
                                  <Bot className="h-2 w-2" />
                                  AI
                                </>
                              ) : (
                                <>
                                  <User className="h-2 w-2" />人
                                </>
                              )}
                            </Badge>
                          </div>
                        </div>

                        <p className="text-xs text-muted-foreground/90 truncate leading-relaxed">
                          {agent.specialty}
                        </p>

                        {agent.note && (
                          <p className="text-xs text-muted-foreground/70 truncate mt-0.5">
                            {agent.note}
                          </p>
                        )}

                        {/* Tags - Show only 1-2 tags to save space */}
                        <div className="flex flex-wrap gap-0.5 mt-1">
                          {agent.tags.slice(0, 1).map((tag) => (
                            <Badge
                              key={tag}
                              variant="outline"
                              className="text-xs px-1 py-0 h-3.5"
                            >
                              {tag}
                            </Badge>
                          ))}
                          {agent.tags.length > 1 && (
                            <Badge
                              variant="outline"
                              className="text-xs px-1 py-0 h-3.5"
                            >
                              +{agent.tags.length - 1}
                            </Badge>
                          )}
                        </div>
                      </div>

                      {/* Action Button */}
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex-shrink-0"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleStartConversation(agent)
                        }}
                      >
                        <MessageCircle className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                }
              >
                <ContextMenuItem
                  onClick={() => handleStartConversation(agent)}
                  className="flex items-center gap-2"
                >
                  <MessageCircle className="h-4 w-4" />
                  开始对话
                </ContextMenuItem>
                <ContextMenuItem
                  onClick={() => handleDeleteContact(agent)}
                  destructive
                  className="flex items-center gap-2"
                >
                  <Trash2 className="h-4 w-4" />
                  删除
                </ContextMenuItem>
              </ContextMenu>
            )
          })
        )}
      </div>
    </div>
  )
}

export default ContactList
