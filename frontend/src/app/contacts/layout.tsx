"use client";

import { useState } from "react";
import { MiddlePanel } from "@/components/layout/MiddlePanel";
import { AppLayout } from "@/components/layout/AppLayout";

interface ContactsLayoutProps {
  children: React.ReactNode;
}

export default function ContactsLayout({ children }: ContactsLayoutProps) {
  const [selectedItem, setSelectedItem] = useState<string | null>(null);

  return (
    <AppLayout>
      {/* Middle Panel - Contacts List */}
      <MiddlePanel
        mode="contacts"
        selectedItem={selectedItem}
        onItemSelect={setSelectedItem}
      />

      {/* Right Panel - Contact Content */}
      <div className="flex-1">
        {children}
      </div>
    </AppLayout>
  );
}