import type { Plugin, PluginCategory } from "@/types/plugin"

export const pluginCategories: PluginCategory[] = [
  {
    id: "development",
    name: "开发工具",
    description: "提升开发效率的专业工具集",
    icon: "🔧",
    plugins: [
      {
        id: "plugin-dev-1",
        name: "代码生成器",
        displayName: "AI 代码生成器",
        version: "1.2.0",
        description: "基于需求自动生成高质量代码",
        longDescription: "强大的AI代码生成工具，支持多种编程语言，提供智能代码补全、自动注释生成和代码质量检查功能。",
        icon: "🔧",
        author: {
          name: "Connet AI Team",
          email: "dev@connet.ai"
        },
        category: "development",
        tags: ["代码生成", "AI", "开发工具", "自动化"],
        rating: 4.8,
        downloadCount: 15420,
        configured: true,
        enabled: true,
        featured: true,
        verified: true,
        features: ["支持20+编程语言", "智能代码补全", "自动注释生成", "代码质量检查"],
        requirements: ["API Key", "网络连接"],
        configTemplate: {
          version: "1.0",
          sections: [
            {
              id: "basic",
              title: "基本配置",
              description: "配置基本的 API 连接信息",
              fields: [
                {
                  key: "apiKey",
                  type: "password",
                  label: "API Key",
                  description: "用于访问代码生成服务的密钥",
                  placeholder: "请输入您的 API Key",
                  required: true,
                  validation: {
                    required: true,
                    minLength: 10
                  }
                },
                {
                  key: "model",
                  type: "select",
                  label: "AI 模型",
                  description: "选择用于代码生成的AI模型",
                  required: true,
                  options: [
                    { label: "GPT-4 (推荐)", value: "gpt-4", description: "最强大的模型，适合复杂任务" },
                    { label: "GPT-3.5 Turbo", value: "gpt-3.5-turbo", description: "快速响应，适合简单任务" },
                    { label: "Claude-3", value: "claude-3", description: "优秀的代码理解能力" }
                  ]
                }
              ]
            },
            {
              id: "advanced",
              title: "高级设置",
              description: "自定义代码生成的行为参数",
              collapsible: true,
              fields: [
                {
                  key: "temperature",
                  type: "slider",
                  label: "创造性",
                  description: "控制代码生成的创造性程度，数值越高越有创意",
                  defaultValue: 0.7,
                  min: 0,
                  max: 1,
                  step: 0.1
                },
                {
                  key: "maxTokens",
                  type: "number",
                  label: "最大令牌数",
                  description: "单次生成的最大长度",
                  defaultValue: 2000,
                  min: 100,
                  max: 4000,
                  step: 100
                },
                {
                  key: "languages",
                  type: "multiselect",
                  label: "支持的语言",
                  description: "选择支持的编程语言",
                  options: [
                    { label: "JavaScript", value: "javascript" },
                    { label: "TypeScript", value: "typescript" },
                    { label: "Python", value: "python" },
                    { label: "Java", value: "java" },
                    { label: "Go", value: "go" },
                    { label: "Rust", value: "rust" }
                  ],
                  defaultValue: ["javascript", "typescript", "python"]
                }
              ]
            }
          ]
        },
        createdAt: "2024-01-15T08:30:00Z",
        updatedAt: "2024-03-10T14:22:00Z",
        supportUrl: "https://support.connet.ai/code-generator",
        documentationUrl: "https://docs.connet.ai/plugins/code-generator"
      },
      {
        id: "plugin-dev-2",
        name: "API测试工具",
        description: "快速测试和调试API接口",
        icon: "🔌",
        rating: 4.6,
        configured: false,
        features: ["RESTful API测试", "GraphQL支持", "自动化测试", "响应时间监控"],
        configFields: [
          { key: "baseUrl", label: "Base URL", type: "url", required: true },
          { key: "timeout", label: "超时时间(秒)", type: "number", min: 1, max: 300 },
          { key: "retries", label: "重试次数", type: "number", min: 0, max: 5 },
        ],
      },
      {
        id: "plugin-dev-3",
        name: "数据库工具",
        description: "数据库连接和管理工具",
        icon: "🗄️",
        rating: 4.7,
        configured: false,
        features: ["多数据库支持", "SQL查询优化", "数据迁移", "备份恢复"],
        configFields: [
          {
            key: "dbType",
            label: "数据库类型",
            type: "select",
            options: ["MySQL", "PostgreSQL", "MongoDB"],
            required: true,
          },
          { key: "host", label: "主机地址", type: "text", required: true },
          { key: "port", label: "端口", type: "number", min: 1, max: 65535 },
          { key: "username", label: "用户名", type: "text", required: true },
          { key: "password", label: "密码", type: "password", required: true },
        ],
      },
    ] as Plugin[],
  },
  {
    id: "design",
    name: "设计工具",
    plugins: [
      {
        id: "plugin-design-1",
        name: "设计素材库",
        description: "海量设计素材和模板",
        icon: "🎨",
        rating: 4.7,
        configured: true,
        features: ["10万+设计素材", "AI图片生成", "品牌色彩管理", "字体推荐"],
        configFields: [
          { key: "apiKey", label: "API Key", type: "password", required: true },
          { key: "quality", label: "图片质量", type: "select", options: ["高", "中", "低"], required: true },
          { key: "watermark", label: "水印设置", type: "text" },
        ],
      },
      {
        id: "plugin-design-2",
        name: "颜色搭配助手",
        description: "智能颜色搭配建议",
        icon: "🌈",
        rating: 4.5,
        configured: false,
        features: ["色彩理论分析", "品牌色彩提取", "无障碍色彩检查", "色彩趋势预测"],
        configFields: [
          { key: "colorSpace", label: "色彩空间", type: "select", options: ["RGB", "HSL", "CMYK"], required: true },
          { key: "accessibility", label: "无障碍检查", type: "checkbox" },
        ],
      },
    ] as Plugin[],
  },
  {
    id: "productivity",
    name: "效率工具",
    plugins: [
      {
        id: "plugin-prod-1",
        name: "项目管理",
        description: "任务分配和进度跟踪",
        icon: "📋",
        rating: 4.9,
        configured: true,
        features: ["甘特图管理", "团队协作", "时间追踪", "报告生成"],
        configFields: [
          { key: "webhookUrl", label: "Webhook URL", type: "url" },
          { key: "notifications", label: "通知设置", type: "checkbox" },
          { key: "timezone", label: "时区", type: "select", options: ["Asia/Shanghai", "UTC", "America/New_York"] },
        ],
      },
      {
        id: "plugin-prod-2",
        name: "时间追踪",
        description: "工作时间统计和分析",
        icon: "⏰",
        rating: 4.4,
        configured: false,
        features: ["自动时间记录", "项目时间分析", "效率报告", "团队统计"],
        configFields: [
          { key: "autoStart", label: "自动开始", type: "checkbox" },
          { key: "reminderInterval", label: "提醒间隔(分钟)", type: "number", min: 5, max: 60 },
        ],
      },
    ] as Plugin[],
  },
]