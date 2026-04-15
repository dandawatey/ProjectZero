# Command: /design-system-init

## Purpose
Scaffold a full design system: color tokens, typography scale, spacing, Framer Motion variants, Storybook, and base component library — wired into the product from day one.

## Trigger
- Auto-run during `/bootstrap-product` (Step 12)
- Manual: `/design-system-init` after bootstrap if skipped

## Flags

| Flag | Effect |
|------|--------|
| `--framework=next\|react\|vue` | Override framework detection |
| `--pm=npm\|yarn\|pnpm\|bun` | Override package manager detection |
| `--skip=storybook` | Skip Storybook install (tokens + motion still created) |
| `--skip=framer` | Skip Framer Motion (use CSS transitions only) |
| `--theme=light\|dark\|both` | Default theme mode (default: both) |
| `--brand-color=#hex` | Seed primary brand color for palette generation |

---

## Step-by-Step Process

### Step 1: Detect Environment

Scan `package.json` (or `package.json` siblings) for:

| Signal | Detected As |
|--------|-------------|
| `next` in deps | Next.js |
| `react` + no `next` | React (Vite/CRA) |
| `vue` | Vue 3 |
| `svelte` | Svelte |
| `yarn.lock` | yarn |
| `pnpm-lock.yaml` | pnpm |
| `bun.lockb` | bun |
| else | npm |

Report: `Framework: Next.js 14 | Package manager: pnpm`

---

### Step 2: Install Dependencies

```bash
# Core design system
{pm} add framer-motion clsx class-variance-authority

# Storybook (framework-aware)
npx storybook@latest init --skip-install
{pm} install

# Storybook addons
{pm} add -D @storybook/addon-docs @storybook/addon-a11y \
  @storybook/addon-themes @storybook/test
```

Framework-specific Storybook builder:
- Next.js → `@storybook/nextjs`
- Vite/React → `@storybook/react-vite`
- Vue → `@storybook/vue3-vite`

---

### Step 3: Design Token File

Create `src/design-system/tokens.ts`:

```ts
export const colors = {
  // Brand palette (5 shades per semantic role)
  brand: {
    50:  '#f0f9ff',
    100: '#e0f2fe',
    200: '#bae6fd',
    300: '#7dd3fc',
    400: '#38bdf8',
    500: '#0ea5e9',   // primary
    600: '#0284c7',
    700: '#0369a1',
    800: '#075985',
    900: '#0c4a6e',
    950: '#082f49',
  },
  neutral: {
    0:   '#ffffff',
    50:  '#f8fafc',
    100: '#f1f5f9',
    200: '#e2e8f0',
    300: '#cbd5e1',
    400: '#94a3b8',
    500: '#64748b',
    600: '#475569',
    700: '#334155',
    800: '#1e293b',
    900: '#0f172a',
    950: '#020617',
  },
  semantic: {
    success: { bg: '#f0fdf4', text: '#166534', border: '#bbf7d0' },
    warning: { bg: '#fffbeb', text: '#92400e', border: '#fde68a' },
    error:   { bg: '#fef2f2', text: '#991b1b', border: '#fecaca' },
    info:    { bg: '#eff6ff', text: '#1e40af', border: '#bfdbfe' },
  },
}

export const typography = {
  fontFamily: {
    sans:  'var(--font-sans, ui-sans-serif, system-ui, sans-serif)',
    mono:  'var(--font-mono, ui-monospace, "Cascadia Code", monospace)',
    serif: 'var(--font-serif, ui-serif, Georgia, serif)',
  },
  fontSize: {
    xs:   ['0.75rem',  { lineHeight: '1rem' }],
    sm:   ['0.875rem', { lineHeight: '1.25rem' }],
    base: ['1rem',     { lineHeight: '1.5rem' }],
    lg:   ['1.125rem', { lineHeight: '1.75rem' }],
    xl:   ['1.25rem',  { lineHeight: '1.75rem' }],
    '2xl':['1.5rem',   { lineHeight: '2rem' }],
    '3xl':['1.875rem', { lineHeight: '2.25rem' }],
    '4xl':['2.25rem',  { lineHeight: '2.5rem' }],
  },
  fontWeight: { normal: '400', medium: '500', semibold: '600', bold: '700' },
}

export const spacing = {
  px: '1px', 0: '0', 0.5: '0.125rem', 1: '0.25rem',
  2: '0.5rem', 3: '0.75rem', 4: '1rem', 5: '1.25rem',
  6: '1.5rem', 8: '2rem', 10: '2.5rem', 12: '3rem',
  16: '4rem', 20: '5rem', 24: '6rem', 32: '8rem',
}

export const radii = {
  none: '0', sm: '0.125rem', base: '0.25rem', md: '0.375rem',
  lg: '0.5rem', xl: '0.75rem', '2xl': '1rem', '3xl': '1.5rem', full: '9999px',
}

export const shadows = {
  sm:  '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  base:'0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
  md:  '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg:  '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl:  '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  none:'none',
}

export const zIndex = {
  base: 0, raised: 1, dropdown: 10, sticky: 20,
  overlay: 30, modal: 40, popover: 50, toast: 60,
}

export const breakpoints = {
  sm: '640px', md: '768px', lg: '1024px', xl: '1280px', '2xl': '1536px',
}
```

---

### Step 4: Framer Motion Variants

Create `src/design-system/motion.ts`:

```ts
import type { Variants, Transition } from 'framer-motion'

// Base transitions
export const transitions = {
  fast:    { type: 'tween', duration: 0.15, ease: 'easeOut' } satisfies Transition,
  base:    { type: 'tween', duration: 0.25, ease: 'easeOut' } satisfies Transition,
  slow:    { type: 'tween', duration: 0.4,  ease: 'easeInOut' } satisfies Transition,
  spring:  { type: 'spring', stiffness: 400, damping: 30 } satisfies Transition,
  bounce:  { type: 'spring', stiffness: 500, damping: 20 } satisfies Transition,
} as const

// Reusable page/section variants
export const fadeIn: Variants = {
  hidden:  { opacity: 0 },
  visible: { opacity: 1, transition: transitions.base },
  exit:    { opacity: 0, transition: transitions.fast },
}

export const fadeUp: Variants = {
  hidden:  { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: transitions.base },
  exit:    { opacity: 0, y: -8, transition: transitions.fast },
}

export const fadeDown: Variants = {
  hidden:  { opacity: 0, y: -16 },
  visible: { opacity: 1, y: 0, transition: transitions.base },
  exit:    { opacity: 0, y: 8, transition: transitions.fast },
}

export const slideInLeft: Variants = {
  hidden:  { opacity: 0, x: -24 },
  visible: { opacity: 1, x: 0, transition: transitions.base },
  exit:    { opacity: 0, x: 24, transition: transitions.fast },
}

export const scaleIn: Variants = {
  hidden:  { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1, transition: transitions.spring },
  exit:    { opacity: 0, scale: 0.95, transition: transitions.fast },
}

export const stagger = (staggerChildren = 0.07, delayChildren = 0): Variants => ({
  hidden:  {},
  visible: { transition: { staggerChildren, delayChildren } },
})

// Component-level motion presets
export const buttonTap   = { scale: 0.97, transition: transitions.fast }
export const cardHover   = { y: -4, boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.15)', transition: transitions.base }
export const overlayBg   = { hidden: { opacity: 0 }, visible: { opacity: 1 } }
export const drawerSlide = {
  right: {
    hidden:  { x: '100%', opacity: 0 },
    visible: { x: 0, opacity: 1, transition: transitions.spring },
    exit:    { x: '100%', opacity: 0, transition: transitions.base },
  },
  bottom: {
    hidden:  { y: '100%', opacity: 0 },
    visible: { y: 0, opacity: 1, transition: transitions.spring },
    exit:    { y: '100%', opacity: 0, transition: transitions.base },
  },
}
```

---

### Step 5: Base Component Scaffold

Create each component as `src/design-system/components/<Name>/<Name>.tsx` + `<Name>.stories.tsx`.

**Components to create:**

| Component | Variants | States |
|-----------|----------|--------|
| `Button` | primary, secondary, ghost, outline, destructive | default, hover, active, loading, disabled |
| `Input` | default, error, success | empty, focused, filled, disabled |
| `Card` | default, elevated, interactive | default, hover |
| `Badge` | default, success, warning, error, info | — |
| `Spinner` | sm, md, lg | — |
| `Avatar` | image, initials | sm, md, lg |

Each component:
- Uses `clsx` + `class-variance-authority` for variant logic
- Accepts `motion` prop (boolean) to opt into Framer Motion animation
- Fully typed with TypeScript
- Exports a `.stories.tsx` with all variants displayed

**Button example:**
```tsx
// src/design-system/components/Button/Button.tsx
import { motion } from 'framer-motion'
import { cva, type VariantProps } from 'class-variance-authority'
import { buttonTap } from '../../motion'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        primary:     'bg-brand-600 text-white hover:bg-brand-700',
        secondary:   'bg-neutral-100 text-neutral-900 hover:bg-neutral-200',
        ghost:       'hover:bg-neutral-100 text-neutral-700',
        outline:     'border border-neutral-300 bg-transparent hover:bg-neutral-50',
        destructive: 'bg-red-600 text-white hover:bg-red-700',
      },
      size: {
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 text-sm',
        lg: 'h-12 px-6 text-base',
      },
    },
    defaultVariants: { variant: 'primary', size: 'md' },
  }
)

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>,
  VariantProps<typeof buttonVariants> {
  loading?: boolean
  animate?: boolean
}

export function Button({ variant, size, loading, animate = true, children, className, ...props }: ButtonProps) {
  const Comp = animate ? motion.button : 'button'
  return (
    <Comp
      className={buttonVariants({ variant, size, className })}
      whileTap={animate ? buttonTap : undefined}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading && <Spinner size="sm" />}
      {children}
    </Comp>
  )
}
```

---

### Step 6: Index Barrel

Create `src/design-system/index.ts`:
```ts
export * from './tokens'
export * from './motion'
export * from './components/Button/Button'
export * from './components/Input/Input'
export * from './components/Card/Card'
export * from './components/Badge/Badge'
export * from './components/Spinner/Spinner'
export * from './components/Avatar/Avatar'
```

---

### Step 7: Storybook Configuration

**`.storybook/main.ts`:**
```ts
import type { StorybookConfig } from '@storybook/nextjs'  // or react-vite

const config: StorybookConfig = {
  stories: ['../src/**/*.stories.@(ts|tsx|mdx)'],
  addons: [
    '@storybook/addon-docs',
    '@storybook/addon-a11y',
    '@storybook/addon-themes',
    '@storybook/addon-viewport',
  ],
  framework: { name: '@storybook/nextjs', options: {} },
  docs: { autodocs: 'tag' },
}
export default config
```

**`.storybook/preview.tsx`:**
```tsx
import type { Preview } from '@storybook/react'
import { themes } from '@storybook/theming'

const preview: Preview = {
  parameters: {
    layout: 'centered',
    docs: { theme: themes.dark },
    backgrounds: {
      default: 'light',
      values: [
        { name: 'light', value: '#ffffff' },
        { name: 'dark',  value: '#0f172a' },
        { name: 'brand', value: '#0ea5e9' },
      ],
    },
  },
}
export default preview
```

---

### Step 8: package.json Scripts

Append to product `package.json`:
```json
{
  "scripts": {
    "storybook":       "storybook dev -p 6006",
    "storybook:build": "storybook build",
    "storybook:test":  "test-storybook"
  }
}
```

---

### Step 9: Validate

```bash
{pm} run storybook:build  # must exit 0
```

If build fails → log error, attempt auto-fix (missing peer deps, wrong framework config), retry once.

---

### Step 10: Report

```
Design System Init
══════════════════
Framework:     Next.js 14
Package mgr:   pnpm
Storybook:     ✓ 6.0.0 (6006)
Framer Motion: ✓ 11.x
Tokens:        ✓ src/design-system/tokens.ts
Motion:        ✓ src/design-system/motion.ts
Components:    ✓ Button · Input · Card · Badge · Spinner · Avatar
Stories:       ✓ 6 stories scaffolded

Run: pnpm storybook
```

---

## Required Inputs
- Product root (from bootstrap context)
- Framework (auto-detected or `--framework` flag)
- Brand color (optional — default: blue-sky palette)

## Outputs
- `src/design-system/tokens.ts`
- `src/design-system/motion.ts`
- `src/design-system/index.ts`
- `src/design-system/components/` (6 base components + stories)
- `.storybook/main.ts` + `.storybook/preview.tsx`
- `package.json` updated with storybook scripts

## Failure Handling
- Framework not detected → prompt user, block
- Storybook install fails → log deps, offer `--skip=storybook`
- Build fails → auto-fix peer deps, retry once, then warn + continue

## Invoked Agents
- `frontend-agent` — component scaffold, story generation
- `design-agent` — token palette, motion curves

## Related Commands
- `/component-create` — add new components to design system
- `/component-review` — audit existing components against tokens
- `/ui-audit` — check production UI against design system compliance

## Next Command
After bootstrap: `/spec` → stories reference design system components
