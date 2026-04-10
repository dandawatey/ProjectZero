#!/usr/bin/env bash
# =============================================================================
# init-repo.sh
# Initializes a new product repository from the ProjectZeroFactory template.
#
# This script is a lower-level utility used by bootstrap-product.sh.
# It can also be used standalone to set up a repo that already exists
# but needs the factory template applied.
#
# Usage:
#   bash scripts/init-repo.sh <product-name> <target-directory>
#
# Example:
#   bash scripts/init-repo.sh customer-portal /Users/dev/customer-portal
#
# What this script does:
#   1. Validates inputs
#   2. Creates the standard directory structure
#   3. Copies factory templates and governance files
#   4. Initializes git (if not already initialized)
#   5. Creates the initial product configuration
#   6. Makes an initial commit
#
# Exit codes:
#   0 - Success
#   1 - Invalid arguments
#   2 - Factory root not found
#   3 - Target directory creation failed
#   4 - Git initialization failed
# =============================================================================

set -euo pipefail

# --- Color Output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }

# --- Determine Factory Root ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FACTORY_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# --- Validate Arguments ---
if [[ $# -lt 2 ]]; then
  echo "Usage: bash scripts/init-repo.sh <product-name> <target-directory>"
  echo ""
  echo "Arguments:"
  echo "  product-name       Lowercase name with hyphens (e.g. customer-portal)"
  echo "  target-directory   Absolute path to the product directory"
  echo ""
  echo "Example:"
  echo "  bash scripts/init-repo.sh customer-portal /Users/dev/customer-portal"
  exit 1
fi

PRODUCT_NAME="$1"
TARGET_DIR="$2"

# --- Validate product name ---
if [[ ! "$PRODUCT_NAME" =~ ^[a-z][a-z0-9-]*$ ]]; then
  log_error "Invalid product name: '$PRODUCT_NAME'"
  log_error "Must start with a lowercase letter, contain only lowercase letters, numbers, and hyphens."
  exit 1
fi

# --- Validate factory root ---
if [[ ! -f "$FACTORY_ROOT/.claude/CLAUDE.md" ]]; then
  log_error "Factory root not found or incomplete at: $FACTORY_ROOT"
  log_error "Ensure this script is located in a valid ProjectZeroFactory/scripts/ directory."
  exit 2
fi

log_info "Factory root: $FACTORY_ROOT"
log_info "Product name: $PRODUCT_NAME"
log_info "Target directory: $TARGET_DIR"
echo ""

# =============================================================================
# Step 1: Create Target Directory
# =============================================================================
log_info "Creating target directory..."

if [[ -d "$TARGET_DIR" ]]; then
  log_warn "Target directory already exists: $TARGET_DIR"
else
  if ! mkdir -p "$TARGET_DIR"; then
    log_error "Failed to create directory: $TARGET_DIR"
    exit 3
  fi
  log_success "Created: $TARGET_DIR"
fi

# =============================================================================
# Step 2: Create Standard Directory Structure
# =============================================================================
log_info "Creating standard directory structure..."

# Core directories every product needs
DIRECTORIES=(
  ".claude/memory"
  ".claude/knowledge"
  ".claude/checkpoints"
  ".claude/templates"
  ".claude/checklists"
  "src"
  "src/components"
  "src/services"
  "src/utils"
  "src/types"
  "tests"
  "tests/unit"
  "tests/integration"
  "tests/e2e"
  "docs"
  "docs/adr"
  "docs/api"
  "scripts"
  "config"
)

for dir in "${DIRECTORIES[@]}"; do
  mkdir -p "$TARGET_DIR/$dir"
done

log_success "Created ${#DIRECTORIES[@]} directories"

# =============================================================================
# Step 3: Copy Factory Templates and Governance Files
# =============================================================================
log_info "Copying factory governance files..."

# Copy the operating contract
cp "$FACTORY_ROOT/.claude/CLAUDE.md" "$TARGET_DIR/.claude/CLAUDE.md"
log_success "Copied CLAUDE.md"

# Copy settings
if [[ -f "$FACTORY_ROOT/.claude/settings.json" ]]; then
  cp "$FACTORY_ROOT/.claude/settings.json" "$TARGET_DIR/.claude/settings.json"
  log_success "Copied settings.json"
fi

# Copy factory directories that contain content
for subdir in templates checklists contracts guardrails knowledge; do
  if [[ -d "$FACTORY_ROOT/.claude/$subdir" ]] && [[ "$(ls -A "$FACTORY_ROOT/.claude/$subdir" 2>/dev/null)" ]]; then
    cp -r "$FACTORY_ROOT/.claude/$subdir/." "$TARGET_DIR/.claude/$subdir/"
    log_success "Copied .claude/$subdir/"
  fi
done

# =============================================================================
# Step 4: Create Product Configuration Files
# =============================================================================
log_info "Creating product configuration files..."

# --- .gitignore ---
cat > "$TARGET_DIR/.gitignore" << 'GITIGNORE'
# Environment
.env
.env.local
.env.*.local

# Dependencies
node_modules/
package-lock.json
yarn.lock
pnpm-lock.yaml

# Python
__pycache__/
*.py[cod]
venv/
.venv/

# IDE
.vscode/settings.json
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build
dist/
build/
out/

# Testing
coverage/
.nyc_output/
.pytest_cache/
.coverage

# Logs
*.log
logs/

# Claude temporary files
.claude/memory/*.tmp
.claude/logs/

# Secrets
*.pem
*.key
credentials.json
secrets/
GITIGNORE
log_success "Created .gitignore"

# --- .env.example ---
if [[ -f "$FACTORY_ROOT/.env.example" ]]; then
  cp "$FACTORY_ROOT/.env.example" "$TARGET_DIR/.env.example"
  log_success "Copied .env.example"
fi

# --- Product-specific README ---
cat > "$TARGET_DIR/README.md" << EOF
# $PRODUCT_NAME

> Bootstrapped from [ProjectZeroFactory](https://github.com/your-org/ProjectZeroFactory)

## Overview

This product was created using ProjectZeroFactory and follows its governed development process.

## Getting Started

1. Install dependencies (once package.json is created):
   \`\`\`bash
   npm install
   \`\`\`

2. Configure environment:
   \`\`\`bash
   cp .env.example .env
   # Edit .env with your values
   \`\`\`

3. Start Claude Code:
   \`\`\`bash
   claude
   \`\`\`

4. Initialize:
   \`\`\`
   /factory-init
   \`\`\`

## Governance

This product follows the ProjectZeroFactory governance model:

- **BMAD**: Business, Market, Architecture, Delivery
- **SPARC**: Specification, Pseudocode, Architecture, Refinement, Completion
- **TDD**: Test-Driven Development (80% minimum coverage)
- **No Ticket No Work**: Every change is tracked
- **Maker-Checker-Reviewer-Approver**: Four-eye principle

## Command Flow

\`\`\`
/factory-init -> /spec -> /arch -> /implement -> /check -> /review -> /approve -> /release
\`\`\`

## Directory Structure

\`\`\`
$PRODUCT_NAME/
  .claude/           # Governance, memory, and configuration
  src/               # Source code
    components/      # UI components
    services/        # Business logic and API services
    utils/           # Utility functions
    types/           # Type definitions
  tests/             # Test suites
    unit/            # Unit tests
    integration/     # Integration tests
    e2e/             # End-to-end tests
  docs/              # Documentation
    adr/             # Architecture Decision Records
    api/             # API documentation
  scripts/           # Build and utility scripts
  config/            # Configuration files
\`\`\`
EOF
log_success "Created README.md"

# --- Memory initialization ---
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

cat > "$TARGET_DIR/.claude/memory/session-log.md" << EOF
# Session Log -- $PRODUCT_NAME

## $TIMESTAMP -- Repository Initialized
- Product initialized from ProjectZeroFactory
- Factory version: $(grep -o '"version": "[^"]*"' "$FACTORY_ROOT/.claude/settings.json" 2>/dev/null | head -1 | cut -d'"' -f4 || echo "unknown")
- Directory structure created
- Governance files copied
- Awaiting /factory-init
EOF

cat > "$TARGET_DIR/.claude/memory/decisions.md" << EOF
# Architecture & Design Decisions -- $PRODUCT_NAME

<!-- Format:
## YYYY-MM-DD -- [TICKET-ID] Decision Title
**Decision**: What was decided
**Alternatives**: What else was considered
**Rationale**: Why this option was chosen
**Consequences**: What this means going forward
-->
EOF

cat > "$TARGET_DIR/.claude/memory/blockers.md" << EOF
# Blockers & Resolutions -- $PRODUCT_NAME

<!-- Format:
## YYYY-MM-DD -- [TICKET-ID] Blocker Title
**Description**: What is blocking progress
**Impact**: What cannot proceed until this is resolved
**Resolution**: How it was resolved (filled in after resolution)
**Time to Resolve**: How long it took
-->
EOF

cat > "$TARGET_DIR/.claude/memory/patterns.md" << EOF
# Reusable Patterns -- $PRODUCT_NAME

<!-- Format:
## YYYY-MM-DD -- Pattern Name
**Context**: When this pattern applies
**Implementation**: How to implement it
**Benefits**: Why it works well
**Promote to Factory**: Yes/No (if Yes, submit for factory-level review)
-->
EOF

cat > "$TARGET_DIR/.claude/memory/learnings.md" << EOF
# Learnings -- $PRODUCT_NAME

<!-- Format:
## YYYY-MM-DD -- [TICKET-ID] Learning Title
**What Happened**: Description of the event
**What We Learned**: The takeaway
**Future Action**: How this changes our approach going forward
-->
EOF

log_success "Initialized memory files"

# --- ADR template ---
cat > "$TARGET_DIR/docs/adr/000-template.md" << 'EOF'
# ADR-NNN: [Title]

## Status
Proposed | Accepted | Deprecated | Superseded

## Context
What is the issue that we are seeing that is motivating this decision or change?

## Decision
What is the change that we are proposing and/or doing?

## Consequences
What becomes easier or more difficult to do because of this change?

## Alternatives Considered
What other options were evaluated? Why were they rejected?
EOF
log_success "Created ADR template"

# =============================================================================
# Step 5: Initialize Git
# =============================================================================
log_info "Initializing git repository..."

cd "$TARGET_DIR"

if [[ -d ".git" ]]; then
  log_warn "Git already initialized. Skipping git init."
else
  if ! git init -b main; then
    log_error "Failed to initialize git repository."
    exit 4
  fi
  log_success "Initialized git with 'main' branch"
fi

# =============================================================================
# Step 6: Initial Commit
# =============================================================================
log_info "Creating initial commit..."

# Check if there are files to commit
if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
  git add -A
  FACTORY_VERSION=$(grep -o '"version": "[^"]*"' "$FACTORY_ROOT/.claude/settings.json" 2>/dev/null | head -1 | cut -d'"' -f4 || echo "unknown")

  git commit -m "feat: initialize $PRODUCT_NAME from ProjectZeroFactory v$FACTORY_VERSION

- Standard directory structure created
- Governance files copied from factory
- Memory system initialized
- Ready for /factory-init

Factory: $FACTORY_ROOT"

  log_success "Initial commit created"
else
  log_info "No new files to commit"
fi

# =============================================================================
# Done
# =============================================================================
echo ""
echo -e "${GREEN}${BOLD}Repository initialized successfully.${NC}"
echo -e "  Product: $PRODUCT_NAME"
echo -e "  Location: $TARGET_DIR"
echo -e "  Branch: main"
echo ""
echo -e "Next: ${BLUE}cd $TARGET_DIR && claude${NC}"
echo -e "Then: ${BLUE}/factory-init${NC}"
