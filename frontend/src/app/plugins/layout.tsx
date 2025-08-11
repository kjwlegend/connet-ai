"use client";

import { useState } from "react";
import { MiddlePanel } from "@/components/layout/MiddlePanel";
import { AppLayout } from "@/components/layout/AppLayout";
import { MainContent } from "@/components/layout/MainContent";

export default function PluginsLayout() {
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
      <MainContent
        mode="plugins"
        selectedItem={selectedItem}
        onItemSelect={setSelectedItem}
      />
    </AppLayout>
  );
}