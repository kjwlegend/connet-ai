'use client'

import { useState } from 'react'
import { MiddlePanel } from '@/components/layout/MiddlePanel'
import { AppLayout } from '@/components/layout/AppLayout'
import { LayoutGuard } from '@/components/auth/RouteGuard'

interface SettingsLayoutProps {
  children: React.ReactNode
}

export default function SettingsLayout({ children }: SettingsLayoutProps) {
  const [selectedItem, setSelectedItem] = useState<string | null>(null)

  return (
    <LayoutGuard>
      <AppLayout>
      {/* Middle Panel - Settings Menu */}
      <MiddlePanel
        mode="settings"
        selectedItem={selectedItem}
        onItemSelect={setSelectedItem}
      />

      {/* Right Panel - Settings Content */}
      <div className="flex-1 h-screen overflow-auto">{children}</div>
      </AppLayout>
    </LayoutGuard>
  )
}
