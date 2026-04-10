# Design Token Rules

## Colors
- Primary: brand color scale (50-950)
- Secondary: accent color scale
- Semantic: success (green), warning (amber), error (red), info (blue)
- Neutral: gray scale for text, borders, backgrounds
- Never use hex/rgb directly — always reference tokens

## Typography
- Font family: system font stack (fast, native feel)
- Size scale: xs (12px), sm (14px), base (16px), lg (18px), xl (20px), 2xl (24px), 3xl (30px), 4xl (36px)
- Weight: normal (400), medium (500), semibold (600), bold (700)
- Line height: tight (1.25), normal (1.5), relaxed (1.75)

## Spacing
- Base unit: 4px
- Scale: 0, 1 (4px), 2 (8px), 3 (12px), 4 (16px), 5 (20px), 6 (24px), 8 (32px), 10 (40px), 12 (48px), 16 (64px)
- Use spacing tokens for padding, margin, gap

## Borders
- Width: 1px (default), 2px (emphasis)
- Radius: sm (4px), md (8px), lg (12px), full (9999px)

## Shadows
- sm: subtle depth (cards)
- md: moderate depth (dropdowns)
- lg: strong depth (modals)
- xl: maximum depth (popovers)

## Breakpoints
- sm: 640px
- md: 768px
- lg: 1024px
- xl: 1280px

## Rules
1. All visual properties must use tokens
2. No hardcoded values in application code
3. New tokens require design review
4. Token changes are breaking changes — PR required
