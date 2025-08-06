"use client";

import { useState } from "react";
import { MiddlePanel } from "@/components/layout/MiddlePanel";
import { AppLayout } from "@/components/layout/AppLayout";

interface SocialLayoutProps {
  children: React.ReactNode;
}

export default function SocialLayout({ children }: SocialLayoutProps) {
  const [selectedItem, setSelectedItem] = useState<string | null>(null);

  return (
    <AppLayout>
      {/* Middle Panel - Social Timeline */}
      <MiddlePanel
        mode="social"
        selectedItem={selectedItem}
        onItemSelect={setSelectedItem}
      />

      {/* Right Panel - Social Content */}
      <div className="flex-1">
        {children}
      </div>
    </AppLayout>
  );
}