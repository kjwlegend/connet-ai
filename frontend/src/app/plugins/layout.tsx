"use client";

import { useState } from "react";
import { MiddlePanel } from "@/components/layout/MiddlePanel";
import { AppLayout } from "@/components/layout/AppLayout";

interface PluginsLayoutProps {
  children: React.ReactNode;
}

export default function PluginsLayout({ children }: PluginsLayoutProps) {
  const [selectedItem, setSelectedItem] = useState<string | null>(null);

  return (
    <AppLayout>
      {/* Middle Panel - Plugins List */}
      <MiddlePanel
        mode="plugins"
        selectedItem={selectedItem}
        onItemSelect={setSelectedItem}
      />

      {/* Right Panel - Plugin Content */}
      <div className="flex-1">
        {children}
      </div>
    </AppLayout>
  );
}