/**
 * Static guide content — PRJ0-31.
 * Data only. Swap this for a CMS fetch later without touching UserGuide layout.
 */

export interface GuideSubsection {
  heading: string;
  body: string;
}

export interface GuideSection {
  title: string;
  intro: string;
  subsections: GuideSubsection[];
}

export const GUIDE_SECTIONS: Record<string, GuideSection> = {
  'Getting Started': {
    title: 'Getting Started',
    intro:
      'ProjectZero Control Tower is the governance layer for all product development in your organisation. Every feature flows through a gated pipeline: Specification → Architecture → Realization → Completion.',
    subsections: [
      {
        heading: 'First Login',
        body: 'Sign in with your work email and password. Admins can register new users via the API (/api/v1/auth/register). Your role (admin / developer / viewer) is shown in the sidebar footer.',
      },
      {
        heading: 'Dashboard Overview',
        body: 'The home dashboard shows live workflow counts — active, completed, failed, blocked — and recent workflow runs. Click any row to open the workflow detail view.',
      },
      {
        heading: 'Navigation',
        body: 'Use the left sidebar to switch between modules. CXO provides portfolio-level metrics. Workflows, Agents, Approvals, Artifacts, and Audit Log cover the full development lifecycle.',
      },
      {
        heading: 'Roles & Permissions',
        body: 'Admin: full access including user management and forced approvals. Developer: can start workflows, submit artifacts, and resolve approvals. Viewer: read-only access to all dashboards and logs.',
      },
    ],
  },

  Workflows: {
    title: 'Workflows',
    intro:
      'A Workflow Run tracks one feature or bug from ticket to release. It moves through four stages — Specification, Architecture, Realization, Completion — and cannot skip stages.',
    subsections: [
      {
        heading: 'Starting a Workflow',
        body: 'Click "Start Workflow" on the Workflows page, choose a type (feature / bugfix / refactor), and provide the JIRA feature ID. The factory assigns the workflow to the appropriate agent team.',
      },
      {
        heading: 'Stage Gates',
        body: 'Each stage must be approved before the next begins. Pending approvals appear on the Approvals page. A stage fails if its quality gates (tests, coverage ≥80%, lint) do not pass.',
      },
      {
        heading: 'Status Badges',
        body: 'Pending (gray) → Running (blue) → Completed (green) / Failed (red) / Blocked (yellow). A blocked workflow has an unresolved approval or a dependency that failed.',
      },
      {
        heading: 'Retrying Failures',
        body: 'Click "Retry" on a failed workflow run. The factory replays from the last successful step. Root cause is shown in the step error message on the Workflow Detail page.',
      },
    ],
  },

  Agents: {
    title: 'Agents',
    intro:
      'Agents are AI specialists that execute workflow steps. Each agent type owns a narrow responsibility and hands off to the next via a structured handshake protocol.',
    subsections: [
      {
        heading: 'Agent Types',
        body: 'Spec Agent: parses requirements, generates user stories. Arch Agent: designs system architecture, produces ADRs. Impl Agent: writes code using TDD. Review Agent: static analysis and code review. Test Agent: integration and E2E tests. Deploy Agent: release tagging and changelog.',
      },
      {
        heading: 'Agent Contributions',
        body: 'Every action an agent takes is logged as an AgentContribution. View contributions per workflow on the Agents page. Each record shows agent type, action taken, result, and duration.',
      },
      {
        heading: 'CXO Team',
        body: 'The CXO team (CTO, CFO, CMO agents) monitors portfolio health, generates executive summaries, and flags risks. Their output feeds the CXO Dashboard.',
      },
      {
        heading: 'Multi-Agent Handshake',
        body: 'Agents communicate via Temporal signals. A sending agent sets its step to "completed" and emits a signal containing its output artifact ID. The receiving agent reads the artifact before acting — ensuring full context transfer with no silent mutations.',
      },
    ],
  },

  'CXO Dashboard': {
    title: 'CXO Dashboard',
    intro:
      'The CXO Dashboard provides executive-level visibility into all active JIRA projects. Portfolio cards show completion percentage; drill-down reveals sprint-level agile metrics.',
    subsections: [
      {
        heading: 'Portfolio View',
        body: 'Each project card shows: total tickets, done / in-progress / todo counts, and a completion donut chart. The stacked bar chart at the bottom compares all projects side-by-side. Click a card to drill into project metrics.',
      },
      {
        heading: 'Velocity Chart',
        body: 'Shows story points committed vs completed for the last 6 closed sprints. A consistent gap between committed and completed indicates scope creep or underestimation.',
      },
      {
        heading: 'Burndown & Cycle Time',
        body: 'Burndown tracks remaining story points by day in the current sprint. Cycle time scatter plot shows days from ticket creation to resolution — outliers are candidates for process improvement.',
      },
      {
        heading: 'Refresh & Caching',
        body: 'Metrics are cached in Postgres to avoid hammering the JIRA API. Click "Refresh from JIRA" on any project page to force a live fetch. Cache is project-scoped so refreshing one project does not affect others.',
      },
    ],
  },

  'JIRA Integration': {
    title: 'JIRA Integration',
    intro:
      'ProjectZero connects to your Atlassian JIRA Cloud instance via REST API. All ticket creation, status transitions, and metric fetches use the credentials configured in your .env file.',
    subsections: [
      {
        heading: 'Configuration',
        body: 'Set JIRA_BASE_URL (e.g. https://yourorg.atlassian.net), JIRA_USER_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY, and JIRA_BOARD_ID in your .env file. The API token is generated at id.atlassian.com under Security → API tokens.',
      },
      {
        heading: 'Story Points Field',
        body: 'JIRA Cloud uses a custom field for story points (default: customfield_10016). If your instance uses a different field, set JIRA_STORY_POINTS_FIELD in .env. Check your field ID via /rest/api/3/field.',
      },
      {
        heading: 'Health Monitor',
        body: 'A background monitor pings JIRA every 60 seconds (configurable via JIRA_HEALTH_INTERVAL). A circuit breaker opens after 3 consecutive failures and retries after 30 seconds. Status is visible on the Dev Monitor page.',
      },
      {
        heading: 'SPARC Ticket Format',
        body: 'All tickets created by the factory follow SPARC: Specification, Pseudocode, Architecture, Refinement, Completion (DoD). This ensures every ticket has a clear definition of done before implementation begins.',
      },
    ],
  },
};

export const SECTION_NAMES = Object.keys(GUIDE_SECTIONS);
