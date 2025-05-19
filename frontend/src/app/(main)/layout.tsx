// app/(main)/layout.tsx
import React from 'react'

export default function MainLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div>
      {/* Add Navbar, Sidebar etc. here */}
      <main>{children}</main>
    </div>
  )
}
