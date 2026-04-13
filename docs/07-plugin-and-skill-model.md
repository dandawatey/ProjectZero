# Plugin and Skill Model

17 skills. Each executes within agent context inside Temporal workflows. Skills are reusable capabilities. Agents invoke them during workflow steps.

## Architecture

```
Temporal Workflow Step → Agent → Skill Invocation → Result
```

Skills run inside agent context. Agent owns the step. Skill does the work. Result feeds back to the workflow.

## Skill Structure

Every skill lives in `.claude/skills/{skill-name}/` with:

```
SKILL.md        — Definition: purpose, inputs, outputs, instructions
usage.md        — When and how to use this skill
triggers.md     — What conditions trigger this skill
checklist.md    — Validation checklist for skill output
```

## Skill Catalog

| # | Skill | Purpose | Trigger | Workflow Stages |
|---|---|---|---|---|
| 1 | debug-skill | Systematic debugging with structured diagnostics | Test failure, runtime error, unexpected behavior | Realization, Checking |
| 2 | feature-forge | Scaffold complete feature from spec | Story implementation start | Realization |
| 3 | code-reviewer | Automated code review: quality, security, perf | Code artifact ready for review | Review, Checking |
| 4 | playwright-skill | E2E browser tests with Playwright | UI feature ready for E2E testing | Realization, Checking |
| 5 | spec-miner | Extract structured specs from unstructured docs | Raw input docs need structuring | Specification |
| 6 | using-git-worktrees | Parallel dev streams via git worktrees | Multiple tickets need parallel work | Realization |
| 7 | secure-code-guardian | Deep security analysis: data flow, trust boundaries | Code review, security assessment | Review, Checking |
| 8 | rag-architect | Design RAG systems: embeddings, vector stores, retrieval | Product needs RAG capabilities | Architecture, Realization |
| 9 | the-fool | Adversarial testing: break things, challenge assumptions | Review stage chaos testing | Review |
| 10 | refactoring-ui | Visual UI improvement via Refactoring UI methodology | UI needs visual refinement | Realization, Review |
| 11 | ux-heuristics | Nielsen's 10 heuristics evaluation | UI review needed | Review |
| 12 | hooked-ux | Hook Model for engagement: trigger-action-reward-invest | Designing user engagement patterns | Specification, Architecture |
| 13 | frontend-design | UI component design following design system | New component creation | Architecture, Realization |
| 14 | ios-hig-design | Apple HIG compliance for iOS interfaces | iOS/React Native UI work | Architecture, Realization, Review |
| 15 | ui-ux-pro-max | Comprehensive multi-framework UX analysis | Major UI feature deep review | Review |
| 16 | design-sprint | Compressed design sprint for rapid ideation | New product or major feature kickoff | Specification |
| 17 | superpowers | Meta-skill: enhanced prompting, task decomposition, self-correction | Complex operations start | All stages |

## Skill Details

### debug-skill
Systematic debugging. Parse error → trace origin → form hypotheses → validate → fix → recommend regression test. Used by engineering agents when something breaks.

### feature-forge
Scaffold from spec. Read story → extract entities/endpoints/components → generate boilerplate for each layer → generate test stubs → wire imports. Engineer fills in business logic.

### code-reviewer
Automated review. Parse diff → check code smells → validate naming → check security → check performance → validate error handling → verify test coverage → produce actionable review.

### playwright-skill
E2E tests. Parse user flow → generate Playwright test → navigate/interact/assert → add wait strategies → capture screenshots on failure → run axe-core accessibility checks.

### spec-miner
Requirement extraction. Parse unstructured input → classify (functional, non-functional, constraint, out-of-scope) → map to modules → generate user stories → flag ambiguities → produce traceability matrix.

### using-git-worktrees
Parallel work. For each ticket: create feature branch → create worktree → register mapping → return paths. Agents work in parallel. Merge and cleanup when done.

### secure-code-guardian
Deep security. Map data entry points → trace data flow → identify trust boundary crossings → validate sanitization → scan dependencies → check auth → validate encryption → produce findings with CVSS/CWE.

### rag-architect
RAG design. Analyze corpus → select embedding model → design chunking strategy → select vector store → design retrieval pipeline → create evaluation framework → generate implementation.

### the-fool
Adversarial chaos. Read spec → identify assumptions → ask "what if wrong?" → generate unexpected inputs → violate boundary conditions → ask naive questions → report everything.

### refactoring-ui
Visual refinement. Evaluate spacing/layout → typography → color usage → component composition → apply improvements using design tokens → ensure design system consistency.

### ux-heuristics
Nielsen's 10. Evaluate each heuristic → score 0-4 severity → provide violation examples → recommend fixes prioritized by severity → produce overall usability score.

### hooked-ux
Hook Model. Identify core action → design triggers (external + internal) → simplify action → design variable rewards → design investment loops → map complete hook cycle.

### frontend-design
Component design. Analyze requirements → check for extensible existing components → design API (props/events) → plan composition → define responsive behavior → plan accessibility → generate skeleton.

### ios-hig-design
Apple HIG. Evaluate navigation patterns → check control usage → evaluate typography (SF Pro, Dynamic Type) → check colors → evaluate iconography (SF Symbols) → check gestures/haptics → validate VoiceOver.

### ui-ux-pro-max
Multi-framework analysis. Run heuristic evaluation → accessibility audit (WCAG 2.1 AA) → visual design review → information architecture review → interaction design review → synthesize into prioritized roadmap.

### design-sprint
Compressed sprint. Map (problem + user journey) → Sketch (multiple solutions) → Decide (evaluate + select) → Prototype (plan screens/flows) → Test (define test plan + success criteria).

### superpowers
Meta-skill. Analyze task complexity → decompose into subtasks → determine agent sequencing (parallel where possible) → plan context window usage → set self-correction checkpoints.
