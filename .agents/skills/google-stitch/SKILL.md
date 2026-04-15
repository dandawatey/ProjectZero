---
name: google-stitch
description: Generate, iterate, and export production-ready websites using Google Stitch (AI-powered web builder). Use this skill when building landing pages, marketing sites, product pages, or any web presence that benefits from AI-generated layouts and component scaffolding. NOT for component work inside existing React apps — use /ui-ux-pro-max for that. See WHEN-TO-USE.md for full decision guidelines.
author: projectzero
version: "1.1"
tags:
  - ui
  - ux
  - design
  - website
  - google-stitch
  - frontend
---

# Google Stitch — Web Generation Skill

Google Stitch is an AI-powered website builder that generates complete, styled, responsive web pages from natural language prompts. It outputs clean HTML/CSS/JS that can be exported and integrated into any codebase.

## When to Use This Skill

- Building landing pages, marketing sites, product pages, or documentation portals
- Rapidly prototyping full-page layouts before React component build-out
- Generating visual wireframe-to-code for stakeholder review
- Bootstrapping new web properties within a product line
- Any task where "build me a website for X" is faster than composing from scratch

## Workflow

### Step 1 — Prompt Design
Write a structured Stitch prompt covering:
```
Page type: [landing page / product page / documentation / dashboard / marketing]
Brand identity: [colors, fonts, tone — reference design tokens if available]
Key sections: [hero, features, pricing, CTA, footer — list in order]
Content: [headlines, body copy, placeholder vs real content]
Constraints: [accessibility WCAG AA, dark mode, mobile-first, no external dependencies]
```

### Step 2 — Generate via Google Stitch
Navigate to: https://stitch.withgoogle.com
- Paste structured prompt
- Review generated layout
- Iterate with follow-up prompts: "make hero taller", "add a features grid with 3 columns", "use glass card style"

### Step 3 — Export and Integrate
Export options:
- **HTML export**: single-file output — place in `guide/` or `public/`
- **Component export**: break into React components, place in `src/components/`
- **Design token alignment**: map Stitch CSS variables to `src/design/tokens.ts`

### Step 4 — Quality Gate
After export:
- [ ] Validate WCAG AA contrast ratios (use axe DevTools or Lighthouse)
- [ ] Test responsive breakpoints: 375px, 768px, 1280px, 1920px
- [ ] Remove inline styles — move to Tailwind utilities or CSS modules
- [ ] Replace placeholder images with real assets or Unsplash CDN URLs
- [ ] Verify no hardcoded colors — all values from design tokens

## Prompt Patterns

### Landing Page
```
Build a SaaS landing page for [product].
Hero: large headline + subtitle + dual CTA buttons (primary/ghost).
Features: 3-column icon grid. Social proof: logo strip. Pricing: 3-tier cards.
Footer: links + newsletter input. Dark background, glassmorphism cards,
indigo/cyan brand palette. Mobile-first. WCAG AA.
```

### Product Dashboard Page
```
Build a dashboard homepage for [product].
Top nav with logo + user avatar. Sidebar: 6 nav items with icons.
Main: KPI stat cards (4x), recent activity table, progress chart placeholder.
Glass surface cards, dark mode, Inter font. No JS dependencies in export.
```

### Documentation Portal
```
Build a developer docs portal for [product].
Header: logo + search + dark/light toggle. Sidebar: collapsible nav tree.
Main: MDX-ready content area with breadcrumbs. Right rail: on-page TOC.
Clean minimal aesthetic, monospace code blocks, blue accent links.
```

## Integration with ProjectZero Design System

When integrating Stitch output with `src/design/tokens.ts`:

```typescript
// Map Stitch CSS vars → tokens
// Stitch: --color-primary: #6366f1  →  tokens.colors.brand.primary
// Stitch: --radius-card: 16px       →  tokens.radius.xl
// Stitch: --blur-panel: 16px        →  tokens.blur.DEFAULT
```

Run `cn()` conversion on all conditional className strings.

## Guardrails

- ⛔ Never ship Stitch output directly — always validate tokens, a11y, responsiveness
- ⛔ Never commit API keys or auth tokens embedded by Stitch export
- ⛔ Never keep placeholder lorem ipsum in production pages
- ⛔ Do not override ProjectZero design tokens with Stitch-generated values; align Stitch to tokens
- ⛔ External fonts loaded by Stitch — verify they are already in the approved font stack (Inter, JetBrains Mono)

## References

- Google Stitch: https://stitch.withgoogle.com
- Design tokens: `platform/frontend/src/design/tokens.ts`
- Tailwind config: `platform/frontend/tailwind.config.js`
- Component library: `platform/frontend/src/components/ui/index.ts`
