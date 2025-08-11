"use client";

import { useState } from "react";
import { MiddlePanel } from "@/components/layout/MiddlePanel";
import { AppLayout } from "@/components/layout/AppLayout";
import { MainContent } from "@/components/layout/MainContent";

export default function FilesLayout() {
  const [selectedItem, setSelectedItem] = useState<string | null>(null);

  return (
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
  );
}