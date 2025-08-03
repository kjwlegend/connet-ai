import { lazy, ComponentType } from 'react'

// Lazy loading utilities
export function lazyWithRetry<T extends ComponentType<any>>(
  componentImport: () => Promise<{ default: T }>,
  retries = 3
): ComponentType<any> {
  return lazy(async () => {
    let lastError: Error | undefined

    for (let i = 0; i < retries; i++) {
      try {
        return await componentImport()
      } catch (error) {
        lastError = error as Error
        
        // Wait before retrying
        if (i < retries - 1) {
          await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)))
        }
      }
    }

    throw lastError
  })
}

// Performance monitoring
export class PerformanceMonitor {
  private static marks: Map<string, number> = new Map()

  static mark(name: string): void {
    if (typeof window !== 'undefined' && 'performance' in window) {
      this.marks.set(name, performance.now())
    }
  }

  static measure(name: string, startMark: string): number | null {
    if (typeof window === 'undefined' || !('performance' in window)) {
      return null
    }

    const startTime = this.marks.get(startMark)
    if (!startTime) {
      console.warn(`Start mark "${startMark}" not found`)
      return null
    }

    const duration = performance.now() - startTime
    console.log(`Performance: ${name} took ${duration.toFixed(2)}ms`)
    
    return duration
  }

  static clearMarks(): void {
    this.marks.clear()
  }
}

// Debounce and throttle utilities
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout

  return (...args: Parameters<T>) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean

  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}

// Intersection Observer utilities
export function createIntersectionObserver(
  callback: (entries: IntersectionObserverEntry[]) => void,
  options?: IntersectionObserverInit
): IntersectionObserver | null {
  if (typeof window === 'undefined' || !('IntersectionObserver' in window)) {
    return null
  }

  return new IntersectionObserver(callback, {
    threshold: 0.1,
    rootMargin: '50px',
    ...options,
  })
}

// Memory optimization
export function cleanupComponent(cleanup: () => void) {
  return () => {
    try {
      cleanup()
    } catch (error) {
      console.error('Error during component cleanup:', error)
    }
  }
}

// Preloading utilities
export function preloadRoute(routePath: string): void {
  if (typeof window === 'undefined') return

  const link = document.createElement('link')
  link.rel = 'prefetch'
  link.href = routePath
  document.head.appendChild(link)
}

export function preloadImage(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve()
    img.onerror = reject
    img.src = src
  })
}

// Bundle size monitoring
export function logBundleSize(componentName: string, size?: number): void {
  if (process.env.NODE_ENV === 'development') {
    console.log(`Bundle: ${componentName}${size ? ` (${size}KB)` : ''}`)
  }
}

export default {
  lazyWithRetry,
  PerformanceMonitor,
  debounce,
  throttle,
  createIntersectionObserver,
  cleanupComponent,
  preloadRoute,
  preloadImage,
  logBundleSize,
}