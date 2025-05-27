'use client'

import React, { useState, useRef, useEffect, KeyboardEvent } from 'react'
// import { Button } from '@/components/ui/button'; // No longer directly needed here
// import { Input } from '@/components/ui/input'; // No longer directly needed here
// import { ScrollArea } from '@/components/ui/scroll-area'; // No longer directly needed here
// import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"; // No longer directly needed here
// import Image from 'next/image'; // No longer directly needed here

import ChatHeader from './components/ChatHeader'
import MessageList from './components/MessageList'
import ChatInput from './components/ChatInput'
import AgentSelector from './components/AgentSelector'
import ActiveAgentSidebar from './components/ActiveAgentSidebar'
import AgentChatOverlay from './components/AgentChatOverlay'
import TaskGoalManager from './components/TaskGoalManager'

import { Message, AIAgent, mockAgents } from './types' // 或者从 ./mockData.ts
// import useAppStore from '@/store';

// --- 模拟数据 (可以移到 mockData.ts) ---
const initialMessages: Message[] = [
  {
    id: '1',
    sender: 'DefaultAI',
    avatar: '/avatars/default-ai.png',
    text: 'Hello! How can I help you today?',
    timestamp: new Date(),
  },
]

const defaultAgent: AIAgent = {
  id: 'default-ai',
  name: 'DefaultAI',
  avatar: '/avatars/default-ai.png',
}
// --- 模拟数据结束 ---

export default function ChatPage({ params }: { params: { chatId: string } }) {
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [inputValue, setInputValue] = useState('')
  const [showAgentSelector, setShowAgentSelector] = useState(false)
  // searchTerm (for @ detection) is now implicitly part of inputValue processing
  const [activeSideAgents, setActiveSideAgents] = useState<AIAgent[]>([])
  const [overlayAgent, setOverlayAgent] = useState<AIAgent | null>(null)
  const [overlayMessages, setOverlayMessages] = useState<Message[]>([])
  const [chatTitle, setChatTitle] = useState(`Chat with ${defaultAgent.name}`) // Initial title
  const [atMentionSearchTerm, setAtMentionSearchTerm] = useState('')

  const inputRef = useRef<HTMLTextAreaElement>(null)
  const agentSelectorInputRef = useRef<HTMLInputElement>(null) // Pass this to AgentSelector

  const currentUser = { name: 'User', avatar: '/avatars/user.png' } // Mock

  useEffect(() => {
    if (showAgentSelector && agentSelectorInputRef.current) {
      // No timeout needed if autoFocus is on the AgentSelector's input
      agentSelectorInputRef.current.focus()
    }
  }, [showAgentSelector])

  const handleChatTitleChange = (newTitle: string) => {
    setChatTitle(newTitle)
    // TODO: Persist this change (e.g., API call)
    console.log('Chat title changed to:', newTitle)
  }

  const handleMainPageKeyDown = (e: globalThis.KeyboardEvent) => {
    // Listen globally perhaps
    if (e.key === 'Escape' && showAgentSelector) {
      closeAgentSelector()
    }
  }
  const handleAgentSelect = (agent: AIAgent) => {
    // This function remains largely the same
    const atIndex = inputValue.lastIndexOf('@')
    if (atIndex !== -1) {
      const textBeforeAt = inputValue.substring(0, atIndex)
      const textAfterMention = inputValue.substring(
        inputValue.indexOf(' ', atIndex) !== -1
          ? inputValue.indexOf(' ', atIndex)
          : inputValue.length
      ) // Get text after the mention if any
      const newValue =
        textBeforeAt + `@${agent.name} ` + textAfterMention.trimStart() // Ensure one space
      setInputValue(newValue)
    } else {
      setInputValue(`@${agent.name} `)
    }
    // onClose will be called by AgentSelector's CommandItem onSelect
    // setShowAgentSelector(false); // No longer needed here directly
    setAtMentionSearchTerm('')
    inputRef.current?.focus()
  }

  const closeAgentSelector = () => {
    setShowAgentSelector(false)
    // setAtMentionSearchTerm(''); // You can decide if you want to clear this
    if (inputRef.current) {
      // Check if the main input ref exists
      inputRef.current.focus() // Always try to focus the main input when selector closes
    }
  }

  useEffect(() => {
    document.addEventListener('keydown', handleMainPageKeyDown)
    return () => document.removeEventListener('keydown', handleMainPageKeyDown)
  }, [showAgentSelector, closeAgentSelector]) // Add dependencies

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      sender: currentUser.name,
      avatar: currentUser.avatar,
      text: inputValue,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])

    const mentionedAgentPattern = /@([\w-]+)/g
    let match
    const mentionedAgentsInInput: AIAgent[] = []
    const uniqueMentionedAgentIds = new Set<string>()

    while ((match = mentionedAgentPattern.exec(inputValue)) !== null) {
      const agentName = match[1]
      const agent = mockAgents.find(
        (a) => a.name.toLowerCase() === agentName.toLowerCase()
      )
      if (agent && !uniqueMentionedAgentIds.has(agent.id)) {
        mentionedAgentsInInput.push(agent)
        uniqueMentionedAgentIds.add(agent.id)
      }
    }

    let mainAiResponded = false

    if (mentionedAgentsInInput.length > 0) {
      let mainAiResponseText = "OK, I've noted your requests"
      if (mentionedAgentsInInput.length === 1) {
        mainAiResponseText = `OK, I've asked ${
          mentionedAgentsInInput[0].name
        } to handle: "${inputValue
          .replace(new RegExp(`@${mentionedAgentsInInput[0].name}`, 'gi'), '') // case-insensitive replace
          .trim()}"`
      } else {
        const agentNames = mentionedAgentsInInput.map((a) => a.name).join(', ')
        mainAiResponseText = `OK, I've asked ${agentNames} to look into this.`
      }

      const mainAiConfirmation: Message = {
        id: (Date.now() + 1).toString(),
        sender: defaultAgent.name,
        avatar: defaultAgent.avatar,
        text: mainAiResponseText,
        timestamp: new Date(),
        isDelegatedTask: true,
      }
      setMessages((prev) => [...prev, mainAiConfirmation])
      mainAiResponded = true

      const newAgentsToAdd = mentionedAgentsInInput.filter(
        (mentionedAgent) =>
          !activeSideAgents.find(
            (activeAgent) => activeAgent.id === mentionedAgent.id
          )
      )
      if (newAgentsToAdd.length > 0) {
        setActiveSideAgents((prev) => [...prev, ...newAgentsToAdd])
      }

      mentionedAgentsInInput.forEach((agent, index) => {
        setTimeout(() => {
          const delegatedAiResponse: Message = {
            id: (Date.now() + 2 + index).toString(),
            sender: agent.name,
            avatar: agent.avatar,
            text: `Hi, I'm ${agent.name}. I'm working on your request.`,
            timestamp: new Date(),
          }
          if (overlayAgent?.id === agent.id) {
            setOverlayMessages((prev) => [...prev, delegatedAiResponse])
          } else {
            // For prototype, we can also add to main messages with a prefix
            // Or have a notification system later
            // setMessages(prev => [...prev, {...delegatedAiResponse, text: `[Update from ${agent.name}]: ${delegatedAiResponse.text}`}]);
            console.log(
              `Message for ${agent.name} (not overlay):`,
              delegatedAiResponse
            )
          }
        }, 2000 + index * 500)
      })
    } else {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        sender: defaultAgent.name,
        avatar: defaultAgent.avatar,
        text: `You said: ${inputValue}`,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, aiResponse])
      mainAiResponded = true
    }

    if (!mainAiResponded && mentionedAgentsInInput.length > 0) {
      // This case might be less likely now with the improved logic
      // but good as a fallback.
      const fallbackResponse: Message = {
        id: (Date.now() + Date.now()).toString(), // ensure unique id
        sender: defaultAgent.name,
        avatar: defaultAgent.avatar,
        text: "I've noted your mentions. Some agents might not be available or the task was unclear for me.",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, fallbackResponse])
    }

    setInputValue('')
    setShowAgentSelector(false)
  }

  const handleRetryMessage = (messageToRetry: Message) => {
    alert(`Retry message: "${messageToRetry.text}" (Not Implemented)`)
    // Logic:
    // 1. Remove the AI's previous response (if applicable).
    // 2. Resend the user's message that led to this AI response, or re-trigger the AI.
    // 3. Or, if it's an AI message itself, ask the AI to regenerate its last response.
  }

  const handleMainInputKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    // This handler is now mostly for ChatInput to call onSendMessage on Enter.
    // The @ detection logic is in handleMainInputChange.
    // The AgentSelector's keydown is handled by its own component.
    // However, we might still need to prevent default for Enter here if ChatInput doesn't.
    if (e.key === 'Escape' && showAgentSelector) {
      closeAgentSelector()
    }
  }

  const handleMaybeShowAgentSelector = (
    currentInputValue: string,
    caretPosition: number | null
  ) => {
    if (caretPosition === null) {
      setShowAgentSelector(false)
      return
    }

    const textUptoCaret = currentInputValue.substring(0, caretPosition)
    // Try to find the last '@' that could start a mention
    let lastAtInstanceIndex = -1
    for (let i = textUptoCaret.length - 1; i >= 0; i--) {
      if (textUptoCaret[i] === '@') {
        // Check if it's a valid start of a mention (preceded by space or start of input)
        if (i === 0 || /\s/.test(textUptoCaret[i - 1])) {
          lastAtInstanceIndex = i
          break
        }
      }
      // If we hit a space moving backwards from caret before finding a valid @, then it's not an active mention
      if (/\s/.test(textUptoCaret[i]) && i < textUptoCaret.length - 1) {
        // length -1 because caret is after last typed char
        // break; // This might be too aggressive, consider user editing in the middle
      }
    }

    if (lastAtInstanceIndex !== -1) {
      // Extract the potential agent name part (text between last valid '@' and caret)
      const potentialAgentNamePart = textUptoCaret.substring(
        lastAtInstanceIndex + 1
      )

      // Ensure no spaces within the agent name part itself (e.g. "@agent name" should not keep selector open for "name")
      if (potentialAgentNamePart.includes(' ')) {
        setShowAgentSelector(false)
        return
      }

      // Check what's immediately after the caret in the full input
      const charAfterCaret =
        currentInputValue.length > caretPosition
          ? currentInputValue[caretPosition]
          : null

      // If there's a space immediately after the agent name part (typed by user), close the selector
      if (charAfterCaret === ' ' && potentialAgentNamePart.length > 0) {
        setShowAgentSelector(false)
        return
      }

      // 立即显示AgentSelector，不需要等待输入文本
      setShowAgentSelector(true)
      setAtMentionSearchTerm(potentialAgentNamePart)
      return
    }

    setShowAgentSelector(false)
  }
  const handleSideAgentClick = (agent: AIAgent) => {
    setOverlayAgent(agent)
    setOverlayMessages([
      {
        id: 'overlay-welcome',
        sender: agent.name,
        avatar: agent.avatar,
        text: `This is the chat for ${agent.name}.`,
        timestamp: new Date(),
      },
    ])
  }

  const handleCloseOverlay = () => {
    setOverlayAgent(null)
    setOverlayMessages([])
  }

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-900 overflow-hidden">
      {' '}
      {/* overflow-hidden on parent */}
      <ActiveAgentSidebar
        agents={activeSideAgents}
        onAgentClick={handleSideAgentClick}
        activeOverlayAgentId={overlayAgent?.id}
      />
      <div className="flex flex-col flex-1 h-full relative overflow-hidden">
        {' '}
        {/* Main chat area */}
        <ChatHeader
          agent={defaultAgent}
          chatId={params.chatId}
          chatTitle={chatTitle}
          onTitleChange={handleChatTitleChange}
        />
        <MessageList
          messages={messages}
          currentUserAvatar={currentUser.avatar}
          currentUserName={currentUser.name}
          onRetryMessage={handleRetryMessage}
        />
        <AgentSelector
          show={showAgentSelector}
          agents={mockAgents} // Pass the full list
          onSelectAgent={handleAgentSelect}
          onClose={closeAgentSelector}
          triggerRef={inputRef as React.RefObject<HTMLTextAreaElement>} // Ref of the Textarea
          initialSearchTerm={atMentionSearchTerm}
        />
        <ChatInput
          inputValue={inputValue}
          onInputChange={setInputValue}
          onSendMessage={handleSendMessage}
          inputRef={inputRef as React.RefObject<HTMLTextAreaElement>}
          onMaybeShowSelector={handleMaybeShowAgentSelector}
        />
        <AgentChatOverlay
          agent={overlayAgent}
          messages={overlayMessages}
          onClose={handleCloseOverlay}
          currentUserAvatar={currentUser.avatar}
          currentUserName={currentUser.name}
        />
      </div>
      <TaskGoalManager /> {/* Added new component */}
    </div>
  )
}
