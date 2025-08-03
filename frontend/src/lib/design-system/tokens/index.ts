export * from './colors';
export * from './typography';
export * from './spacing';

import type { ColorTokens } from './colors';
import type { TypographyTokens } from './typography';
import type { SpacingTokens } from './spacing';

import { colorTokens } from './colors';
import { typographyTokens } from './typography';
import { spacingTokens } from './spacing';

export interface DesignTokens {
  colors: ColorTokens;
  typography: TypographyTokens;
  spacing: SpacingTokens;
}

export const designTokens: DesignTokens = {
  colors: colorTokens,
  typography: typographyTokens,
  spacing: spacingTokens,
};

export function getDesignTokens(): DesignTokens {
  return designTokens;
}