# PRJ0-84: Glassmorphism Design System — Design Strategy

## Overview
ProjectZero uses a Glassmorphism Enterprise UX design language. All UI is built using the governed component library in `src/components/ui/`. Storybook is the living catalog and source of truth.

## Design Direction: Glassmorphism Enterprise
- Frosted-glass surfaces (backdrop-blur + rgba backgrounds)
- Subtle transparency (8–18% white opacity)
- Soft layered elevation (shadow-glass system)
- Dark mode primary, light mode supported
- WCAG AA accessible contrast
- Framer Motion for interactions (subtle, not flashy)

## Token System
All values come from `src/design/tokens.ts`. Never hardcode colors, spacing, or radii.

## Build Order (Non-Negotiable)
1. Tokens → 2. Theme → 3. Storybook → 4. Components → 5. Layout → 6. Motion → 7. Templates → 8. App modules

## Brand Configuration
Edit `src/design/theme.ts` → `defaultBrand` to set org name, colors, mode, density.
