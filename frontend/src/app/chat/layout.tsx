"use client";

import { useState } from "react";
import { MiddlePanel } from "@/components/layout/MiddlePanel";
import { AppLayout } from "@/components/layout/AppLayout";
import { MainContent } from "@/components/layout/MainContent";

export default function ChatLayout() {
  const [selectedItem, setSelectedItem] = useState<string | null>(null);

  return (
    <AppLayout>
      {/* Middle Panel - Chat List */}
      <MiddlePanel
        mode="chat"
        selectedItem={selectedItem}
        onItemSelect={setSelectedItem}
      />

      {/* Right Panel - Chat Content */}
      <MainContent
        mode="chat"
        selectedItem={selectedItem}
        onItemSelect={setSelectedItem}
      />
    </AppLayout>
  );
}