# Connet.AI Design System

## 📋 概述

Connet.AI 设计系统为我们的 AI 协作平台提供统一的视觉语言和交互标准。本系统遵循现代化、社交化的设计理念，旨在创造直观、高效的用户体验。

---

## 🎨 品牌标识

### Logo 设计原则

- **简洁性**：清晰识别，适配各种尺寸和应用场景
- **科技感**：体现 AI 技术的创新性和前瞻性
- **连接性**：视觉化表达人机协作和智能体连接的概念
- **专业性**：建立可信赖的企业形象

### Logo 应用规范

```
最小使用尺寸：
- 数字媒体：24px × 24px
- 印刷媒体：15mm × 15mm

清晰空间：
- Logo 周围保持等于 Logo 高度 1/2 的空白区域

禁用情况：
- 变形、拉伸或压缩
- 改变颜色比例关系
- 添加阴影或特效（除非设计系统明确规定）
```

---

## 🎨 色彩系统

### 主色调 (Primary Colors)

```css
/* 品牌主色 - 深蓝灰色系 */
--primary-900: #000000; /* 纯黑 - 主要文字、强调元素 */
--primary-800: #081727; /* 深蓝黑 - 导航栏、主要容器背景 */
--primary-700: #161b25; /* 深蓝灰 - 次要文字、图标 */
--primary-500: #2b3a4f; /* 中蓝灰 - 边框、分割线、辅助背景 */
--primary-300: #c9d4dc; /* 浅蓝灰 - 辅助文字、占位符 */
--primary-100: #ffffff; /* 纯白 - 主要背景、卡片背景 */

/* 品牌强调色 - 基于主色调的衍生色 */
--accent-500: #2b3a4f; /* 品牌强调色 - 主要按钮、链接 */
--accent-400: #3d4e63; /* 中等强调 - 悬停状态 */
--accent-300: #5a6b7d; /* 浅强调 - 轻微悬停 */
--accent-200: #8a9ba8; /* 极浅强调 - 禁用状态 */
--accent-100: #e8eef2; /* 背景高亮 - 选中状态背景 */
```

### 功能色彩 (Functional Colors)

```css
/* 成功状态 */
--success-500: #28a745;
--success-100: #d4edda;

/* 警告状态 */
--warning-500: #ffc107;
--warning-100: #fff3cd;

/* 错误状态 */
--error-500: #dc3545;
--error-100: #f8d7da;

/* 信息状态 */
--info-500: #17a2b8;
--info-100: #d1ecf1;
```

### 中性色彩 (Neutral Colors)

```css
--white: #ffffff;
--gray-50: #fafafa;
--gray-100: #f5f5f5;
--gray-200: #eeeeee;
--gray-300: #e0e0e0;
--gray-400: #bdbdbd;
--gray-500: #9e9e9e;
--gray-600: #757575;
--gray-700: #616161;
--gray-800: #424242;
--gray-900: #212121;
--black: #000000;
```

### 色彩应用指南 (Color Usage Guidelines)

```css
/* 深色主题配色应用 */
.dark-theme {
  /* 背景层级 */
  --bg-primary: var(--primary-800); /* 主背景 - 深蓝黑 */
  --bg-secondary: var(--primary-700); /* 次要背景 - 深蓝灰 */
  --bg-elevated: var(--primary-500); /* 浮层背景 - 中蓝灰 */

  /* 文字颜色 */
  --text-primary: var(--primary-100); /* 主要文字 - 纯白 */
  --text-secondary: var(--primary-300); /* 次要文字 - 浅蓝灰 */
  --text-muted: var(--primary-500); /* 弱化文字 - 中蓝灰 */

  /* 边框和分割线 */
  --border-default: var(--primary-500); /* 默认边框 */
  --border-muted: var(--primary-700); /* 弱化边框 */
}

/* 浅色主题配色应用 */
.light-theme {
  /* 背景层级 */
  --bg-primary: var(--primary-100); /* 主背景 - 纯白 */
  --bg-secondary: #f8f9fa; /* 次要背景 - 极浅灰 */
  --bg-elevated: var(--primary-100); /* 浮层背景 - 纯白 */

  /* 文字颜色 */
  --text-primary: var(--primary-900); /* 主要文字 - 纯黑 */
  --text-secondary: var(--primary-800); /* 次要文字 - 深蓝黑 */
  --text-muted: var(--primary-300); /* 弱化文字 - 浅蓝灰 */

  /* 边框和分割线 */
  --border-default: var(--primary-300); /* 默认边框 */
  --border-muted: #e9ecef; /* 弱化边框 */
}

/* 交互状态色彩 */
.interactive-states {
  /* 悬停状态 */
  --hover-overlay: rgba(43, 58, 79, 0.08); /* 浅色主题悬停蒙层 */
  --hover-overlay-dark: rgba(201, 212, 220, 0.12); /* 深色主题悬停蒙层 */

  /* 激活/选中状态 */
  --active-bg: var(--accent-100);
  --active-border: var(--accent-500);

  /* 焦点状态 */
  --focus-ring: 0 0 0 2px var(--accent-500), 0 0 0 4px rgba(43, 58, 79, 0.2);
}
```

### 色彩语义化命名

```css
/* 基于用途的语义化色彩变量 */
:root {
  /* 导航相关 */
  --nav-bg: var(--primary-800);
  --nav-text: var(--primary-100);
  --nav-text-secondary: var(--primary-300);
  --nav-border: var(--primary-700);

  /* 内容区域 */
  --content-bg: var(--primary-100);
  --content-text: var(--primary-900);
  --content-text-secondary: var(--primary-700);

  /* 卡片组件 */
  --card-bg: var(--primary-100);
  --card-border: var(--primary-300);
  --card-shadow: rgba(8, 23, 39, 0.1);

  /* 按钮组件 */
  --btn-primary-bg: var(--primary-800);
  --btn-primary-text: var(--primary-100);
  --btn-primary-hover: var(--primary-700);

  --btn-secondary-bg: transparent;
  --btn-secondary-text: var(--primary-800);
  --btn-secondary-border: var(--primary-500);
  --btn-secondary-hover: var(--accent-100);
}
```

---

## ✍️ 字体系统

### 字体族

```css
/* 主要字体 - 现代无衬线 */
--font-primary: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto",
  sans-serif;

/* 代码字体 - 等宽 */
--font-mono: "JetBrains Mono", "Fira Code", "Consolas", monospace;

/* 中文字体支持 */
--font-chinese: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
```

### 字体层级

```css
/* 标题层级 */
--text-h1: 2.5rem; /* 40px - 页面主标题 */
--text-h2: 2rem; /* 32px - 区块标题 */
--text-h3: 1.5rem; /* 24px - 子标题 */
--text-h4: 1.25rem; /* 20px - 卡片标题 */

/* 正文层级 */
--text-lg: 1.125rem; /* 18px - 重要正文 */
--text-base: 1rem; /* 16px - 标准正文 */
--text-sm: 0.875rem; /* 14px - 辅助文字 */
--text-xs: 0.75rem; /* 12px - 标注文字 */

/* 字重 */
--font-light: 300;
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;

/* 行高 */
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.75;
```

---

## 📐 间距系统

### 基础间距单位

```css
/* 8px 基础网格系统 */
--space-1: 0.25rem; /* 4px */
--space-2: 0.5rem; /* 8px */
--space-3: 0.75rem; /* 12px */
--space-4: 1rem; /* 16px */
--space-5: 1.25rem; /* 20px */
--space-6: 1.5rem; /* 24px */
--space-8: 2rem; /* 32px */
--space-10: 2.5rem; /* 40px */
--space-12: 3rem; /* 48px */
--space-16: 4rem; /* 64px */
--space-20: 5rem; /* 80px */
```

### 应用场景

- **组件内间距**：space-2 to space-4
- **组件间间距**：space-4 to space-6
- **区块间间距**：space-8 to space-12
- **页面级间距**：space-16 to space-20

---

## 🔲 圆角系统

```css
--radius-sm: 0.25rem; /* 4px - 小元素 */
--radius-md: 0.5rem; /* 8px - 按钮、输入框 */
--radius-lg: 0.75rem; /* 12px - 卡片 */
--radius-xl: 1rem; /* 16px - 模态框 */
--radius-2xl: 1.5rem; /* 24px - 大型容器 */
--radius-full: 9999px; /* 圆形 - 头像、标签 */
```

---

## 🌊 阴影系统

```css
/* 层级阴影 */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);

/* 特殊阴影 */
--shadow-inner: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);
--shadow-outline: 0 0 0 3px rgba(0, 123, 255, 0.1);
```

---

## 🎭 图标系统

### 图标风格

- **主要风格**：线性图标 (Outline)
- **强调使用**：填充图标 (Filled)
- **尺寸规格**：16px, 20px, 24px, 32px, 48px
- **描边宽度**：1.5px (标准), 2px (加粗)

### 图标分类

```
导航图标：
- 💬 chat (对话)
- 👥 contacts (联系人)
- 📁 files (文件)
- 🌟 timeline (朋友圈)
- 🔧 plugins (插件)
- ⚙️ settings (设置)

功能图标：
- ➕ add (添加)
- 🔍 search (搜索)
- 📎 attachment (附件)
- 😊 emoji (表情)
- 📤 send (发送)
- 🔔 notification (通知)

状态图标：
- ✅ success (成功)
- ⚠️ warning (警告)
- ❌ error (错误)
- ℹ️ info (信息)
- 🟢 online (在线)
- 🔴 offline (离线)
```

---

## 🧩 组件规范

### 按钮 (Button)

```css
/* 主要按钮 - 使用品牌深色 */
.btn-primary {
  background: var(--btn-primary-bg); /* #081727 */
  color: var(--btn-primary-text); /* #ffffff */
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-md);
  font-weight: var(--font-medium);
  font-size: var(--text-base);
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: var(--btn-primary-hover); /* #161b25 */
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-primary:focus {
  box-shadow: var(--focus-ring);
}

.btn-primary:active {
  transform: translateY(0);
  background: var(--primary-900); /* #000000 */
}

/* 次要按钮 - 描边样式 */
.btn-secondary {
  background: var(--btn-secondary-bg);
  color: var(--btn-secondary-text); /* #081727 */
  border: 1px solid var(--btn-secondary-border); /* #2b3a4f */
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-md);
  font-weight: var(--font-medium);
  font-size: var(--text-base);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--btn-secondary-hover); /* #e8eef2 */
  border-color: var(--primary-700); /* #161b25 */
}

.btn-secondary:focus {
  box-shadow: var(--focus-ring);
}

/* 淡化按钮 - 浅色背景 */
.btn-ghost {
  background: transparent;
  color: var(--primary-700); /* #161b25 */
  border: none;
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-md);
  font-weight: var(--font-medium);
  font-size: var(--text-base);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-ghost:hover {
  background: var(--hover-overlay);
  color: var(--primary-800);
}

/* 危险按钮 */
.btn-danger {
  background: var(--error-500);
  color: var(--white);
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-md);
  font-weight: var(--font-medium);
  font-size: var(--text-base);
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-danger:hover {
  background: #c82333;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* 尺寸变体 */
.btn-sm {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
}

.btn-lg {
  padding: var(--space-4) var(--space-8);
  font-size: var(--text-lg);
}

/* 禁用状态 */
.btn:disabled {
  background: var(--gray-300);
  color: var(--gray-500);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-secondary:disabled {
  background: transparent;
  border-color: var(--gray-300);
  color: var(--gray-500);
}
```

### 卡片 (Card)

```css
/* 基础卡片 */
.card {
  background: var(--card-bg); /* #ffffff */
  border-radius: var(--radius-lg);
  box-shadow: var(--card-shadow); /* rgba(8, 23, 39, 0.1) */
  padding: var(--space-6);
  border: 1px solid var(--card-border); /* #c9d4dc */
  transition: all 0.2s ease;
}

.card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
  border-color: var(--primary-500); /* #2b3a4f */
}

.card-header {
  margin-bottom: var(--space-4);
  border-bottom: 1px solid var(--card-border);
  padding-bottom: var(--space-4);
  color: var(--content-text); /* #000000 */
}

.card-title {
  font-size: var(--text-h4);
  font-weight: var(--font-semibold);
  color: var(--content-text);
  margin: 0;
}

.card-subtitle {
  font-size: var(--text-sm);
  color: var(--content-text-secondary); /* #161b25 */
  margin: var(--space-1) 0 0 0;
}

.card-content {
  color: var(--content-text-secondary);
  line-height: var(--leading-normal);
}

/* 深色卡片变体 */
.card-dark {
  background: var(--primary-800); /* #081727 */
  border-color: var(--primary-700); /* #161b25 */
  color: var(--primary-100); /* #ffffff */
}

.card-dark .card-header {
  border-color: var(--primary-700);
  color: var(--primary-100);
}

.card-dark .card-title {
  color: var(--primary-100);
}

.card-dark .card-subtitle {
  color: var(--primary-300); /* #c9d4dc */
}

.card-dark:hover {
  border-color: var(--primary-500);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

/* 交互式卡片 */
.card-interactive {
  cursor: pointer;
}

.card-interactive:hover {
  background: var(--hover-overlay);
  border-color: var(--primary-700);
}

.card-interactive:active {
  transform: translateY(0);
  box-shadow: var(--shadow-sm);
}

/* 选中状态卡片 */
.card-selected {
  border-color: var(--accent-500); /* #2b3a4f */
  background: var(--accent-100); /* #e8eef2 */
  box-shadow: 0 0 0 1px var(--accent-500);
}
```

### 输入框 (Input)

```css
/* 基础输入框 */
.input {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--primary-300); /* #c9d4dc */
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-family: var(--font-primary);
  background: var(--primary-100); /* #ffffff */
  color: var(--primary-900); /* #000000 */
  transition: all 0.2s ease;
}

.input::placeholder {
  color: var(--primary-300); /* #c9d4dc */
}

.input:focus {
  outline: none;
  border-color: var(--primary-500); /* #2b3a4f */
  box-shadow: var(--focus-ring);
  background: var(--primary-100);
}

.input:hover:not(:focus):not(:disabled) {
  border-color: var(--primary-500);
}

.input:disabled {
  background: var(--gray-100);
  border-color: var(--gray-300);
  color: var(--gray-500);
  cursor: not-allowed;
}

/* 错误状态 */
.input.error {
  border-color: var(--error-500);
  box-shadow: 0 0 0 2px rgba(220, 53, 69, 0.2);
}

.input.error:focus {
  box-shadow: 0 0 0 2px rgba(220, 53, 69, 0.2);
}

/* 成功状态 */
.input.success {
  border-color: var(--success-500);
  box-shadow: 0 0 0 2px rgba(40, 167, 69, 0.2);
}

/* 深色主题输入框 */
.input-dark {
  background: var(--primary-700); /* #161b25 */
  border-color: var(--primary-500); /* #2b3a4f */
  color: var(--primary-100); /* #ffffff */
}

.input-dark::placeholder {
  color: var(--primary-300);
}

.input-dark:focus {
  background: var(--primary-800); /* #081727 */
  border-color: var(--primary-300); /* #c9d4dc */
  box-shadow: 0 0 0 2px rgba(201, 212, 220, 0.3);
}

/* 输入框尺寸变体 */
.input-sm {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
}

.input-lg {
  padding: var(--space-4) var(--space-5);
  font-size: var(--text-lg);
}

/* 文本域 */
.textarea {
  resize: vertical;
  min-height: 120px;
  line-height: var(--leading-normal);
}

/* 输入组 */
.input-group {
  position: relative;
  display: flex;
  align-items: center;
}

.input-group .input {
  padding-left: var(--space-10); /* 为图标留空间 */
}

.input-group .input-icon {
  position: absolute;
  left: var(--space-3);
  color: var(--primary-300);
  pointer-events: none;
  z-index: 1;
}

.input-group .input:focus + .input-icon {
  color: var(--primary-500);
}
```

---

## 📱 布局系统

### 网格系统

```css
/* 12列网格系统 */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-4);
}

.row {
  display: flex;
  flex-wrap: wrap;
  margin: 0 calc(var(--space-2) * -1);
}

.col {
  flex: 1;
  padding: 0 var(--space-2);
}

/* 响应式断点 */
@media (min-width: 640px) {
  /* sm */
}
@media (min-width: 768px) {
  /* md */
}
@media (min-width: 1024px) {
  /* lg */
}
@media (min-width: 1280px) {
  /* xl */
}
```

### 三栏布局（核心布局）

```css
/* 主布局容器 */
.main-layout {
  display: flex;
  height: 100vh;
  background: var(--primary-100); /* #ffffff - 主背景 */
  overflow: hidden;
}

/* 左侧导航栏 - 窄边栏设计 */
.sidebar {
  width: 80px; /* 60-120px范围 */
  background: var(--nav-bg); /* #081727 - 深蓝黑导航背景 */
  border-right: 1px solid var(--nav-border); /* #161b25 */
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-4) var(--space-2);
  box-shadow: 2px 0 4px rgba(8, 23, 39, 0.1);
  z-index: 100;
}

/* 导航项 */
.sidebar-nav-item {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-2);
  border-radius: var(--radius-lg);
  color: var(--nav-text-secondary); /* #c9d4dc */
  transition: all 0.2s ease;
  cursor: pointer;
}

.sidebar-nav-item:hover {
  background: rgba(201, 212, 220, 0.1);
  color: var(--nav-text); /* #ffffff */
}

.sidebar-nav-item.active {
  background: var(--primary-500); /* #2b3a4f */
  color: var(--nav-text);
  box-shadow: 0 2px 8px rgba(43, 58, 79, 0.3);
}

/* 中间面板 */
.middle-panel {
  width: 320px; /* 300-400px范围 */
  background: var(--content-bg); /* #ffffff */
  border-right: 1px solid var(--border-default); /* #c9d4dc */
  display: flex;
  flex-direction: column;
  position: relative;
}

.middle-panel-header {
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--border-default);
  background: var(--content-bg);
  position: sticky;
  top: 0;
  z-index: 10;
}

.middle-panel-title {
  font-size: var(--text-h3);
  font-weight: var(--font-semibold);
  color: var(--content-text); /* #000000 */
  margin: 0;
}

.middle-panel-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-2) 0;
}

/* 右侧内容区 */
.content-area {
  flex: 1;
  background: var(--content-bg); /* #ffffff */
  display: flex;
  flex-direction: column;
  position: relative;
}

.content-header {
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--border-default);
  background: var(--content-bg);
  position: sticky;
  top: 0;
  z-index: 10;
}

.content-main {
  flex: 1;
  padding: var(--space-6);
  overflow-y: auto;
}

/* 深色主题布局变体 */
.main-layout.dark {
  background: var(--primary-800); /* #081727 */
}

.main-layout.dark .middle-panel,
.main-layout.dark .content-area {
  background: var(--primary-700); /* #161b25 */
  color: var(--primary-100); /* #ffffff */
}

.main-layout.dark .middle-panel-header,
.main-layout.dark .content-header {
  background: var(--primary-800);
  border-color: var(--primary-500);
}

.main-layout.dark .middle-panel-title {
  color: var(--primary-100);
}
```

---

## 🎬 动画系统

### 缓动函数

```css
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### 动画时长

```css
--duration-fast: 150ms;
--duration-normal: 250ms;
--duration-slow: 400ms;
```

### 常用动画

```css
/* 渐入效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 弹性缩放 */
@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 滑入效果 */
@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
```

---

## 📱 响应式设计

### 断点系统

```css
/* 移动端优先设计 */
.responsive-element {
  /* 默认移动端样式 */
  font-size: var(--text-sm);
  padding: var(--space-2);
}

/* 平板端 */
@media (min-width: 768px) {
  .responsive-element {
    font-size: var(--text-base);
    padding: var(--space-4);
  }

  /* 三栏布局调整为双栏 */
  .main-layout {
    .sidebar {
      width: 60px;
    }
    .middle-panel {
      width: 280px;
    }
  }
}

/* 桌面端 */
@media (min-width: 1024px) {
  .responsive-element {
    font-size: var(--text-lg);
    padding: var(--space-6);
  }
}
```

### 移动端适配

```css
/* 手机端单栏布局 */
@media (max-width: 767px) {
  .main-layout {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    height: 60px;
    flex-direction: row;
    order: 3; /* 底部导航 */
  }

  .middle-panel {
    display: none; /* 隐藏中间面板 */
  }

  .content-area {
    order: 1;
    flex: 1;
  }
}
```

---

## ♿ 可访问性 (Accessibility)

### 颜色对比度

- **大文字 (18px+)**：至少 3:1 对比度
- **标准文字 (16px-)**：至少 4.5:1 对比度
- **非文本元素**：至少 3:1 对比度

### 焦点管理

```css
.focusable:focus {
  outline: 2px solid var(--accent-500);
  outline-offset: 2px;
}

.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: var(--accent-500);
  color: white;
  padding: 8px;
  text-decoration: none;
  z-index: 1000;
}

.skip-link:focus {
  top: 6px;
}
```

### 语义化标记

```html
<!-- 正确的语义化结构 -->
<main role="main">
  <header role="banner">
    <nav role="navigation" aria-label="主导航"></nav>
  </header>

  <section aria-labelledby="chat-section">
    <h2 id="chat-section">聊天区域</h2>
    <!-- 聊天内容 -->
  </section>
</main>
```

---

## 🔧 实现指南

### CSS 变量使用

```css
/* 主题切换支持 */
:root {
  /* 亮色主题 */
  --bg-primary: var(--white);
  --text-primary: var(--gray-900);
}

[data-theme="dark"] {
  /* 暗色主题 */
  --bg-primary: var(--gray-900);
  --text-primary: var(--white);
}
```

### 组件库集成

```tsx
// 使用 shadcn/ui + Tailwind CSS
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

// 自定义主题配置
const theme = {
  colors: {
    primary: "hsl(var(--primary))",
    accent: "hsl(var(--accent))",
  },
  borderRadius: {
    sm: "var(--radius-sm)",
    md: "var(--radius-md)",
    lg: "var(--radius-lg)",
  },
};
```

---

## 📋 检查清单

### 设计交付检查

- [ ] 颜色符合品牌规范和对比度要求
- [ ] 字体层级清晰合理
- [ ] 间距使用 8px 网格系统
- [ ] 组件状态完整（默认、悬停、聚焦、禁用）
- [ ] 响应式设计适配多端
- [ ] 可访问性标准符合 WCAG 2.1 AA

### 开发实现检查

- [ ] CSS 变量正确使用
- [ ] 动画性能优化
- [ ] 语义化 HTML 标记
- [ ] 键盘导航支持
- [ ] 屏幕阅读器兼容

---

## 📚 资源与工具

### 设计工具

- **Figma**：UI 设计和原型制作
- **Framer**：高保真交互原型
- **Adobe Color**：配色方案生成

### 开发工具

- **Tailwind CSS**：快速样式开发
- **shadcn/ui**：高质量组件库
- **Storybook**：组件展示和测试

### 可访问性工具

- **axe DevTools**：可访问性检测
- **WAVE**：Web 可访问性评估
- **Color Oracle**：色盲模拟器

---

## 📝 更新日志

### v1.1 - 品牌色彩系统优化 (2024 年)

**核心更新**

- 🎨 **更新品牌主色调**：采用深蓝灰色系 (#000000, #081727, #161b25, #2b3a4f, #c9d4dc, #ffffff)
- 🌈 **新增色彩应用指南**：提供深浅主题的配色方案和语义化色彩变量
- 🧩 **组件样式优化**：按钮、卡片、输入框等组件全面适配新色彩系统
- 📱 **三栏布局重设计**：导航栏采用深色设计，突出品牌调性

**色彩语义化**

- 主导航：深蓝黑背景 (#081727) + 白色文字，营造专业科技感
- 内容区域：纯白背景 (#ffffff) + 黑色文字，确保最佳可读性
- 交互元素：中蓝灰色 (#2b3a4f) 作为强调色，保持品牌一致性
- 辅助信息：浅蓝灰色 (#c9d4dc) 用于次要文字和占位符

**设计原则**

- ✅ 保持高对比度，确保可访问性标准
- ✅ 支持深浅主题切换
- ✅ 语义化命名，便于开发维护
- ✅ 响应式设计，适配多端设备

**下一步计划**

- [ ] 添加更多组件样式规范
- [ ] 制定图标设计规范
- [ ] 完善动效设计指南
- [ ] 建立组件库实现

---

_最后更新：2024 年_
_版本：v1.1_
_维护者：Connet.AI 设计团队_
