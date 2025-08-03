import { useUI } from '@/store'

export function MiddlePanel() {
  const { currentNavigation } = useUI()

  const renderContent = () => {
    switch (currentNavigation) {
      case 'chat':
        return <ChatList />
      case 'contacts':
        return <ContactsList />
      case 'files':
        return <FilesList />
      case 'timeline':
        return <TimelineList />
      case 'plugins':
        return <PluginsList />
      case 'settings':
        return <SettingsList />
      default:
        return <div>未知导航</div>
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex-shrink-0 h-16 border-b border px-4 flex items-center">
        <h2 className="text-lg font-semibold capitalize">
          {getNavigationTitle(currentNavigation)}
        </h2>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">{renderContent()}</div>
    </div>
  )
}

function getNavigationTitle(nav: string): string {
  const titles: Record<string, string> = {
    chat: '对话',
    contacts: '联系人',
    files: '文件',
    timeline: '时间线',
    plugins: '插件',
    settings: '设置',
  }
  return titles[nav] || nav
}

// Placeholder components - these will be implemented later
function ChatList() {
  return (
    <div className="p-4">
      <div className="text-sm text-muted-foreground">对话列表</div>
    </div>
  )
}

function ContactsList() {
  return (
    <div className="p-4">
      <div className="text-sm text-muted-foreground">联系人列表</div>
    </div>
  )
}

function FilesList() {
  return (
    <div className="p-4">
      <div className="text-sm text-muted-foreground">文件列表</div>
    </div>
  )
}

function TimelineList() {
  return (
    <div className="p-4">
      <div className="text-sm text-muted-foreground">时间线列表</div>
    </div>
  )
}

function PluginsList() {
  return (
    <div className="p-4">
      <div className="text-sm text-muted-foreground">插件列表</div>
    </div>
  )
}

function SettingsList() {
  return (
    <div className="p-4">
      <div className="text-sm text-muted-foreground">设置选项</div>
    </div>
  )
}

export default MiddlePanel
