export class StorageUtil {
  static setItem(key: string, value: any): void {
    if (typeof window === 'undefined') return
    
    try {
      localStorage.setItem(key, JSON.stringify(value))
      
      // Also set as cookie for proxy access
      if (key === 'auth-token') {
        document.cookie = `auth-token=${value}; path=/; max-age=${7 * 24 * 60 * 60}; SameSite=Lax`
      }
    } catch (error) {
      console.error('Failed to save to localStorage:', error)
    }
  }

  static getItem<T>(key: string, defaultValue?: T): T | null {
    if (typeof window === 'undefined') return defaultValue || null
    
    try {
      const item = localStorage.getItem(key)
      return item ? JSON.parse(item) : defaultValue || null
    } catch (error) {
      console.error('Failed to read from localStorage:', error)
      return defaultValue || null
    }
  }

  static removeItem(key: string): void {
    if (typeof window === 'undefined') return
    
    try {
      localStorage.removeItem(key)
      
      // Also remove cookie for proxy access
      if (key === 'auth-token') {
        document.cookie = 'auth-token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
      }
    } catch (error) {
      console.error('Failed to remove from localStorage:', error)
    }
  }

  static clear(): void {
    if (typeof window === 'undefined') return
    
    try {
      localStorage.clear()
    } catch (error) {
      console.error('Failed to clear localStorage:', error)
    }
  }

  static hasItem(key: string): boolean {
    if (typeof window === 'undefined') return false
    
    return localStorage.getItem(key) !== null
  }
}

export class SessionStorageUtil {
  static setItem(key: string, value: any): void {
    if (typeof window === 'undefined') return
    
    try {
      sessionStorage.setItem(key, JSON.stringify(value))
    } catch (error) {
      console.error('Failed to save to sessionStorage:', error)
    }
  }

  static getItem<T>(key: string, defaultValue?: T): T | null {
    if (typeof window === 'undefined') return defaultValue || null
    
    try {
      const item = sessionStorage.getItem(key)
      return item ? JSON.parse(item) : defaultValue || null
    } catch (error) {
      console.error('Failed to read from sessionStorage:', error)
      return defaultValue || null
    }
  }

  static removeItem(key: string): void {
    if (typeof window === 'undefined') return
    
    try {
      sessionStorage.removeItem(key)
    } catch (error) {
      console.error('Failed to remove from sessionStorage:', error)
    }
  }

  static clear(): void {
    if (typeof window === 'undefined') return
    
    try {
      sessionStorage.clear()
    } catch (error) {
      console.error('Failed to clear sessionStorage:', error)
    }
  }
}