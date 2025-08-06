"use client";

import { MainContent } from "@/components/layout/MainContent";

export default function FilesPage() {
  return (
    <MainContent
      mode="files"
      selectedItem={null}
      onItemSelect={() => {}}
    />
  );
}