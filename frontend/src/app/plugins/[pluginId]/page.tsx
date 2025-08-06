"use client";

import { MainContent } from "@/components/layout/MainContent";

interface PluginDetailPageProps {
  params: {
    pluginId: string;
  };
}

export default function PluginDetailPage({ params }: PluginDetailPageProps) {
  return (
    <MainContent
      mode="plugins"
      selectedItem={params.pluginId}
      onItemSelect={() => {}}
    />
  );
}