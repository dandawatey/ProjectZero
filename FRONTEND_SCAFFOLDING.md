# ProjectZero SaaS — Frontend Scaffolding

**Status**: Design (before /arch)  
**Date**: 2026-04-19  
**Framework**: React 18 + TypeScript + TailwindCSS + Vite  
**Package Manager**: pnpm

---

## 1. Project Structure

```
frontend/
├── public/
│   ├── favicon.ico
│   ├── logo.svg
│   └── logo-dark.svg
├── src/
│   ├── components/
│   │   ├── common/                 # Shared UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Avatar.tsx
│   │   │   ├── Dropdown.tsx
│   │   │   ├── Alert.tsx
│   │   │   ├── Tabs.tsx
│   │   │   ├── Pagination.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   └── Skeleton.tsx
│   │   ├── layout/                 # Layout components
│   │   │   ├── AppLayout.tsx       # Main app wrapper (sidebar + topbar)
│   │   │   ├── Sidebar.tsx         # Nav sidebar
│   │   │   ├── Topbar.tsx          # Header with user menu
│   │   │   ├── BreadcrumbNav.tsx
│   │   │   └── Footer.tsx
│   │   ├── forms/                  # Form components
│   │   │   ├── LoginForm.tsx
│   │   │   ├── SignupForm.tsx
│   │   │   ├── InviteMemberForm.tsx
│   │   │   ├── OrgSettingsForm.tsx
│   │   │   ├── BillingForm.tsx
│   │   │   └── WebhookConfigForm.tsx
│   │   ├── dashboard/              # Dashboard-specific
│   │   │   ├── MetricsCard.tsx
│   │   │   ├── TrendChart.tsx
│   │   │   ├── QuotaIndicator.tsx
│   │   │   ├── WorkflowStatusTable.tsx
│   │   │   ├── RecentActivityFeed.tsx
│   │   │   └── CostAnalysisChart.tsx
│   │   ├── billing/                # Billing-specific
│   │   │   ├── PricingCard.tsx
│   │   │   ├── PricingTable.tsx
│   │   │   ├── UpgradeModal.tsx
│   │   │   ├── UsageBreakdown.tsx
│   │   │   ├── InvoiceTable.tsx
│   │   │   └── StripeCheckout.tsx
│   │   ├── members/                # Member management
│   │   │   ├── MembersTable.tsx
│   │   │   ├── MemberRow.tsx
│   │   │   ├── RoleSelector.tsx
│   │   │   └── RemoveConfirmModal.tsx
│   │   ├── compliance/             # Compliance-specific
│   │   │   ├── AuditLogTable.tsx
│   │   │   ├── AuditFilterBar.tsx
│   │   │   ├── ComplianceChecklist.tsx
│   │   │   ├── ComplianceChart.tsx
│   │   │   ├── SOC2ReportModal.tsx
│   │   │   └── ExportButton.tsx
│   │   ├── auth/                   # Auth components
│   │   │   ├── ProtectedRoute.tsx
│   │   │   ├── MFASetup.tsx
│   │   │   ├── MFAPrompt.tsx
│   │   │   ├── SSOButton.tsx
│   │   │   └── APIKeyGenerator.tsx
│   │   └── workspaces/             # Workspace management
│   │       ├── WorkspaceList.tsx
│   │       ├── WorkspaceCard.tsx
│   │       ├── CreateWorkspaceModal.tsx
│   │       └── WorkspaceSelector.tsx
│   ├── pages/                      # Page components
│   │   ├── auth/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── SignupPage.tsx
│   │   │   ├── ForgotPasswordPage.tsx
│   │   │   └── MFAVerifyPage.tsx
│   │   ├── onboarding/
│   │   │   ├── OnboardingStep1.tsx (welcome)
│   │   │   ├── OnboardingStep2.tsx (invite team)
│   │   │   ├── OnboardingStep3.tsx (choose plan)
│   │   │   └── OnboardingStep4.tsx (complete)
│   │   ├── dashboard/
│   │   │   ├── DashboardPage.tsx   # Home dashboard
│   │   │   └── AgentFleetPage.tsx  # Agent workflows view
│   │   ├── workspaces/
│   │   │   ├── WorkspacesListPage.tsx
│   │   │   └── WorkspaceDetailPage.tsx
│   │   ├── billing/
│   │   │   ├── BillingPage.tsx
│   │   │   ├── PricingPage.tsx
│   │   │   ├── InvoicesPage.tsx
│   │   │   └── UsagePage.tsx
│   │   ├── settings/
│   │   │   ├── SettingsPage.tsx    # Main settings redirect
│   │   │   ├── ProfilePage.tsx
│   │   │   ├── MembersPage.tsx
│   │   │   ├── SecurityPage.tsx    (MFA, SSO, API keys)
│   │   │   └── IntegrationsPage.tsx
│   │   ├── compliance/
│   │   │   ├── CompliancePage.tsx
│   │   │   ├── AuditLogsPage.tsx
│   │   │   └── ReportsPage.tsx
│   │   ├── 404Page.tsx
│   │   └── 500Page.tsx
│   ├── hooks/                      # Custom React hooks
│   │   ├── useAuth.ts              # Auth context + API
│   │   ├── useOrg.ts               # Org context
│   │   ├── useWorkspace.ts         # Workspace context
│   │   ├── useBilling.ts           # Billing API calls
│   │   ├── useFetch.ts             # Generic fetch hook
│   │   ├── useLocalStorage.ts
│   │   ├── useDebounce.ts
│   │   ├── useMediaQuery.ts
│   │   └── usePagination.ts
│   ├── context/                    # React context providers
│   │   ├── AuthContext.tsx
│   │   ├── OrgContext.tsx
│   │   ├── ToastContext.tsx        # Notifications
│   │   └── ModalContext.tsx        # Global modal state
│   ├── services/                   # API client services
│   │   ├── api.ts                  # Axios base config
│   │   ├── auth.service.ts         # Login, signup, SSO
│   │   ├── org.service.ts          # Org CRUD
│   │   ├── billing.service.ts      # Stripe, subscriptions, invoices
│   │   ├── members.service.ts      # User invites, role updates
│   │   ├── workspace.service.ts    # Workspace CRUD
│   │   ├── audit.service.ts        # Audit log queries
│   │   ├── compliance.service.ts   # Report generation
│   │   └── webhook.service.ts      # Integration configs
│   ├── utils/                      # Utility functions
│   │   ├── formatters.ts           # Date, currency, size formatting
│   │   ├── validators.ts           # Form validation rules
│   │   ├── constants.ts            # App-wide constants (tier limits, etc.)
│   │   ├── classNames.ts           # Tailwind classname helper
│   │   └── logger.ts               # Client-side logging
│   ├── types/                      # TypeScript types
│   │   ├── index.ts                # Re-exports
│   │   ├── api.ts                  # API response/request types
│   │   ├── models.ts               # Domain models (User, Org, etc.)
│   │   ├── forms.ts                # Form input types
│   │   └── ui.ts                   # UI-specific types (theme, modal, etc.)
│   ├── styles/                     # Global styles
│   │   ├── globals.css             # Tailwind + global styles
│   │   ├── variables.css           # CSS custom properties (colors, spacing)
│   │   └── animations.css          # Keyframe animations
│   ├── App.tsx                     # Root component
│   ├── main.tsx                    # Entry point
│   └── router.tsx                  # React Router config
├── .env.example
├── .env.local (gitignored)
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.ts
├── package.json
└── pnpm-lock.yaml
```

---

## 2. Page Layouts & Wireframes

### Authentication Pages

**LoginPage** (`/auth/login`)
```
┌─────────────────────────────┐
│                             │
│      ProjectZero Logo       │
│      "AI-Powered Dev"       │
│                             │
│   Email:    [__________]    │
│   Password: [__________]    │
│                             │
│   [ Sign In ]  Forgot pass? │
│                             │
│   ─── OR ───                │
│   [ Sign in with Google ]   │
│   [ Sign in with GitHub ]   │
│                             │
│   Don't have account?       │
│   [ Sign up here ]          │
│                             │
└─────────────────────────────┘
```

**SignupPage** (`/auth/signup`)
```
┌─────────────────────────────┐
│      ProjectZero Logo       │
│      "Start for Free"       │
│                             │
│   Email:        [_______]   │
│   Org Name:     [_______]   │
│   Password:     [_______]   │
│   Confirm Pwd:  [_______]   │
│                             │
│   ☑ I agree to Terms        │
│                             │
│   [ Sign Up ]               │
│                             │
│   Already have account?     │
│   [ Login here ]            │
│                             │
└─────────────────────────────┘
```

### Onboarding Pages

**OnboardingStep1** (Welcome)
```
┌───────────────────────────────┐
│   ProjectZero Onboarding      │
│   Step 1 of 4: Welcome        │
│                               │
│   👋 Welcome to ProjectZero!  │
│                               │
│   Govern AI-driven product    │
│   development with automated  │
│   gates + compliance.         │
│                               │
│   ✓ Multi-tenant isolation    │
│   ✓ RBAC + audit logs         │
│   ✓ Compliance dashboards     │
│                               │
│   [ Next: Invite Team ]       │
│                               │
└───────────────────────────────┘
```

**OnboardingStep2** (Invite Team)
```
┌─────────────────────────────┐
│   Step 2 of 4: Invite Team  │
│                             │
│   Invite email:             │
│   [____________________]     │
│                             │
│   Role: [Engineer ▼]        │
│                             │
│   [+ Add Another]           │
│                             │
│   ┌─────────────────────┐   │
│   │ john@corp.com      │ X │ │ Engineer
│   │ jane@corp.com      │ X │ │ Reviewer
│   └─────────────────────┘   │
│                             │
│   [ Back ] [ Next ]         │
│                             │
└─────────────────────────────┘
```

**OnboardingStep3** (Choose Plan)
```
┌──────────────────────────────────┐
│   Step 3 of 4: Choose Plan       │
│                                  │
│  ┌──────────┐ ┌──────────┐      │
│  │ Starter  │ │ Prof. ✓ │      │
│  │ $0/mo    │ │ $499/mo  │      │
│  │          │ │          │      │
│  │ 1 user   │ │ 50 users │      │
│  │ 1 repo   │ │ 10 repos │      │
│  │ No gates │ │ 4-gate   │      │
│  └──────────┘ └──────────┘      │
│                                  │
│  [ Back ] [ Finish ]             │
│                                  │
└──────────────────────────────────┘
```

### Dashboard Pages

**DashboardPage** (`/dashboard`)
```
┌────────────────────────────────────────┐
│ ☰ Sidebar | Topbar (user, notif, etc) │
├────────────────────────────────────────┤
│                                        │
│  Dashboard                             │
│                                        │
│  ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ 42 Runs  │ │ 5 Repos  │ │ 8 Team │ │
│  │ This mth │ │ Used     │ │ Mbrs   │ │
│  └──────────┘ └──────────┘ └────────┘ │
│  ┌──────────────────────────────────┐ │
│  │ Quota: 5/10 repos [████░░░░░░] 50% │
│  │ Usage: 950/1000 agents [█████░░░]   │
│  └──────────────────────────────────┘ │
│                                        │
│  Recent Workflows (Last 48h)           │
│  ┌──────────────────────────────────┐ │
│  │ ID     │ Ticket │ Status │ Dur  │ │
│  │ WF-432 │ PRJ0-1 │ ✅Done │ 8h   │ │
│  │ WF-431 │ PRJ0-2 │ 🔄 ...  │ 4h   │ │
│  │ WF-430 │ PRJ0-3 │ ❌ Fail │ 2h   │ │
│  └──────────────────────────────────┘ │
│                                        │
└────────────────────────────────────────┘
```

### Workspaces Pages

**WorkspacesListPage** (`/workspaces`)
```
┌────────────────────────────────────┐
│ ☰ | Topbar                         │
├────────────────────────────────────┤
│                                    │
│  Workspaces                        │
│                                    │
│  [+ New Workspace]                 │
│                                    │
│  ┌────────────────────────────┐   │
│  │📁 ProjectZero-Main         │   │
│  │ 10 repos | Last: 2 min ago │   │
│  │ us-east-1 | 50GB storage   │   │
│  │ [View] [Settings] [...]    │   │
│  └────────────────────────────┘   │
│  ┌────────────────────────────┐   │
│  │📁 AI-Product-2             │   │
│  │ 5 repos | Last: 1h ago     │   │
│  │ eu-west-1 | 20GB storage   │   │
│  │ [View] [Settings] [...]    │   │
│  └────────────────────────────┘   │
│                                    │
└────────────────────────────────────┘
```

### Billing Pages

**BillingPage** (`/billing`)
```
┌──────────────────────────────────┐
│ ☰ | Topbar                       │
├──────────────────────────────────┤
│                                  │
│  Billing                          │
│                                  │
│  Current Subscription             │
│  ┌──────────────────────────────┐ │
│  │ Professional - $499/month    │ │
│  │                              │ │
│  │ Billing period:              │ │
│  │ Apr 19 - May 19, 2026        │ │
│  │ ████████░░░░░░ 35% through   │ │
│  │                              │ │
│  │ Usage:                       │ │
│  │ Agents: 950/1000 ████████░░  │ │
│  │ Repos:  5/10     ██████░░░░░ │ │
│  │ Users:  8/50     ██░░░░░░░░░  │ │
│  │                              │ │
│  │ [ Upgrade ] [ Cancel ]       │ │
│  └──────────────────────────────┘ │
│                                  │
│  Recent Invoices                  │
│  ┌──────────────────────────────┐ │
│  │ Date     │ Amount │ Status   │ │
│  │ Apr 2026 │ $499   │ ✅ Paid  │ │
│  │ Mar 2026 │ $499   │ ✅ Paid  │ │
│  └──────────────────────────────┘ │
│                                  │
└──────────────────────────────────┘
```

**PricingPage** (`/pricing`)
```
┌──────────────────────────────────┐
│ ☰ | Topbar                       │
├──────────────────────────────────┤
│                                  │
│  Choose Your Plan                │
│                                  │
│  ┌──────┐ ┌──────────┐ ┌──────┐ │
│  │ ST   │ │ PROF ✓  │ │ ENT  │ │
│  │ $0   │ │ $499     │ │ Cusx │ │
│  │      │ │          │ │      │ │
│  │ 5us  │ │ 50 users │ │ ∞    │ │
│  │ 1rp  │ │ 10 repos │ │ ∞    │ │
│  │ No   │ │ 4-gate   │ │ 4+   │ │
│  │gate  │ │          │ │      │ │
│  │      │ │[Upgrade] │ │[Talk]│ │
│  └──────┘ └──────────┘ └──────┘ │
│                                  │
│  Feature Comparison Table         │
│  (scroll down)                    │
│                                  │
└──────────────────────────────────┘
```

### Settings Pages

**SettingsPage** (`/settings`)
```
┌────────────────────────────────┐
│ ☰ | Topbar                     │
├────────────────────────────────┤
│                                │
│  Settings                       │
│                                │
│  Sidebar:                       │
│  • Organization                 │
│  • Members                       │
│  • Security                      │
│  • Integrations                  │
│  • Billing (→ /billing)         │
│  • Compliance (→ /compliance)   │
│                                │
└────────────────────────────────┘
```

**ProfilePage** (`/settings/organization`)
```
┌──────────────────────────────┐
│ Organization Settings        │
│                              │
│ Organization Name:           │
│ [____________________]       │
│                              │
│ Description:                 │
│ [_________________________]  │
│ [_________________________]  │
│                              │
│ Logo:                        │
│ [🖼️ Upload] [❌ Remove]     │
│ Preview: [__________]        │
│                              │
│ Billing Contact Email:       │
│ [____________________]       │
│                              │
│ Region: [us-east-1 ▼]      │
│                              │
│ [ Save Changes ]             │
│                              │
└──────────────────────────────┘
```

**MembersPage** (`/settings/members`)
```
┌──────────────────────────────┐
│ Team Members                 │
│                              │
│ [+ Invite Member]            │
│                              │
│ ┌──────────────────────────┐ │
│ │ Email │ Role │ Joined   │ │
│ ├──────────────────────────┤ │
│ │ y@.. │ Owner│ Apr 1 26  │ │
│ │ j@.. │ Engr │ Apr 10 26 │ │
│ │ z@.. │ Rev  │ Apr 15 26 │ │
│ └──────────────────────────┘ │
│                              │
│ Member row expanded:         │
│ [jane@...] [Reviewer ▼] [🗑️] │
│                              │
└──────────────────────────────┘
```

**SecurityPage** (`/settings/security`)
```
┌──────────────────────────────┐
│ Security                     │
│                              │
│ Multi-Factor Auth            │
│ ☑ MFA Enabled               │
│ [Manage Codes]               │
│                              │
│ SSO (Enterprise)             │
│ ☐ SSO Configured            │
│ [Configure SSO]              │
│                              │
│ API Keys                      │
│ ┌──────────────────────────┐ │
│ │ Key │ Scopes │ Expires   │ │
│ │ sk.. │ read   │ Apr 2027  │ │
│ └──────────────────────────┘ │
│ [+ Generate Key]             │
│                              │
│ Password                      │
│ [Change Password]            │
│                              │
└──────────────────────────────┘
```

### Compliance Pages

**AuditLogsPage** (`/compliance/audit-logs`)
```
┌────────────────────────────────┐
│ Audit Logs                      │
│                                │
│ Filters:                        │
│ [All Actions ▼] [All Actors ▼] │
│ [Date Range ▼] [Search]        │
│ [Export CSV]                    │
│                                │
│ ┌──────────────────────────────┐│
│ │Time│Action│Actor │ Changes   ││
│ ├──────────────────────────────┤│
│ │2:15│User │j@..  │ role:     ││
│ │    │invi │      │ Engr→Rev  ││
│ │    │ted  │      │          ││
│ │1:42│ Sub │y@..  │ status:   ││
│ │    │scri │      │ activ→   ││
│ │    │pt.  │      │ past_due  ││
│ │    │upd  │      │          ││
│ └──────────────────────────────┘│
│                                │
│ Pagination: < 1 of 20 >        │
│                                │
└────────────────────────────────┘
```

**CompliancePage** (`/compliance`)
```
┌──────────────────────────────┐
│ Compliance Dashboard         │
│                              │
│ Tabs: [SOC2] [ISO] [DPDP]   │
│                              │
│ SOC2 Type II Status:         │
│ ████████░░░░░░░░░░░░ 44%    │
│ (4 of 9 items complete)     │
│                              │
│ Checklist:                   │
│ ✅ Audit logging            │
│ ✅ MFA enforced             │
│ ✅ Data encrypted           │
│ ⚠️ Incident response plan   │
│ ❌ SOC2 audit scheduled     │
│                              │
│ [Generate SOC2 Report]       │
│ [Download Report Archive]    │
│                              │
└──────────────────────────────┘
```

---

## 3. Component Hierarchy

### Root Level
- **App** → Router setup, error boundary, providers (Auth, Toast, Org)

### Layout Components
```
AppLayout
├── Sidebar
│   ├── Logo
│   ├── NavLinks (Dashboard, Workspaces, Billing, Compliance, Settings)
│   └── Org Selector (if multi-org)
├── Topbar
│   ├── BreadcrumbNav
│   ├── UserMenu (Profile, Logout)
│   └── NotificationBell
└── MainContent (page-specific)
```

### Dashboard Components
```
DashboardPage
├── MetricsCard (4x: runs, repos, users, storage)
├── QuotaIndicator (progress bars)
├── TrendChart (agents runs last 7 days)
└── WorkflowStatusTable
    ├── WorkflowRow (clickable → detail modal)
    │   ├── StatusBadge
    │   ├── Avatar (agent type)
    │   └── Duration
    └── Pagination
```

### Billing Components
```
BillingPage
├── SubscriptionCard
│   ├── TierBadge (Professional)
│   ├── BillingPeriod (progress)
│   └── UsageBreakdown
│       ├── UsageBar (agents/repos/users)
│       └── PercentageLabel
├── InvoiceTable
│   └── InvoiceRow
│       ├── Date
│       ├── Amount
│       └── DownloadButton
└── UpgradeButton (→ PricingPage)
```

### Settings Components
```
SettingsPage
├── SettingsSidebar
│   ├── NavItem (Organization)
│   ├── NavItem (Members)
│   ├── NavItem (Security)
│   └── NavItem (Integrations)
└── SettingsContent
    └── ProfilePage | MembersPage | SecurityPage | IntegrationsPage
        ├── Form | Table | Checklist
        └── SaveButton | CancelButton
```

### Compliance Components
```
CompliancePage
├── TabNav (SOC2, ISO, DPDP)
├── ComplianceChart (progress ring)
├── ComplianceChecklist
│   ├── ChecklistItem
│   │   ├── Icon (✅/⚠️/❌)
│   │   ├── Title
│   │   └── EvidenceLink
│   └── ManualReviewBadge
└── GenerateReportButton → Modal
```

---

## 4. Component Library (Shadcn/ui)

Use Shadcn/ui for unstyled, composable components:
- Button, Input, Card, Modal, Badge, Avatar, Dropdown, Tabs, Pagination
- Table (headless, sortable, paginated)
- Form (React Hook Form integration)
- Alert, Skeleton, LoadingSpinner
- Popover, Tooltip, Toast (Sonner)

**Installation** (via CLI):
```bash
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card input modal
npx shadcn-ui@latest add table tabs pagination
npx shadcn-ui@latest add alert badge avatar dropdown
```

---

## 5. Routing Structure

```
/                              → Redirect to /dashboard (if logged in) or /auth/login
/auth/login                    → LoginPage
/auth/signup                   → SignupPage
/auth/forgot-password          → ForgotPasswordPage
/auth/mfa-verify               → MFAVerifyPage
/onboarding                    → Onboarding flow (4 steps)
/onboarding/step-2             → Invite team
/onboarding/step-3             → Choose plan
/dashboard                     → DashboardPage (home)
/workspaces                    → WorkspacesListPage
/workspaces/:id                → WorkspaceDetailPage
/billing                       → BillingPage
/billing/pricing               → PricingPage
/billing/invoices              → InvoicesPage
/billing/usage                 → UsagePage
/settings                      → SettingsPage (redirect to /settings/organization)
/settings/organization         → ProfilePage
/settings/members              → MembersPage
/settings/security             → SecurityPage
/settings/integrations         → IntegrationsPage
/compliance                    → CompliancePage
/compliance/audit-logs         → AuditLogsPage
/compliance/reports            → ReportsPage
/404                           → NotFoundPage
/500                           → ErrorPage
```

---

## 6. State Management

**Auth Context** (useAuth)
```typescript
interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login(email, password): Promise<void>;
  signup(email, orgName, password): Promise<void>;
  logout(): void;
  setMFAToken(token): void;
}
```

**Org Context** (useOrg)
```typescript
interface OrgContextType {
  org: Organization | null;
  users: User[];
  subscriptions: Subscription | null;
  isLoading: boolean;
  updateOrg(data): Promise<void>;
  inviteMember(email, role): Promise<void>;
}
```

**Toast Context** (notifications)
```typescript
type Toast = { id, message, type: 'success' | 'error' | 'info', duration };
```

---

## 7. API Integration

**Services** (auto-generated from OpenAPI spec):
```typescript
// auth.service.ts
export const authService = {
  login(email, password),
  signup(email, orgName, password),
  logout(),
  verifyMFA(code),
  refreshToken(),
};

// billing.service.ts
export const billingService = {
  getSubscription(),
  getInvoices(),
  getUsage(),
  upgradeSubscription(tier),
  cancelSubscription(),
};

// members.service.ts
export const membersService = {
  getMembers(),
  inviteMember(email, role),
  updateMemberRole(userId, role),
  removeMember(userId),
};
```

**Axios Instance** (with interceptors):
```typescript
const api = axios.create({
  baseURL: process.env.VITE_API_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Request: add auth token
api.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Response: handle 401 → logout, 5xx → error toast
```

---

## 8. Form Validation

**React Hook Form** + **Zod** (TypeScript-safe validation):

```typescript
const signupSchema = z.object({
  email: z.string().email('Invalid email'),
  orgName: z.string().min(3, 'Org name required'),
  password: z.string().min(12, 'Password too weak'),
});

// In component:
const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(signupSchema),
});
```

---

## 9. UI/UX Patterns

### Loading States
- Skeleton screens (card + lines)
- Spinners (center of card)
- Progressive loading (load header first, then table)

### Empty States
- Illustrated empty state
- Call-to-action button
- Example: "No workspaces yet. Create one to get started."

### Error Handling
- Toast notifications (top-right, auto-dismiss 5s)
- Form field errors (red border + error message)
- Page-level errors (error card + retry button)

### Confirmation Dialogs
- Destructive actions require confirmation
- Example: "Remove member jane@corp.com?" (cancel/confirm)

### Modals
- Backdrop (dark overlay, clickable to close)
- Header (title + close button)
- Body (content)
- Footer (cancel + action button)

---

## 10. Design System / Tailwind Config

**Colors** (from Figma/Palette):
```javascript
colors: {
  primary: '#2563eb',     // Blue
  success: '#10b981',     // Green
  warning: '#f59e0b',     // Amber
  danger: '#ef4444',      // Red
  neutral: '#6b7280',     // Gray
  bg: '#ffffff',
  bg-secondary: '#f9fafb',
  border: '#e5e7eb',
  text: '#111827',
  text-secondary: '#6b7280',
}
```

**Spacing** (Tailwind default: 4px base)
- xs: 4px, sm: 8px, md: 16px, lg: 24px, xl: 32px

**Typography**:
- h1: 32px, bold, primary color
- h2: 24px, bold, text-gray-900
- body: 14px, text-gray-700
- caption: 12px, text-gray-600

**Shadows**:
- sm: subtle card shadow
- md: dropdown/modal shadow
- lg: floating action button

**Animations**:
- fade-in: 200ms
- slide-up: 300ms
- bounce: 500ms

---

## 11. Accessibility (a11y)

- **ARIA labels** on buttons, icons, form fields
- **Keyboard navigation** (Tab, Enter, Escape)
- **Color contrast** (WCAG AA minimum)
- **Focus indicators** (ring-2 ring-blue-500)
- **Semantic HTML** (<button>, <form>, <nav>)
- **Alt text** on images/icons

---

## 12. Performance Optimizations

- **Code splitting**: React.lazy() for pages
- **Image optimization**: WebP format, lazy loading
- **Tree-shaking**: ES modules, no unused exports
- **Bundle size**: <200KB gzipped (target)
- **Memoization**: React.memo() for expensive components
- **Virtual scrolling**: For large tables (TanStack Table)

---

## 13. Testing Strategy

**Unit Tests** (Vitest + React Testing Library):
- Component rendering
- User interactions (click, input)
- Conditional rendering (based on props/state)

**Integration Tests**:
- Form submission → API call → success/error toast
- Auth flow (login → dashboard redirect)

**E2E Tests** (Playwright):
- Sign-up flow (end-to-end)
- Invite team member → get email → join org
- Upgrade subscription → Stripe checkout

**Coverage Target**: ≥80%

---

## 14. Build & Deployment

**Build**:
```bash
pnpm install
pnpm run build  # Vite build → dist/
```

**Environment Variables** (.env.local):
```
VITE_API_URL=https://api.projectzero.dev
VITE_AUTH0_DOMAIN=projectzero.auth0.com
VITE_AUTH0_CLIENT_ID=xxx
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_xxx
```

**Docker** (optional):
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY src ./src
RUN pnpm run build
EXPOSE 3000
CMD ["pnpm", "run", "preview"]
```

---

## 15. Next Steps

1. **Create React project** (Vite):
   ```bash
   pnpm create vite projectzero-saas --template react-ts
   cd projectzero-saas
   pnpm install
   pnpm add -D tailwindcss postcss autoprefixer
   npx tailwindcss init -p
   pnpm add @shadcn/ui
   ```

2. **Set up folder structure** (from Section 1)

3. **Install dependencies**:
   ```bash
   pnpm add axios react-router-dom react-hook-form zod zustand
   pnpm add @tanstack/react-table sonner recharts
   pnpm add -D vitest @testing-library/react @testing-library/jest-dom
   ```

4. **Create base components** (from section 3)

5. **Setup routing** (React Router, from section 5)

6. **Implement pages** (start with auth, then dashboard)

7. **Integrate API** (axios + service layer)

8. **Add tests** (unit + integration)

9. **E2E testing** (Playwright)

---

**Document Version**: 1.0  
**Created**: 2026-04-19  
**Framework**: React 18 + TypeScript + TailwindCSS + Vite  
**Status**: Ready for Frontend Implementation (Phase 1)
