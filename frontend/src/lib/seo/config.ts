import type { SEOConfig, OpenGraphConfig, TwitterConfig, JSONLDConfig } from './types';

export const defaultSEOConfig: SEOConfig = {
  title: 'Connet.AI - AI协作平台',
  description: '智能AI协作平台，支持多Agent协作，提供强大的AI工具和智能对话功能。',
  keywords: [
    'AI协作',
    'AI助手',
    '人工智能',
    '多Agent协作',
    'AI工具',
    '智能对话',
    'Connet.AI'
  ],
  author: 'Connet.AI Team',
  siteName: 'Connet.AI',
  siteUrl: 'https://connet.ai',
  locale: 'zh-CN',
  type: 'website',
  image: '/images/og-image.png',
  imageAlt: 'Connet.AI - AI协作平台',
};

export const getOpenGraphConfig = (config: Partial<SEOConfig>): OpenGraphConfig => ({
  title: config.title || defaultSEOConfig.title,
  description: config.description || defaultSEOConfig.description,
  url: config.siteUrl || defaultSEOConfig.siteUrl,
  siteName: config.siteName || defaultSEOConfig.siteName,
  locale: config.locale || defaultSEOConfig.locale,
  type: config.type || defaultSEOConfig.type,
  images: config.image ? [{
    url: config.image,
    width: 1200,
    height: 630,
    alt: config.imageAlt || defaultSEOConfig.imageAlt,
    type: 'image/png',
  }] : undefined,
});

export const getTwitterConfig = (config: Partial<SEOConfig>): TwitterConfig => ({
  card: 'summary_large_image',
  site: '@connet_ai',
  creator: '@connet_ai',
  title: config.title || defaultSEOConfig.title,
  description: config.description || defaultSEOConfig.description,
  image: config.image || defaultSEOConfig.image,
  imageAlt: config.imageAlt || defaultSEOConfig.imageAlt,
});

export const getJSONLDConfig = (config: Partial<SEOConfig>): JSONLDConfig => ({
  '@context': 'https://schema.org',
  '@type': 'WebSite',
  name: config.siteName || defaultSEOConfig.siteName,
  description: config.description || defaultSEOConfig.description,
  url: config.siteUrl || defaultSEOConfig.siteUrl,
  logo: `${config.siteUrl || defaultSEOConfig.siteUrl}/images/logo.png`,
  sameAs: [
    'https://twitter.com/connet_ai',
    'https://github.com/connet-ai',
    'https://linkedin.com/company/connet-ai'
  ],
  author: {
    '@type': 'Organization',
    name: config.author || defaultSEOConfig.author || 'Connet.AI Team',
  },
});

// 页面特定的SEO配置
export const pageSEOConfigs = {
  home: {
    title: 'Connet.AI - 智能AI协作平台',
    description: '体验下一代AI协作，多Agent智能助手为您提供编程、设计、分析等全方位支持。',
    keywords: ['AI协作平台', '多Agent', 'AI助手', '智能工具'],
  },
  chat: {
    title: '智能对话 - Connet.AI',
    description: '与AI助手进行智能对话，获得专业的建议和帮助。',
    keywords: ['AI对话', '智能助手', 'AI聊天'],
  },
  contacts: {
    title: 'AI助手管理 - Connet.AI',
    description: '管理您的AI助手，配置专业工具和技能。',
    keywords: ['AI助手管理', 'Agent配置', 'AI工具'],
  },
  files: {
    title: '文件管理 - Connet.AI',
    description: '智能文件管理和知识库，让AI助手更好地理解您的内容。',
    keywords: ['文件管理', '知识库', 'AI文档'],
  },
  timeline: {
    title: '动态时间线 - Connet.AI',
    description: '查看AI助手的工作动态和协作历史。',
    keywords: ['AI动态', '时间线', '协作历史'],
  },
  plugins: {
    title: '插件市场 - Connet.AI',
    description: '发现和安装强大的AI工具插件，扩展您的AI助手能力。',
    keywords: ['AI插件', '工具市场', 'AI扩展'],
  },
  settings: {
    title: '设置中心 - Connet.AI',
    description: '配置您的AI协作环境，个性化您的使用体验。',
    keywords: ['AI设置', '个性化配置', '用户偏好'],
  },
};