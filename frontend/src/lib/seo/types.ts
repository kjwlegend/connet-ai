export interface SEOConfig {
  title: string;
  description: string;
  keywords?: string[];
  author?: string;
  siteName?: string;
  siteUrl?: string;
  locale?: string;
  type?: 'website' | 'article' | 'profile';
  image?: string;
  imageAlt?: string;
  noindex?: boolean;
  nofollow?: boolean;
}

export interface OpenGraphConfig {
  title: string;
  description: string;
  url?: string;
  siteName?: string;
  images?: OpenGraphImage[];
  locale?: string;
  type?: 'website' | 'article' | 'profile';
}

export interface OpenGraphImage {
  url: string;
  width?: number;
  height?: number;
  alt?: string;
  type?: string;
}

export interface TwitterConfig {
  card?: 'summary' | 'summary_large_image' | 'app' | 'player';
  site?: string;
  creator?: string;
  title?: string;
  description?: string;
  image?: string;
  imageAlt?: string;
}

export interface JSONLDConfig {
  '@context': string;
  '@type': string;
  name?: string;
  description?: string;
  url?: string;
  logo?: string;
  sameAs?: string[];
  author?: {
    '@type': string;
    name: string;
  };
}