"use client";

import { useState } from "react";
import { MiddlePanel } from "@/components/layout/MiddlePanel";
import { AppLayout } from "@/components/layout/AppLayout";
import { MainContent } from "@/components/layout/MainContent";
import { LayoutGuard } from "@/components/auth/RouteGuard";

export default function FilesLayout() {
  const [selectedItem, setSelectedItem] = useState<string | null>(null);

  return (
    <LayoutGuard>
      <AppLayout>
      {/* Middle Panel - Files List */}
      <MiddlePanel
        mode="files"
        selectedItem={selectedItem}
        onItemSelect={setSelectedItem}
      />

      {/* Right Panel - File Content */}
      <MainContent
        mode="files"
        selectedItem={selectedItem}
        onItemSelect={setSelectedItem}
      />
      </AppLayout>
    </LayoutGuard>
  );
}