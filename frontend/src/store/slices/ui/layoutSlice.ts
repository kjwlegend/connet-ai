import { StateCreator } from 'zustand'
import { UIState, LayoutState, NavigationMode, BreadcrumbItem } from '../../types/ui'

/**
 * Layout Slice - handles runtime layout state and navigation
 * This data can be cached but is not as critical to persist as preferences
 */

// Default layout state
const DEFAULT_LAYOUT_STATE: LayoutState = {
  sidebarCollapsed: false,
  sidebarWidth: 240,
  middlePanelWidth: 350,
  rightPanelWidth: 400,
  headerHeight: 64,
  footerVisible: false,
}

const DEFAULT_NAVIGATION = {
  currentMode: 'chat' as NavigationMode,
  previousMode: null as NavigationMode | null,
  history: ['chat'] as NavigationMode[],
  breadcrumbs: [] as BreadcrumbItem[],
}

// State interface
export interface LayoutSliceState {
  layout: LayoutState
  navigation: typeof DEFAULT_NAVIGATION
}

// Actions interface
export interface LayoutActions {
  // Sidebar actions
  toggleSidebar: () => void
  setSidebarCollapsed: (collapsed: boolean) => void
  setSidebarWidth: (width: number) => void
  
  // Panel actions
  setMiddlePanelWidth: (width: number) => void
  setRightPanelWidth: (width: number) => void
  
  // Header/Footer actions
  setHeaderHeight: (height: number) => void
  setFooterVisible: (visible: boolean) => void
  
  // Navigation actions
  setCurrentNavigation: (mode: NavigationMode) => void
  navigateTo: (mode: NavigationMode, addToHistory?: boolean) => void
  navigateBack: () => void
  clearNavigationHistory: () => void
  
  // Breadcrumb actions
  setBreadcrumbs: (breadcrumbs: BreadcrumbItem[]) => void
  addBreadcrumb: (breadcrumb: BreadcrumbItem) => void
  removeBreadcrumb: (id: string) => void
  clearBreadcrumbs: () => void
  
  // Layout presets
  applyLayoutPreset: (preset: 'standard' | 'compact' | 'wide' | 'focus') => void
  resetLayout: () => void
  
  // Responsive helpers
  handleResize: (width: number, height: number) => void
  updateBreakpoint: (breakpoint: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl') => void
}

// Complete slice type
export type LayoutSlice = LayoutSliceState & LayoutActions

// Layout presets
const LAYOUT_PRESETS = {
  standard: {
    sidebarWidth: 240,
    middlePanelWidth: 350,
    rightPanelWidth: 400,
    sidebarCollapsed: false,
  },
  compact: {
    sidebarWidth: 200,
    middlePanelWidth: 300,
    rightPanelWidth: 350,
    sidebarCollapsed: false,
  },
  wide: {
    sidebarWidth: 280,
    middlePanelWidth: 400,
    rightPanelWidth: 500,
    sidebarCollapsed: false,
  },
  focus: {
    sidebarWidth: 240,
    middlePanelWidth: 300,
    rightPanelWidth: 0,
    sidebarCollapsed: true,
  },
} as const

// Slice creator
const createLayoutSlice: StateCreator<
  UIState,
  [],
  [],
  LayoutSlice
> = (set, get) => ({
  // Initial state
  layout: DEFAULT_LAYOUT_STATE,
  navigation: DEFAULT_NAVIGATION,

  // Sidebar actions
  toggleSidebar: () => set((state) => ({
    layout: {
      ...state.layout,
      sidebarCollapsed: !state.layout.sidebarCollapsed,
    },
  })),

  setSidebarCollapsed: (collapsed) => set((state) => ({
    layout: {
      ...state.layout,
      sidebarCollapsed: collapsed,
    },
  })),

  setSidebarWidth: (width) => set((state) => ({
    layout: {
      ...state.layout,
      sidebarWidth: Math.max(150, Math.min(400, width)), // Clamp between 150-400px
    },
  })),

  // Panel actions
  setMiddlePanelWidth: (width) => set((state) => ({
    layout: {
      ...state.layout,
      middlePanelWidth: Math.max(250, Math.min(500, width)), // Clamp between 250-500px
    },
  })),

  setRightPanelWidth: (width) => set((state) => ({
    layout: {
      ...state.layout,
      rightPanelWidth: Math.max(300, Math.min(600, width)), // Clamp between 300-600px
    },
  })),

  // Header/Footer actions
  setHeaderHeight: (height) => set((state) => ({
    layout: {
      ...state.layout,
      headerHeight: Math.max(48, Math.min(100, height)), // Clamp between 48-100px
    },
  })),

  setFooterVisible: (footerVisible) => set((state) => ({
    layout: {
      ...state.layout,
      footerVisible,
    },
  })),

  // Navigation actions
  setCurrentNavigation: (mode) => set((state) => ({
    navigation: {
      ...state.navigation,
      previousMode: state.navigation.currentMode,
      currentMode: mode,
    },
  })),

  navigateTo: (mode, addToHistory = true) => set((state) => {
    const newHistory = addToHistory
      ? [...state.navigation.history, mode].slice(-10) // Keep last 10 entries
      : state.navigation.history

    return {
      navigation: {
        ...state.navigation,
        previousMode: state.navigation.currentMode,
        currentMode: mode,
        history: newHistory,
      },
    }
  }),

  navigateBack: () => set((state) => {
    const history = state.navigation.history
    if (history.length > 1) {
      const previousMode = history[history.length - 2]
      const newHistory = history.slice(0, -1)
      
      return {
        navigation: {
          ...state.navigation,
          previousMode: state.navigation.currentMode,
          currentMode: previousMode,
          history: newHistory,
        },
      }
    }
    return state
  }),

  clearNavigationHistory: () => set((state) => ({
    navigation: {
      ...state.navigation,
      history: [state.navigation.currentMode],
    },
  })),

  // Breadcrumb actions
  setBreadcrumbs: (breadcrumbs) => set((state) => ({
    navigation: {
      ...state.navigation,
      breadcrumbs,
    },
  })),

  addBreadcrumb: (breadcrumb) => set((state) => ({
    navigation: {
      ...state.navigation,
      breadcrumbs: [...state.navigation.breadcrumbs, breadcrumb],
    },
  })),

  removeBreadcrumb: (id) => set((state) => ({
    navigation: {
      ...state.navigation,
      breadcrumbs: state.navigation.breadcrumbs.filter((b) => b.id !== id),
    },
  })),

  clearBreadcrumbs: () => set((state) => ({
    navigation: {
      ...state.navigation,
      breadcrumbs: [],
    },
  })),

  // Layout presets
  applyLayoutPreset: (preset) => {
    const presetConfig = LAYOUT_PRESETS[preset]
    if (!presetConfig) return

    set((state) => ({
      layout: {
        ...state.layout,
        ...presetConfig,
      },
    }))
  },

  resetLayout: () => set({
    layout: { ...DEFAULT_LAYOUT_STATE },
  }),

  // Responsive helpers
  handleResize: (width, height) => {
    const { layout } = get()
    
    // Auto-collapse sidebar on small screens
    if (width < 768 && !layout.sidebarCollapsed) {
      get().setSidebarCollapsed(true)
    } else if (width >= 768 && layout.sidebarCollapsed && get().preferences.layout.autoCollapseSidebar === false) {
      get().setSidebarCollapsed(false)
    }

    // Adjust panel widths on medium screens
    if (width < 1024) {
      if (layout.middlePanelWidth > 300) {
        get().setMiddlePanelWidth(300)
      }
      if (layout.rightPanelWidth > 350) {
        get().setRightPanelWidth(350)
      }
    }

    // Update header height based on screen size
    const newHeaderHeight = width < 640 ? 56 : 64
    if (layout.headerHeight !== newHeaderHeight) {
      get().setHeaderHeight(newHeaderHeight)
    }
  },

  updateBreakpoint: (breakpoint) => {
    // This would be handled by the responsive slice
    // but we can trigger layout adjustments here if needed
    const { layout } = get()
    
    switch (breakpoint) {
      case 'xs':
      case 'sm':
        if (!layout.sidebarCollapsed) {
          get().setSidebarCollapsed(true)
        }
        break
      case 'md':
        get().applyLayoutPreset('compact')
        break
      case 'lg':
      case 'xl':
      case '2xl':
        get().applyLayoutPreset('standard')
        break
    }
  },
})

export default createLayoutSlice