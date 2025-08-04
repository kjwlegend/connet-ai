"use client"

import { useState } from "react"
import { Sidebar } from "@/components/layout/Sidebar"
import { MiddlePanel } from "@/components/layout/MiddlePanel"
import { MainContent } from "@/components/layout/MainContent"
import { ErrorBoundary } from "@/components/common/ErrorBoundary"
import type { NavigationMode } from "@/types"

export default function Home() {
  const [currentMode, setCurrentMode] = useState<NavigationMode>("chat")
  const [selectedItem, setSelectedItem] = useState<string | null>("agent-1")

  return (
    <ErrorBoundary>
      <div className="flex h-screen bg-background">
        {/* Left Sidebar - Navigation */}
        <Sidebar currentMode={currentMode} onModeChange={setCurrentMode} />

        {/* Middle Panel - Context List */}
        <MiddlePanel mode={currentMode} selectedItem={selectedItem} onItemSelect={setSelectedItem} />

        {/* Right Panel - Main Content */}
        <MainContent mode={currentMode} selectedItem={selectedItem} onItemSelect={setSelectedItem} />
      </div>
    </ErrorBoundary>
  )
}