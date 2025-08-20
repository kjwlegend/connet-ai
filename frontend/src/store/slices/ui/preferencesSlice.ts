import { StateCreator } from 'zustand'
import { UIState, UserUIPreferences, ThemeMode } from '../../types/ui'
import { Slice } from '../../types/common'

/**
 * UI Preferences Slice - handles persistent user preferences
 * This data is stored permanently and syncs across devices
 */

// Default preferences
const DEFAULT_PREFERENCES: UserUIPreferences = {
  theme: {
    mode: 'system',
    colorScheme: 'default',
    fontScale: 1.0,
    compactMode: false,
  },
  layout: {
    defaultLayout: 'standard',
    rememberPanelSizes: true,
    autoCollapseSidebar: false,
  },
  notifications: {
    showToasts: true,
    playSound: false,
    browserNotifications: true,
  },
  accessibility: {
    reducedMotion: false,
    highContrast: false,
    fontSize: 'md',
    keyboardNavigation: false,
    screenReader: false,
  },
  language: 'en',
}

// State interface
export interface PreferencesState {
  preferences: UserUIPreferences
}

// Actions interface
export interface PreferencesActions {
  // Theme actions
  setTheme: (mode: ThemeMode) => void
  setColorScheme: (scheme: 'default' | 'blue' | 'green' | 'purple') => void
  setFontScale: (scale: number) => void
  toggleCompactMode: () => void
  
  // Layout actions
  setDefaultLayout: (layout: 'standard' | 'compact' | 'wide') => void
  toggleRememberPanelSizes: () => void
  toggleAutoCollapseSidebar: () => void
  
  // Notification actions
  toggleShowToasts: () => void
  togglePlaySound: () => void
  toggleBrowserNotifications: () => void
  
  // Accessibility actions
  toggleReducedMotion: () => void
  toggleHighContrast: () => void
  setFontSize: (size: 'sm' | 'md' | 'lg' | 'xl') => void
  toggleKeyboardNavigation: () => void
  setScreenReaderMode: (enabled: boolean) => void
  
  // Language
  setLanguage: (language: 'en' | 'zh') => void
  
  // Bulk updates
  updatePreferences: (updates: Partial<UserUIPreferences>) => void
  resetPreferences: () => void
  importPreferences: (preferences: UserUIPreferences) => void
  exportPreferences: () => UserUIPreferences
}

// Complete slice type
export type PreferencesSlice = PreferencesState & PreferencesActions

// Slice creator
const createPreferencesSlice: StateCreator<
  PreferencesSlice,
  [],
  [],
  PreferencesSlice
> = (set, get) => ({
  // Initial state
  preferences: DEFAULT_PREFERENCES,

  // Theme actions
  setTheme: (mode) => set((state) => ({
    preferences: {
      ...state.preferences,
      theme: {
        ...state.preferences.theme,
        mode,
      },
    },
  })),

  setColorScheme: (colorScheme) => set((state) => ({
    preferences: {
      ...state.preferences,
      theme: {
        ...state.preferences.theme,
        colorScheme,
      },
    },
  })),

  setFontScale: (fontScale) => set((state) => ({
    preferences: {
      ...state.preferences,
      theme: {
        ...state.preferences.theme,
        fontScale: Math.max(0.8, Math.min(1.5, fontScale)), // Clamp between 0.8 and 1.5
      },
    },
  })),

  toggleCompactMode: () => set((state) => ({
    preferences: {
      ...state.preferences,
      theme: {
        ...state.preferences.theme,
        compactMode: !state.preferences.theme.compactMode,
      },
    },
  })),

  // Layout actions
  setDefaultLayout: (defaultLayout) => set((state) => ({
    preferences: {
      ...state.preferences,
      layout: {
        ...state.preferences.layout,
        defaultLayout,
      },
    },
  })),

  toggleRememberPanelSizes: () => set((state) => ({
    preferences: {
      ...state.preferences,
      layout: {
        ...state.preferences.layout,
        rememberPanelSizes: !state.preferences.layout.rememberPanelSizes,
      },
    },
  })),

  toggleAutoCollapseSidebar: () => set((state) => ({
    preferences: {
      ...state.preferences,
      layout: {
        ...state.preferences.layout,
        autoCollapseSidebar: !state.preferences.layout.autoCollapseSidebar,
      },
    },
  })),

  // Notification actions
  toggleShowToasts: () => set((state) => ({
    preferences: {
      ...state.preferences,
      notifications: {
        ...state.preferences.notifications,
        showToasts: !state.preferences.notifications.showToasts,
      },
    },
  })),

  togglePlaySound: () => set((state) => ({
    preferences: {
      ...state.preferences,
      notifications: {
        ...state.preferences.notifications,
        playSound: !state.preferences.notifications.playSound,
      },
    },
  })),

  toggleBrowserNotifications: () => set((state) => ({
    preferences: {
      ...state.preferences,
      notifications: {
        ...state.preferences.notifications,
        browserNotifications: !state.preferences.notifications.browserNotifications,
      },
    },
  })),

  // Accessibility actions
  toggleReducedMotion: () => set((state) => ({
    preferences: {
      ...state.preferences,
      accessibility: {
        ...state.preferences.accessibility,
        reducedMotion: !state.preferences.accessibility.reducedMotion,
      },
    },
  })),

  toggleHighContrast: () => set((state) => ({
    preferences: {
      ...state.preferences,
      accessibility: {
        ...state.preferences.accessibility,
        highContrast: !state.preferences.accessibility.highContrast,
      },
    },
  })),

  setFontSize: (fontSize) => set((state) => ({
    preferences: {
      ...state.preferences,
      accessibility: {
        ...state.preferences.accessibility,
        fontSize,
      },
    },
  })),

  toggleKeyboardNavigation: () => set((state) => ({
    preferences: {
      ...state.preferences,
      accessibility: {
        ...state.preferences.accessibility,
        keyboardNavigation: !state.preferences.accessibility.keyboardNavigation,
      },
    },
  })),

  setScreenReaderMode: (screenReader) => set((state) => ({
    preferences: {
      ...state.preferences,
      accessibility: {
        ...state.preferences.accessibility,
        screenReader,
      },
    },
  })),

  // Language
  setLanguage: (language) => set((state) => ({
    preferences: {
      ...state.preferences,
      language,
    },
  })),

  // Bulk operations
  updatePreferences: (updates) => set((state) => ({
    preferences: {
      ...state.preferences,
      ...updates,
      // Deep merge nested objects
      theme: updates.theme ? { ...state.preferences.theme, ...updates.theme } : state.preferences.theme,
      layout: updates.layout ? { ...state.preferences.layout, ...updates.layout } : state.preferences.layout,
      notifications: updates.notifications ? { ...state.preferences.notifications, ...updates.notifications } : state.preferences.notifications,
      accessibility: updates.accessibility ? { ...state.preferences.accessibility, ...updates.accessibility } : state.preferences.accessibility,
    },
  })),

  resetPreferences: () => set({
    preferences: { ...DEFAULT_PREFERENCES },
  }),

  importPreferences: (preferences) => {
    // Validate the imported preferences structure
    try {
      const validatedPreferences = {
        ...DEFAULT_PREFERENCES,
        ...preferences,
        // Ensure nested objects are properly merged
        theme: { ...DEFAULT_PREFERENCES.theme, ...preferences.theme },
        layout: { ...DEFAULT_PREFERENCES.layout, ...preferences.layout },
        notifications: { ...DEFAULT_PREFERENCES.notifications, ...preferences.notifications },
        accessibility: { ...DEFAULT_PREFERENCES.accessibility, ...preferences.accessibility },
      }

      set({ preferences: validatedPreferences })
    } catch (error) {
      console.error('Failed to import preferences:', error)
      throw new Error('Invalid preferences format')
    }
  },

  exportPreferences: () => {
    return get().preferences
  },
})

export default createPreferencesSlice