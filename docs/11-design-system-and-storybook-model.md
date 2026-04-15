# 11 - Design System and Storybook Model

## Overview

Design system initializes automatically during `/bootstrap-product` (Step 10 of 13). No separate invocation needed for new products. Can be re-run manually with `/design-system-init`.

Installs: `framer-motion`, `clsx`, `class-variance-authority`, Storybook.

## Auto-Bootstrap (Step 10 of 13)

`/design-system-init` fires as `DesignSystemInitActivity` inside `BootstrapProductWorkflow`. It:

1. Installs deps: `framer-motion clsx class-variance-authority`
2. Installs Storybook + addons
3. Creates `src/design-system/tokens.ts`
4. Creates `src/design-system/motion.ts`
5. Scaffolds `src/design-system/components/` with 6 base components
6. Creates `.storybook/main.ts` + `.storybook/preview.tsx`
7. Adds `package.json` scripts

Skip flags:
```bash
/bootstrap-product --name "MyProduct" --skip=design-system   # skip entire DS
/bootstrap-product --name "MyProduct" --skip=storybook       # DS tokens/motion only
/bootstrap-product --name "MyProduct" --skip=framer          # no framer-motion
```

## Design Tokens (`src/design-system/tokens.ts`)

Single TypeScript file. No JSON intermediary for product repos.

### Colors

Three tiers — brand primitives, neutral scale, semantic aliases:

```typescript
export const colors = {
  brand: {
    50: '#eff6ff', 100: '#dbeafe', 200: '#bfdbfe',
    500: '#3b82f6', 600: '#2563eb', 700: '#1d4ed8',
    900: '#1e3a5f',
  },
  neutral: {
    0: '#ffffff', 50: '#f8fafc', 100: '#f1f5f9',
    200: '#e2e8f0', 300: '#cbd5e1', 400: '#94a3b8',
    500: '#64748b', 600: '#475569', 700: '#334155',
    800: '#1e293b', 900: '#0f172a',
  },
  semantic: {
    primary:        '#2563eb',
    primaryHover:   '#1d4ed8',
    background:     '#f8fafc',
    surface:        '#ffffff',
    border:         '#e2e8f0',
    textPrimary:    '#0f172a',
    textSecondary:  '#64748b',
    error:          '#dc2626',
    warning:        '#d97706',
    success:        '#16a34a',
    info:           '#0284c7',
  },
};
```

### Typography

```typescript
export const typography = {
  fontFamily: {
    sans: 'Inter, system-ui, -apple-system, sans-serif',
    mono: 'JetBrains Mono, Menlo, monospace',
  },
  fontSize: {
    xs: '0.75rem', sm: '0.875rem', base: '1rem',
    lg: '1.125rem', xl: '1.25rem',
    '2xl': '1.5rem', '3xl': '1.875rem', '4xl': '2.25rem',
  },
  fontWeight: { normal: 400, medium: 500, semibold: 600, bold: 700 },
  lineHeight: { tight: 1.25, snug: 1.375, normal: 1.5, relaxed: 1.625 },
};
```

### Spacing, Radii, Shadows, Z-Index, Breakpoints

```typescript
export const spacing = {
  px: '1px', 0: '0', 1: '0.25rem', 2: '0.5rem', 3: '0.75rem',
  4: '1rem', 5: '1.25rem', 6: '1.5rem', 8: '2rem', 10: '2.5rem',
  12: '3rem', 16: '4rem', 20: '5rem', 24: '6rem',
};

export const radii = {
  none: '0', sm: '0.25rem', base: '0.375rem', md: '0.5rem',
  lg: '0.75rem', xl: '1rem', '2xl': '1.5rem', full: '9999px',
};

export const shadows = {
  sm:  '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  base:'0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
  md:  '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg:  '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl:  '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
};

export const zIndex = {
  base: 0, raised: 10, dropdown: 100, sticky: 200,
  overlay: 300, modal: 400, toast: 500,
};

export const breakpoints = {
  sm: '640px', md: '768px', lg: '1024px', xl: '1280px', '2xl': '1536px',
};
```

## Motion (`src/design-system/motion.ts`)

Framer Motion variants + transition presets for consistent animation across the product.

### Transition Presets

```typescript
export const transitions = {
  fast:    { duration: 0.15, ease: [0.4, 0, 0.2, 1] },
  base:    { duration: 0.2,  ease: [0.4, 0, 0.2, 1] },
  slow:    { duration: 0.3,  ease: [0.4, 0, 0.2, 1] },
  spring:  { type: 'spring', stiffness: 400, damping: 30 },
  bounce:  { type: 'spring', stiffness: 600, damping: 20 },
};
```

### Variants

```typescript
export const variants = {
  fadeIn: {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: transitions.base },
    exit:   { opacity: 0, transition: transitions.fast },
  },
  fadeUp: {
    hidden:  { opacity: 0, y: 8 },
    visible: { opacity: 1, y: 0, transition: transitions.base },
    exit:    { opacity: 0, y: 8, transition: transitions.fast },
  },
  scaleIn: {
    hidden:  { opacity: 0, scale: 0.95 },
    visible: { opacity: 1, scale: 1, transition: transitions.spring },
    exit:    { opacity: 0, scale: 0.95, transition: transitions.fast },
  },
  stagger: {
    hidden:  { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.07 } },
  },
  drawerSlide: {
    hidden:  { x: '100%' },
    visible: { x: 0, transition: transitions.slow },
    exit:    { x: '100%', transition: transitions.base },
  },
  buttonTap: { scale: 0.97, transition: transitions.fast },
  cardHover: { y: -2, shadow: shadows.lg, transition: transitions.base },
};
```

Usage:
```tsx
import { motion, AnimatePresence } from 'framer-motion';
import { variants } from '@/design-system/motion';

<motion.div variants={variants.fadeUp} initial="hidden" animate="visible" exit="exit">
  Content
</motion.div>
```

## Base Components (`src/design-system/components/`)

Six components created at bootstrap. Each has implementation + `.stories.tsx`:

| Component | Variants / Props | Stories |
|---|---|---|
| `Button` | primary / secondary / ghost / danger / outline; sm/md/lg; loading, disabled | Primary, AllVariants, Sizes, Loading, Disabled |
| `Input` | default / error / success; sm/md/lg; label, hint, error message | Default, WithLabel, States, Sizes |
| `Card` | default / elevated / outlined; clickable | Default, Elevated, Clickable |
| `Badge` | default / success / warning / error / info; sm/md | AllVariants, AllSizes |
| `Spinner` | sm / md / lg / xl; with label | Sizes, WithLabel |
| `Avatar` | image / initials / fallback; xs/sm/md/lg/xl | WithImage, WithInitials, Sizes |

All components use `clsx` + `class-variance-authority` for variant management. All accept standard HTML attributes + `className` override.

## Storybook

Config lives in `.storybook/`:
- `main.ts` — Vite builder, autodocs, addons (a11y, controls, actions, viewport)
- `preview.tsx` — global decorators (theme provider, motion AnimatePresence wrapper)

Scripts in `package.json`:
```json
{
  "storybook":       "storybook dev -p 6006",
  "storybook:build": "storybook build",
  "storybook:test":  "test-storybook"
}
```

Run: `npm run storybook` → `localhost:6006`

## Ongoing: Design System Commands

After bootstrap, use these commands for ongoing component work:

| Command | Purpose |
|---|---|
| `/component-create --name X --module Y` | New component: design → implement → stories → governance chain |
| `/component-review --name X` | Run governance chain (maker → checker → reviewer → approver) |
| `/ui-audit` | Scan entire UI for token compliance, a11y violations, ad-hoc styles |

## Architecture: Where Things Live

```
src/
  design-system/
    tokens.ts           # All design tokens (colors, spacing, typography, etc.)
    motion.ts           # Framer Motion variants and transition presets
    components/
      Button/
        Button.tsx
        Button.stories.tsx
        index.ts
      Input/
      Card/
      Badge/
      Spinner/
      Avatar/
    index.ts            # Re-exports all tokens + components
  .storybook/
    main.ts
    preview.tsx
```

## UI Governance Rules

1. **Shared components first** — check `src/design-system/components/` before creating anything new
2. **No ad-hoc styles** — all styling via tokens; no hardcoded colors, spacing, or magic numbers
3. **Accessibility mandatory** — WCAG 2.1 AA; keyboard nav, ARIA attrs, 4.5:1 contrast
4. **TypeScript strict** — all props fully typed; no `any`; forwarded refs on all components
5. **Stories required** — every component variant needs a Storybook story before it ships

## Temporal Integration

| Command | Activity/Workflow |
|---|---|
| `/design-system-init` (auto at bootstrap) | `DesignSystemInitActivity` inside `BootstrapProductWorkflow` |
| `/component-create` | `ComponentCreateWorkflow` |
| `/component-review` | Governance child workflow (maker → checker → reviewer → approver) |
| `/ui-audit` | `UIAuditWorkflow` |

All state tracked in Postgres via FastAPI.
