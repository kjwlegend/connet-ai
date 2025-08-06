import type { Metadata } from 'next';
import type { SEOConfig } from './types';
import { defaultSEOConfig, getOpenGraphConfig, getTwitterConfig } from './config';

export function generateMetadata(config: Partial<SEOConfig> = {}): Metadata {
  const mergedConfig = { ...defaultSEOConfig, ...config };
  const openGraph = getOpenGraphConfig(mergedConfig);
  const twitter = getTwitterConfig(mergedConfig);

  const metadata: Metadata = {
    title: mergedConfig.title,
    description: mergedConfig.description,
    keywords: mergedConfig.keywords,
    authors: mergedConfig.author ? [{ name: mergedConfig.author }] : undefined,
    creator: mergedConfig.author,
    publisher: mergedConfig.siteName,
    
    // 基础元标签
    metadataBase: mergedConfig.siteUrl ? new URL(mergedConfig.siteUrl) : undefined,
    alternates: {
      canonical: mergedConfig.siteUrl,
      languages: {
        'en': `${mergedConfig.siteUrl}/en`,
        'zh-CN': `${mergedConfig.siteUrl}/zh-CN`,
      },
    },
    
    // Open Graph
    openGraph: {
      title: openGraph.title,
      description: openGraph.description,
      url: openGraph.url,
      siteName: openGraph.siteName,
      locale: openGraph.locale,
      type: openGraph.type,
      images: openGraph.images,
    },
    
    // Twitter
    twitter: {
      card: twitter.card,
      site: twitter.site,
      creator: twitter.creator,
      title: twitter.title,
      description: twitter.description,
      images: twitter.image ? [{
        url: twitter.image,
        alt: twitter.imageAlt,
      }] : undefined,
    },
    
    // 机器人指令
    robots: {
      index: !mergedConfig.noindex,
      follow: !mergedConfig.nofollow,
      googleBot: {
        index: !mergedConfig.noindex,
        follow: !mergedConfig.nofollow,
      },
    },
    
    // PWA相关
    manifest: '/manifest.json',
    
    // 验证
    verification: {
      google: process.env.NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION,
      yandex: process.env.NEXT_PUBLIC_YANDEX_VERIFICATION,
      other: {
        'baidu-site-verification': process.env.NEXT_PUBLIC_BAIDU_SITE_VERIFICATION,
      },
    },
    
    // 其他元标签
    other: {
      'application-name': mergedConfig.siteName,
      'apple-mobile-web-app-title': mergedConfig.siteName,
      'apple-mobile-web-app-status-bar-style': 'default',
      'format-detection': 'telephone=no',
      'mobile-web-app-capable': 'yes',
      'msapplication-config': '/browserconfig.xml',
      'msapplication-TileColor': '#000000',
      'theme-color': '#000000',
    },
  };

  return metadata;
}

// 页面特定的元数据生成器
export function generatePageMetadata(
  pageKey: string,
  customConfig: Partial<SEOConfig> = {}
): Metadata {
  // 这里可以根据pageKey获取特定配置
  // 从pageSEOConfigs中获取对应页面的配置
  
  return generateMetadata(customConfig);
}

// JSON-LD结构化数据生成器
export function generateJSONLD(config: Partial<SEOConfig> = {}): string {
  const mergedConfig = { ...defaultSEOConfig, ...config };
  
  const jsonLD = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: mergedConfig.siteName,
    description: mergedConfig.description,
    url: mergedConfig.siteUrl,
    logo: `${mergedConfig.siteUrl}/images/logo.png`,
    sameAs: [
      'https://twitter.com/connet_ai',
      'https://github.com/connet-ai',
    ],
    potentialAction: {
      '@type': 'SearchAction',
      target: `${mergedConfig.siteUrl}/search?q={search_term_string}`,
      'query-input': 'required name=search_term_string',
    },
    author: {
      '@type': 'Organization',
      name: mergedConfig.author,
      url: mergedConfig.siteUrl,
    },
  };

  return JSON.stringify(jsonLD);
}