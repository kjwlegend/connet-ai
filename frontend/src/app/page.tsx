"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // 重定向到聊天页面作为默认首页
    router.replace("/chat");
  }, [router]);

  return (
    <div className="flex items-center justify-center w-full h-screen">
      <LoadingSpinner />
    </div>
  );
}
