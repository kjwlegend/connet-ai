import { useUI } from '@/store'
import { cn } from '@/lib/utils'
import { APP_CONFIG } from '@/lib/config/constants'

export function Sidebar() {
  const {
    sidebarCollapsed,
    toggleSidebar,
    currentNavigation,
    setCurrentNavigation,
  } = useUI()

  const navigationItems = [
    { id: 'chat', icon: '💬', label: '对话', shortcut: 'C' },
    { id: 'contacts', icon: '👥', label: '联系人', shortcut: 'O' },
    { id: 'files', icon: '📁', label: '文件', shortcut: 'F' },
    { id: 'timeline', icon: '📰', label: '时间线', shortcut: 'T' },
    { id: 'plugins', icon: '🧩', label: '插件', shortcut: 'P' },
    { id: 'settings', icon: '⚙️', label: '设置', shortcut: 'S' },
  ]

  return (
    <div
      className={cn(
        'flex-shrink-0 bg-sidebar border-r border transition-all duration-200',
        sidebarCollapsed ? 'w-16' : 'w-20'
      )}
      style={{
        width: sidebarCollapsed
          ? APP_CONFIG.SIDEBAR_WIDTH.MIN
          : APP_CONFIG.SIDEBAR_WIDTH.DEFAULT,
      }}
    >
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="flex items-center justify-center h-16 border-b border">
          <button
            onClick={toggleSidebar}
            className="p-2 hover:bg-sidebar-accent rounded-md transition-colors"
            title="切换侧边栏"
          >
            {sidebarCollapsed ? '→' : '←'}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4">
          <div className="space-y-2 px-2">
            {navigationItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setCurrentNavigation(item.id)}
                className={cn(
                  'w-full flex flex-col items-center justify-center p-3 rounded-lg transition-all duration-200',
                  'hover:bg-sidebar-accent',
                  currentNavigation === item.id &&
                    'bg-sidebar-accent border border-sidebar-border'
                )}
                title={`${item.label} (${item.shortcut})`}
              >
                <span className="text-lg mb-1">{item.icon}</span>
                {!sidebarCollapsed && (
                  <span className="text-xs text-sidebar-foreground/80">
                    {item.label}
                  </span>
                )}
              </button>
            ))}
          </div>
        </nav>

        {/* User Area */}
        <div className="p-2 border-t border">
          <button className="w-full p-3 rounded-lg hover:bg-sidebar-accent transition-colors">
            <div className="flex flex-col items-center">
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                U
              </div>
              {!sidebarCollapsed && (
                <span className="text-xs mt-1 text-sidebar-foreground/80">
                  用户
                </span>
              )}
            </div>
          </button>
        </div>
      </div>
    </div>
  )
}

export default Sidebar
