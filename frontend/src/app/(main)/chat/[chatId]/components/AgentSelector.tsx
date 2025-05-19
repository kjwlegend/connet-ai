// src/app/(main)/chat/[chatId]/components/AgentSelector.tsx
import React, { useEffect, useRef } from 'react'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  // CommandSeparator, // If you need separators
} from '@/components/ui/command' // Import from shadcn/ui
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { AIAgent } from '../types'

interface AgentSelectorProps {
  show: boolean
  agents: AIAgent[] // This will be the full list, Command handles filtering
  onSelectAgent: (agent: AIAgent) => void
  onClose: () => void
  triggerRef?: React.RefObject<HTMLElement> // For positioning
  initialSearchTerm?: string // Pass the term after @
}

const SELECTOR_MIN_WIDTH = 300
const SELECTOR_OFFSET = 8 // Slightly more offset for popover appearance

export default function AgentSelector({
  show,
  agents,
  onSelectAgent,
  onClose,
  triggerRef,
  initialSearchTerm = '',
}: AgentSelectorProps) {
  const commandRef = useRef<HTMLDivElement>(null)
  const [searchValue, setSearchValue] = React.useState(initialSearchTerm)
  const [positionStyles, setPositionStyles] =
    React.useState<React.CSSProperties>({})

  // Update search value if initialSearchTerm changes when shown
  useEffect(() => {
    if (show) {
      setSearchValue(initialSearchTerm)
      // 聚焦输入框，确保键盘事件在 CommandInput 内部处理
      const input = commandRef.current?.querySelector('input')
      if (input) input.focus()
    }
  }, [show, initialSearchTerm])
  // 让 CommandInput 捕获上下和回车，阻止冒泡到主输入框
  useEffect(() => {
    if (!show) return
    const input = commandRef.current?.querySelector('input')
    if (!input) return
    const stopPropagation = (e: KeyboardEvent) => {
      if (['ArrowUp', 'ArrowDown', 'Enter'].includes(e.key)) {
        e.stopPropagation()
      }
    }
    input.addEventListener('keydown', stopPropagation)
    return () => {
      input.removeEventListener('keydown', stopPropagation)
    }
  }, [show])

  // Positioning logic (same as before, but Command might have its own preferred way via Popover)
  // For now, we'll keep the manual positioning.
  // If you wrap Command in shadcn/ui Popover, Popover handles positioning.
  useEffect(() => {
    if (show && triggerRef?.current && commandRef.current) {
      const triggerRect = triggerRef.current.getBoundingClientRect()
      const windowHeight = window.innerHeight
      const estimatedSelectorHeight = commandRef.current.offsetHeight || 250 // Estimate or measure

      const spaceBelow = windowHeight - triggerRect.bottom - SELECTOR_OFFSET
      const spaceAbove = triggerRect.top - SELECTOR_OFFSET

      let topPosition: number
      if (spaceBelow >= estimatedSelectorHeight || spaceBelow >= spaceAbove) {
        topPosition = triggerRect.bottom + window.scrollY + SELECTOR_OFFSET
      } else {
        topPosition =
          triggerRect.top +
          window.scrollY -
          estimatedSelectorHeight -
          SELECTOR_OFFSET
      }

      setPositionStyles({
        position: 'absolute',
        top: `${topPosition}px`,
        left: `${triggerRect.left + window.scrollX}px`,
        width: `${Math.max(triggerRect.width, SELECTOR_MIN_WIDTH)}px`,
        zIndex: 50,
      })
    }
  }, [show, triggerRef, agents]) // Re-calculate on show, trigger, or agent list

  // Handle click outside and ESC to close (Command itself might handle ESC)
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        commandRef.current &&
        !commandRef.current.contains(event.target as Node) &&
        triggerRef?.current &&
        !triggerRef.current.contains(event.target as Node)
      ) {
        if (show) onClose()
      }
    }
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && show) {
        onClose()
      }
    }

    if (show) {
      document.addEventListener('mousedown', handleClickOutside)
      document.addEventListener('keydown', handleKeyDown)
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [show, onClose, triggerRef])

  if (!show) return null

  return (
    <div
      ref={commandRef}
      style={positionStyles}
      className="rounded-md border bg-popover text-popover-foreground shadow-md outline-none animate-in fade-in-0 zoom-in-95"
    >
      <Command
        shouldFilter={true} // Let Command handle filtering based on CommandInput
        // loop // Optional: enable looping through items with arrow keys
      >
        <CommandInput
          placeholder="Search agents..."
          value={searchValue}
          onValueChange={setSearchValue} // cmk's way of handling input change
          autoFocus // CommandInput usually auto-focuses
        />
        <CommandList className="max-h-[240px] overflow-y-auto overflow-x-hidden">
          <CommandEmpty>No agent found.</CommandEmpty>
          <CommandGroup
            heading={
              agents.length > 0 && searchValue ? 'Results' : 'Suggestions'
            }
          >
            {agents.map((agent) => (
              <CommandItem
                key={agent.id}
                value={`${agent.name} ${agent.description || ''}`} // Value used for filtering/searching
                onSelect={() => {
                  onSelectAgent(agent)
                  onClose() // Close after selection
                }}
                className="flex items-center space-x-2 cursor-pointer p-2 data-[selected=true]:bg-accent data-[selected=true]:text-accent-foreground"
              >
                <Avatar className="h-6 w-6">
                  <AvatarImage src={agent.avatar} alt={agent.name} />
                  <AvatarFallback>{agent.name.substring(0, 1)}</AvatarFallback>
                </Avatar>
                <div className="flex flex-col">
                  <span className="text-sm font-medium">{agent.name}</span>
                  {agent.description && (
                    <span className="text-xs text-muted-foreground">
                      {agent.description}
                    </span>
                  )}
                </div>
              </CommandItem>
            ))}
          </CommandGroup>
        </CommandList>
      </Command>
    </div>
  )
}
