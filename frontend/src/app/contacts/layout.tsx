"use client";

import { useState } from "react";
import { MiddlePanel } from "@/components/layout/MiddlePanel";
import { AppLayout } from "@/components/layout/AppLayout";
import { MainContent } from "@/components/layout/MainContent";
import { LayoutGuard } from "@/components/auth/RouteGuard";

export default function ContactsLayout() {
  const [selectedItem, setSelectedItem] = useState<string | null>(null);

  return (
    <LayoutGuard>
      <AppLayout>
      {/* Middle Panel - Contacts List */}
      <MiddlePanel
        mode="contacts"
        selectedItem={selectedItem}
        onItemSelect={setSelectedItem}
      />

      {/* Right Panel - Contact Content */}
      <MainContent
        mode="contacts"
        selectedItem={selectedItem}
        onItemSelect={setSelectedItem}
      />
      </AppLayout>
    </LayoutGuard>
  );
}