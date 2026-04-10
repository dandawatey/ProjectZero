# 07 - Plugin and Skill Model

## Overview

Skills are reusable capabilities that any agent can invoke. They live in `.claude/skills/` and each skill is a self-contained directory with its own definition, instructions, and (optionally) supporting files. Skills are stateless -- they take input, perform a task, and return output without maintaining state between invocations.

## Skill Architecture

Each skill directory contains:

```
.claude/skills/{skill-name}/
  skill.md          # Skill definition: purpose, trigger, inputs, outputs, instructions
  examples/         # (optional) Example inputs and outputs
  templates/        # (optional) Templates used by the skill
  data/             # (optional) Reference data the skill uses
```

The `skill.md` file is the authoritative definition. It must contain:
- **Purpose**: What the skill does
- **Trigger**: When the skill should be invoked (which agents, which situations)
- **Inputs**: What the skill expects
- **Outputs**: What the skill produces
- **Instructions**: Step-by-step instructions for executing the skill

## Skill Catalog

### debug-skill

**Purpose**: Systematic debugging of code issues using a structured diagnostic approach.

**Trigger**: Invoked by any engineering agent when a test fails, an error occurs, or unexpected behavior is observed.

**Inputs**:
- Error message or failing test output
- Relevant source code files
- Stack trace (if available)
- Expected vs. actual behavior description

**Outputs**:
- Root cause analysis
- Fix recommendation with code changes
- Regression test recommendation

**How it works**:
1. Parse the error message to categorize the failure type (syntax, runtime, logic, type, dependency)
2. Trace the error to its origin in the source code
3. Examine the surrounding context (function, module, recent changes)
4. Form hypotheses ranked by likelihood
5. Validate each hypothesis against the available evidence
6. Produce a fix with explanation
7. Recommend a regression test that would catch this issue in the future

---

### feature-forge

**Purpose**: Scaffold a complete feature implementation from a specification, generating all the boilerplate code for the chosen stack.

**Trigger**: Invoked by backend-engineer or frontend-engineer at the start of implementing a new story.

**Inputs**:
- Story specification (from `.claude/delivery/features/`)
- Module architecture (from `.claude/modules/{name}/architecture.md`)
- Data model (from `.claude/modules/{name}/data-model.md`)
- Stack configuration

**Outputs**:
- Scaffolded source files (routes, controllers, services, repositories, models)
- Test file stubs
- Migration file stubs
- Storybook story stubs (for UI components)

**How it works**:
1. Read the story specification and extract entities, endpoints, and UI components
2. Determine which layers need code (API route, service, repository, model, migration, component, page)
3. Generate boilerplate for each layer following the project's coding patterns
4. Generate test file stubs with test case descriptions from the test plan
5. Wire up imports and dependency injection
6. The engineer then fills in the business logic

---

### code-reviewer

**Purpose**: Automated code review that checks for quality, security, performance, and standards compliance.

**Trigger**: Invoked by the reviewer agent for all code artifacts.

**Inputs**:
- Source code diff (or full files for new code)
- Project coding standards (from `.claude/core/`)
- Architecture decisions (from `.claude/knowledge/adrs/`)
- Previous review comments (for re-reviews)

**Outputs**:
- Review comments with file/line references
- Severity classification (CRITICAL, MAJOR, MINOR, SUGGESTION)
- Summary with pass/fail recommendation

**How it works**:
1. Parse the diff to understand what changed
2. Check for common code smells (long functions, deep nesting, magic numbers, duplicated code)
3. Validate naming conventions against project standards
4. Check for security issues (SQL injection, XSS, hardcoded secrets, insecure dependencies)
5. Check for performance issues (N+1 queries, unnecessary re-renders, missing indexes)
6. Validate error handling (are all error paths covered?)
7. Check for test coverage (does the new code have corresponding tests?)
8. Produce a review summary with actionable comments

---

### playwright-skill

**Purpose**: Write and execute end-to-end browser tests using Playwright.

**Trigger**: Invoked by qa-engineer or frontend-engineer for E2E testing of UI features.

**Inputs**:
- User flow description (from `.claude/modules/{name}/ui-flows.md`)
- Acceptance criteria (from story specification)
- Page URLs and selectors
- Expected outcomes

**Outputs**:
- Playwright test files
- Test execution results
- Screenshots on failure
- Accessibility audit results (via Playwright accessibility testing)

**How it works**:
1. Parse the user flow into discrete steps
2. Generate a Playwright test file with proper test structure
3. For each step: navigate, interact (click, type, select), assert
4. Add waiting strategies (wait for network idle, wait for selector)
5. Add screenshot capture on assertion failure
6. Add accessibility checks using `@axe-core/playwright`
7. Generate test data using fixtures from `.claude/data/fixtures/`

---

### spec-miner

**Purpose**: Extract structured specifications from unstructured documents (meeting notes, emails, Slack conversations, existing docs).

**Trigger**: Invoked by product-manager when processing raw input documents into structured specifications.

**Inputs**:
- Unstructured document (text, markdown, or pasted content)
- Product context (from `.claude/knowledge/product-context.md`)
- Existing specifications (for deduplication)

**Outputs**:
- Extracted requirements (functional and non-functional)
- Proposed user stories with acceptance criteria
- Identified ambiguities needing clarification
- Traceability map (which requirement came from which part of the input)

**How it works**:
1. Parse the input document and identify requirement-like statements
2. Classify each as functional requirement, non-functional requirement, constraint, or out-of-scope
3. Map requirements to existing modules (or propose new modules)
4. Generate user stories in standard format
5. Flag ambiguities and contradictions
6. Produce a traceability matrix

---

### using-git-worktrees

**Purpose**: Manage parallel development streams using git worktrees, enabling work on multiple features simultaneously without branch switching.

**Trigger**: Invoked by any engineering agent when parallel work is needed, or by ralph-controller for pipeline-mode parallel implementation.

**Inputs**:
- List of ticket IDs to work on in parallel
- Base branch
- Repository path

**Outputs**:
- Created worktree paths
- Branch-to-worktree mapping
- Instructions for working in each worktree

**How it works**:
1. For each ticket, create a feature branch from the base branch
2. Create a git worktree for each branch at a predictable path
3. Register the worktree mapping in `.claude/delivery/github/state/`
4. Return the paths so agents can work in parallel
5. When work is complete, merge and clean up worktrees

---

### secure-code-guardian

**Purpose**: Deep security analysis of code, going beyond surface-level pattern matching to understand data flow and trust boundaries.

**Trigger**: Invoked by security-reviewer agent during code review, and by backend-engineer for self-assessment.

**Inputs**:
- Source code files
- Data flow context (what data enters, how it flows, where it exits)
- Authentication and authorization configuration
- Dependency manifests (package.json, requirements.txt)

**Outputs**:
- Security findings with CVSS scores
- Data flow diagrams showing trust boundary crossings
- Dependency vulnerability report
- Remediation code suggestions
- Compliance checklist (OWASP, CWE)

**How it works**:
1. Map data entry points (API endpoints, form inputs, file uploads)
2. Trace data flow through the application (input -> validation -> processing -> storage -> output)
3. Identify trust boundary crossings (where untrusted data enters trusted contexts)
4. Check each crossing for proper validation and sanitization
5. Scan dependencies for known vulnerabilities
6. Check authentication and authorization implementation
7. Validate encryption usage (at rest and in transit)
8. Produce findings with severity, CWE reference, and fix suggestion

---

### rag-architect

**Purpose**: Design and implement retrieval-augmented generation (RAG) systems, including embedding strategies, vector store configuration, and retrieval pipelines.

**Trigger**: Invoked by architect or backend-engineer when the product requires RAG capabilities (search, knowledge bases, chatbots).

**Inputs**:
- Content corpus description
- Query patterns (what users will ask)
- Performance requirements (latency, accuracy)
- Infrastructure constraints

**Outputs**:
- Embedding strategy (model, chunking, overlap)
- Vector store configuration
- Retrieval pipeline design
- Evaluation framework
- Implementation code

**How it works**:
1. Analyze the content corpus (size, format, update frequency)
2. Select embedding model based on content type and performance requirements
3. Design chunking strategy (size, overlap, semantic boundaries)
4. Select vector store (Pinecone, Weaviate, pgvector, Chroma)
5. Design retrieval pipeline (query preprocessing, retrieval, reranking, context assembly)
6. Create evaluation framework (relevance, faithfulness, answer quality)
7. Generate implementation code

---

### the-fool

**Purpose**: Adversarial testing agent that deliberately tries to break things. Asks naive questions, tries unexpected inputs, and challenges assumptions.

**Trigger**: Invoked during review stage as a chaos/adversarial tester. Can also be invoked on-demand.

**Inputs**:
- The artifact to test (code, spec, design)
- The specification it should meet

**Outputs**:
- List of "foolish" questions that expose assumptions
- Edge cases that were not considered
- Unexpected input combinations that cause failures
- Boundary condition violations

**How it works**:
1. Read the specification and identify all assumptions
2. For each assumption, ask "what if this is wrong?"
3. Generate unexpected inputs (empty strings, null values, extremely large values, special characters, unicode, negative numbers, future dates, concurrent requests)
4. Try to violate every boundary condition
5. Ask naive questions that a new team member would ask
6. Report all findings, even if they seem obvious

---

### refactoring-ui

**Purpose**: Improve the visual quality of UI implementations by applying design principles from the Refactoring UI methodology.

**Trigger**: Invoked by frontend-engineer or ux-reviewer when UI needs visual refinement.

**Inputs**:
- UI component code
- Current visual appearance (Storybook screenshots)
- Design system tokens

**Outputs**:
- Specific visual improvements with code changes
- Before/after comparison points
- Design principle references for each change

**How it works**:
1. Evaluate spacing and layout (consistent spacing scale, visual hierarchy)
2. Evaluate typography (font sizes, weights, line heights, contrast)
3. Evaluate color usage (color palette adherence, contrast ratios, meaningful use of color)
4. Evaluate component composition (visual weight balance, alignment, grouping)
5. Apply improvements following the spacing/sizing scale from design tokens
6. Ensure changes are consistent with the design system

---

### ux-heuristics

**Purpose**: Evaluate UI/UX quality using Nielsen's 10 usability heuristics and other established frameworks.

**Trigger**: Invoked by ux-reviewer during UI review.

**Inputs**:
- UI screens or components
- User flow documentation
- Task descriptions (what the user is trying to accomplish)

**Outputs**:
- Heuristic evaluation results (one score per heuristic)
- Specific findings with severity
- Improvement recommendations
- Overall usability score

**How it works**:
1. Evaluate each of Nielsen's 10 heuristics:
   - Visibility of system status
   - Match between system and real world
   - User control and freedom
   - Consistency and standards
   - Error prevention
   - Recognition rather than recall
   - Flexibility and efficiency of use
   - Aesthetic and minimalist design
   - Help users recognize, diagnose, and recover from errors
   - Help and documentation
2. Score each on a 0-4 severity scale
3. Provide specific examples of violations
4. Recommend fixes prioritized by severity

---

### hooked-ux

**Purpose**: Apply the Hook Model (Trigger-Action-Variable Reward-Investment) to design engaging user experiences.

**Trigger**: Invoked by ux-reviewer or product-manager when designing user engagement patterns.

**Inputs**:
- Product context and user personas
- Feature specifications
- Current user flows

**Outputs**:
- Hook analysis for key user flows
- Engagement pattern recommendations
- Notification and trigger strategy
- Investment loop design

**How it works**:
1. Identify the core user action the product wants to encourage
2. Design external triggers (notifications, emails) and internal triggers (emotions, habits)
3. Simplify the action (reduce friction, use progressive disclosure)
4. Design variable rewards (social, hunt, self)
5. Design investment loops (user puts in effort that makes the product more valuable)
6. Map the complete hook cycle for each key user flow

---

### frontend-design

**Purpose**: Generate UI component designs following modern frontend patterns and the project's design system.

**Trigger**: Invoked by frontend-engineer when creating new components.

**Inputs**:
- Component requirements (what it displays, what interactions it supports)
- Design system tokens
- Existing component library
- Accessibility requirements

**Outputs**:
- Component API design (props, events, slots)
- Component composition structure (sub-components)
- Responsive behavior specification
- Accessibility implementation plan
- Example usage code

**How it works**:
1. Analyze the component requirements
2. Check if an existing component can be extended (prefer composition over creation)
3. Design the component API (props for data in, events for data out)
4. Plan the composition (what sub-components are needed)
5. Define responsive breakpoint behavior
6. Plan keyboard navigation and screen reader support
7. Generate the component skeleton with proper TypeScript types

---

### ios-hig-design

**Purpose**: Evaluate and design iOS interfaces following Apple's Human Interface Guidelines.

**Trigger**: Invoked when the product includes iOS native or React Native components targeting iOS.

**Inputs**:
- Screen designs or component specifications
- Target iOS version
- App context (what the app does)

**Outputs**:
- HIG compliance evaluation
- Specific violations and recommendations
- iOS-native component alternatives
- SF Symbols and system color recommendations

**How it works**:
1. Evaluate navigation patterns against HIG (tab bar, navigation controller, split view)
2. Check control usage (standard iOS controls vs. custom)
3. Evaluate typography (SF Pro, Dynamic Type support)
4. Check color usage (system colors, accessibility)
5. Evaluate iconography (SF Symbols usage)
6. Check gesture support and feedback (haptics, animations)
7. Validate accessibility (VoiceOver, Dynamic Type, color contrast)

---

### ui-ux-pro-max

**Purpose**: Comprehensive UI/UX analysis combining multiple evaluation frameworks into a single deep review.

**Trigger**: Invoked for major UI features or when a thorough UX review is needed.

**Inputs**:
- Complete UI screens and flows
- User personas and scenarios
- Business objectives
- Design system

**Outputs**:
- Multi-framework evaluation (heuristics, accessibility, visual design, information architecture)
- Prioritized improvement roadmap
- Quick wins vs. strategic improvements
- Competitive UX comparison (if applicable)

**How it works**:
1. Run Nielsen's heuristic evaluation (via ux-heuristics)
2. Run accessibility audit (WCAG 2.1 AA)
3. Evaluate visual design (Gestalt principles, visual hierarchy, typography, color)
4. Evaluate information architecture (content organization, navigation, labeling)
5. Evaluate interaction design (feedback, affordances, error handling)
6. Synthesize findings into a prioritized roadmap
7. Identify quick wins (high impact, low effort) and strategic improvements (high impact, high effort)

---

### design-sprint

**Purpose**: Run a compressed design sprint process for rapid product or feature ideation.

**Trigger**: Invoked by product-manager or architect at the start of a new product or major feature.

**Inputs**:
- Problem statement
- User personas
- Constraints (technical, business, time)
- Competitive landscape

**Outputs**:
- Problem map
- Solution sketches
- Decision matrix
- Prototype plan
- Test plan

**How it works**:
1. **Map** (Monday): Define the problem, map the user journey, identify the target
2. **Sketch** (Tuesday): Generate multiple solution approaches
3. **Decide** (Wednesday): Evaluate solutions against criteria, select the winner
4. **Prototype** (Thursday): Plan the prototype (which screens, which flows)
5. **Test** (Friday): Define the user test plan and success criteria

---

### superpowers

**Purpose**: Meta-skill that enhances the Claude agent's capabilities by providing advanced prompting patterns, chain-of-thought structures, and self-correction mechanisms.

**Trigger**: Invoked by ralph-controller at the start of complex operations.

**Inputs**:
- Task description
- Complexity assessment
- Available context budget

**Outputs**:
- Enhanced task decomposition
- Optimal agent sequencing
- Context management strategy
- Self-correction checkpoints

**How it works**:
1. Analyze the task for complexity (number of steps, dependencies, ambiguity)
2. Decompose into subtasks with clear boundaries
3. Determine optimal agent sequencing (parallel where possible, sequential where required)
4. Plan context window usage (what to keep, what to summarize, what to offload to files)
5. Set self-correction checkpoints (where to pause and validate before continuing)

---

## Adding Custom Skills

To add a custom skill:

1. Create a directory: `.claude/skills/{skill-name}/`
2. Create `skill.md` with the required sections (Purpose, Trigger, Inputs, Outputs, Instructions)
3. Run `/setup validate` to ensure the skill passes validation
4. The plugin-validator agent will check the skill for completeness and security

Custom skills inherit the factory's governance -- they are validated before use and their outputs pass through the same governance chain as any other artifact.
