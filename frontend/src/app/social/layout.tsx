"use client";

import { useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { SocialSidebar } from "@/components/features/timeline/components/SocialSidebar";
import { SocialContent } from "@/components/features/timeline/components/SocialContent";
import { cn } from "@/lib/utils";
import { useTheme } from "next-themes";

interface SocialLayoutProps {
  children: React.ReactNode;
}

export default function SocialLayout({ children }: SocialLayoutProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>("friends-circle");
  const { theme } = useTheme();

  return (
    <AppLayout>
      {/* Middle Panel - Social Categories */}
      <div className={cn(
        "w-64 border-r flex flex-col",
        theme === 'dark' 
          ? "bg-card border-border" 
          : "bg-white border-gray-200"
      )}>
        <SocialSidebar
          selectedCategory={selectedCategory}
          onCategorySelect={setSelectedCategory}
        />
      </div>

      {/* Right Panel - Social Content */}
      <div className="flex-1">
        <SocialContent category={selectedCategory} />
      </div>
    </AppLayout>
  );
}