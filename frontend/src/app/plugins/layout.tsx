"use client";

import { useState } from "react";
import { MiddlePanel } from "@/components/layout/MiddlePanel";
import { AppLayout } from "@/components/layout/AppLayout";
import { MainContent } from "@/components/layout/MainContent";
import { LayoutGuard } from "@/components/auth/RouteGuard";

export default function PluginsLayout() {
  const [selectedItem, setSelectedItem] = useState<string | null>(null);

  return (
    <LayoutGuard>
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
    </LayoutGuard>
  );
}