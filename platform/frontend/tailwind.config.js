/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}', './.storybook/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      colors: {
        glass: {
          white: 'rgba(255,255,255,0.08)',
          'white-md': 'rgba(255,255,255,0.12)',
          dark: 'rgba(0,0,0,0.25)',
        },
        brand: {
          primary: '#6366f1',
          accent: '#06b6d4',
        },
      },
      backdropBlur: {
        xs: '4px',
        sm: '8px',
        DEFAULT: '16px',
        lg: '24px',
        xl: '40px',
      },
      boxShadow: {
        glass: '0 4px 24px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.08)',
        'glass-md': '0 8px 32px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.10)',
        'glass-lg': '0 16px 48px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.12)',
        glow: '0 0 20px rgba(99,102,241,0.25)',
        'glow-accent': '0 0 20px rgba(6,182,212,0.25)',
      },
      animation: {
        'fade-in': 'fadeIn 250ms ease-out',
        'slide-up': 'slideUp 250ms ease-out',
        'glass-shimmer': 'glassShimmer 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
        slideUp: { '0%': { opacity: '0', transform: 'translateY(8px)' }, '100%': { opacity: '1', transform: 'translateY(0)' } },
        glassShimmer: {
          '0%, 100%': { borderColor: 'rgba(255,255,255,0.10)' },
          '50%': { borderColor: 'rgba(255,255,255,0.20)' },
        },
      },
    },
  },
  plugins: [],
};
