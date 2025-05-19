// src/app/(main)/chat/[chatId]/types.ts (或者一个临时的 types.ts)

export interface Message {
  id: string
  sender: 'user' | 'ai' | string // string 可以是 AI agent 的名字
  avatar?: string // AI agent 的头像 URL
  text: string
  timestamp: Date
  isDelegatedTask?: boolean // 标记这条消息是由主AI发出的委派确认
  delegatedTo?: string // 被委派的AI agent名字
}

export interface AIAgent {
  id: string
  name: string
  avatar: string // 头像 URL
  description?: string
}

// 模拟的 AI 智能体列表 (用于 @ 选择)
export const mockAgents: AIAgent[] = [
  {
    id: 'planner-ai',
    name: 'PlannerAI',
    avatar: '/avatars/planner.png',
    description: 'Helps plan tasks',
  },
  {
    id: 'coder-ai',
    name: 'CoderAI',
    avatar: '/avatars/coder.png',
    description: 'Assists with coding',
  },
  {
    id: 'researcher-ai',
    name: 'ResearcherAI',
    avatar: '/avatars/researcher.png',
    description: 'Gathers information',
  },
  {
    id: 'writer-ai',
    name: 'WriterAI',
    avatar: '/avatars/writer.png',
    description: 'Helps with writing content',
  },
]
