import React from 'react'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { AIAgent } from '../types'

interface ActiveAgentSidebarProps {
  agents: AIAgent[]
  onAgentClick: (agent: AIAgent) => void
  activeOverlayAgentId?: string | null
}

export default function ActiveAgentSidebar({
  agents,
  onAgentClick,
  activeOverlayAgentId,
}: ActiveAgentSidebarProps) {
  if (agents.length === 0) return null

  return (
    <div className="w-1/5 min-w-[200px] max-w-[250px] bg-gray-200 dark:bg-gray-800 p-4 border-r border-gray-300 dark:border-gray-700 flex-shrink-0">
      <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200">
        Active Agents
      </h2>
      <ul>
        {agents.map((agent) => (
          <li
            key={agent.id}
            className={`p-2 mb-2 rounded cursor-pointer flex items-center hover:bg-gray-300 dark:hover:bg-gray-700 ${
              activeOverlayAgentId === agent.id
                ? 'bg-blue-100 dark:bg-blue-900'
                : ''
            }`}
            onClick={() => onAgentClick(agent)}
          >
            <Avatar className="w-8 h-8 mr-3">
              <AvatarImage src={agent.avatar} alt={agent.name} />
              <AvatarFallback>
                {agent.name.substring(0, 1).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <span className="text-gray-700 dark:text-gray-300">
              {agent.name}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
