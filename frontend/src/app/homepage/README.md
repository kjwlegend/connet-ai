# Homepage Versions

这里包含了三个版本的 Connet.AI 宣传首页设计。

## 🎨 Version 1 - 创意自由版

**路径**: `/homepage/version1`

### 特色功能：
- 🌟 **创新设计**: 完全自由发挥的创意设计，突出虚拟现实概念
- 🎭 **动态动画**: 使用 Framer Motion 创建的丰富动画效果
  - 浮动网络可视化动画
  - 连接节点的旋转和弹跳效果
  - 平滑的页面滚动动画
- 🌈 **渐变背景**: 多层次的渐变背景营造科技感
- 💫 **三阶段介绍**: "Connect Dots, Create Magic" 的三步骤工作流程
- 🎯 **多个CTA区域**: 英雄区域和底部都有加入候补名单功能

### 设计亮点：
- "Connect **Dots** in Virtual Reality" 的核心概念
- 中央网络Hub连接8个浮动节点
- 蓝紫渐变的品牌色调
- 响应式三面板布局预览

---

## 🎯 Version 2 - 设计驱动版

**路径**: `/homepage/version2`  

### 特色功能：
- 📐 **设计还原**: 基于 `@design/` 目录中的设计素材
- 🎨 **品牌一致性**: 严格遵循品牌设计规范
  - 使用设计稿中的 CircleDot logo
  - 黑白简约的配色方案
  - 清晰的排版层次
- 👥 **头像网络**: 模仿设计稿的用户头像连接可视化
- 🔄 **双英雄布局**: 
  - 主英雄区：`"Your AI Contacts, Your Way"`
  - 副英雄区：`"Connect with AI, Naturally"`
- 📱 **简洁功能**: Discovery, Conversation, Collaboration 三大核心功能

### 设计还原：
- 精确匹配原设计中的用户头像布局
- 保持与品牌设计手册一致的视觉语言
- 简约现代的界面风格

---

## 🚀 Version 3 - VR深色高级版

**路径**: `/homepage/version3`

### 特色功能：
- 🌙 **深色主题**: 专业的深色设计，突出VR虚拟现实概念
- 🥽 **VR头盔可视化**: 3D风格的VR头盔图形，强调沉浸式体验
- ⚡ **高级动效**: 
  - VR头盔周围的浮动UI元素
  - 动态网络连接线动画
  - 发光效果和阴影系统
- 🔗 **固定位置动画**: 解决SSR hydration问题，使用预定义位置
- 🎭 **科技感**: 渐变背景、光效、模糊效果营造未来感
- 🌐 **国际化**: 完整的中英文支持

### 设计亮点：
- "Experience the **Future** of Connection" 的核心概念
- VR头盔主视觉，强调虚拟现实体验
- 深色主题配合蓝紫色渐变光效
- 专业的科技行业设计风格
- 解决了hydration错误的技术实现

---

## 🌐 国际化支持

两个版本都完整支持中英文切换：

### 英文 (`en`)
- Professional, modern tone
- Focus on "Virtual Reality" and "Connect Dots"
- Technical terminology optimized for global audience

### 中文 (`zh`)  
- 本土化的表达方式
- "虚拟现实" 和 "连接点" 的概念
- 符合中国用户习惯的UI文案

---

## 🔧 Waitlist 功能

### 核心特性：
- ✅ **邮箱验证**: 实时邮箱格式验证
- 🚀 **一键加入**: 无需额外信息，只需邮箱
- 🎯 **来源追踪**: 自动标记用户来源 (`homepage_v1` / `homepage_v2`)
- 📊 **UTM参数**: 自动收集营销追踪参数
- 🌍 **地理位置**: 基于时区的大致位置判断
- 💬 **Toast反馈**: 成功/失败的用户反馈
- 🔄 **乐观更新**: 即时UI响应，后端确认
- 📈 **分析集成**: Google Analytics, Facebook Pixel 等

### 技术实现：
```typescript
// 使用方式
const { joinWaitlist, isLoading, isSubmitted } = useWaitlist()

await joinWaitlist(email, 'homepage_v1')
```

### API 端点：
- `POST /api/waitlist/join` - 加入候补名单
- `GET /api/waitlist/check/:email` - 检查邮箱是否已注册  
- `GET /api/waitlist/position/:email` - 查询队列位置
- `POST /api/waitlist/referral` - 生成推荐链接

---

## 🎨 设计系统集成

### UI组件：
- shadcn/ui 组件库
- 完整的主题切换支持 (light/dark)
- 响应式布局适配

### 动画系统：
- Framer Motion 动画库
- 60fps 流畅动画
- 移动端性能优化

### 性能优化：
- 懒加载图片和动画
- 组件级别的性能监控
- 最小化重渲染

---

## 📱 访问方式

### 开发环境：
```bash
cd frontend
pnpm dev

# Version 1: http://localhost:3000/homepage/version1  
# Version 2: http://localhost:3000/homepage/version2
```

### 生产部署：
- Version 1: `https://connet.ai/homepage/version1`
- Version 2: `https://connet.ai/homepage/version2`

---

## 🔄 下一步计划

1. **A/B Testing**: 在两个版本间进行转化率测试
2. **数据分析**: 收集用户行为数据优化转化漏斗  
3. **移动优化**: 进一步优化移动端体验
4. **SEO优化**: 添加结构化数据和元标签
5. **社交分享**: Open Graph 和 Twitter Cards 优化

---

这两个版本为 Connet.AI 的市场推广提供了不同风格的选择，既有创新的视觉冲击力，又有专业的品牌一致性。