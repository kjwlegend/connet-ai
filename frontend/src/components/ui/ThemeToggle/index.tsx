"use client"

import { Button } from "@/components/ui/button"
import { Moon, Sun, Monitor } from "lucide-react"
import { useTheme } from "@/lib/design-system/theme-system"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"

interface ThemeToggleProps {
  className?: string
  variant?: "default" | "ghost" | "outline"
  size?: "default" | "sm" | "lg" | "icon"
}

export function ThemeToggle({ 
  className, 
  variant = "ghost", 
  size = "icon" 
}: ThemeToggleProps) {
  const { currentTheme, changeTheme, availableThemes } = useTheme()

  const getThemeIcon = (theme: string) => {
    switch (theme) {
      case 'light':
        return <Sun className="h-4 w-4" />
      case 'dark':
        return <Moon className="h-4 w-4" />
      default:
        return <Monitor className="h-4 w-4" />
    }
  }

  const getThemeLabel = (theme: string) => {
    switch (theme) {
      case 'light':
        return '浅色主题'
      case 'dark':
        return '深色主题'
      default:
        return '跟随系统'
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant={variant} 
          size={size} 
          className={cn("transition-colors", className)}
          aria-label="切换主题"
        >
          {getThemeIcon(currentTheme)}
          <span className="sr-only">切换主题</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-40">
        {availableThemes.map((theme) => (
          <DropdownMenuItem
            key={theme.name}
            onClick={() => changeTheme(theme.name)}
            className={cn(
              "flex items-center gap-2 cursor-pointer",
              currentTheme === theme.name && "bg-accent"
            )}
          >
            {getThemeIcon(theme.name)}
            <span>{getThemeLabel(theme.name)}</span>
          </DropdownMenuItem>
        ))}
        <DropdownMenuItem
          onClick={() => {
            // 切换到系统主题
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            changeTheme(prefersDark ? 'dark' : 'light');
          }}
          className="flex items-center gap-2 cursor-pointer"
        >
          <Monitor className="h-4 w-4" />
          <span>跟随系统</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

// 简单的主题切换按钮（只在浅色和深色之间切换）
export function SimpleThemeToggle({ className }: { className?: string }) {
  const { currentTheme, toggleTheme } = useTheme()

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={toggleTheme}
      className={cn("transition-colors", className)}
      aria-label="切换主题"
    >
      {currentTheme === 'dark' ? (
        <Sun className="h-4 w-4" />
      ) : (
        <Moon className="h-4 w-4" />
      )}
      <span className="sr-only">切换主题</span>
    </Button>
  )
}