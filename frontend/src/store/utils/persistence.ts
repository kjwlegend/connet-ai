import { PersistOptions } from 'zustand/middleware'
import { StorageUtil } from '@/lib/utils/storage'
import { CachedData } from '../types/common'

/**
 * Enhanced persistence utilities with selective storage and TTL support
 */

// Storage categories with different persistence strategies
export const STORAGE_CATEGORIES = {
  // Persistent across sessions - never expires
  PERMANENT: 'permanent',
  
  // Session-based storage - expires on browser close
  SESSION: 'session',
  
  // Temporary storage - short TTL
  TEMPORARY: 'temporary',
  
  // Cache storage - medium TTL
  CACHE: 'cache',
} as const

export type StorageCategory = typeof STORAGE_CATEGORIES[keyof typeof STORAGE_CATEGORIES]

/**
 * Enhanced storage interface that supports TTL and categories
 */
export interface EnhancedStorage {
  getItem: (name: string) => string | null | Promise<string | null>
  setItem: (name: string, value: string, category?: StorageCategory) => void | Promise<void>
  removeItem: (name: string) => void | Promise<void>
  clear: (category?: StorageCategory) => void | Promise<void>
  getAllKeys: (category?: StorageCategory) => string[] | Promise<string[]>
}

/**
 * Create enhanced storage with category support
 */
const createEnhancedStorage = (): EnhancedStorage => {
  const getStorageKey = (name: string, category?: StorageCategory): string => {
    return category ? `${category}:${name}` : name
  }

  const parseStorageKey = (key: string): { name: string; category?: StorageCategory } => {
    const parts = key.split(':')
    if (parts.length === 2 && Object.values(STORAGE_CATEGORIES).includes(parts[0] as StorageCategory)) {
      return { name: parts[1], category: parts[0] as StorageCategory }
    }
    return { name: key }
  }

  return {
    getItem: (name: string) => {
      // Try different storage categories in order of preference
      const categories: (StorageCategory | undefined)[] = [
        STORAGE_CATEGORIES.PERMANENT,
        STORAGE_CATEGORIES.CACHE,
        STORAGE_CATEGORIES.SESSION,
        STORAGE_CATEGORIES.TEMPORARY,
        undefined, // legacy keys without category
      ]

      for (const category of categories) {
        const key = getStorageKey(name, category)
        const value = StorageUtil.getItem<string>(key)
        if (value !== null) {
          return value
        }
      }

      return null
    },

    setItem: (name: string, value: string, category = STORAGE_CATEGORIES.CACHE) => {
      const key = getStorageKey(name, category)
      StorageUtil.setItem(key, value)
    },

    removeItem: (name: string) => {
      // Remove from all possible categories
      const categories: (StorageCategory | undefined)[] = [
        STORAGE_CATEGORIES.PERMANENT,
        STORAGE_CATEGORIES.CACHE,
        STORAGE_CATEGORIES.SESSION,
        STORAGE_CATEGORIES.TEMPORARY,
        undefined,
      ]

      for (const category of categories) {
        const key = getStorageKey(name, category)
        StorageUtil.removeItem(key)
      }
    },

    clear: (category?: StorageCategory) => {
      if (typeof window === 'undefined') return

      const storage = window.localStorage
      const keysToRemove: string[] = []

      for (let i = 0; i < storage.length; i++) {
        const key = storage.key(i)
        if (!key) continue

        const parsed = parseStorageKey(key)
        if (!category || parsed.category === category) {
          keysToRemove.push(key)
        }
      }

      keysToRemove.forEach(key => storage.removeItem(key))
    },

    getAllKeys: (category?: StorageCategory) => {
      if (typeof window === 'undefined') return []

      const storage = window.localStorage
      const keys: string[] = []

      for (let i = 0; i < storage.length; i++) {
        const key = storage.key(i)
        if (!key) continue

        const parsed = parseStorageKey(key)
        if (!category || parsed.category === category) {
          keys.push(parsed.name)
        }
      }

      return keys
    },
  }
}

// Enhanced storage instance
export const enhancedStorage = createEnhancedStorage()

/**
 * Create persist options with selective partialize and TTL support
 */
export const createPersistOptions = <T extends Record<string, any>>(
  name: string,
  config: {
    // Which fields to persist
    include?: (keyof T)[]
    exclude?: (keyof T)[]
    // Storage category
    category?: StorageCategory
    // Version for migration
    version?: number
    // Custom partialize function
    partialize?: (state: T) => Partial<T>
    // Merge function for rehydration
    merge?: (persistedState: any, currentState: T) => T
    // Whether to skip hydration errors
    skipHydrationErrors?: boolean
  } = {}
): PersistOptions<T> => {
  const {
    include,
    exclude,
    category = STORAGE_CATEGORIES.CACHE,
    version = 1,
    partialize,
    merge,
    skipHydrationErrors = true,
  } = config

  return {
    name,
    storage: {
      getItem: (name: string) => enhancedStorage.getItem(name) as string | null | Promise<string | null>,
      setItem: (name: string, value: string) => enhancedStorage.setItem(name, value, category),
      removeItem: (name: string) => enhancedStorage.removeItem(name),
    },
    version,
    partialize: partialize || ((state: T) => {
      if (include) {
        const result: Partial<T> = {}
        include.forEach(key => {
          if (key in state) {
            result[key] = state[key]
          }
        })
        return result as T
      }

      if (exclude) {
        const result = { ...state }
        exclude.forEach(key => {
          delete result[key]
        })
        return result as T
      }

      return state
    }),
    merge: merge || ((persistedState: any, currentState: T) => {
      try {
        // Validate persisted state structure
        if (!persistedState || typeof persistedState !== 'object') {
          return currentState
        }

        // Merge persisted state into current state
        return {
          ...currentState,
          ...persistedState,
        }
      } catch (error) {
        if (skipHydrationErrors) {
          console.warn(`[Persist] Failed to merge state for ${name}:`, error)
          return currentState
        }
        throw error
      }
    }),
    skipHydration: false,
  }
}

/**
 * Predefined persist configurations for different use cases
 */
export const PERSIST_CONFIGS = {
  // UI preferences - permanent storage
  UI_PREFERENCES: <T extends Record<string, any>>(name: string) => createPersistOptions<T>(name, {
    category: STORAGE_CATEGORIES.PERMANENT,
    version: 1,
  }),

  // Layout state - persistent but can be reset
  LAYOUT_STATE: <T extends Record<string, any>>(name: string) => createPersistOptions<T>(name, {
    category: STORAGE_CATEGORIES.PERMANENT,
    version: 1,
  }),

  // Chat cache - temporary storage with TTL
  CHAT_CACHE: <T extends Record<string, any>>(name: string, include?: (keyof T)[]) => createPersistOptions<T>(name, {
    category: STORAGE_CATEGORIES.CACHE,
    include,
    version: 1,
  }),

  // Session data - cleared on browser close
  SESSION_DATA: <T extends Record<string, any>>(name: string) => createPersistOptions<T>(name, {
    category: STORAGE_CATEGORIES.SESSION,
    version: 1,
  }),

  // Temporary cache - short-lived
  TEMP_CACHE: <T extends Record<string, any>>(name: string) => createPersistOptions<T>(name, {
    category: STORAGE_CATEGORIES.TEMPORARY,
    version: 1,
  }),
} as const

/**
 * Storage cleanup utility
 */
export const storageCleanup = {
  /**
   * Clear expired cache entries
   */
  clearExpiredCache: () => {
    if (typeof window === 'undefined') return

    const storage = window.localStorage
    const now = Date.now()
    const keysToRemove: string[] = []

    for (let i = 0; i < storage.length; i++) {
      const key = storage.key(i)
      if (!key || !key.startsWith(`${STORAGE_CATEGORIES.TEMPORARY}:`)) continue

      try {
        const value = storage.getItem(key)
        if (!value) continue

        const parsed: CachedData<any> = JSON.parse(value)
        if (parsed.timestamp && parsed.ttl && now - parsed.timestamp > parsed.ttl) {
          keysToRemove.push(key)
        }
      } catch {
        // Invalid format, remove it
        keysToRemove.push(key)
      }
    }

    keysToRemove.forEach(key => storage.removeItem(key))
    
    if (keysToRemove.length > 0) {
      console.debug(`[StorageCleanup] Removed ${keysToRemove.length} expired cache entries`)
    }
  },

  /**
   * Clear all data from a specific category
   */
  clearCategory: (category: StorageCategory) => {
    enhancedStorage.clear(category)
  },

  /**
   * Get storage usage statistics
   */
  getUsageStats: () => {
    if (typeof window === 'undefined') return null

    const storage = window.localStorage
    const stats = {
      total: 0,
      [STORAGE_CATEGORIES.PERMANENT]: 0,
      [STORAGE_CATEGORIES.CACHE]: 0,
      [STORAGE_CATEGORIES.SESSION]: 0,
      [STORAGE_CATEGORIES.TEMPORARY]: 0,
      unknown: 0,
    }

    for (let i = 0; i < storage.length; i++) {
      const key = storage.key(i)
      const value = storage.getItem(key || '')
      if (!key || !value) continue

      const size = key.length + value.length
      stats.total += size

      if (key.startsWith(`${STORAGE_CATEGORIES.PERMANENT}:`)) {
        stats[STORAGE_CATEGORIES.PERMANENT] += size
      } else if (key.startsWith(`${STORAGE_CATEGORIES.CACHE}:`)) {
        stats[STORAGE_CATEGORIES.CACHE] += size
      } else if (key.startsWith(`${STORAGE_CATEGORIES.SESSION}:`)) {
        stats[STORAGE_CATEGORIES.SESSION] += size
      } else if (key.startsWith(`${STORAGE_CATEGORIES.TEMPORARY}:`)) {
        stats[STORAGE_CATEGORIES.TEMPORARY] += size
      } else {
        stats.unknown += size
      }
    }

    return stats
  },
}

// Auto-cleanup on page load and unload
if (typeof window !== 'undefined') {
  // Clean up expired entries on page load
  window.addEventListener('load', () => {
    storageCleanup.clearExpiredCache()
  })

  // Clean up temporary data on page unload
  window.addEventListener('beforeunload', () => {
    storageCleanup.clearCategory(STORAGE_CATEGORIES.TEMPORARY)
  })

  // Periodic cleanup every 30 minutes
  setInterval(() => {
    storageCleanup.clearExpiredCache()
  }, 1000 * 60 * 30)
}