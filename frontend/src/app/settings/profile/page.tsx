"use client";

import { MainContent } from "@/components/layout/MainContent";

export default function ProfileSettingsPage() {
  return (
    <MainContent
      mode="settings"
      selectedItem="profile"
      onItemSelect={() => {}}
    />
  );
}