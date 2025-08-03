import { io, Socket } from 'socket.io-client'
import type {
  WebSocketMessage,
  Message,
  Agent,
  TypingIndicator,
  AgentStatus,
} from '@/types'

export class WebSocketService {
  private socket: Socket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private isConnected = false
  private eventListeners: Map<string, Function[]> = new Map()

  constructor() {
    this.connect()
  }

  private connect() {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'

    this.socket = io(wsUrl, {
      transports: ['websocket'],
      autoConnect: true,
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: 1000,
    })

    this.setupEventListeners()
  }

  private setupEventListeners() {
    if (!this.socket) return

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
      this.isConnected = true
      this.reconnectAttempts = 0
      this.emit('connection_status', { status: 'connected' })
    })

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason)
      this.isConnected = false
      this.emit('connection_status', { status: 'disconnected', reason })
    })

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
      this.reconnectAttempts++
      this.emit('connection_status', {
        status: 'error',
        error: error.message,
        attempts: this.reconnectAttempts,
      })
    })

    // Chat message events
    this.socket.on('new_message', (data: Message) => {
      this.emit('new_message', data)
    })

    this.socket.on('message_updated', (data: Message) => {
      this.emit('message_updated', data)
    })

    // Agent events
    this.socket.on(
      'agent_joined',
      (data: { agent: Agent; chatroomId: string }) => {
        this.emit('agent_joined', data)
      }
    )

    this.socket.on(
      'agent_left',
      (data: { agentId: string; chatroomId: string }) => {
        this.emit('agent_left', data)
      }
    )

    this.socket.on('agent_status_update', (data: AgentStatus) => {
      this.emit('agent_status_update', data)
    })

    this.socket.on(
      'agent_response_started',
      (data: { agentId: string; messageId: string; chatroomId: string }) => {
        this.emit('agent_response_started', data)
      }
    )

    this.socket.on(
      'agent_response_chunk',
      (data: {
        agentId: string
        messageId: string
        chunk: string
        isComplete: boolean
      }) => {
        this.emit('agent_response_chunk', data)
      }
    )

    // Typing indicators
    this.socket.on('typing_start', (data: TypingIndicator) => {
      this.emit('typing_start', data)
    })

    this.socket.on('typing_stop', (data: TypingIndicator) => {
      this.emit('typing_stop', data)
    })

    // Multi-agent collaboration events
    this.socket.on(
      'agents_collaborating',
      (data: { chatroomId: string; agentIds: string[]; topic: string }) => {
        this.emit('agents_collaborating', data)
      }
    )

    this.socket.on(
      'collaboration_update',
      (data: {
        chatroomId: string
        agentId: string
        status: 'thinking' | 'responding' | 'completed'
        progress?: number
      }) => {
        this.emit('collaboration_update', data)
      }
    )

    // Error handling
    this.socket.on('error', (data: { message: string; code: string }) => {
      this.emit('error', data)
    })
  }

  // Public methods
  public joinChatroom(chatroomId: string, userId: string) {
    if (!this.socket) return
    this.socket.emit('join_chatroom', { chatroomId, userId })
  }

  public leaveChatroom(chatroomId: string, userId: string) {
    if (!this.socket) return
    this.socket.emit('leave_chatroom', { chatroomId, userId })
  }

  public sendMessage(
    chatroomId: string,
    content: string,
    mentions: string[] = []
  ) {
    if (!this.socket) return
    this.socket.emit('send_message', { chatroomId, content, mentions })
  }

  public mentionAgent(chatroomId: string, agentId: string, context?: string) {
    if (!this.socket) return
    this.socket.emit('mention_agent', { chatroomId, agentId, context })
  }

  public startTyping(chatroomId: string, userId: string) {
    if (!this.socket) return
    this.socket.emit('typing_start', { chatroomId, userId })
  }

  public stopTyping(chatroomId: string, userId: string) {
    if (!this.socket) return
    this.socket.emit('typing_stop', { chatroomId, userId })
  }

  public requestAgentCollaboration(
    chatroomId: string,
    agentIds: string[],
    task: string,
    priority: 'low' | 'medium' | 'high' = 'medium'
  ) {
    if (!this.socket) return
    this.socket.emit('request_collaboration', {
      chatroomId,
      agentIds,
      task,
      priority,
    })
  }

  // Event subscription methods
  public on(event: string, callback: Function) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, [])
    }
    this.eventListeners.get(event)?.push(callback)
  }

  public off(event: string, callback?: Function) {
    if (!callback) {
      this.eventListeners.delete(event)
      return
    }

    const listeners = this.eventListeners.get(event)
    if (listeners) {
      const index = listeners.indexOf(callback)
      if (index > -1) {
        listeners.splice(index, 1)
      }
    }
  }

  private emit(event: string, data: any) {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.forEach((callback) => callback(data))
    }
  }

  // Connection management
  public isConnectedToSocket(): boolean {
    return this.isConnected && this.socket?.connected === true
  }

  public reconnect() {
    if (this.socket) {
      this.socket.connect()
    }
  }

  public disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.isConnected = false
    }
  }

  public getConnectionStatus() {
    if (!this.socket) return 'disconnected'
    return this.socket.connected ? 'connected' : 'disconnected'
  }
}

// Singleton instance
export const websocketService = new WebSocketService()

// React hook for using WebSocket in components
export function useWebSocket() {
  return websocketService
}
