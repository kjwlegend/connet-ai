"use client";

import { MainContent } from "@/components/layout/MainContent";

interface SocialPostPageProps {
  params: {
    postId: string;
  };
}

export default function SocialPostPage({ params }: SocialPostPageProps) {
  return (
    <MainContent
      mode="social"
      selectedItem={params.postId}
      onItemSelect={() => {}}
    />
  );
}