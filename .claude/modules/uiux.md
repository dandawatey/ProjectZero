# UI/UX Module

## Design System Usage
- All components from `packages/ui` — no ad-hoc components for existing patterns
- Design tokens for all visual properties — no hardcoded colors, sizes, spacing
- Consistent patterns across all pages — same component for same function everywhere

## Accessibility (WCAG 2.1 AA)
- Semantic HTML (use `button` not `div` with onClick)
- ARIA labels for icons, images, and non-text content
- Keyboard navigation for all interactive elements
- Focus indicators visible (never `outline: none` without replacement)
- Color contrast minimum 4.5:1 for text, 3:1 for large text
- Touch targets minimum 44x44px on mobile
- Screen reader testing for all critical flows

## Responsive Design
- Mobile-first approach (design for smallest screen first)
- Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- No horizontal scroll at any breakpoint
- Images responsive with appropriate srcset

## Required States
Every interactive element and data display must handle:
- **Loading**: Skeleton or spinner (never empty/broken UI)
- **Error**: Descriptive message with retry action
- **Empty**: Guidance toward first action (never just blank)
- **Success**: Confirmation with clear next step
- **Disabled**: Visually distinct with tooltip explaining why

## Design Review Checklist
- [ ] Uses design tokens (no hardcoded values)
- [ ] Responsive at all breakpoints
- [ ] Accessible (keyboard, screen reader, contrast)
- [ ] All states handled (loading, error, empty, success)
- [ ] Consistent with existing patterns
- [ ] Touch-friendly on mobile
