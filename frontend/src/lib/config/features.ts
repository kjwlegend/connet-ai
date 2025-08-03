import { env } from './env'

export const FEATURE_FLAGS = {
  // Core Features
  ENABLE_CHAT: true,
  ENABLE_CONTACTS: true,
  ENABLE_FILES: true,
  ENABLE_TIMELINE: true,
  ENABLE_PLUGINS: true,

  // Experimental Features
  ENABLE_VOICE_CHAT: false,
  ENABLE_VIDEO_CHAT: false,
  ENABLE_SCREEN_SHARING: false,
  ENABLE_AI_SUGGESTIONS: true,

  // Performance Features
  ENABLE_VIRTUALIZATION: true,
  ENABLE_LAZY_LOADING: true,
  ENABLE_PREFETCHING: true,
  ENABLE_CACHING: true,

  // Debug Features
  ENABLE_PERFORMANCE_MONITORING: env.ENABLE_DEBUG,
  ENABLE_ERROR_REPORTING: !env.ENABLE_DEBUG,
  ENABLE_ANALYTICS: env.ENABLE_ANALYTICS,

  // UI Features
  ENABLE_DARK_MODE: true,
  ENABLE_ANIMATIONS: true,
  ENABLE_TOOLTIPS: true,
  ENABLE_KEYBOARD_SHORTCUTS: true,

  // Security Features
  ENABLE_CSP: true,
  ENABLE_RATE_LIMITING: true,
  ENABLE_INPUT_SANITIZATION: true,
} as const

export type FeatureFlag = keyof typeof FEATURE_FLAGS

export function isFeatureEnabled(feature: FeatureFlag): boolean {
  return FEATURE_FLAGS[feature]
}

export function getEnabledFeatures(): FeatureFlag[] {
  return Object.entries(FEATURE_FLAGS)
    .filter(([, enabled]) => enabled)
    .map(([feature]) => feature as FeatureFlag)
}

export function getDisabledFeatures(): FeatureFlag[] {
  return Object.entries(FEATURE_FLAGS)
    .filter(([, enabled]) => !enabled)
    .map(([feature]) => feature as FeatureFlag)
}

// Runtime feature toggle (for development/testing)
export function toggleFeature(feature: FeatureFlag, enabled?: boolean): void {
  if (env.ENABLE_DEBUG) {
    ;(FEATURE_FLAGS as any)[feature] = enabled ?? !FEATURE_FLAGS[feature]
    console.log(`Feature ${feature} ${FEATURE_FLAGS[feature] ? 'enabled' : 'disabled'}`)
  }
}

export default {
  FEATURE_FLAGS,
  isFeatureEnabled,
  getEnabledFeatures,
  getDisabledFeatures,
  toggleFeature,
}