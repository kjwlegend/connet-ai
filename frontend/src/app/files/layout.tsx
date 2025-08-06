"use client";

import { useState } from "react";
import { MiddlePanel } from "@/components/layout/MiddlePanel";
import { AppLayout } from "@/components/layout/AppLayout";

interface FilesLayoutProps {
  children: React.ReactNode;
}

export default function FilesLayout({ children }: FilesLayoutProps) {
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
      <div className="flex-1">
        {children}
      </div>
    </AppLayout>
  );
}