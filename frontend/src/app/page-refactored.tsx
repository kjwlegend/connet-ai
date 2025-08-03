"use client"

import { useState } from "react"
import { LegacySidebar } from "@/components/layout/LegacySidebar"
import { LegacyMiddlePanel } from "@/components/layout/LegacyMiddlePanel"
import { LegacyMainContent } from "@/components/layout/LegacyMainContent"
import { ErrorBoundary } from "@/components/common/ErrorBoundary"
import type { NavigationMode } from "@/types"

export default function RefactoredHome() {
  const [currentMode, setCurrentMode] = useState<NavigationMode>("chat")
  const [selectedItem, setSelectedItem] = useState<string | null>("agent-1")

  return (
    <ErrorBoundary>
      <div className="flex h-screen bg-gray-50">
        {/* Left Sidebar - Navigation */}
        <LegacySidebar currentMode={currentMode} onModeChange={setCurrentMode} />

        {/* Middle Panel - Context List */}
        <LegacyMiddlePanel mode={currentMode} selectedItem={selectedItem} onItemSelect={setSelectedItem} />

        {/* Right Panel - Main Content */}
        <LegacyMainContent mode={currentMode} selectedItem={selectedItem} onItemSelect={setSelectedItem} />
      </div>
    </ErrorBoundary>
  )
}