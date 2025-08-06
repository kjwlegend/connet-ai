"use client";

import { MainContent } from "@/components/layout/MainContent";

export default function ChatPage() {
  return (
    <MainContent
      mode="chat"
      selectedItem={null}
      onItemSelect={() => {}}
    />
  );
}