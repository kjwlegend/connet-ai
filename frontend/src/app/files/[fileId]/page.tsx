"use client";

import { MainContent } from "@/components/layout/MainContent";

interface FileDetailPageProps {
  params: {
    fileId: string;
  };
}

export default function FileDetailPage({ params }: FileDetailPageProps) {
  return (
    <MainContent
      mode="files"
      selectedItem={params.fileId}
      onItemSelect={() => {}}
    />
  );
}