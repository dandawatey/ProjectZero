/**
 * PRJ0-84 Glassmorphism Enterprise Design Rules
 * These constraints keep the UI readable, accessible, and premium.
 */
export const glassmorphismRules = {
  blur: {
    // Use sm for subtle depth, md for panels, lg for modals only
    recommended: 'blur-[16px]',
    modal: 'blur-[24px]',
    // NEVER use blur > 40px — becomes unreadable
    max: 'blur-[40px]',
  },
  opacity: {
    // Surface opacity: keep text contrast WCAG AA (≥4.5:1)
    panelMin: 0.08,
    panelMax: 0.18,
    // Dark overlay for modals
    overlay: 0.6,
  },
  contrast: {
    // Text must remain readable on glass surfaces
    bodyText: 'text-slate-100',       // dark mode
    secondaryText: 'text-slate-400',
    mutedText: 'text-slate-500',
    // Never use pure white text on glass — use slate-100
  },
  surfaces: {
    // Standard glass panel class combinations
    panel: 'bg-white/[0.08] backdrop-blur-[16px] border border-white/[0.10]',
    panelMd: 'bg-white/[0.12] backdrop-blur-[16px] border border-white/[0.16]',
    card: 'bg-white/[0.08] backdrop-blur-[12px] border border-white/[0.10] rounded-xl',
    modal: 'bg-slate-900/80 backdrop-blur-[24px] border border-white/[0.12]',
    input: 'bg-white/[0.06] border border-white/[0.12] focus:border-indigo-500',
  },
  motion: {
    // Use framer-motion variants — keep transitions under 400ms
    pageTransition: { initial: { opacity: 0, y: 8 }, animate: { opacity: 1, y: 0 }, exit: { opacity: 0, y: -8 } },
    panelEntrance: { initial: { opacity: 0, scale: 0.97 }, animate: { opacity: 1, scale: 1 } },
    listItem: { initial: { opacity: 0, x: -8 }, animate: { opacity: 1, x: 0 } },
  },
  accessibility: {
    // Always provide focus rings
    focusRing: 'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900',
    // Reduce motion when preferred
    reducedMotion: '@media (prefers-reduced-motion: reduce)',
    // Min touch target
    minTouchTarget: '44px',
  },
  antiPatterns: [
    'No excessive glow effects — max 1 glow per focal element',
    'No stacking more than 3 glass layers',
    'No blur on text — only on background surfaces',
    'No pure white (#fff) on glass — use rgba with opacity',
    'No backdrop-blur on mobile without perf testing',
    'Tables and forms stay crisp — avoid glass on dense data',
  ],
} as const;
