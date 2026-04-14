export const tokens = {
  colors: {
    // Base palette
    glass: {
      white: 'rgba(255,255,255,0.08)',
      whiteMd: 'rgba(255,255,255,0.12)',
      whiteLg: 'rgba(255,255,255,0.18)',
      dark: 'rgba(0,0,0,0.25)',
      darkMd: 'rgba(0,0,0,0.40)',
    },
    brand: {
      primary: '#6366f1',       // indigo-500
      primaryLight: '#818cf8',  // indigo-400
      primaryDark: '#4f46e5',   // indigo-600
      accent: '#06b6d4',        // cyan-500
      accentLight: '#22d3ee',
    },
    semantic: {
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#3b82f6',
      successBg: 'rgba(16,185,129,0.12)',
      warningBg: 'rgba(245,158,11,0.12)',
      errorBg: 'rgba(239,68,68,0.12)',
      infoBg: 'rgba(59,130,246,0.12)',
    },
    surface: {
      dark: '#0f172a',
      darkMid: '#1e293b',
      darkPanel: '#1a2744',
      light: '#f8fafc',
      lightMid: '#f1f5f9',
      lightPanel: '#ffffff',
    },
    text: {
      primary: '#f1f5f9',
      secondary: '#94a3b8',
      muted: '#64748b',
      inverse: '#0f172a',
      link: '#818cf8',
    },
    border: {
      glass: 'rgba(255,255,255,0.10)',
      glassMd: 'rgba(255,255,255,0.16)',
      focus: '#6366f1',
    },
  },
  blur: {
    sm: 'blur(8px)',
    md: 'blur(16px)',
    lg: 'blur(24px)',
    xl: 'blur(40px)',
  },
  radius: {
    sm: '0.375rem',
    md: '0.75rem',
    lg: '1rem',
    xl: '1.5rem',
    full: '9999px',
  },
  shadow: {
    glass: '0 4px 24px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.08)',
    glassMd: '0 8px 32px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.10)',
    glassLg: '0 16px 48px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.12)',
    glow: '0 0 20px rgba(99,102,241,0.25)',
    glowAccent: '0 0 20px rgba(6,182,212,0.25)',
  },
  spacing: {
    xs: '0.25rem', sm: '0.5rem', md: '1rem',
    lg: '1.5rem', xl: '2rem', '2xl': '3rem', '3xl': '4rem',
  },
  typography: {
    fontSans: "'Inter', 'system-ui', sans-serif",
    fontMono: "'JetBrains Mono', 'Fira Code', monospace",
    scale: {
      xs: '0.75rem', sm: '0.875rem', base: '1rem',
      lg: '1.125rem', xl: '1.25rem', '2xl': '1.5rem',
      '3xl': '1.875rem', '4xl': '2.25rem',
    },
  },
  motion: {
    fast: '150ms ease-out',
    normal: '250ms ease-out',
    slow: '400ms ease-out',
    spring: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
    easeGlass: 'cubic-bezier(0.16, 1, 0.3, 1)',
  },
  zIndex: {
    base: 0, raised: 10, dropdown: 100,
    sticky: 200, overlay: 300, modal: 400, toast: 500,
  },
  breakpoints: {
    sm: '640px', md: '768px', lg: '1024px', xl: '1280px', '2xl': '1536px',
  },
};

export type Tokens = typeof tokens;
