# Component Governance

## Shared Components (packages/ui)
- All reusable components live here
- Adding new component requires PR with design review
- Modifying existing component requires review (may affect all consumers)
- Deprecation: add @deprecated tag → migration guide → 2-sprint grace → remove

## Rules
1. Check packages/ui BEFORE creating any component
2. If similar component exists, extend it (don't create new)
3. New shared component needs: implementation, tests, Storybook stories, accessibility audit
4. One-off components stay in the application (not packages/ui)
5. If an app component is used in 2+ places, promote to packages/ui
