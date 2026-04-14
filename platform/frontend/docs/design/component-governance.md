# Component Governance Rules — PRJ0-84

## Rule 1: Use Existing Components First
Before building any UI, check `src/components/ui/`. If the component exists, USE IT.

## Rule 2: No Hardcoded Values
All colors, spacing, radii come from `src/design/tokens.ts`.
Use `cn()` from `src/design/cn.ts` for conditional classNames.

## Rule 3: Adding New Components
1. Create `src/components/ui/YourComponent.tsx`
2. Create `src/stories/YourComponent.stories.tsx` with all states
3. Export from `src/components/ui/index.ts`
4. Document purpose, props, variants in JSDoc

## Rule 4: Naming Convention
- Components: PascalCase (`GlassPanel`, `StatCard`)
- Stories: `ComponentName.stories.tsx`
- Tokens: camelCase within the tokens object

## Rule 5: Accessibility
Every interactive component must have:
- `focus-visible` ring
- ARIA labels where needed
- Keyboard navigation

## Contribution Checklist
- [ ] Component file created in `src/components/ui/`
- [ ] Story created with all variants + states
- [ ] Exported from barrel `index.ts`
- [ ] TypeScript props fully typed
- [ ] No hardcoded design values
- [ ] Accessible (focus ring, ARIA)
- [ ] Dark mode tested
