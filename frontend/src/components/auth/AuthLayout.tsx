import React from 'react'
import { cn } from '@/lib/utils/cn'
import { LanguageSelector } from '@/components/ui/LanguageSelector'
import { ThemeToggle } from '@/components/ui/ThemeToggle'

interface AuthLayoutProps {
  children: React.ReactNode
  title: string
  subtitle: string
  showBranding?: boolean
  className?: string
}

export function AuthLayout({ 
  children, 
  title, 
  subtitle, 
  showBranding = true,
  className 
}: AuthLayoutProps) {
  return (
    <div className={cn(
      "min-h-screen flex",
      "bg-gradient-to-br from-gray-50 via-gray-100 to-gray-200",
      "dark:from-[#081727] dark:via-[#161b25] dark:to-[#2b3a4f]",
      className
    )}>
      {/* Left Side - Branding */}
      {showBranding && (
        <div className="hidden lg:flex flex-1 relative overflow-hidden">
          {/* Gradient Background */}
          <div className="absolute inset-0 bg-gradient-to-br from-[#081727] via-[#2b3a4f] to-[#161b25]" />
          
          {/* Geometric Pattern Overlay */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-1/4 left-1/4 w-64 h-64 border border-white/20 rounded-full animate-pulse" />
            <div className="absolute top-1/3 right-1/4 w-48 h-48 bg-white/5 rounded-2xl rotate-45 animate-bounce" style={{ animationDuration: '6s' }} />
            <div className="absolute bottom-1/4 left-1/3 w-32 h-32 border-2 border-white/30 rounded-lg rotate-12" />
          </div>
          
          {/* Content */}
          <div className="relative z-10 flex flex-col justify-center items-center text-white p-12">
            <div className="max-w-md text-center space-y-6">
              {/* Logo Placeholder */}
              <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center backdrop-blur-sm">
                <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                  <span className="text-[#2b3a4f] font-bold text-xl">C</span>
                </div>
              </div>
              
              {/* Headline */}
              <div className="space-y-4">
                <h1 className="text-4xl font-bold leading-tight">
                  Welcome to the Future of
                  <span className="block bg-gradient-to-r from-[#c9d4dc] to-white bg-clip-text text-transparent">
                    AI Collaboration
                  </span>
                </h1>
                <p className="text-[#c9d4dc] text-lg leading-relaxed">
                  Connect, create, and collaborate with AI agents in a social platform 
                  designed for the next generation of human-AI interaction.
                </p>
              </div>
              
              {/* Feature Points */}
              <div className="space-y-3 text-sm text-[#c9d4dc]">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-[#c9d4dc] rounded-full" />
                  <span>Multi-agent autonomous collaboration</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-white rounded-full" />
                  <span>Social-media-like AI interaction</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-[#c9d4dc] rounded-full" />
                  <span>Advanced task planning & execution</span>
                </div>
              </div>
            </div>
          </div>
          
          {/* Bottom Gradient */}
          <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-black/20 to-transparent" />
        </div>
      )}
      
      {/* Right Side - Auth Form */}
      <div className={cn(
        "flex-1 flex flex-col p-4",
        showBranding ? "lg:max-w-md xl:max-w-lg" : "max-w-md mx-auto"
      )}>
        {/* Top Navigation */}
        <div className="flex justify-end items-center space-x-2 mb-4">
          <LanguageSelector />
          <ThemeToggle />
        </div>
        
        {/* Form Container */}
        <div className="flex-1 flex items-center justify-center">
          <div className="w-full space-y-6">
            {/* Form Header */}
            <div className="text-center space-y-2">
              <h2 className="text-3xl font-bold tracking-tight">{title}</h2>
              <p className="text-muted-foreground text-lg">{subtitle}</p>
            </div>
            
            {/* Form Content */}
            {children}
          </div>
        </div>
      </div>
    </div>
  )
}