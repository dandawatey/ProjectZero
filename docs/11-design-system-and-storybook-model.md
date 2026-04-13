# 11 - Design System and Storybook Model

## Overview

ProjectZeroFactory enforces UI governance through a shared design system, component-first development, and Storybook-driven visual testing. No ad-hoc styling is permitted. All UI work uses shared components and design tokens. Every component change goes through the governance chain as a Temporal child workflow.

## Architecture: Where Things Live

Two repos. Two roles. One system.

**Factory repo** (ProjectZeroFactory) -- defines the standards:

```
.claude/design-system/
  tokens/
    colors.json           # Color palette with semantic naming
    typography.json        # Font families, sizes, weights, line heights
    spacing.json           # Spacing scale (4px base unit)
    breakpoints.json       # Responsive breakpoints
    shadows.json           # Box shadow definitions
    borders.json           # Border radii, widths, styles
    motion.json            # Animation durations, easing functions
    z-index.json           # Z-index scale
  components/
    registry.json          # Master list of all shared components
    component-status.json  # Status of each component (draft, review, stable)
  patterns/
    layout-patterns.md     # Standard layout patterns
    form-patterns.md       # Standard form patterns
    navigation-patterns.md # Standard navigation patterns
    feedback-patterns.md   # Standard feedback patterns (loading, error, empty)
  guidelines/
    accessibility.md       # Accessibility standards and implementation guide
    responsive.md          # Responsive design guide
    naming.md              # Component and CSS naming conventions
```

**Product repo** -- contains the implementation:

```
packages/ui/
  src/
    components/
      Button/
        Button.tsx
        Button.stories.tsx
        Button.test.tsx
        Button.module.css
        index.ts
      Input/
      Card/
      Modal/
      Table/
      Form/
      Layout/
      Navigation/
      Feedback/
    hooks/
      useTheme.ts
      useBreakpoint.ts
      useReducedMotion.ts
    tokens/
      index.ts              # Generated from factory .claude/design-system/tokens/
      colors.ts
      typography.ts
      spacing.ts
    utils/
      cn.ts                 # Classname merge utility
      a11y.ts               # Accessibility helpers
    index.ts                # Public API (all exports)
  .storybook/
    main.ts                 # Storybook configuration
    preview.ts              # Global decorators and parameters
    theme.ts                # Storybook theme customization
  package.json
  tsconfig.json
```

Factory defines the rules. Product repo implements them. Storybook runs in the product repo for visual dev and testing.

## Design System Initialization

The `/design-system-init` command triggers a Temporal activity that scaffolds the design system.

```
/design-system-init
```

What happens:
1. Temporal activity `initialize_design_system` fires
2. Creates `.claude/design-system/` structure in the factory with default token standards
3. Scaffolds `packages/ui/` in the product repo with Storybook configuration
4. Creates the initial set of base components (Button, Input, Card, Layout)
5. Configures the token-to-code generation pipeline
6. Sets up Storybook with the project theme
7. Registers completion in Postgres via FastAPI

The default tokens can be customized to match the product's brand. Update the JSON files in `.claude/design-system/tokens/` and run:

```
/design-system-init --regenerate-tokens
```

This regenerates the TypeScript token files in `packages/ui/src/tokens/`.

## Design Tokens

Design tokens are the foundation of visual consistency. They are defined as JSON in the factory `.claude/design-system/tokens/` and consumed by the product repo component library.

### Color Tokens (colors.json)

```json
{
  "primitive": {
    "blue-50": "#EFF6FF",
    "blue-100": "#DBEAFE",
    "blue-500": "#3B82F6",
    "blue-600": "#2563EB",
    "blue-700": "#1D4ED8",
    "gray-50": "#F9FAFB",
    "gray-100": "#F3F4F6",
    "gray-500": "#6B7280",
    "gray-900": "#111827"
  },
  "semantic": {
    "primary": "{primitive.blue-600}",
    "primary-hover": "{primitive.blue-700}",
    "background": "{primitive.gray-50}",
    "surface": "#FFFFFF",
    "text-primary": "{primitive.gray-900}",
    "text-secondary": "{primitive.gray-500}",
    "border": "{primitive.gray-100}",
    "error": "#DC2626",
    "warning": "#F59E0B",
    "success": "#16A34A",
    "info": "{primitive.blue-500}"
  }
}
```

### Spacing Tokens (spacing.json)

```json
{
  "base": 4,
  "scale": {
    "0": "0px",
    "1": "4px",
    "2": "8px",
    "3": "12px",
    "4": "16px",
    "5": "20px",
    "6": "24px",
    "8": "32px",
    "10": "40px",
    "12": "48px",
    "16": "64px",
    "20": "80px",
    "24": "96px"
  }
}
```

### Typography Tokens (typography.json)

```json
{
  "font-family": {
    "sans": "Inter, system-ui, -apple-system, sans-serif",
    "mono": "JetBrains Mono, Menlo, monospace"
  },
  "font-size": {
    "xs": "12px",
    "sm": "14px",
    "base": "16px",
    "lg": "18px",
    "xl": "20px",
    "2xl": "24px",
    "3xl": "30px",
    "4xl": "36px"
  },
  "font-weight": {
    "normal": 400,
    "medium": 500,
    "semibold": 600,
    "bold": 700
  },
  "line-height": {
    "tight": 1.25,
    "normal": 1.5,
    "relaxed": 1.75
  }
}
```

## Storybook Integration

Storybook runs in the product repo at `localhost:6006` (configurable via `STORYBOOK_PORT` in `.env`).

### Purpose

1. **Development environment**: Components are developed in isolation in Storybook before being composed into pages
2. **Visual testing**: Every component has stories that serve as visual regression tests
3. **Documentation**: Storybook is the living component documentation

### Story Structure

Every component has a `.stories.tsx` file with at minimum:

```typescript
// Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'ghost', 'danger'],
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
    },
    disabled: { control: 'boolean' },
  },
};

export default meta;
type Story = StoryObj<typeof Button>;

export const Primary: Story = {
  args: {
    children: 'Button',
    variant: 'primary',
  },
};

export const AllVariants: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '8px' }}>
      <Button variant="primary">Primary</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="ghost">Ghost</Button>
      <Button variant="danger">Danger</Button>
    </div>
  ),
};

export const Disabled: Story = {
  args: {
    children: 'Disabled',
    disabled: true,
  },
};

export const Loading: Story = {
  args: {
    children: 'Loading...',
    loading: true,
  },
};
```

### Required Stories

Every component must have stories for:
- **Default state**: The component with default props
- **All variants**: Every visual variant the component supports
- **Disabled state**: If the component can be disabled
- **Loading state**: If the component has a loading state
- **Error state**: If the component displays errors
- **Empty state**: If the component handles empty data
- **Responsive**: Mobile, tablet, and desktop layouts (if layout changes)
- **Dark mode**: If the product supports dark mode
- **Accessibility**: Stories demonstrating keyboard navigation and screen reader behavior

## Component Creation Workflow

When a new shared component is needed, the `/component-create` command kicks off a Temporal workflow.

### Step 1: Request

```
/component-create --name DataTable --module billing
```

This starts `ComponentCreateWorkflow` in Temporal.

### Step 2: Design Phase (Temporal Activity)

The frontend-design skill produces:
- Component API (props, events)
- Sub-component structure
- Responsive behavior
- Accessibility plan
- Usage examples

### Step 3: Implementation (Temporal Activity)

The frontend-engineer agent:
1. Creates the component directory in `packages/ui/src/components/`
2. Implements the component using design tokens
3. Creates the Storybook stories (all required variants)
4. Writes unit tests
5. Registers the component in `.claude/design-system/components/registry.json`

### Step 4: Governance Chain (Temporal Child Workflow)

Every component goes through the full governance chain, executed as a Temporal child workflow:

```
maker -> checker -> reviewer -> approver
```

The `/component-review` command triggers this:

```
/component-review --name DataTable
```

The review includes:
- Code quality review (code-reviewer skill) -- checker
- Visual review (refactoring-ui skill) -- reviewer
- Accessibility audit (ux-heuristics skill) -- reviewer
- Design system compliance check -- reviewer
- Final approval -- approver

### Step 5: Registration

After passing the governance chain:
- Component status updated to "stable" in `component-status.json`
- Component available for use by all modules
- Storybook documentation published

## UI Audit

The `/ui-audit` command runs a comprehensive audit of the entire UI against design system standards.

```
/ui-audit
```

This triggers a Temporal workflow that:
1. Scans all components in `packages/ui/` for token compliance
2. Validates all stories render without errors
3. Runs accessibility checks (WCAG 2.1 AA) on all stories
4. Checks for ad-hoc styles or hardcoded values
5. Verifies component registry is in sync
6. Produces an audit report with pass/fail per component

## UI Governance Rules

### Rule 1: Shared Components First

Before creating a new component, check:
1. Does the design system already have this component? (Check `packages/ui/src/components/`)
2. Can an existing component be extended or composed to meet the need?
3. If a new component is truly needed, it must go through the `/component-create` workflow

**Enforcement**: The checker agent validates that new UI code does not create ad-hoc components when shared components exist.

### Rule 2: No Ad-Hoc Styles

All styling must use:
- Design tokens (colors, spacing, typography from the token system)
- CSS modules scoped to components
- Utility classes from the design system

**Forbidden**:
- Inline styles with hardcoded values
- Global CSS overrides
- Magic numbers for spacing, colors, or font sizes
- `!important` declarations

**Enforcement**: The reviewer agent (invoking code-reviewer skill) flags ad-hoc styling.

### Rule 3: Accessibility is Not Optional

WCAG 2.1 AA compliance is mandatory. All components must:
- Meet WCAG 2.1 AA standards
- Support keyboard navigation
- Have appropriate ARIA attributes
- Maintain 4.5:1 contrast ratio for normal text, 3:1 for large text
- Support reduced motion preferences
- Work with screen readers

**Enforcement**: The ux-reviewer agent runs accessibility audits on all UI stories. The `/ui-audit` command validates the entire UI.

### Rule 4: Component API Standards

All components must follow:
- **Props-based API**: Data in via props, events out via callbacks
- **TypeScript types**: All props fully typed, no `any`
- **Default props**: Sensible defaults for optional props
- **Forwarded refs**: Components forward refs to their root DOM element
- **Composition**: Prefer composition over configuration (compound components)

## Temporal Integration Summary

| Command | Temporal Workflow/Activity | What It Does |
|---|---|---|
| `/design-system-init` | `initialize_design_system` activity | Scaffolds design system in both repos |
| `/component-create` | `ComponentCreateWorkflow` | Design + implement + govern a new component |
| `/component-review` | Child workflow: maker-checker-reviewer-approver | Governance chain for component approval |
| `/story-create` | Activity within component workflow | Creates Storybook stories for a component |
| `/story-validate` | Activity within UI audit workflow | Validates stories render and pass a11y |
| `/ui-audit` | `UIAuditWorkflow` | Full UI compliance audit |

All state tracked in Postgres via FastAPI. All visibility in Temporal UI at `localhost:8233`.
