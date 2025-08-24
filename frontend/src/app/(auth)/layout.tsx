'use client'

import { PageGuard } from "@/components/auth/RouteGuard"

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <PageGuard requireAuth={false}>
      <div>
        {children}
      </div>
    </PageGuard>
  )
}