import { CachedData, SyncStatus } from '../types/common'

/**
 * Cache utilities for managing TTL and data freshness
 */

// Cache TTL constants (in milliseconds)
export const CACHE_TTL = {
  // UI state - very long TTL (persistent across sessions)
  UI_PREFERENCES: Infinity,
  LAYOUT_STATE: 1000 * 60 * 60 * 24 * 30, // 30 days
  
  // Chat data - moderate TTL
  CONVERSATIONS: 1000 * 60 * 60 * 2, // 2 hours  
  MESSAGES: 1000 * 60 * 30, // 30 minutes
  DRAFTS: 1000 * 60 * 60 * 24 * 7, // 7 days
  
  // User data - short TTL
  USER_PROFILE: 1000 * 60 * 15, // 15 minutes
  PERMISSIONS: 1000 * 60 * 30, // 30 minutes
  
  // Realtime data - very short TTL  
  PRESENCE: 1000 * 60 * 2, // 2 minutes
  TYPING_INDICATORS: 1000 * 30, // 30 seconds
} as const

/**
 * Check if cached data is still valid
 */
export const isCacheValid = <T>(cached: CachedData<T> | null | undefined): cached is CachedData<T> => {
  if (!cached) return false
  if (cached.ttl === Infinity) return true
  return Date.now() - cached.timestamp < cached.ttl
}

/**
 * Check if cached data is expired
 */
export const isCacheExpired = <T>(cached: CachedData<T> | null | undefined): boolean => {
  return !isCacheValid(cached)
}

/**
 * Get the remaining TTL for cached data
 */
export const getRemainingTTL = <T>(cached: CachedData<T>): number => {
  if (cached.ttl === Infinity) return Infinity
  const elapsed = Date.now() - cached.timestamp
  return Math.max(0, cached.ttl - elapsed)
}

/**
 * Create a new cached data entry
 */
export const createCachedData = <T>(
  data: T, 
  ttl: number = CACHE_TTL.MESSAGES,
  version: number = 1
): CachedData<T> => ({
  data,
  timestamp: Date.now(),
  ttl,
  version,
})

/**
 * Update cached data while preserving metadata
 */
export const updateCachedData = <T>(
  cached: CachedData<T>,
  data: T,
  extendTTL?: boolean
): CachedData<T> => ({
  ...cached,
  data,
  timestamp: extendTTL ? Date.now() : cached.timestamp,
})

/**
 * Merge two cached data entries (for partial updates)
 */
export const mergeCachedData = <T extends Record<string, any>>(
  cached: CachedData<T>,
  updates: Partial<T>,
  extendTTL: boolean = false
): CachedData<T> => ({
  ...cached,
  data: { ...cached.data, ...updates },
  timestamp: extendTTL ? Date.now() : cached.timestamp,
})

/**
 * Cache storage interface
 */
export interface CacheStorage {
  get<T>(key: string): CachedData<T> | null
  set<T>(key: string, data: CachedData<T>): void
  remove(key: string): void
  clear(): void
  keys(): string[]
  size(): number
}

/**
 * Memory-based cache implementation
 */
class MemoryCache implements CacheStorage {
  private cache = new Map<string, CachedData<any>>()

  get<T>(key: string): CachedData<T> | null {
    const cached = this.cache.get(key)
    if (!cached) return null
    
    // Auto-cleanup expired entries
    if (isCacheExpired(cached)) {
      this.cache.delete(key)
      return null
    }
    
    return cached as CachedData<T>
  }

  set<T>(key: string, data: CachedData<T>): void {
    this.cache.set(key, data)
  }

  remove(key: string): void {
    this.cache.delete(key)
  }

  clear(): void {
    this.cache.clear()
  }

  keys(): string[] {
    return Array.from(this.cache.keys())
  }

  size(): number {
    return this.cache.size
  }

  /**
   * Clean up expired entries
   */
  cleanup(): number {
    let removed = 0
    for (const [key, value] of this.cache.entries()) {
      if (isCacheExpired(value)) {
        this.cache.delete(key)
        removed++
      }
    }
    return removed
  }

  /**
   * Get cache statistics
   */
  getStats(): {
    size: number
    expired: number
    totalSize: number
  } {
    let expired = 0
    let totalSize = 0
    
    for (const [_, value] of this.cache.entries()) {
      if (isCacheExpired(value)) expired++
      totalSize += JSON.stringify(value).length
    }

    return {
      size: this.cache.size,
      expired,
      totalSize,
    }
  }
}

// Global cache instance
export const memoryCache = new MemoryCache()

/**
 * Cache manager with automatic cleanup
 */
export class CacheManager {
  private storage: CacheStorage
  private cleanupInterval: number
  private intervalId: NodeJS.Timeout | null = null

  constructor(
    storage: CacheStorage = memoryCache,
    cleanupInterval: number = 1000 * 60 * 5 // 5 minutes
  ) {
    this.storage = storage
    this.cleanupInterval = cleanupInterval
    this.startCleanup()
  }

  /**
   * Get data from cache
   */
  get<T>(key: string): T | null {
    const cached = this.storage.get<T>(key)
    return cached?.data ?? null
  }

  /**
   * Get cached data with metadata
   */
  getCached<T>(key: string): CachedData<T> | null {
    return this.storage.get<T>(key)
  }

  /**
   * Set data in cache
   */
  set<T>(key: string, data: T, ttl?: number, version?: number): void {
    const cached = createCachedData(data, ttl, version)
    this.storage.set(key, cached)
  }

  /**
   * Update existing cached data
   */
  update<T>(key: string, data: T, extendTTL?: boolean): boolean {
    const cached = this.storage.get<T>(key)
    if (!cached) return false
    
    const updated = updateCachedData(cached, data, extendTTL)
    this.storage.set(key, updated)
    return true
  }

  /**
   * Merge data into existing cache entry
   */
  merge<T extends Record<string, any>>(
    key: string, 
    updates: Partial<T>, 
    extendTTL?: boolean
  ): boolean {
    const cached = this.storage.get<T>(key)
    if (!cached) return false
    
    const merged = mergeCachedData(cached, updates, extendTTL)
    this.storage.set(key, merged)
    return true
  }

  /**
   * Remove data from cache
   */
  remove(key: string): void {
    this.storage.remove(key)
  }

  /**
   * Clear all cache data
   */
  clear(): void {
    this.storage.clear()
  }

  /**
   * Check if data is cached and valid
   */
  isValid(key: string): boolean {
    const cached = this.storage.get(key)
    return isCacheValid(cached)
  }

  /**
   * Get cache keys
   */
  keys(): string[] {
    return this.storage.keys()
  }

  /**
   * Start automatic cleanup
   */
  startCleanup(): void {
    if (this.intervalId) return
    
    this.intervalId = setInterval(() => {
      if (this.storage instanceof MemoryCache) {
        const removed = this.storage.cleanup()
        if (removed > 0) {
          console.debug(`[CacheManager] Cleaned up ${removed} expired entries`)
        }
      }
    }, this.cleanupInterval)
  }

  /**
   * Stop automatic cleanup
   */
  stopCleanup(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId)
      this.intervalId = null
    }
  }

  /**
   * Get cache statistics
   */
  getStats() {
    if (this.storage instanceof MemoryCache) {
      return this.storage.getStats()
    }
    return {
      size: this.storage.size(),
      expired: 0,
      totalSize: 0,
    }
  }

  /**
   * Destroy cache manager
   */
  destroy(): void {
    this.stopCleanup()
    this.clear()
  }
}

// Global cache manager instance
export const cacheManager = new CacheManager()

// Auto-cleanup on page unload
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', () => {
    cacheManager.destroy()
  })
}