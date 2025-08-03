"use client"

import { useState, useEffect, useCallback } from 'react';

export interface ThemeConfig {
  name: string;
  label: string;
  colors: {
    // 语义化颜色映射
    background: {
      primary: string;
      secondary: string;
      elevated: string;
    };
    text: {
      primary: string;
      secondary: string;
      muted: string;
    };
    border: {
      default: string;
      muted: string;
    };
    // 交互状态颜色
    interactive: {
      default: string;
      hover: string;
      active: string;
      disabled: string;
    };
  };
}

export class ThemeManager {
  private themes: Map<string, ThemeConfig> = new Map();
  private currentTheme: string = 'light';
  
  constructor() {
    this.registerDefaultThemes();
  }
  
  private registerDefaultThemes(): void {
    // 浅色主题
    this.registerTheme({
      name: 'light',
      label: '浅色主题',
      colors: {
        background: {
          primary: '#ffffff',
          secondary: '#f8f9fa',
          elevated: '#ffffff',
        },
        text: {
          primary: '#000000',
          secondary: '#081727',
          muted: '#c9d4dc',
        },
        border: {
          default: '#c9d4dc',
          muted: '#e9ecef',
        },
        interactive: {
          default: '#081727',
          hover: '#161b25',
          active: '#000000',
          disabled: '#e0e0e0',
        },
      }
    });
    
    // 深色主题
    this.registerTheme({
      name: 'dark',
      label: '深色主题',
      colors: {
        background: {
          primary: '#081727',
          secondary: '#161b25',
          elevated: '#2b3a4f',
        },
        text: {
          primary: '#ffffff',
          secondary: '#c9d4dc',
          muted: '#2b3a4f',
        },
        border: {
          default: '#2b3a4f',
          muted: '#161b25',
        },
        interactive: {
          default: '#2b3a4f',
          hover: '#3d4e63',
          active: '#5a6b7d',
          disabled: '#757575',
        },
      }
    });
  }
  
  registerTheme(theme: ThemeConfig): void {
    this.themes.set(theme.name, theme);
  }
  
  setTheme(themeName: string): void {
    const theme = this.themes.get(themeName);
    if (!theme) {
      console.warn(`Theme "${themeName}" not found`);
      return;
    }
    
    this.currentTheme = themeName;
    this.applyTheme(theme);
  }
  
  private applyTheme(theme: ThemeConfig): void {
    const root = document.documentElement;
    
    // 应用主题颜色
    Object.entries(theme.colors).forEach(([category, colors]) => {
      Object.entries(colors).forEach(([key, value]) => {
        root.style.setProperty(`--theme-${category}-${key}`, value);
      });
    });
    
    // 设置主题标识
    root.setAttribute('data-theme', theme.name);
    
    // 存储到 localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('theme', theme.name);
    }
    
    // 触发主题变更事件
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('theme-changed', {
        detail: { theme: theme.name }
      }));
    }
  }
  
  getCurrentTheme(): string {
    return this.currentTheme;
  }
  
  getAvailableThemes(): ThemeConfig[] {
    return Array.from(this.themes.values());
  }
  
  initializeTheme(): void {
    if (typeof window !== 'undefined') {
      // 检查本地存储的主题偏好
      const savedTheme = localStorage.getItem('theme');
      if (savedTheme && this.themes.has(savedTheme)) {
        this.setTheme(savedTheme);
        return;
      }
      
      // 检查系统主题偏好
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      this.setTheme(prefersDark ? 'dark' : 'light');
    }
  }
}

// 全局主题管理器实例
let themeManagerInstance: ThemeManager | null = null;

export function getThemeManager(): ThemeManager {
  if (!themeManagerInstance) {
    themeManagerInstance = new ThemeManager();
  }
  return themeManagerInstance;
}

// React Hook for theme management
export function useTheme() {
  const [currentTheme, setCurrentTheme] = useState<string>('light');
  const [availableThemes, setAvailableThemes] = useState<ThemeConfig[]>([]);
  
  useEffect(() => {
    const themeManager = getThemeManager();
    setCurrentTheme(themeManager.getCurrentTheme());
    setAvailableThemes(themeManager.getAvailableThemes());
    
    // 初始化主题
    themeManager.initializeTheme();
    
    const handleThemeChange = (event: CustomEvent) => {
      setCurrentTheme(event.detail.theme);
    };
    
    if (typeof window !== 'undefined') {
      window.addEventListener('theme-changed', handleThemeChange as EventListener);
      
      // 监听系统主题变化
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleSystemThemeChange = (e: MediaQueryListEvent) => {
        // 只有在没有保存的主题偏好时才跟随系统
        if (!localStorage.getItem('theme')) {
          themeManager.setTheme(e.matches ? 'dark' : 'light');
        }
      };
      
      mediaQuery.addEventListener('change', handleSystemThemeChange);
      
      return () => {
        window.removeEventListener('theme-changed', handleThemeChange as EventListener);
        mediaQuery.removeEventListener('change', handleSystemThemeChange);
      };
    }
  }, []);
  
  const changeTheme = useCallback((themeName: string) => {
    const themeManager = getThemeManager();
    themeManager.setTheme(themeName);
  }, []);
  
  const toggleTheme = useCallback(() => {
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    changeTheme(newTheme);
  }, [currentTheme, changeTheme]);
  
  return {
    currentTheme,
    availableThemes,
    changeTheme,
    toggleTheme,
  };
}