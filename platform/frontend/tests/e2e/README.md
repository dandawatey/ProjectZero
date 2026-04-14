# Playwright E2E Tests — PRJ0-65

## Setup
```bash
cd platform/frontend
npm install
npx playwright install chromium
```

## Run
```bash
# Start dev server first
npm run dev &

# Run tests
npx playwright test

# Headed (see browser)
npx playwright test --headed

# Single spec
npx playwright test tests/e2e/dashboard.spec.ts
```

## Test coverage
- auth.spec.ts — landing page, redirect, login form, wrong credentials
- dashboard.spec.ts — stat cards, project tiles, navigation
- factory-floor.spec.ts — no 401 errors, page renders
- agents.spec.ts — registry tab, execution history tab
- navigation.spec.ts — 6 core pages load without errors
