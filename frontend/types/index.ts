export type NavigationMode = "chat" | "contacts" | "files" | "social" | "plugins" | "settings"

export interface AIAgent {
  id: string
  name: string
  avatar: string
  specialty: string
  description: string
  status: "online" | "offline" | "busy"
  category: string
  lastActive?: string
  tags?: string[]
  note?: string
}

export interface Conversation {
  id: string
  name: string
  avatar: string
  lastMessage: string
  timestamp: string
  unreadCount: number
  isGroup: boolean
  participants?: string[]
}

export interface FileItem {
  id: string
  name: string
  type: string
  size: string
  sharedBy: string
  timestamp: string
  category: "recent" | "shared" | "documents" | "images"
}

export interface SocialPost {
  id: string
  author: string
  avatar: string
  content: string
  timestamp: string
  likes: number
  comments: number
  category: string
}

export interface Plugin {
  id: string
  name: string
  description: string
  icon: string
  category: string
  installed: boolean
  rating: number
}
