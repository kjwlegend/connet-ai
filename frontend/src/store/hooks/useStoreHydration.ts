import { useEffect, useState } from 'react'
import useAppStore from '../index.new'

/**
 * Hook to handle store hydration and prevent SSR mismatches
 */
export const useStoreHydration = () => {
  const [isHydrated, setIsHydrated] = useState(false)

  useEffect(() => {
    // Mark as hydrated on client side
    setIsHydrated(true)
    
    // Initialize store data
    const state = useAppStore.getState()
    
    // Load initial conversations if not already loaded
    if (state.conversations.data.length === 0) {
      state.loadConversations()
    }
  }, [])

  return {
    isHydrated,
    isReady: isHydrated,
  }
}

/**
 * Enhanced store hook that handles hydration gracefully
 */
export const useHydratedStore = <T>(
  selector: (state: any) => T,
  defaultValue: T
) => {
  const { isHydrated } = useStoreHydration()
  const storeValue = useAppStore(selector)
  
  return isHydrated ? storeValue : defaultValue
}

/**
 * Theme hook with hydration support
 */
export const useTheme = () => {
  return useHydratedStore(
    (state) => ({
      theme: state.preferences.theme.mode,
      colorScheme: state.preferences.theme.colorScheme,
      setTheme: state.setTheme,
      setColorScheme: state.setColorScheme,
    }),
    {
      theme: 'system' as const,
      colorScheme: 'default' as const,
      setTheme: () => {},
      setColorScheme: () => {},
    }
  )
}

/**
 * Language hook with hydration support
 */
export const useLanguage = () => {
  return useHydratedStore(
    (state) => ({
      language: state.preferences.language,
      setLanguage: state.setLanguage,
    }),
    {
      language: 'en' as const,
      setLanguage: () => {},
    }
  )
}