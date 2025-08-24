/**
 * Hooks 统一入口文件
 * 重构后的新架构 hooks 导出
 */

// Business Logic Hooks - 业务逻辑层
export * from './business'

// UI Hooks - 界面状态层
export * from './ui'

// Composite Hooks - 页面级组合层
export * from './composite'

// 保留一些独立的工具 hooks
export { useErrorHandler } from './useErrorHandler'
export { useKeyboardShortcuts } from './useKeyboardShortcuts'
export { useShareContact } from './useShareContact'

// Legacy hooks（标记为废弃，逐步移除）
// 注意：这些 hooks 已被重构，建议使用新的 business hooks
// export * from './legacy' // 不再默认导出，避免冲突