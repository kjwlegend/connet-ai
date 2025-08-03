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

export const typographyTokens: TypographyTokens = {
  fontFamily: {
    primary: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    mono: '"JetBrains Mono", "Fira Code", "Consolas", monospace',
    chinese: '"PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif',
  },
  fontSize: {
    h1: '2.5rem',
    h2: '2rem',
    h3: '1.5rem',
    h4: '1.25rem',
    lg: '1.125rem',
    base: '1rem',
    sm: '0.875rem',
    xs: '0.75rem',
  },
  fontWeight: {
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  },
};