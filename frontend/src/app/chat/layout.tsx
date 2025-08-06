"use client";

import { useState } from "react";
import { MiddlePanel } from "@/components/layout/MiddlePanel";
import { AppLayout } from "@/components/layout/AppLayout";

interface ChatLayoutProps {
  children: React.ReactNode;
}

export default function ChatLayout({ children }: ChatLayoutProps) {
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
      <div className="flex-1">
        {children}
      </div>
    </AppLayout>
  );
}