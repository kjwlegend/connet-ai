"use client";

import { MainContent } from "@/components/layout/MainContent";

interface ChatDetailPageProps {
  params: {
    chatId: string;
  };
}

export default function ChatDetailPage({ params }: ChatDetailPageProps) {
  return (
    <MainContent
      mode="chat"
      selectedItem={params.chatId}
      onItemSelect={() => {}}
    />
  );
}