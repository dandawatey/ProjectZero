# Google Stitch vs /ui-ux-pro-max — Decision Guidelines

## TL;DR

| Question | Answer |
|---|---|
| Need a full website/page fast, from scratch? | **Google Stitch** |
| Building components inside existing codebase? | **/ui-ux-pro-max** |
| Need design decisions (colors, fonts, patterns)? | **/ui-ux-pro-max** |
| Prototyping for stakeholder sign-off? | **Google Stitch** |
| Implementing inside React/Vue/Svelte stack? | **/ui-ux-pro-max** |
| Exporting static HTML for guide/ or marketing? | **Google Stitch** |
| UX review / accessibility audit? | **/ui-ux-pro-max** |

---

## What Each Tool Does

### Google Stitch
AI-powered **website generator**. Input: natural language prompt. Output: complete HTML/CSS/JS page.

- Generates full-page layouts end-to-end
- No codebase context — works from blank slate
- Output is static HTML; requires post-processing to integrate into React stack
- Best for: landing pages, marketing sites, product pages, documentation portals
- Hosted tool — requires browser session at stitch.withgoogle.com

### /ui-ux-pro-max
AI-powered **design intelligence layer**. Input: task + codebase. Output: design decisions, component code, UX guidance.

- 50+ styles, 161 palettes, 57 font pairings, 99 UX guidelines built-in
- Works inside your existing stack (React, Next.js, Vue, Tailwind, shadcn/ui, etc.)
- Understands ProjectZero design tokens (`src/design/tokens.ts`)
- Best for: components, pages within app, design reviews, accessibility audits
- Runs in-context — no external tool required

---

## Decision Tree

```
Need UI work?
│
├─ Starting from ZERO (no existing codebase page)?
│   ├─ Yes → Static site / marketing / docs portal?
│   │         └─ Yes → GOOGLE STITCH → export → run through /ui-ux-pro-max for token alignment
│   │
│   └─ No → Building inside React app? → /UI-UX-PRO-MAX
│
├─ Adding to EXISTING page or component?
│   └─ Always → /UI-UX-PRO-MAX
│
├─ Need DESIGN DECISIONS (palette, typography, spacing)?
│   └─ Always → /UI-UX-PRO-MAX
│
├─ Need PROTOTYPE for stakeholder review (speed > code quality)?
│   └─ Google Stitch → iterate fast → sign off → rebuild properly with /ui-ux-pro-max
│
└─ Need UX AUDIT / accessibility review?
    └─ Always → /UI-UX-PRO-MAX
```

---

## Use Together (The Pipeline)

For new web properties, use **both in sequence**:

```
1. Google Stitch    → generate full-page layout quickly
2. /ui-ux-pro-max   → review output, enforce tokens, fix a11y, align to design system
3. FrontendDev      → componentize into React, wire up data
```

This gives you: speed of AI generation + quality of governed design system.

---

## Concrete Scenarios

### Scenario A — New marketing landing page
> "Build a landing page for ProductX"

→ **Google Stitch first.**  
Prompt Stitch with brand colors, sections needed, tone.  
Export HTML. Then run `/ui-ux-pro-max` to align tokens, fix contrast, add animations.

### Scenario B — New dashboard page inside Control Tower
> "Add a metrics dashboard to the React app"

→ **Skip Stitch. Use /ui-ux-pro-max directly.**  
Stitch output is static HTML — converting to React components costs more than building with pro-max directly inside the stack.

### Scenario C — Component redesign
> "Redesign the approval card component"

→ **Skip Stitch. /ui-ux-pro-max only.**  
Stitch has no knowledge of existing components, props, or state. Pro-max works in-context.

### Scenario D — Stakeholder prototype (speed critical)
> "I need something to show the client tomorrow"

→ **Google Stitch.**  
Generate in minutes. Polish with pro-max if time allows. Not for production — for approval.

### Scenario E — Design system choice
> "What font pairing and color palette for the new product?"

→ **Skip Stitch. /ui-ux-pro-max only.**  
Pro-max has 161 palettes + 57 font pairings with reasoning. Stitch has no design intelligence, just generation.

### Scenario F — New guide/ documentation page
> "Add a page to the guide for the new agent"

→ **Stitch optional, /ui-ux-pro-max preferred.**  
Guide pages follow an established HTML template. Use the template. Stitch adds no value here.

---

## Hard Rules

| Rule | Detail |
|---|---|
| Never ship Stitch output raw | Always pass through /ui-ux-pro-max quality check first |
| Never use Stitch for component work | Stitch produces pages, not components |
| Never use Stitch inside React codebase | Export mismatch → more work than building direct |
| Always use /ui-ux-pro-max for a11y | Stitch does not enforce WCAG AA |
| Always align Stitch output to tokens.ts | Stitch generates its own CSS vars — map them before integrating |
| Stitch for speed, pro-max for quality | They are complementary, not competing |
