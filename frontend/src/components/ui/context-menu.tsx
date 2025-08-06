'use client'

import * as React from 'react'
import { cn } from '@/lib/utils/cn'

interface ContextMenuProps {
  children: React.ReactNode
  trigger: React.ReactNode
  onOpenChange?: (open: boolean) => void
}

interface ContextMenuItemProps {
  children: React.ReactNode
  onClick?: () => void
  className?: string
  disabled?: boolean
  destructive?: boolean
}

export function ContextMenu({
  children,
  trigger,
  onOpenChange,
}: ContextMenuProps) {
  const [isOpen, setIsOpen] = React.useState(false)
  const [position, setPosition] = React.useState({ x: 0, y: 0 })
  const menuRef = React.useRef<HTMLDivElement>(null)

  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()

    const rect = e.currentTarget.getBoundingClientRect()
    setPosition({ x: e.clientX, y: e.clientY })
    setIsOpen(true)
    onOpenChange?.(true)
  }

  const handleClose = () => {
    setIsOpen(false)
    onOpenChange?.(false)
  }

  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        handleClose()
      }
    }

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        handleClose()
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      document.addEventListener('keydown', handleEscape)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keydown', handleEscape)
    }
  }, [isOpen])

  return (
    <>
      <div onContextMenu={handleContextMenu}>{trigger}</div>

      {isOpen && (
        <div
          ref={menuRef}
          className="fixed z-50 min-w-[8rem] overflow-hidden rounded-md border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-1 text-gray-900 dark:text-gray-100 shadow-lg animate-in fade-in-0 zoom-in-95"
          style={{
            left: position.x,
            top: position.y,
          }}
        >
          {children}
        </div>
      )}
    </>
  )
}

export function ContextMenuItem({
  children,
  onClick,
  className,
  disabled = false,
  destructive = false,
}: ContextMenuItemProps) {
  const handleClick = () => {
    if (disabled) return
    onClick?.()
  }

  return (
    <div
      className={cn(
        'relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors',
        disabled
          ? 'pointer-events-none opacity-50'
          : destructive
          ? 'text-red-600 hover:bg-red-50 hover:text-red-900 dark:text-red-400 dark:hover:bg-red-900/20 dark:hover:text-red-300'
          : 'hover:bg-gray-100 hover:text-gray-900 dark:hover:bg-gray-700 dark:hover:text-gray-100',
        className
      )}
      onClick={handleClick}
    >
      {children}
    </div>
  )
}

export function ContextMenuSeparator() {
  return <div className="-mx-1 my-1 h-px bg-gray-200 dark:bg-gray-700" />
}
