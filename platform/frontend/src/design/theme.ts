import { tokens } from './tokens';

export type ThemeMode = 'dark' | 'light';
export type Density = 'compact' | 'cozy' | 'comfortable';
export type MotionIntensity = 'none' | 'subtle' | 'normal' | 'expressive';

export interface BrandConfig {
  orgName: string;
  primaryColor: string;
  accentColor: string;
  logoUrl?: string;
  mode: ThemeMode;
  density: Density;
  borderRadius: 'sharp' | 'rounded' | 'pill';
  motionIntensity: MotionIntensity;
}

export const defaultBrand: BrandConfig = {
  orgName: 'ProjectZero',
  primaryColor: tokens.colors.brand.primary,
  accentColor: tokens.colors.brand.accent,
  mode: 'dark',
  density: 'cozy',
  borderRadius: 'rounded',
  motionIntensity: 'subtle',
};

export const darkTheme = {
  bg: tokens.colors.surface.dark,
  bgMid: tokens.colors.surface.darkMid,
  panel: tokens.colors.surface.darkPanel,
  glass: tokens.colors.glass.white,
  glassMd: tokens.colors.glass.whiteMd,
  border: tokens.colors.border.glass,
  borderMd: tokens.colors.border.glassMd,
  text: tokens.colors.text.primary,
  textSecondary: tokens.colors.text.secondary,
  textMuted: tokens.colors.text.muted,
};

export const lightTheme = {
  bg: tokens.colors.surface.light,
  bgMid: tokens.colors.surface.lightMid,
  panel: tokens.colors.surface.lightPanel,
  glass: 'rgba(255,255,255,0.70)',
  glassMd: 'rgba(255,255,255,0.85)',
  border: 'rgba(0,0,0,0.08)',
  borderMd: 'rgba(0,0,0,0.12)',
  text: tokens.colors.text.inverse,
  textSecondary: '#475569',
  textMuted: '#94a3b8',
};
