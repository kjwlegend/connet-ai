import { useEffect, useCallback } from 'react'

export interface KeyboardShortcut {
  key: string
  ctrl?: boolean
  shift?: boolean
  alt?: boolean
  meta?: boolean
  action: () => void
  description?: string
}

export interface UseKeyboardShortcutsOptions {
  shortcuts: KeyboardShortcut[]
  enabled?: boolean
  preventDefault?: boolean
}

export function useKeyboardShortcuts({
  shortcuts,
  enabled = true,
  preventDefault = true
}: UseKeyboardShortcutsOptions) {
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (!enabled) return

    const matchingShortcut = shortcuts.find(shortcut => {
      const keyMatch = shortcut.key.toLowerCase() === event.key.toLowerCase()
      const ctrlMatch = !!shortcut.ctrl === (event.ctrlKey || event.metaKey)
      const shiftMatch = !!shortcut.shift === event.shiftKey
      const altMatch = !!shortcut.alt === event.altKey
      const metaMatch = !!shortcut.meta === event.metaKey

      // For shortcuts without modifiers, ensure no modifiers are pressed
      if (!shortcut.ctrl && !shortcut.shift && !shortcut.alt && !shortcut.meta) {
        return keyMatch && !event.ctrlKey && !event.shiftKey && !event.altKey && !event.metaKey
      }

      return keyMatch && ctrlMatch && shiftMatch && altMatch && metaMatch
    })

    if (matchingShortcut) {
      if (preventDefault) {
        event.preventDefault()
      }
      matchingShortcut.action()
    }
  }, [shortcuts, enabled, preventDefault])

  useEffect(() => {
    if (enabled) {
      document.addEventListener('keydown', handleKeyDown)
      return () => document.removeEventListener('keydown', handleKeyDown)
    }
  }, [handleKeyDown, enabled])

  return { shortcuts }
}

// Chat-specific shortcuts hook
export function useChatShortcuts({
  onSend,
  onNewConversation,
  onToggleSearch,
  onFocusInput,
  onClearInput,
  enabled = true
}: {
  onSend?: () => void
  onNewConversation?: () => void
  onToggleSearch?: () => void
  onFocusInput?: () => void
  onClearInput?: () => void
  enabled?: boolean
}) {
  const shortcuts: KeyboardShortcut[] = [
    // Send message
    {
      key: 'Enter',
      ctrl: true,
      action: () => onSend?.(),
      description: 'Send message'
    },
    // New conversation
    {
      key: 'n',
      ctrl: true,
      action: () => onNewConversation?.(),
      description: 'Start new conversation'
    },
    // Toggle search
    {
      key: 'k',
      ctrl: true,
      action: () => onToggleSearch?.(),
      description: 'Toggle search'
    },
    // Focus input
    {
      key: '/',
      action: () => onFocusInput?.(),
      description: 'Focus input'
    },
    // Clear input
    {
      key: 'Escape',
      action: () => onClearInput?.(),
      description: 'Clear input'
    }
  ]

  return useKeyboardShortcuts({
    shortcuts,
    enabled
  })
}

// Input-specific shortcuts
export function useInputShortcuts({
  onSend,
  onClear,
  onFormatBold,
  onFormatItalic,
  onFormatCode,
  onSelectAll,
  enabled = true
}: {
  onSend?: () => void
  onClear?: () => void
  onFormatBold?: () => void
  onFormatItalic?: () => void
  onFormatCode?: () => void
  onSelectAll?: () => void
  enabled?: boolean
}) {
  const shortcuts: KeyboardShortcut[] = [
    // Send (alternative to Enter)
    {
      key: 'Enter',
      ctrl: true,
      action: () => onSend?.(),
      description: 'Send message (Ctrl+Enter)'
    },
    // Clear input
    {
      key: 'Escape',
      action: () => onClear?.(),
      description: 'Clear input'
    },
    // Format bold
    {
      key: 'b',
      ctrl: true,
      action: () => onFormatBold?.(),
      description: 'Format as bold'
    },
    // Format italic
    {
      key: 'i',
      ctrl: true,
      action: () => onFormatItalic?.(),
      description: 'Format as italic'
    },
    // Format code
    {
      key: '`',
      ctrl: true,
      action: () => onFormatCode?.(),
      description: 'Format as code'
    },
    // Select all
    {
      key: 'a',
      ctrl: true,
      action: () => onSelectAll?.(),
      description: 'Select all text'
    }
  ]

  return useKeyboardShortcuts({
    shortcuts,
    enabled,
    preventDefault: false // Let default browser behavior work for text selection
  })
}