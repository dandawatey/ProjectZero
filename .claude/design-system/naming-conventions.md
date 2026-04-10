# Naming Conventions

## Components
- PascalCase: `Button`, `DataTable`, `UserProfileCard`
- Folder name matches component name

## Files
- kebab-case: `user-profile-card.tsx`, `data-table.test.tsx`
- Stories: `component-name.stories.tsx`
- Tests: `component-name.test.tsx`

## Tokens
- kebab-case with category prefix: `color-primary-500`, `spacing-4`, `font-size-lg`

## CSS
- BEM or CSS Modules (scoped by default)
- No global styles except reset/tokens
- Class names: kebab-case

## Props
- camelCase: `isLoading`, `onSubmit`, `errorMessage`
- Boolean props: `is`/`has` prefix: `isDisabled`, `hasError`
- Event handlers: `on` prefix: `onClick`, `onChange`
