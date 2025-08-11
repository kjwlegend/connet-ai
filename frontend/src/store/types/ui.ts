import { BaseEntity, DeviceInfo, LoadingState } from './common'

/**
 * UI-related types for interface state management
 */

// Theme types
export type ThemeMode = 'light' | 'dark' | 'system'

export interface ThemePreferences {
  mode: ThemeMode
  colorScheme?: 'default' | 'blue' | 'green' | 'purple'
  fontScale: number
  compactMode: boolean
}

// Layout types
export interface LayoutState {
  sidebarCollapsed: boolean
  sidebarWidth: number
  middlePanelWidth: number
  rightPanelWidth: number
  headerHeight: number
  footerVisible: boolean
}

export interface LayoutPreferences {
  defaultLayout: 'standard' | 'compact' | 'wide'
  rememberPanelSizes: boolean
  autoCollapseSidebar: boolean
}

// Navigation types
export type NavigationMode = 'chat' | 'contacts' | 'files' | 'social' | 'plugins' | 'settings'

export interface NavigationState {
  currentMode: NavigationMode
  previousMode: NavigationMode | null
  history: NavigationMode[]
  breadcrumbs: BreadcrumbItem[]
}

export interface BreadcrumbItem {
  id: string
  label: string
  path: string
  icon?: string
}

// Modal types
export interface Modal {
  id: string
  type: string
  component?: string
  props?: Record<string, any>
  isOpen: boolean
  closable: boolean
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  position?: 'center' | 'top' | 'bottom'
}

export interface ModalState {
  modals: Modal[]
  activeModalId: string | null
  backdrop: boolean
}

// Toast/Notification types
export type ToastType = 'success' | 'error' | 'warning' | 'info' | 'loading'

export interface Toast extends BaseEntity {
  type: ToastType
  title: string
  description?: string
  duration?: number
  action?: {
    label: string
    onClick: () => void
  }
  persistent: boolean
}

export interface NotificationState {
  toasts: Toast[]
  maxToasts: number
  defaultDuration: number
  position: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center'
}

// Responsive types
export interface ResponsiveState extends DeviceInfo {
  breakpoint: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl'
  orientation: 'portrait' | 'landscape'
  hasHover: boolean
  hasTouch: boolean
}

// Accessibility types
export interface AccessibilityState {
  reducedMotion: boolean
  highContrast: boolean
  fontSize: 'sm' | 'md' | 'lg' | 'xl'
  keyboardNavigation: boolean
  screenReader: boolean
}

// User preferences that should be persisted
export interface UserUIPreferences {
  theme: ThemePreferences
  layout: LayoutPreferences
  notifications: {
    showToasts: boolean
    playSound: boolean
    browserNotifications: boolean
  }
  accessibility: AccessibilityState
  language: 'en' | 'zh'
}

// Complete UI state
export interface UIState {
  // Persistent preferences
  preferences: UserUIPreferences
  
  // Runtime state
  layout: LayoutState
  navigation: NavigationState
  modals: ModalState
  notifications: NotificationState
  responsive: ResponsiveState
  loading: LoadingState
  
  // Temporary UI state (not persisted)
  dragState: {
    isDragging: boolean
    dragType?: string
    dragData?: any
  }
  
  focusState: {
    focusedElement: string | null
    focusVisible: boolean
  }
  
  scrollState: Record<string, {
    x: number
    y: number
  }>
}