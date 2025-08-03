"use client"

import { useState } from "react"
import { Sidebar } from "@/components/sidebar"
import { MiddlePanel } from "@/components/middle-panel"
import { MainContent } from "@/components/main-content"
import type { NavigationMode } from "@/types"

export default function Home() {
  const [currentMode, setCurrentMode] = useState<NavigationMode>("chat")
  const [selectedItem, setSelectedItem] = useState<string | null>("agent-1")

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Left Sidebar - Navigation */}
      <Sidebar currentMode={currentMode} onModeChange={setCurrentMode} />

      {/* Middle Panel - Context List */}
      <MiddlePanel mode={currentMode} selectedItem={selectedItem} onItemSelect={setSelectedItem} />

      {/* Right Panel - Main Content */}
      <MainContent mode={currentMode} selectedItem={selectedItem} onItemSelect={setSelectedItem} />
    </div>
  )
}