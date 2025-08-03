import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface ContentAreaProps {
  children: ReactNode
  className?: string
}

export function ContentArea({ children, className }: ContentAreaProps) {
  return (
    <div className={cn('h-full bg-background', className)}>
      <div className="h-full overflow-auto">
        {children}
      </div>
    </div>
  )
}

export default ContentArea