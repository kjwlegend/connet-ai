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
  UserCheck,
  Clock,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useState, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { useChat } from '@/store'
import { useTranslations } from '@/lib/i18n/client'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from '@/components/ui/dropdown-menu'
import { ContextMenu, ContextMenuItem } from '@/components/ui/context-menu'
import {
  AIAgent,
  ContactRequest,
  ContactFilter,
  AddContactSearchResult,
} from '@/types/contact'
import AddContactDialog from '../AddContactDialog'

// Enhanced mock data with new structure
const mockAgents: AIAgent[] = [
  {
    id: 'ai-coding-assistant',
    name: 'AI编程助手',
    displayName: 'CodeBot Pro',
    avatar: '/placeholder.svg?height=40&width=40',
    specialty: '全栈开发',
    description: '代码优化专家',
    status: 'online',
    type: 'agent',
    tags: ['编程', '代码审查'],
    note: '我的专属编程助手',
    isVerified: true,
    capabilities: ['code-generation', 'code-review', 'debugging'],
    createdAt: '2024-01-01',
    updatedAt: '2024-01-15',
  },
  {
    id: 'ai-designer',
    name: 'AI设计师',
    avatar: '/placeholder.svg?height=40&width=40',
    specialty: 'UI/UX设计',
    description: '界面设计助手',
    status: 'online',
    type: 'agent',
    tags: ['设计', 'UI'],
    isVerified: true,
    createdAt: '2024-01-01',
    updatedAt: '2024-01-15',
  },
  {
    id: 'john-doe',
    name: 'John Doe',
    displayName: '张三',
    avatar: '/placeholder.svg?height=40&width=40',
    specialty: '产品经理',
    description: '产品设计专家',
    status: 'online',
    type: 'human',
    tags: ['产品', '设计'],
    note: '我的同事',
    isVerified: false,
    createdAt: '2024-01-01',
    updatedAt: '2024-01-15',
  },
  {
    id: 'data-analyst-ai',
    name: 'AI数据分析师',
    displayName: 'DataBot',
    avatar: '/placeholder.svg?height=40&width=40',
    specialty: '数据科学',
    description: '数据洞察专家',
    status: 'busy',
    type: 'agent',
    tags: ['数据', '分析'],
    createdAt: '2024-01-01',
    updatedAt: '2024-01-15',
  },
  {
    id: 'jane-smith',
    name: '李四',
    avatar: '/placeholder.svg?height=40&width=40',
    specialty: '前端开发',
    description: 'React专家',
    status: 'offline',
    type: 'human',
    tags: ['前端', 'React'],
    note: 'React技术专家',
    createdAt: '2024-01-01',
    updatedAt: '2024-01-15',
  },
]

const mockPendingRequests: ContactRequest[] = [
  {
    id: 'req-1',
    fromUserId: 'alice-cooper',
    fromUserName: 'Alice Cooper',
    fromUserAvatar: '/placeholder.svg',
    toUserId: 'current-user',
    message: '你好，我是Alice，希望能够添加你为好友，一起讨论前端技术。',
    status: 'pending',
    createdAt: '2024-01-20',
    type: 'human',
  },
  {
    id: 'req-2',
    fromUserId: 'bob-wilson',
    fromUserName: 'Bob Wilson',
    fromUserAvatar: '/placeholder.svg',
    toUserId: 'current-user',
    message: '我看到了你在技术社区的分享，很有启发，希望能够交流学习。',
    status: 'pending',
    createdAt: '2024-01-21',
    type: 'human',
  },
]

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
  const t = useTranslations()
  const [filter, setFilter] = useState<ContactFilter>({ type: 'all' })
  const [localSearchQuery, setLocalSearchQuery] = useState('')
  const [showAddDialog, setShowAddDialog] = useState(false)
  const [showPendingRequests, setShowPendingRequests] = useState(false)
  const router = useRouter()
  const { createNewConversation, conversations } = useChat()

  const typeFilters = [
    { id: 'all', name: t('contacts.allContacts'), count: mockAgents.length },
    {
      id: 'agent',
      name: t('contacts.aiAgents'),
      count: mockAgents.filter((a) => a.type === 'agent').length,
    },
    {
      id: 'human',
      name: t('contacts.humans'),
      count: mockAgents.filter((a) => a.type === 'human').length,
    },
  ]

  const displayData = useMemo(() => {
    if (showPendingRequests) {
      return { contacts: [], pendingRequests: mockPendingRequests }
    }

    const filteredContacts = mockAgents.filter((agent) => {
      const typeMatch = filter.type === 'all' || agent.type === filter.type
      const tagMatch = !filter.tag || agent.tags.includes(filter.tag)

      // Combined search logic
      const combinedQuery = searchQuery || localSearchQuery
      const searchMatch =
        !combinedQuery.trim() ||
        agent.name.toLowerCase().includes(combinedQuery.toLowerCase()) ||
        agent.id.toLowerCase().includes(combinedQuery.toLowerCase()) ||
        (agent.displayName &&
          agent.displayName
            .toLowerCase()
            .includes(combinedQuery.toLowerCase())) ||
        agent.specialty.toLowerCase().includes(combinedQuery.toLowerCase()) ||
        agent.description.toLowerCase().includes(combinedQuery.toLowerCase())

      return typeMatch && tagMatch && searchMatch
    })

    return { contacts: filteredContacts, pendingRequests: [] }
  }, [filter, searchQuery, localSearchQuery, showPendingRequests])

  const getDisplayName = (agent: AIAgent) => {
    return agent.displayName || agent.name
  }

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
    return t(`contacts.${status}`)
  }

  const handleStartConversation = async (agent: AIAgent) => {
    try {
      const existingConversation = conversations.find(
        (conv) =>
          conv.participants.length === 2 &&
          conv.participants.some((p) => p.id === agent.id)
      )

      if (existingConversation) {
        router.push(`/chat/${existingConversation.id}`)
      } else {
        const conversationId = await createNewConversation(
          agent.id,
          getDisplayName(agent)
        )
        router.push(`/chat/${conversationId}`)
      }
    } catch (error) {
      console.error('Failed to start conversation:', error)
    }
  }

  const handleDeleteContact = (agent: AIAgent) => {
    console.log('Delete contact:', agent.id, getDisplayName(agent))
  }

  // Mock functions for add contact dialog
  const handleSearchContacts = async (
    query: string
  ): Promise<AddContactSearchResult[]> => {
    // Mock search - in real app this would call an API
    return new Promise((resolve) => {
      setTimeout(() => {
        const results = mockAgents
          .filter(
            (agent) =>
              agent.name.toLowerCase().includes(query.toLowerCase()) ||
              agent.id.toLowerCase().includes(query.toLowerCase()) ||
              (agent.displayName &&
                agent.displayName.toLowerCase().includes(query.toLowerCase()))
          )
          .map((agent) => ({ ...agent, searchScore: Math.random() }))
        resolve(results)
      }, 500)
    })
  }

  const handleAddContact = (contactId: string) => {
    console.log('Add contact:', contactId)
  }

  const handleSendContactRequest = async (
    contactId: string,
    message: string
  ) => {
    console.log('Send contact request:', contactId, message)
  }

  const handleApproveRequest = (requestId: string) => {
    console.log('Approve request:', requestId)
  }

  const handleRejectRequest = (requestId: string) => {
    console.log('Reject request:', requestId)
  }

  const PendingRequestItem = ({ request }: { request: ContactRequest }) => {
    const isActive = selectedItem === request.id
    return (
      <div
        className={cn(
          'px-3 py-2.5 cursor-pointer transition-all duration-200 ease-out border-r-2 border-transparent relative',
          'hover:bg-accent/30 hover:border-r-primary/40',
          isActive && 'bg-accent/50 border-r-primary'
        )}
        onClick={() => onItemSelect(request.id)}
      >
        <div className="flex items-start space-x-2.5 w-full">
          <div className="relative flex-shrink-0">
            <Avatar className="h-8 w-8">
              <AvatarImage src={request.fromUserAvatar} />
              <AvatarFallback className="text-xs">
                {request.fromUserName[0]}
              </AvatarFallback>
            </Avatar>
          </div>

          <div className="flex-1 min-w-0 overflow-hidden">
            <div className="flex items-center justify-between mb-0.5">
              <h3 className="font-medium text-foreground truncate text-sm">
                {request.fromUserName}
              </h3>
              <Badge className="text-xs px-1.5 py-0.5 bg-orange-500 text-white border-0 font-medium">
                <Clock className="h-2.5 w-2.5 mr-1" />
                {t('contacts.pending')}
              </Badge>
            </div>

            <p className="text-xs text-muted-foreground/70 truncate mt-0.5">
              {request.message}
            </p>
          </div>
        </div>
      </div>
    )
  }

  const ContactItem = ({ agent }: { agent: AIAgent }) => {
    const isActive = selectedItem === agent.id
    return (
      <ContextMenu
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
              <div className="relative flex-shrink-0">
                <Avatar className="h-8 w-8">
                  <AvatarImage src={agent.avatar} />
                  <AvatarFallback className="text-xs">
                    {getDisplayName(agent)[0]}
                  </AvatarFallback>
                </Avatar>
                <div
                  className={cn(
                    'absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full border border-background',
                    getStatusColor(agent.status)
                  )}
                />
              </div>

              <div className="flex-1 min-w-0 overflow-hidden">
                <div className="flex items-center justify-between mb-0.5">
                  <div className="flex items-center space-x-1 flex-1 min-w-0 overflow-hidden">
                    <h3 className="font-medium text-foreground truncate text-sm leading-tight">
                      {getDisplayName(agent)}
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
                          <User className="h-2 w-2" />
                          {t('contacts.humans')}
                        </>
                      )}
                    </Badge>
                  </div>
                </div>

                <p className="text-xs text-muted-foreground/90 truncate leading-relaxed">
                  @{agent.id}
                </p>

                <p className="text-xs text-muted-foreground/70 truncate leading-relaxed">
                  {agent.specialty}
                </p>

                {/* Tags */}
                <div className="flex flex-wrap gap-0.5 mt-1">
                  {agent.tags.slice(0, 2).map((tag) => (
                    <Badge
                      key={tag}
                      variant="outline"
                      className="text-xs px-1 py-0 h-3.5"
                    >
                      {tag}
                    </Badge>
                  ))}
                  {agent.tags.length > 2 && (
                    <Badge
                      variant="outline"
                      className="text-xs px-1 py-0 h-3.5"
                    >
                      +{agent.tags.length - 2}
                    </Badge>
                  )}
                </div>
              </div>

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
          {t('contacts.startConversation')}
        </ContextMenuItem>
        <ContextMenuItem
          onClick={() => handleDeleteContact(agent)}
          destructive
          className="flex items-center gap-2"
        >
          <Trash2 className="h-4 w-4" />
          {t('contacts.deleteContact')}
        </ContextMenuItem>
      </ContextMenu>
    )
  }

  return (
    <>
      <div className="h-full flex flex-col bg-background overflow-hidden">
        {/* Header */}
        <div className="flex-shrink-0 px-3 py-2 border-b border-border/40">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-foreground">
              {t('contacts.title')}
            </h3>
            <Button
              size="sm"
              variant="ghost"
              className="h-6 w-6 p-0 rounded hover:bg-accent/50"
              title={t('contacts.addContact')}
              onClick={() => setShowAddDialog(true)}
            >
              <Plus className="h-3 w-3" />
            </Button>
          </div>

          {/* Pending Requests Alert */}
          {mockPendingRequests.length > 0 && !showPendingRequests && (
            <div className="mb-2">
              <Button
                variant="outline"
                size="sm"
                className="w-full h-7 text-xs justify-between hover:bg-accent/50 transition-all duration-200"
                onClick={() => setShowPendingRequests(true)}
              >
                <span>{t('contacts.pendingRequests')}</span>
                <Badge className="ml-2 h-4 px-1.5 text-xs bg-orange-500 hover:bg-orange-600 text-white border-0 font-medium">
                  {mockPendingRequests.length}
                </Badge>
              </Button>
            </div>
          )}

          {/* Type Filter Tags */}
          <div className="flex gap-1 flex-wrap mb-2">
            {!showPendingRequests &&
              typeFilters.map((filterOption) => {
                const Icon =
                  filterOption.id === 'agent'
                    ? Bot
                    : filterOption.id === 'human'
                    ? User
                    : Users
                return (
                  <Button
                    key={filterOption.id}
                    variant="ghost"
                    size="sm"
                    className={cn(
                      'h-6 px-1.5 text-xs transition-all duration-200 flex items-center gap-1',
                      filter.type === filterOption.id
                        ? 'bg-accent/60 text-accent-foreground font-medium'
                        : 'hover:bg-accent/40'
                    )}
                    onClick={() =>
                      setFilter({
                        ...filter,
                        type:
                          filterOption.id === filter.type
                            ? 'all'
                            : (filterOption.id as ContactFilter['type']),
                      })
                    }
                  >
                    <Icon className="h-2.5 w-2.5" />
                    {filterOption.name.length > 4
                      ? filterOption.name.slice(0, 3)
                      : filterOption.name}
                  </Button>
                )
              })}

            {showPendingRequests && (
              <Button
                variant="outline"
                size="sm"
                className="h-6 px-2 text-xs"
                onClick={() => setShowPendingRequests(false)}
              >
                {t('common.back')}
              </Button>
            )}
          </div>

          {/* Local Search */}
          {!showPendingRequests && (
            <div className="relative">
              <Search className="absolute left-2.5 top-1/2 transform -translate-y-1/2 h-3 w-3 text-muted-foreground/70" />
              <Input
                value={localSearchQuery}
                onChange={(e) => setLocalSearchQuery(e.target.value)}
                placeholder={t('contacts.searchLocal')}
                className="pl-8 h-7 text-xs bg-muted/30 border-border/40 rounded focus:bg-background focus:border-ring/20 transition-all duration-200 placeholder:text-muted-foreground/60"
              />
            </div>
          )}
        </div>

        {/* Content List */}
        <div className="flex-1 overflow-y-auto overflow-x-hidden scrollbar-thin scrollbar-thumb-border/40 scrollbar-track-transparent">
          {showPendingRequests ? (
            // Pending Requests List
            <>
              {mockPendingRequests.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-32 px-6">
                  <p className="text-sm text-muted-foreground/80 text-center">
                    {t('contacts.noResults')}
                  </p>
                </div>
              ) : (
                mockPendingRequests.map((request) => (
                  <PendingRequestItem key={request.id} request={request} />
                ))
              )}
            </>
          ) : (
            // Contacts List
            <>
              {displayData.contacts.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-32 px-6">
                  <p className="text-sm text-muted-foreground/80 text-center">
                    {searchQuery.trim() || localSearchQuery.trim() ? (
                      <>
                        {t('contacts.noResultsFor')} "
                        {searchQuery || localSearchQuery}"
                      </>
                    ) : (
                      <>{t('contacts.noResults')}</>
                    )}
                  </p>
                </div>
              ) : (
                displayData.contacts.map((agent) => (
                  <ContactItem key={agent.id} agent={agent} />
                ))
              )}
            </>
          )}
        </div>
      </div>

      {/* Add Contact Dialog */}
      <AddContactDialog
        isOpen={showAddDialog}
        onClose={() => setShowAddDialog(false)}
        onSearchContacts={handleSearchContacts}
        onAddContact={handleAddContact}
        onSendContactRequest={handleSendContactRequest}
        existingContacts={mockAgents}
      />
    </>
  )
}

export default ContactList
