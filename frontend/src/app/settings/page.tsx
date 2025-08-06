"use client";

import { MainContent } from "@/components/layout/MainContent";

export default function SettingsPage() {
  return (
    <MainContent
      mode="settings"
      selectedItem={null}
      onItemSelect={() => {}}
    />
  );
}