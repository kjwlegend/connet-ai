import { ReactNode } from 'react'
import { Sidebar } from '../Sidebar'
import { MiddlePanel } from '../MiddlePanel'
import { ContentArea } from '../ContentArea'
import { useUI } from '@/store'
import { cn } from '@/lib/utils'

interface MainLayoutProps {
  children: ReactNode
  className?: string
}

export function MainLayout({ children, className }: MainLayoutProps) {
  const { sidebarCollapsed, middlePanelWidth } = useUI()

  return (
    <div className={cn('flex h-screen bg-background ', className)}>
      {/* Left Sidebar */}
      <Sidebar />

      {/* Middle Panel */}
      <div
        className="shrink-0 border-r border h-full scroll-auto"
        style={{ width: middlePanelWidth }}
      >
        <MiddlePanel />
      </div>

      {/* Main Content Area */}
      <div className="flex-1 min-w-0 h-full scroll-auto">
        <ContentArea>{children}</ContentArea>
      </div>
    </div>
  )
}

export default MainLayout
