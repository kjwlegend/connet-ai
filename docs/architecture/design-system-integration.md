# Design System Integration Patterns - Connet.AI

## 概述

本文档详细描述了如何在 Connet.AI 项目中实现设计系统的集成，确保前端组件与品牌视觉规范的完美统一，建立可维护、可扩展的设计系统实现方案。

## 设计系统集成原则

### 1. 统一性原则 (Consistency)
- **视觉一致性**: 所有组件遵循统一的品牌色彩、字体、间距系统
- **交互一致性**: 相同类型的交互行为在不同组件中保持一致
- **代码一致性**: 统一的 CSS 变量命名、组件 API 设计模式

### 2. 可扩展性原则 (Scalability)
- **组件变体支持**: 支持不同尺寸、状态、主题的组件变体
- **主题切换能力**: 支持深色/浅色主题无缝切换
- **国际化支持**: 支持不同语言的排版和布局适配

### 3. 可维护性原则 (Maintainability)
- **单一数据源**: 设计 tokens 作为唯一的样式定义来源
- **自动化同步**: 设计变更能够自动同步到代码实现
- **版本控制**: 设计系统版本与代码版本同步管理

## Design Tokens 实现

### 1. 核心 Design Tokens 结构

```typescript
// tokens/index.ts - Design Tokens 主入口
export interface DesignTokens {
  colors: ColorTokens;
  typography: TypographyTokens;
  spacing: SpacingTokens;
  elevation: ElevationTokens;
  borderRadius: BorderRadiusTokens;
  animation: AnimationTokens;
}

// tokens/colors.ts - 色彩系统 Tokens
export interface ColorTokens {
  // 品牌主色调
  primary: {
    900: string; // #000000 - 纯黑
    800: string; // #081727 - 深蓝黑
    700: string; // #161b25 - 深蓝灰
    500: string; // #2b3a4f - 中蓝灰
    300: string; // #c9d4dc - 浅蓝灰
    100: string; // #ffffff - 纯白
  };
  
  // 品牌强调色
  accent: {
    500: string; // #2b3a4f - 品牌强调色
    400: string; // #3d4e63 - 中等强调
    300: string; // #5a6b7d - 浅强调
    200: string; // #8a9ba8 - 极浅强调
    100: string; // #e8eef2 - 背景高亮
  };
  
  // 功能色彩
  semantic: {
    success: {
      500: string; // #28a745
      100: string; // #d4edda
    };
    warning: {
      500: string; // #ffc107
      100: string; // #fff3cd
    };
    error: {
      500: string; // #dc3545
      100: string; // #f8d7da
    };
    info: {
      500: string; // #17a2b8
      100: string; // #d1ecf1
    };
  };
  
  // 中性色彩
  neutral: {
    white: string;   // #ffffff
    gray: {
      50: string;    // #fafafa
      100: string;   // #f5f5f5
      200: string;   // #eeeeee
      300: string;   // #e0e0e0
      400: string;   // #bdbdbd
      500: string;   // #9e9e9e
      600: string;   // #757575
      700: string;   // #616161
      800: string;   // #424242
      900: string;   // #212121
    };
    black: string;   // #000000
  };
}

// tokens/typography.ts - 字体系统 Tokens
export interface TypographyTokens {
  fontFamily: {
    primary: string;   // Inter
    mono: string;      // JetBrains Mono
    chinese: string;   // PingFang SC
  };
  
  fontSize: {
    h1: string;        // 2.5rem (40px)
    h2: string;        // 2rem (32px)
    h3: string;        // 1.5rem (24px)
    h4: string;        // 1.25rem (20px)
    lg: string;        // 1.125rem (18px)
    base: string;      // 1rem (16px)
    sm: string;        // 0.875rem (14px)
    xs: string;        // 0.75rem (12px)
  };
  
  fontWeight: {
    light: number;     // 300
    normal: number;    // 400
    medium: number;    // 500
    semibold: number;  // 600
    bold: number;      // 700
  };
  
  lineHeight: {
    tight: number;     // 1.25
    normal: number;    // 1.5
    relaxed: number;   // 1.75
  };
}

// tokens/spacing.ts - 间距系统 Tokens
export interface SpacingTokens {
  1: string;   // 0.25rem (4px)
  2: string;   // 0.5rem (8px)
  3: string;   // 0.75rem (12px)
  4: string;   // 1rem (16px)
  5: string;   // 1.25rem (20px)
  6: string;   // 1.5rem (24px)
  8: string;   // 2rem (32px)
  10: string;  // 2.5rem (40px)
  12: string;  // 3rem (48px)
  16: string;  // 4rem (64px)
  20: string;  // 5rem (80px)
}
```

### 2. Tokens 到 CSS 变量的映射

```typescript
// lib/design-system/token-generator.ts
export class TokenGenerator {
  static generateCSSVariables(tokens: DesignTokens): string {
    const cssVariables: string[] = [];
    
    // 生成颜色变量
    this.generateColorVariables(tokens.colors, cssVariables);
    
    // 生成字体变量
    this.generateTypographyVariables(tokens.typography, cssVariables);
    
    // 生成间距变量
    this.generateSpacingVariables(tokens.spacing, cssVariables);
    
    return cssVariables.join('\n');
  }
  
  private static generateColorVariables(
    colors: ColorTokens, 
    cssVariables: string[]
  ): void {
    // 主色调变量
    Object.entries(colors.primary).forEach(([shade, value]) => {
      cssVariables.push(`  --color-primary-${shade}: ${value};`);
    });
    
    // 强调色变量
    Object.entries(colors.accent).forEach(([shade, value]) => {
      cssVariables.push(`  --color-accent-${shade}: ${value};`);
    });
    
    // 语义色变量
    Object.entries(colors.semantic).forEach(([semantic, shades]) => {
      Object.entries(shades).forEach(([shade, value]) => {
        cssVariables.push(`  --color-${semantic}-${shade}: ${value};`);
      });
    });
    
    // 中性色变量
    Object.entries(colors.neutral.gray).forEach(([shade, value]) => {
      cssVariables.push(`  --color-gray-${shade}: ${value};`);
    });
    
    cssVariables.push(`  --color-white: ${colors.neutral.white};`);
    cssVariables.push(`  --color-black: ${colors.neutral.black};`);
  }
  
  private static generateTypographyVariables(
    typography: TypographyTokens,
    cssVariables: string[]
  ): void {
    // 字体族
    Object.entries(typography.fontFamily).forEach(([key, value]) => {
      cssVariables.push(`  --font-family-${key}: ${value};`);
    });
    
    // 字体大小
    Object.entries(typography.fontSize).forEach(([key, value]) => {
      cssVariables.push(`  --font-size-${key}: ${value};`);
    });
    
    // 字体粗细
    Object.entries(typography.fontWeight).forEach(([key, value]) => {
      cssVariables.push(`  --font-weight-${key}: ${value};`);
    });
    
    // 行高
    Object.entries(typography.lineHeight).forEach(([key, value]) => {
      cssVariables.push(`  --line-height-${key}: ${value};`);
    });
  }
}

// 使用示例
const tokens = getDesignTokens();
const cssVariables = TokenGenerator.generateCSSVariables(tokens);

// 生成的 CSS 文件
const generatedCSS = `
:root {
${cssVariables}
}
`;
```

### 3. 主题系统实现

```typescript
// lib/design-system/theme-system.ts
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
          primary: 'var(--color-primary-100)',     // #ffffff
          secondary: '#f8f9fa',                    // 极浅灰
          elevated: 'var(--color-primary-100)',    // #ffffff
        },
        text: {
          primary: 'var(--color-primary-900)',     // #000000
          secondary: 'var(--color-primary-800)',   // #081727
          muted: 'var(--color-primary-300)',       // #c9d4dc
        },
        border: {
          default: 'var(--color-primary-300)',     // #c9d4dc
          muted: '#e9ecef',                        // 更淡的边框
        },
        interactive: {
          default: 'var(--color-primary-800)',     // #081727
          hover: 'var(--color-primary-700)',       // #161b25
          active: 'var(--color-primary-900)',      // #000000
          disabled: 'var(--color-gray-300)',       // #e0e0e0
        },
      }
    });
    
    // 深色主题
    this.registerTheme({
      name: 'dark',
      label: '深色主题',
      colors: {
        background: {
          primary: 'var(--color-primary-800)',     // #081727
          secondary: 'var(--color-primary-700)',   // #161b25
          elevated: 'var(--color-primary-500)',    // #2b3a4f
        },
        text: {
          primary: 'var(--color-primary-100)',     // #ffffff
          secondary: 'var(--color-primary-300)',   // #c9d4dc
          muted: 'var(--color-primary-500)',       // #2b3a4f
        },
        border: {
          default: 'var(--color-primary-500)',     // #2b3a4f
          muted: 'var(--color-primary-700)',       // #161b25
        },
        interactive: {
          default: 'var(--color-accent-500)',      // #2b3a4f
          hover: 'var(--color-accent-400)',        // #3d4e63
          active: 'var(--color-accent-300)',       // #5a6b7d
          disabled: 'var(--color-gray-600)',       // #757575
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
    
    // 触发主题变更事件
    window.dispatchEvent(new CustomEvent('theme-changed', {
      detail: { theme: theme.name }
    }));
  }
  
  getCurrentTheme(): string {
    return this.currentTheme;
  }
  
  getAvailableThemes(): ThemeConfig[] {
    return Array.from(this.themes.values());
  }
}

// React Hook for theme management
export function useTheme() {
  const [currentTheme, setCurrentTheme] = useState<string>('light');
  const [availableThemes, setAvailableThemes] = useState<ThemeConfig[]>([]);
  
  useEffect(() => {
    const themeManager = getThemeManager();
    setCurrentTheme(themeManager.getCurrentTheme());
    setAvailableThemes(themeManager.getAvailableThemes());
    
    const handleThemeChange = (event: CustomEvent) => {
      setCurrentTheme(event.detail.theme);
    };
    
    window.addEventListener('theme-changed', handleThemeChange as EventListener);
    
    return () => {
      window.removeEventListener('theme-changed', handleThemeChange as EventListener);
    };
  }, []);
  
  const changeTheme = useCallback((themeName: string) => {
    const themeManager = getThemeManager();
    themeManager.setTheme(themeName);
  }, []);
  
  return {
    currentTheme,
    availableThemes,
    changeTheme,
  };
}
```

## 组件系统集成

### 1. 基础组件设计模式

```typescript
// components/ui/base/BaseComponent.tsx
export interface BaseComponentProps {
  className?: string;
  variant?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  theme?: 'light' | 'dark' | 'auto';
  disabled?: boolean;
  children?: React.ReactNode;
}

export interface ComponentVariants {
  [key: string]: {
    [key: string]: string; // CSS classes or styles
  };
}

// 组件变体生成器
export class VariantGenerator {
  static generateVariants(
    baseClass: string,
    variants: ComponentVariants
  ): Record<string, Record<string, string>> {
    const result: Record<string, Record<string, string>> = {};
    
    Object.entries(variants).forEach(([variantType, options]) => {
      result[variantType] = {};
      Object.entries(options).forEach(([option, classes]) => {
        result[variantType][option] = `${baseClass} ${classes}`;
      });
    });
    
    return result;
  }
}

// components/ui/Button/Button.tsx
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

// 使用 CVA 定义按钮变体
const buttonVariants = cva(
  // 基础样式
  [
    'inline-flex items-center justify-center',
    'font-medium transition-all duration-200',
    'focus-visible:outline-none focus-visible:ring-2',
    'disabled:pointer-events-none disabled:opacity-50',
    'border border-transparent',
  ],
  {
    variants: {
      // 按钮类型变体
      variant: {
        primary: [
          'bg-[--theme-interactive-default] text-[--theme-text-primary]',
          'hover:bg-[--theme-interactive-hover]',
          'active:bg-[--theme-interactive-active]',
          'focus-visible:ring-[--theme-interactive-default]',
        ],
        secondary: [
          'bg-transparent text-[--theme-interactive-default]',
          'border-[--theme-border-default]',
          'hover:bg-[--theme-background-secondary]',
          'focus-visible:ring-[--theme-interactive-default]',
        ],
        ghost: [
          'bg-transparent text-[--theme-text-secondary]',
          'hover:bg-[--theme-background-secondary]',
          'hover:text-[--theme-text-primary]',
        ],
        danger: [
          'bg-[--color-error-500] text-white',
          'hover:bg-red-600',
          'focus-visible:ring-red-500',
        ],
      },
      
      // 尺寸变体
      size: {
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 text-base',
        lg: 'h-12 px-6 text-lg',
        xl: 'h-14 px-8 text-xl',
      },
      
      // 圆角变体
      radius: {
        none: 'rounded-none',
        sm: 'rounded-sm',
        md: 'rounded-md',
        lg: 'rounded-lg',
        full: 'rounded-full',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
      radius: 'md',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    className, 
    variant, 
    size, 
    radius,
    asChild = false, 
    loading = false,
    icon,
    iconPosition = 'left',
    disabled,
    children,
    ...props 
  }, ref) => {
    const Comp = asChild ? Slot : 'button';
    
    const isDisabled = disabled || loading;
    
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, radius, className }))}
        ref={ref}
        disabled={isDisabled}
        {...props}
      >
        {loading && (
          <LoadingSpinner 
            size={size === 'sm' ? 'xs' : 'sm'} 
            className={cn(
              'animate-spin',
              children && (iconPosition === 'left' ? 'mr-2' : 'ml-2')
            )}
          />
        )}
        
        {!loading && icon && iconPosition === 'left' && (
          <span className={cn('flex items-center', children && 'mr-2')}>
            {icon}
          </span>
        )}
        
        {children}
        
        {!loading && icon && iconPosition === 'right' && (
          <span className={cn('flex items-center', children && 'ml-2')}>
            {icon}
          </span>
        )}
      </Comp>
    );
  }
);

Button.displayName = 'Button';
```

### 2. 复合组件设计模式

```typescript
// components/ui/Card/Card.tsx
import { cn } from '@/lib/utils';
import { cva, type VariantProps } from 'class-variance-authority';

const cardVariants = cva(
  [
    'rounded-lg border transition-all duration-200',
    'bg-[--theme-background-primary]',
    'border-[--theme-border-default]',
  ],
  {
    variants: {
      variant: {
        default: 'shadow-sm hover:shadow-md',
        elevated: 'shadow-md hover:shadow-lg',
        outlined: 'border-2 shadow-none',
        ghost: 'border-none shadow-none bg-transparent',
      },
      padding: {
        none: 'p-0',
        sm: 'p-4',
        md: 'p-6',
        lg: 'p-8',
      },
      interactive: {
        true: 'cursor-pointer hover:bg-[--theme-background-secondary] hover:border-[--theme-interactive-default]',
        false: '',
      },
    },
    defaultVariants: {
      variant: 'default',
      padding: 'md',
      interactive: false,
    },
  }
);

export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant, padding, interactive, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(cardVariants({ variant, padding, interactive }), className)}
      {...props}
    />
  )
);

// Card Header
export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {}

const CardHeader = React.forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'flex flex-col space-y-1.5 pb-4',
        'border-b border-[--theme-border-muted]',
        className
      )}
      {...props}
    />
  )
);

// Card Title
export interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  as?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
}

const CardTitle = React.forwardRef<HTMLHeadingElement, CardTitleProps>(
  ({ className, as: Comp = 'h3', ...props }, ref) => (
    <Comp
      ref={ref as any}
      className={cn(
        'text-[--font-size-h4] font-[--font-weight-semibold]',
        'text-[--theme-text-primary] leading-none tracking-tight',
        className
      )}
      {...props}
    />
  )
);

// Card Description
export interface CardDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {}

const CardDescription = React.forwardRef<HTMLParagraphElement, CardDescriptionProps>(
  ({ className, ...props }, ref) => (
    <p
      ref={ref}
      className={cn(
        'text-[--font-size-sm] text-[--theme-text-secondary]',
        className
      )}
      {...props}
    />
  )
);

// Card Content
export interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {}

const CardContent = React.forwardRef<HTMLDivElement, CardContentProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('text-[--theme-text-secondary]', className)}
      {...props}
    />
  )
);

// Card Footer
export interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {}

const CardFooter = React.forwardRef<HTMLDivElement, CardFooterProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'flex items-center pt-4',
        'border-t border-[--theme-border-muted]',
        className
      )}
      {...props}
    />
  )
);

Card.displayName = 'Card';
CardHeader.displayName = 'CardHeader';
CardTitle.displayName = 'CardTitle';
CardDescription.displayName = 'CardDescription';
CardContent.displayName = 'CardContent';
CardFooter.displayName = 'CardFooter';

export {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
};

// 使用示例
const ExampleUsage = () => (
  <Card variant="elevated" interactive>
    <CardHeader>
      <CardTitle>代码助手</CardTitle>
      <CardDescription>专业的编程和代码审查助手</CardDescription>
    </CardHeader>
    <CardContent>
      <p>能够帮助您生成代码、进行代码审查、调试问题和编写文档。</p>
    </CardContent>
    <CardFooter>
      <Button variant="primary" size="sm">
        开始对话
      </Button>
    </CardFooter>
  </Card>
);
```

### 3. 专业组件实现

```typescript
// components/features/chat/MessageBubble/MessageBubble.tsx
import { cn } from '@/lib/utils';
import { cva, type VariantProps } from 'class-variance-authority';
import { Avatar } from '@/components/ui/Avatar';
import { formatMessageTime } from '@/lib/utils/date';

const messageBubbleVariants = cva(
  [
    'group relative max-w-[80%] rounded-lg px-4 py-3',
    'transition-all duration-200',
  ],
  {
    variants: {
      sender: {
        user: [
          'ml-auto bg-[--theme-interactive-default]',
          'text-[--theme-text-primary]',
          'rounded-br-sm',
        ],
        agent: [
          'mr-auto bg-[--theme-background-secondary]',
          'text-[--theme-text-primary]',
          'border border-[--theme-border-default]',
          'rounded-bl-sm',
        ],
        system: [
          'mx-auto bg-[--color-info-100]',
          'text-[--color-info-500]',
          'text-center text-sm',
          'rounded-full px-6 py-2',
        ],
      },
      status: {
        sending: 'opacity-70',
        sent: 'opacity-100',
        failed: 'opacity-50 border-[--color-error-500]',
      },
    },
    defaultVariants: {
      sender: 'user',
      status: 'sent',
    },
  }
);

export interface MessageBubbleProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof messageBubbleVariants> {
  message: Message;
  showAvatar?: boolean;
  showTimestamp?: boolean;
  onRetry?: () => void;
}

export const MessageBubble = React.forwardRef<HTMLDivElement, MessageBubbleProps>(
  ({ 
    className, 
    message,
    sender,
    status,
    showAvatar = true,
    showTimestamp = true,
    onRetry,
    ...props 
  }, ref) => {
    const isUser = message.sender_type === 'user';
    const isAgent = message.sender_type === 'agent';
    const isSystem = message.sender_type === 'system';
    
    const currentSender = isUser ? 'user' : isAgent ? 'agent' : 'system';
    const currentStatus = message.status === 'failed' ? 'failed' : 
                         message.status === 'sending' ? 'sending' : 'sent';
    
    return (
      <div
        ref={ref}
        className={cn(
          'flex items-end gap-2 mb-4',
          isUser && 'flex-row-reverse',
          className
        )}
        {...props}
      >
        {/* Avatar */}
        {showAvatar && !isSystem && (
          <Avatar
            src={message.sender_avatar}
            alt={message.sender_name}
            size="sm"
            className={cn(
              'flex-shrink-0',
              isUser && 'order-last',
            )}
          />
        )}
        
        {/* Message Content */}
        <div className={cn('flex flex-col', isUser && 'items-end')}>
          {/* Sender Name */}
          {!isUser && !isSystem && (
            <div className="mb-1 text-xs text-[--theme-text-muted] px-1">
              {message.sender_name}
            </div>
          )}
          
          {/* Message Bubble */}
          <div
            className={cn(
              messageBubbleVariants({ 
                sender: currentSender, 
                status: currentStatus 
              })
            )}
          >
            {/* Message Content */}
            <MessageContent content={message.content} type={message.message_type} />
            
            {/* Retry Button for Failed Messages */}
            {currentStatus === 'failed' && onRetry && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onRetry}
                className="mt-2 text-xs"
              >
                重试发送
              </Button>
            )}
          </div>
          
          {/* Timestamp and Status */}
          {showTimestamp && (
            <div className={cn(
              'mt-1 text-xs text-[--theme-text-muted] px-1',
              'opacity-0 group-hover:opacity-100 transition-opacity',
              isUser && 'text-right'
            )}>
              {formatMessageTime(message.created_at)}
              {currentStatus === 'sending' && (
                <span className="ml-1">发送中...</span>
              )}
              {currentStatus === 'failed' && (
                <span className="ml-1 text-[--color-error-500]">发送失败</span>
              )}
            </div>
          )}
        </div>
      </div>
    );
  }
);

MessageBubble.displayName = 'MessageBubble';

// Message Content Component
interface MessageContentProps {
  content: string;
  type: 'text' | 'image' | 'file' | 'code' | 'system';
}

const MessageContent: React.FC<MessageContentProps> = ({ content, type }) => {
  switch (type) {
    case 'code':
      return (
        <pre className={cn(
          'bg-[--theme-background-elevated] rounded p-3',
          'text-sm font-mono overflow-x-auto',
          'border border-[--theme-border-muted]'
        )}>
          <code>{content}</code>
        </pre>
      );
      
    case 'image':
      return (
        <img
          src={content}
          alt="Message attachment"
          className="max-w-full rounded"
          loading="lazy"
        />
      );
      
    case 'file':
      return (
        <div className={cn(
          'flex items-center gap-2 p-2',
          'bg-[--theme-background-elevated] rounded',
          'border border-[--theme-border-muted]'
        )}>
          <FileIcon className="w-4 h-4" />
          <span className="text-sm">{content}</span>
        </div>
      );
      
    default:
      return (
        <div className="prose prose-sm max-w-none">
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              code: ({ node, inline, className, children, ...props }) => {
                if (inline) {
                  return (
                    <code
                      className={cn(
                        'bg-[--theme-background-elevated] px-1 py-0.5 rounded text-sm',
                        className
                      )}
                      {...props}
                    >
                      {children}
                    </code>
                  );
                }
                return (
                  <pre className={cn(
                    'bg-[--theme-background-elevated] rounded p-3',
                    'text-sm font-mono overflow-x-auto',
                    'border border-[--theme-border-muted]',
                    className
                  )}>
                    <code {...props}>{children}</code>
                  </pre>
                );
              },
            }}
          >
            {content}
          </ReactMarkdown>
        </div>
      );
  }
};
```

## 响应式设计集成

### 1. 断点系统

```typescript
// lib/design-system/breakpoints.ts
export const breakpoints = {
  xs: '320px',
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

export type Breakpoint = keyof typeof breakpoints;

// Tailwind配置中的断点
export const tailwindBreakpoints = {
  screens: {
    'xs': '320px',
    'sm': '640px',
    'md': '768px',
    'lg': '1024px',
    'xl': '1280px',
    '2xl': '1536px',
  },
};

// 响应式工具类
export class ResponsiveUtils {
  static getBreakpointValue(breakpoint: Breakpoint): number {
    return parseInt(breakpoints[breakpoint].replace('px', ''));
  }
  
  static isBreakpointActive(breakpoint: Breakpoint): boolean {
    if (typeof window === 'undefined') return false;
    
    const breakpointValue = this.getBreakpointValue(breakpoint);
    return window.innerWidth >= breakpointValue;
  }
  
  static useBreakpoint(breakpoint: Breakpoint): boolean {
    const [isActive, setIsActive] = useState(false);
    
    useEffect(() => {
      const checkBreakpoint = () => {
        setIsActive(this.isBreakpointActive(breakpoint));
      };
      
      checkBreakpoint();
      window.addEventListener('resize', checkBreakpoint);
      
      return () => window.removeEventListener('resize', checkBreakpoint);
    }, [breakpoint]);
    
    return isActive;
  }
}

// 响应式Hook
export function useResponsive() {
  const [screenSize, setScreenSize] = useState({
    width: 0,
    height: 0,
    breakpoint: 'xs' as Breakpoint,
  });
  
  useEffect(() => {
    const updateScreenSize = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      
      let breakpoint: Breakpoint = 'xs';
      
      if (width >= ResponsiveUtils.getBreakpointValue('2xl')) {
        breakpoint = '2xl';
      } else if (width >= ResponsiveUtils.getBreakpointValue('xl')) {
        breakpoint = 'xl';
      } else if (width >= ResponsiveUtils.getBreakpointValue('lg')) {
        breakpoint = 'lg';
      } else if (width >= ResponsiveUtils.getBreakpointValue('md')) {
        breakpoint = 'md';
      } else if (width >= ResponsiveUtils.getBreakpointValue('sm')) {
        breakpoint = 'sm';
      }
      
      setScreenSize({ width, height, breakpoint });
    };
    
    updateScreenSize();
    window.addEventListener('resize', updateScreenSize);
    
    return () => window.removeEventListener('resize', updateScreenSize);
  }, []);
  
  return {
    ...screenSize,
    isMobile: screenSize.breakpoint === 'xs' || screenSize.breakpoint === 'sm',
    isTablet: screenSize.breakpoint === 'md',
    isDesktop: screenSize.breakpoint === 'lg' || screenSize.breakpoint === 'xl' || screenSize.breakpoint === '2xl',
    isXs: screenSize.breakpoint === 'xs',
    isSm: screenSize.breakpoint === 'sm',
    isMd: screenSize.breakpoint === 'md',
    isLg: screenSize.breakpoint === 'lg',
    isXl: screenSize.breakpoint === 'xl',
    is2xl: screenSize.breakpoint === '2xl',
  };
}
```

### 2. 三栏布局响应式实现

```typescript
// components/layout/MainLayout/MainLayout.tsx
import { cn } from '@/lib/utils';
import { useResponsive } from '@/lib/design-system/breakpoints';
import { useState, useEffect } from 'react';

export interface MainLayoutProps {
  children: React.ReactNode;
  sidebarContent?: React.ReactNode;
  middlePanelContent?: React.ReactNode;
  showSidebar?: boolean;
  showMiddlePanel?: boolean;
}

export const MainLayout: React.FC<MainLayoutProps> = ({
  children,
  sidebarContent,
  middlePanelContent,
  showSidebar = true,
  showMiddlePanel = true,
}) => {
  const responsive = useResponsive();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [middlePanelCollapsed, setMiddlePanelCollapsed] = useState(false);
  
  // 响应式自动调整
  useEffect(() => {
    if (responsive.isMobile) {
      // 移动端：隐藏侧边栏和中间面板，使用底部导航
      setSidebarCollapsed(true);
      setMiddlePanelCollapsed(true);
    } else if (responsive.isTablet) {
      // 平板端：保持侧边栏，根据需要折叠中间面板
      setSidebarCollapsed(false);
      setMiddlePanelCollapsed(!showMiddlePanel);
    } else {
      // 桌面端：显示所有面板
      setSidebarCollapsed(false);
      setMiddlePanelCollapsed(false);
    }
  }, [responsive.breakpoint, showMiddlePanel]);
  
  return (
    <div className={cn(
      'flex h-screen bg-[--theme-background-primary]',
      'overflow-hidden relative'
    )}>
      {/* 左侧边栏 */}
      {showSidebar && (
        <>
          {/* 桌面端侧边栏 */}
          <aside
            className={cn(
              'hidden md:flex flex-col',
              'bg-[--theme-background-primary]',
              'border-r border-[--theme-border-default]',
              'transition-all duration-300',
              sidebarCollapsed ? 'w-16' : 'w-20 lg:w-24',
              'shadow-sm z-30'
            )}
          >
            {sidebarContent}
          </aside>
          
          {/* 移动端底部导航 */}
          <nav className={cn(
            'md:hidden fixed bottom-0 left-0 right-0 z-50',
            'bg-[--theme-background-primary]',
            'border-t border-[--theme-border-default]',
            'px-2 py-1 shadow-lg'
          )}>
            {sidebarContent}
          </nav>
        </>
      )}
      
      {/* 中间面板 */}
      {showMiddlePanel && !middlePanelCollapsed && (
        <div
          className={cn(
            'hidden sm:flex flex-col',
            'bg-[--theme-background-primary]',
            'border-r border-[--theme-border-default]',
            'transition-all duration-300',
            responsive.isMobile ? 'w-0' : 
            responsive.isTablet ? 'w-64' : 'w-80 lg:w-96',
            'shadow-sm z-20'
          )}
        >
          {middlePanelContent}
        </div>
      )}
      
      {/* 主内容区域 */}
      <main
        className={cn(
          'flex-1 flex flex-col',
          'bg-[--theme-background-primary]',
          'overflow-hidden relative',
          responsive.isMobile && 'mb-16' // 为底部导航留空间
        )}
      >
        {children}
      </main>
      
      {/* 移动端遮罩层（当侧边栏或中间面板展开时） */}
      {responsive.isMobile && (!sidebarCollapsed || !middlePanelCollapsed) && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => {
            setSidebarCollapsed(true);
            setMiddlePanelCollapsed(true);
          }}
        />
      )}
    </div>
  );
};

// 响应式侧边栏组件
export const ResponsiveSidebar: React.FC<{
  children: React.ReactNode;
  collapsed?: boolean;
}> = ({ children, collapsed = false }) => {
  const responsive = useResponsive();
  
  if (responsive.isMobile) {
    // 移动端渲染为底部导航
    return (
      <div className="flex justify-around items-center h-14">
        {children}
      </div>
    );
  }
  
  // 桌面端渲染为侧边栏
  return (
    <div className={cn(
      'flex flex-col items-center py-4 space-y-2',
      'h-full overflow-y-auto'
    )}>
      {children}
    </div>
  );
};

// 响应式中间面板组件
export const ResponsiveMiddlePanel: React.FC<{
  children: React.ReactNode;
  title?: string;
}> = ({ children, title }) => {
  const responsive = useResponsive();
  
  return (
    <div className="flex flex-col h-full">
      {/* 面板头部 */}
      {title && (
        <header className={cn(
          'flex items-center justify-between',
          'px-4 py-3 border-b border-[--theme-border-default]',
          'bg-[--theme-background-primary]'
        )}>
          <h2 className="text-lg font-semibold text-[--theme-text-primary]">
            {title}
          </h2>
          
          {/* 响应式控制按钮 */}
          {responsive.isTablet && (
            <Button
              variant="ghost"
              size="sm"
              className="md:hidden"
            >
              <ChevronLeftIcon className="w-4 h-4" />
            </Button>
          )}
        </header>
      )}
      
      {/* 面板内容 */}
      <div className="flex-1 overflow-y-auto">
        {children}
      </div>
    </div>
  );
};
```

## 国际化集成

### 1. 设计系统国际化支持

```typescript
// lib/design-system/i18n-integration.ts
export interface I18nDesignTokens {
  fontFamily: {
    [locale: string]: string;
  };
  textDirection: {
    [locale: string]: 'ltr' | 'rtl';
  };
  spacing: {
    [locale: string]: {
      text: number; // 文字间距调整
      line: number; // 行间距调整
    };
  };
}

export const i18nDesignTokens: I18nDesignTokens = {
  fontFamily: {
    'en': 'var(--font-family-primary)', // Inter
    'zh-CN': 'var(--font-family-chinese), var(--font-family-primary)', // PingFang SC, Inter
    'zh-TW': 'var(--font-family-chinese), var(--font-family-primary)',
    'ja': '"Hiragino Sans", "Yu Gothic", var(--font-family-primary)',
    'ko': '"Malgun Gothic", var(--font-family-primary)',
    'ar': '"Noto Sans Arabic", var(--font-family-primary)',
  },
  textDirection: {
    'en': 'ltr',
    'zh-CN': 'ltr',
    'zh-TW': 'ltr',
    'ja': 'ltr',
    'ko': 'ltr',
    'ar': 'rtl',
  },
  spacing: {
    'en': { text: 1, line: 1 },
    'zh-CN': { text: 1.05, line: 1.1 }, // 中文需要稍大的间距
    'zh-TW': { text: 1.05, line: 1.1 },
    'ja': { text: 1.02, line: 1.05 },
    'ko': { text: 1.02, line: 1.05 },
    'ar': { text: 1, line: 1.1 },
  },
};

// 国际化主题管理器
export class I18nThemeManager {
  private currentLocale: string = 'en';
  
  setLocale(locale: string): void {
    this.currentLocale = locale;
    this.applyLocaleStyles(locale);
  }
  
  private applyLocaleStyles(locale: string): void {
    const root = document.documentElement;
    const tokens = i18nDesignTokens;
    
    // 应用字体
    const fontFamily = tokens.fontFamily[locale] || tokens.fontFamily['en'];
    root.style.setProperty('--font-family-localized', fontFamily);
    
    // 应用文字方向
    const direction = tokens.textDirection[locale] || 'ltr';
    root.setAttribute('dir', direction);
    root.style.setProperty('--text-direction', direction);
    
    // 应用间距调整
    const spacing = tokens.spacing[locale] || tokens.spacing['en'];
    root.style.setProperty('--text-spacing-multiplier', spacing.text.toString());
    root.style.setProperty('--line-spacing-multiplier', spacing.line.toString());
    
    // 触发本地化变更事件
    window.dispatchEvent(new CustomEvent('locale-changed', {
      detail: { locale, direction }
    }));
  }
  
  getCurrentLocale(): string {
    return this.currentLocale;
  }
  
  isRTL(): boolean {
    return i18nDesignTokens.textDirection[this.currentLocale] === 'rtl';
  }
}

// React Hook for I18n theme
export function useI18nTheme() {
  const [locale, setLocale] = useState('en');
  const [direction, setDirection] = useState<'ltr' | 'rtl'>('ltr');
  
  useEffect(() => {
    const themeManager = getI18nThemeManager();
    setLocale(themeManager.getCurrentLocale());
    setDirection(themeManager.isRTL() ? 'rtl' : 'ltr');
    
    const handleLocaleChange = (event: CustomEvent) => {
      setLocale(event.detail.locale);
      setDirection(event.detail.direction);
    };
    
    window.addEventListener('locale-changed', handleLocaleChange as EventListener);
    
    return () => {
      window.removeEventListener('locale-changed', handleLocaleChange as EventListener);
    };
  }, []);
  
  const changeLocale = useCallback((newLocale: string) => {
    const themeManager = getI18nThemeManager();
    themeManager.setLocale(newLocale);
  }, []);
  
  return {
    locale,
    direction,
    isRTL: direction === 'rtl',
    changeLocale,
  };
}
```

### 2. RTL 支持组件

```typescript
// components/ui/RTLSupport/RTLWrapper.tsx
export interface RTLWrapperProps {
  children: React.ReactNode;
  className?: string;
}

export const RTLWrapper: React.FC<RTLWrapperProps> = ({
  children,
  className,
}) => {
  const { isRTL } = useI18nTheme();
  
  return (
    <div
      className={cn(
        'transition-all duration-300',
        isRTL && 'rtl-support',
        className
      )}
      dir={isRTL ? 'rtl' : 'ltr'}
    >
      {children}
    </div>
  );
};

// RTL 适配的 Flexbox 工具类
export const rtlFlexUtils = {
  'flex-row-rtl': 'flex-row rtl:flex-row-reverse',
  'ml-auto-rtl': 'ml-auto rtl:ml-0 rtl:mr-auto',
  'mr-auto-rtl': 'mr-auto rtl:mr-0 rtl:ml-auto',
  'pl-4-rtl': 'pl-4 rtl:pl-0 rtl:pr-4',
  'pr-4-rtl': 'pr-4 rtl:pr-0 rtl:pl-4',
  'border-l-rtl': 'border-l rtl:border-l-0 rtl:border-r',
  'border-r-rtl': 'border-r rtl:border-r-0 rtl:border-l',
  'rounded-l-rtl': 'rounded-l rtl:rounded-l-none rtl:rounded-r',
  'rounded-r-rtl': 'rounded-r rtl:rounded-r-none rtl:rounded-l',
};

// RTL 适配的消息气泡组件
const RTLMessageBubble = React.forwardRef<HTMLDivElement, MessageBubbleProps>(
  ({ message, className, ...props }, ref) => {
    const { isRTL } = useI18nTheme();
    const isUser = message.sender_type === 'user';
    
    return (
      <div
        ref={ref}
        className={cn(
          'flex items-end gap-2 mb-4',
          // RTL 适配
          isUser && !isRTL && 'flex-row-reverse',
          isUser && isRTL && 'flex-row',
          !isUser && isRTL && 'flex-row-reverse',
          className
        )}
        {...props}
      >
        {/* 消息内容和其他元素 */}
      </div>
    );
  }
);
```

## 性能优化集成

### 1. 组件懒加载

```typescript
// lib/design-system/lazy-loading.ts
export function createLazyComponent<T extends React.ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>,
  fallback?: React.ComponentType
): React.LazyExoticComponent<T> {
  const LazyComponent = React.lazy(importFunc);
  
  // 预加载组件
  const preload = () => importFunc();
  
  // 附加预加载方法到组件
  (LazyComponent as any).preload = preload;
  
  return LazyComponent;
}

// 预加载 Hook
export function usePreloadComponent(
  lazyComponent: React.LazyExoticComponent<any> & { preload?: () => void }
): void {
  useEffect(() => {
    // 在空闲时预加载组件
    if ('requestIdleCallback' in window) {
      requestIdleCallback(() => {
        lazyComponent.preload?.();
      });
    } else {
      // 兜底方案
      setTimeout(() => {
        lazyComponent.preload?.();
      }, 100);
    }
  }, [lazyComponent]);
}

// 懒加载的设计系统组件
export const LazyComponents = {
  // 复杂组件懒加载
  DataTable: createLazyComponent(
    () => import('@/components/ui/DataTable/DataTable')
  ),
  
  RichTextEditor: createLazyComponent(
    () => import('@/components/ui/RichTextEditor/RichTextEditor')
  ),
  
  FileUploader: createLazyComponent(
    () => import('@/components/ui/FileUploader/FileUploader')
  ),
  
  ColorPicker: createLazyComponent(
    () => import('@/components/ui/ColorPicker/ColorPicker')
  ),
};

// Suspense 包装器组件
export const LazyComponentWrapper: React.FC<{
  children: React.ReactNode;
  fallback?: React.ReactNode;
}> = ({ 
  children, 
  fallback = <ComponentLoadingSkeleton /> 
}) => (
  <Suspense fallback={fallback}>
    {children}
  </Suspense>
);

// 组件加载骨架屏
const ComponentLoadingSkeleton: React.FC = () => (
  <div className="animate-pulse">
    <div className="h-4 bg-[--theme-background-secondary] rounded mb-2"></div>
    <div className="h-4 bg-[--theme-background-secondary] rounded w-3/4 mb-2"></div>
    <div className="h-8 bg-[--theme-background-secondary] rounded"></div>
  </div>
);
```

### 2. 主题切换优化

```typescript
// lib/design-system/theme-optimization.ts
export class OptimizedThemeManager extends ThemeManager {
  private transitionTimeout: NodeJS.Timeout | null = null;
  private isTransitioning = false;
  
  setTheme(themeName: string): void {
    if (this.isTransitioning) return;
    
    this.isTransitioning = true;
    
    // 添加过渡类
    document.documentElement.classList.add('theme-transitioning');
    
    // 应用新主题
    super.setTheme(themeName);
    
    // 清除过渡类
    if (this.transitionTimeout) {
      clearTimeout(this.transitionTimeout);
    }
    
    this.transitionTimeout = setTimeout(() => {
      document.documentElement.classList.remove('theme-transitioning');
      this.isTransitioning = false;
    }, 300); // 与 CSS 过渡时间匹配
  }
  
  // 预加载主题资源
  preloadTheme(themeName: string): void {
    const theme = this.themes.get(themeName);
    if (!theme) return;
    
    // 创建隐藏的样式元素来预加载主题
    const style = document.createElement('style');
    style.textContent = this.generateThemeCSS(theme);
    style.setAttribute('data-theme-preload', themeName);
    document.head.appendChild(style);
    
    // 一段时间后移除预加载样式
    setTimeout(() => {
      document.head.removeChild(style);
    }, 5000);
  }
  
  private generateThemeCSS(theme: ThemeConfig): string {
    // 生成主题对应的 CSS
    return Object.entries(theme.colors)
      .flatMap(([category, colors]) =>
        Object.entries(colors).map(([key, value]) =>
          `[data-theme="${theme.name}"] { --theme-${category}-${key}: ${value}; }`
        )
      )
      .join('\n');
  }
}

// 主题切换 CSS 优化
const themeTransitionCSS = `
/* 主题切换时的过渡效果 */
:root {
  --theme-transition-duration: 300ms;
  --theme-transition-easing: cubic-bezier(0.4, 0, 0.2, 1);
}

/* 需要过渡的属性 */
.theme-transitioning *,
.theme-transitioning *::before,
.theme-transitioning *::after {
  transition-property: 
    background-color, 
    border-color, 
    color, 
    fill, 
    stroke, 
    box-shadow !important;
  transition-duration: var(--theme-transition-duration) !important;
  transition-timing-function: var(--theme-transition-easing) !important;
}

/* 避免某些元素的过渡 */
.theme-transitioning .no-theme-transition,
.theme-transitioning .no-theme-transition *,
.theme-transitioning video,
.theme-transitioning iframe,
.theme-transitioning object,
.theme-transitioning embed {
  transition: none !important;
}
`;
```

## 测试集成

### 1. 设计系统测试工具

```typescript
// lib/design-system/testing-utils.ts
export interface ComponentTestUtils {
  renderWithTheme: (
    component: React.ReactElement,
    theme?: string
  ) => RenderResult;
  
  renderWithI18n: (
    component: React.ReactElement,
    locale?: string
  ) => RenderResult;
  
  renderWithResponsive: (
    component: React.ReactElement,
    breakpoint?: Breakpoint
  ) => RenderResult;
}

export const createTestUtils = (): ComponentTestUtils => {
  const renderWithTheme = (
    component: React.ReactElement,
    theme: string = 'light'
  ) => {
    const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
      <ThemeProvider defaultTheme={theme}>
        <div data-theme={theme}>
          {children}
        </div>
      </ThemeProvider>
    );
    
    return render(component, { wrapper: TestWrapper });
  };
  
  const renderWithI18n = (
    component: React.ReactElement,
    locale: string = 'en'
  ) => {
    const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
      <I18nProvider locale={locale}>
        <div dir={i18nDesignTokens.textDirection[locale] || 'ltr'}>
          {children}
        </div>
      </I18nProvider>
    );
    
    return render(component, { wrapper: TestWrapper });
  };
  
  const renderWithResponsive = (
    component: React.ReactElement,
    breakpoint: Breakpoint = 'lg'
  ) => {
    // 模拟屏幕尺寸
    const width = ResponsiveUtils.getBreakpointValue(breakpoint);
    
    // 设置视口大小
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: width,
    });
    
    // 触发 resize 事件
    window.dispatchEvent(new Event('resize'));
    
    return render(component);
  };
  
  return {
    renderWithTheme,
    renderWithI18n,
    renderWithResponsive,
  };
};

// 设计系统测试套件
export const designSystemTestSuite = {
  // 测试所有主题变体
  testAllThemes: (
    componentFactory: () => React.ReactElement,
    testFn: (result: RenderResult) => void
  ) => {
    const themes = ['light', 'dark'];
    const testUtils = createTestUtils();
    
    themes.forEach(theme => {
      it(`renders correctly in ${theme} theme`, () => {
        const result = testUtils.renderWithTheme(componentFactory(), theme);
        testFn(result);
      });
    });
  },
  
  // 测试所有断点
  testAllBreakpoints: (
    componentFactory: () => React.ReactElement,
    testFn: (result: RenderResult, breakpoint: Breakpoint) => void
  ) => {
    const breakpoints: Breakpoint[] = ['xs', 'sm', 'md', 'lg', 'xl', '2xl'];
    const testUtils = createTestUtils();
    
    breakpoints.forEach(breakpoint => {
      it(`renders correctly at ${breakpoint} breakpoint`, () => {
        const result = testUtils.renderWithResponsive(componentFactory(), breakpoint);
        testFn(result, breakpoint);
      });
    });
  },
  
  // 测试可访问性
  testAccessibility: async (component: React.ReactElement) => {
    const testUtils = createTestUtils();
    const { container } = testUtils.renderWithTheme(component);
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  },
};
```

### 2. Visual Regression Testing

```typescript
// .storybook/test-runner.ts
import type { TestRunnerConfig } from '@storybook/test-runner';
import { toMatchImageSnapshot } from 'jest-image-snapshot';

const config: TestRunnerConfig = {
  setup() {
    expect.extend({ toMatchImageSnapshot });
  },
  
  async postRender(page, context) {
    const { id, title } = context;
    
    // 等待所有动画完成
    await page.waitForTimeout(500);
    
    // 截图测试
    const screenshot = await page.screenshot({
      fullPage: true,
      animations: 'disabled',
    });
    
    expect(screenshot).toMatchImageSnapshot({
      customSnapshotIdentifier: `${title}-${id}`,
      threshold: 0.2,
      comparisonMethod: 'pixelmatch',
    });
  },
};

export default config;

// 主题特定的视觉测试
export const themeVisualTests = {
  testThemeConsistency: async (page: Page, storyId: string) => {
    const themes = ['light', 'dark'];
    
    for (const theme of themes) {
      // 切换主题
      await page.evaluate((themeName) => {
        const themeManager = window.__THEME_MANAGER__;
        themeManager?.setTheme(themeName);
      }, theme);
      
      // 等待主题应用
      await page.waitForTimeout(300);
      
      // 截图
      const screenshot = await page.screenshot({
        animations: 'disabled',
      });
      
      expect(screenshot).toMatchImageSnapshot({
        customSnapshotIdentifier: `${storyId}-${theme}`,
        threshold: 0.1,
      });
    }
  },
};
```

---

**设计系统集成版本**: v1.0  
**最后更新**: 2025-01-08  
**下次审查**: 设计系统更新时同步审查  

这个设计系统集成方案提供了：

1. **完整的 Design Tokens 系统**: 从设计规范到代码实现的无缝转换
2. **主题系统**: 支持多主题切换和自定义主题
3. **组件系统**: 统一的组件设计模式和变体管理
4. **响应式设计**: 完整的断点系统和自适应布局
5. **国际化支持**: 多语言和 RTL 布局支持
6. **性能优化**: 懒加载、预加载和优化的主题切换
7. **测试集成**: 完整的测试工具和视觉回归测试

这个集成方案将确保 Connet.AI 的设计系统在前端实现中得到完美体现。