# Storybook Usage Guide — PRJ0-84

## Running Storybook
```bash
cd platform/frontend
npm install
npm run storybook
# Opens at http://localhost:6006
```

## Structure
- **Design System / Foundation** — GlassPanel, Card, Divider, Skeleton
- **Design System / Inputs** — Button, Input, Select, Checkbox, Toggle
- **Design System / Navigation** — Tabs, Breadcrumbs
- **Design System / Feedback** — Badge, Progress, EmptyState, Toast
- **Design System / Data Display** — Table, StatCard, Avatar, Accordion
- **Design System / Layout** — AppShell

## How to Build Screens
1. Open Storybook — browse what exists
2. Import what you need: `import { Card, Button, Badge } from '../components/ui'`
3. Compose your screen from existing components
4. If you need a NEW component: add it to the library first, add story, THEN use it

## Adding Stories
Stories live in `src/stories/`. Pattern: `ComponentName.stories.tsx`.
Use `tags: ['autodocs']` for automatic prop documentation.
