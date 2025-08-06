"use client";

import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import { Sidebar } from "@/components/layout/Sidebar";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import type { NavigationMode } from "@/types";

interface AppLayoutProps {
  children: React.ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const pathname = usePathname();
  
  // 根据当前路径确定导航模式
  const getCurrentMode = (): NavigationMode => {
    if (pathname.startsWith("/chat")) return "chat";
    if (pathname.startsWith("/contacts")) return "contacts";
    if (pathname.startsWith("/files")) return "files";
    if (pathname.startsWith("/social")) return "social";
    if (pathname.startsWith("/plugins")) return "plugins";
    if (pathname.startsWith("/settings")) return "settings";
    return "chat";
  };

  const [currentMode, setCurrentMode] = useState<NavigationMode>(getCurrentMode);

  // 当路径改变时更新当前模式
  useEffect(() => {
    setCurrentMode(getCurrentMode());
  }, [pathname]);

  return (
    <ErrorBoundary>
      {/* Left Sidebar - Navigation */}
      <Sidebar currentMode={currentMode} onModeChange={setCurrentMode} />
      
      {/* Main Content Area */}
      <div className="flex-1 flex">
        {children}
      </div>
    </ErrorBoundary>
  );
}

export default AppLayout;