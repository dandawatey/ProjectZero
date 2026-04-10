#!/usr/bin/env bash
# =============================================================================
# bootstrap-product.sh
# Creates a new product repository from the ProjectZeroFactory template.
#
# Usage:
#   bash scripts/bootstrap-product.sh
#   bash scripts/bootstrap-product.sh --name my-product --dir ../my-product
#
# This script:
#   1. Validates that it is running from a valid factory repo
#   2. Asks for the product name (or accepts --name flag)
#   3. Creates or validates the product directory
#   4. Copies the .claude/ template to the product
#   5. Initializes git in the product
#   6. Validates the .env configuration
#   7. Prints next steps
# =============================================================================

set -euo pipefail

# --- Color Output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }
log_step()    { echo -e "\n${BOLD}>>> $1${NC}"; }

# --- Determine Factory Root ---
# The script may be called from the factory root or from scripts/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FACTORY_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# --- Parse Arguments ---
PRODUCT_NAME=""
PRODUCT_DIR=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --name)
      PRODUCT_NAME="$2"
      shift 2
      ;;
    --dir)
      PRODUCT_DIR="$2"
      shift 2
      ;;
    --help|-h)
      echo "Usage: bash scripts/bootstrap-product.sh [--name PRODUCT_NAME] [--dir PRODUCT_DIR]"
      echo ""
      echo "Options:"
      echo "  --name    Product name (will be prompted if not provided)"
      echo "  --dir     Product directory path (defaults to ../PRODUCT_NAME)"
      echo "  --help    Show this help message"
      exit 0
      ;;
    *)
      log_error "Unknown argument: $1"
      exit 1
      ;;
  esac
done

# =============================================================================
# Step 1: Validate Factory Repository
# =============================================================================
log_step "Step 1: Validating factory repository"

if [[ ! -f "$FACTORY_ROOT/.claude/CLAUDE.md" ]]; then
  log_error "Cannot find .claude/CLAUDE.md in $FACTORY_ROOT"
  log_error "This script must be run from a valid ProjectZeroFactory repository."
  exit 1
fi

if [[ ! -f "$FACTORY_ROOT/.claude/settings.json" ]]; then
  log_error "Cannot find .claude/settings.json in $FACTORY_ROOT"
  log_error "Factory configuration is missing. Re-clone the factory repository."
  exit 1
fi

if [[ ! -d "$FACTORY_ROOT/.git" ]]; then
  log_error "Factory repository is not a git repo. Initialize git first."
  exit 1
fi

log_success "Factory repository validated at: $FACTORY_ROOT"

# =============================================================================
# Step 2: Get Product Name
# =============================================================================
log_step "Step 2: Product configuration"

if [[ -z "$PRODUCT_NAME" ]]; then
  echo -n "Enter product name (lowercase, hyphens allowed, e.g. customer-portal): "
  read -r PRODUCT_NAME
fi

# Validate product name
if [[ -z "$PRODUCT_NAME" ]]; then
  log_error "Product name cannot be empty."
  exit 1
fi

if [[ ! "$PRODUCT_NAME" =~ ^[a-z][a-z0-9-]*$ ]]; then
  log_error "Invalid product name: '$PRODUCT_NAME'"
  log_error "Product name must start with a lowercase letter and contain only lowercase letters, numbers, and hyphens."
  exit 1
fi

log_success "Product name: $PRODUCT_NAME"

# =============================================================================
# Step 3: Create or Validate Product Directory
# =============================================================================
log_step "Step 3: Setting up product directory"

if [[ -z "$PRODUCT_DIR" ]]; then
  PRODUCT_DIR="$(dirname "$FACTORY_ROOT")/$PRODUCT_NAME"
  echo -n "Product directory [$PRODUCT_DIR]: "
  read -r USER_DIR
  if [[ -n "$USER_DIR" ]]; then
    PRODUCT_DIR="$USER_DIR"
  fi
fi

# Resolve to absolute path
PRODUCT_DIR="$(cd "$(dirname "$PRODUCT_DIR")" 2>/dev/null && pwd)/$(basename "$PRODUCT_DIR")" 2>/dev/null || PRODUCT_DIR="$PRODUCT_DIR"

if [[ -d "$PRODUCT_DIR" ]]; then
  # Directory exists -- check if it is empty or already bootstrapped
  if [[ -f "$PRODUCT_DIR/.claude/CLAUDE.md" ]]; then
    log_warn "Product directory already contains a .claude/ configuration."
    echo -n "Overwrite existing .claude/ configuration? (y/N): "
    read -r OVERWRITE
    if [[ "$OVERWRITE" != "y" && "$OVERWRITE" != "Y" ]]; then
      log_info "Keeping existing configuration. Skipping copy step."
      SKIP_COPY=true
    fi
  elif [[ "$(ls -A "$PRODUCT_DIR" 2>/dev/null)" ]]; then
    log_warn "Directory $PRODUCT_DIR exists and is not empty."
    echo -n "Continue anyway? Files will not be deleted. (y/N): "
    read -r CONTINUE
    if [[ "$CONTINUE" != "y" && "$CONTINUE" != "Y" ]]; then
      log_error "Aborted by user."
      exit 1
    fi
  fi
else
  mkdir -p "$PRODUCT_DIR"
  log_success "Created product directory: $PRODUCT_DIR"
fi

# =============================================================================
# Step 4: Copy .claude/ Template to Product
# =============================================================================
log_step "Step 4: Copying governance template"

if [[ "${SKIP_COPY:-false}" != "true" ]]; then
  # Create the .claude directory structure in the product
  mkdir -p "$PRODUCT_DIR/.claude/memory"
  mkdir -p "$PRODUCT_DIR/.claude/knowledge"
  mkdir -p "$PRODUCT_DIR/.claude/checkpoints"

  # Copy the operating contract
  cp "$FACTORY_ROOT/.claude/CLAUDE.md" "$PRODUCT_DIR/.claude/CLAUDE.md"
  log_success "Copied CLAUDE.md (operating contract)"

  # Copy settings, but mark it as a product instance
  if [[ -f "$FACTORY_ROOT/.claude/settings.json" ]]; then
    cp "$FACTORY_ROOT/.claude/settings.json" "$PRODUCT_DIR/.claude/settings.json"
    log_success "Copied settings.json"
  fi

  # Copy templates if they exist
  if [[ -d "$FACTORY_ROOT/.claude/templates" ]]; then
    cp -r "$FACTORY_ROOT/.claude/templates" "$PRODUCT_DIR/.claude/templates"
    log_success "Copied templates/"
  fi

  # Copy checklists if they exist
  if [[ -d "$FACTORY_ROOT/.claude/checklists" ]]; then
    cp -r "$FACTORY_ROOT/.claude/checklists" "$PRODUCT_DIR/.claude/checklists"
    log_success "Copied checklists/"
  fi

  # Copy contracts if they exist
  if [[ -d "$FACTORY_ROOT/.claude/contracts" ]]; then
    cp -r "$FACTORY_ROOT/.claude/contracts" "$PRODUCT_DIR/.claude/contracts"
    log_success "Copied contracts/"
  fi

  # Copy guardrails if they exist
  if [[ -d "$FACTORY_ROOT/.claude/guardrails" ]]; then
    cp -r "$FACTORY_ROOT/.claude/guardrails" "$PRODUCT_DIR/.claude/guardrails"
    log_success "Copied guardrails/"
  fi

  # Initialize memory files
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  cat > "$PRODUCT_DIR/.claude/memory/session-log.md" << EOF
# Session Log -- $PRODUCT_NAME

## $TIMESTAMP -- Product Bootstrapped
- Product created from ProjectZeroFactory
- Factory root: $FACTORY_ROOT
- Governance template copied
- Ready for /factory-init
EOF

  cat > "$PRODUCT_DIR/.claude/memory/decisions.md" << EOF
# Architecture & Design Decisions -- $PRODUCT_NAME

<!-- Record all significant decisions here. Each entry must include:
     - Date
     - Ticket ID
     - Decision made
     - Alternatives considered
     - Rationale for the choice
-->
EOF

  cat > "$PRODUCT_DIR/.claude/memory/blockers.md" << EOF
# Blockers & Resolutions -- $PRODUCT_NAME

<!-- Record blockers encountered and how they were resolved.
     Each entry must include:
     - Date
     - Ticket ID (if applicable)
     - Description of the blocker
     - Resolution
     - Time to resolve
-->
EOF

  cat > "$PRODUCT_DIR/.claude/memory/patterns.md" << EOF
# Reusable Patterns -- $PRODUCT_NAME

<!-- Record patterns discovered during development.
     Each entry must include:
     - Date
     - Pattern name
     - Context where it applies
     - Implementation notes
     - Whether it should be promoted to factory level
-->
EOF

  cat > "$PRODUCT_DIR/.claude/memory/learnings.md" << EOF
# Learnings -- $PRODUCT_NAME

<!-- Record lessons learned for future reference.
     Each entry must include:
     - Date
     - Ticket ID (if applicable)
     - What was learned
     - How it changes future approach
-->
EOF

  log_success "Initialized memory files"
else
  log_info "Skipped .claude/ copy (existing configuration preserved)"
fi

# =============================================================================
# Step 5: Initialize Git in Product
# =============================================================================
log_step "Step 5: Initializing git repository"

if [[ -d "$PRODUCT_DIR/.git" ]]; then
  log_info "Git repository already initialized in $PRODUCT_DIR"
else
  cd "$PRODUCT_DIR"
  git init -b main
  log_success "Initialized git repository with 'main' branch"

  # Create a .gitignore for the product
  cat > "$PRODUCT_DIR/.gitignore" << 'GITIGNORE'
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

  # Create initial commit
  git add -A
  git commit -m "feat: bootstrap product from ProjectZeroFactory

Product: $PRODUCT_NAME
Factory: $FACTORY_ROOT
Template version: $(cat "$FACTORY_ROOT/.claude/settings.json" | grep -o '"version": "[^"]*"' | head -1 | cut -d'"' -f4)"
  log_success "Created initial commit"
fi

# =============================================================================
# Step 6: Validate Environment
# =============================================================================
log_step "Step 6: Validating environment"

# Copy .env.example to product if it exists and product doesn't have one
if [[ -f "$FACTORY_ROOT/.env.example" && ! -f "$PRODUCT_DIR/.env.example" ]]; then
  cp "$FACTORY_ROOT/.env.example" "$PRODUCT_DIR/.env.example"
  log_success "Copied .env.example to product"
fi

# Check if factory .env exists and has the minimum required keys
if [[ -f "$FACTORY_ROOT/.env" ]]; then
  MISSING_KEYS=()

  check_env_key() {
    local key="$1"
    local value
    value=$(grep "^${key}=" "$FACTORY_ROOT/.env" 2>/dev/null | cut -d'=' -f2- | tr -d '[:space:]')
    if [[ -z "$value" ]]; then
      MISSING_KEYS+=("$key")
    fi
  }

  check_env_key "ANTHROPIC_API_KEY"
  check_env_key "GITHUB_TOKEN"
  check_env_key "GITHUB_ORG"

  if [[ ${#MISSING_KEYS[@]} -gt 0 ]]; then
    log_warn "The following required keys are missing or empty in factory .env:"
    for key in "${MISSING_KEYS[@]}"; do
      echo -e "  ${YELLOW}- $key${NC}"
    done
    log_warn "Set these in $FACTORY_ROOT/.env before running /factory-init"
  else
    log_success "Factory .env has all required keys"
  fi
else
  log_warn "No .env file found in factory. Copy .env.example to .env and configure it."
fi

# =============================================================================
# Step 7: Print Next Steps
# =============================================================================
log_step "Bootstrap Complete"

echo ""
echo -e "${GREEN}${BOLD}Product '$PRODUCT_NAME' has been created successfully.${NC}"
echo ""
echo -e "${BOLD}Product location:${NC} $PRODUCT_DIR"
echo ""
echo -e "${BOLD}Next steps:${NC}"
echo ""
echo -e "  1. Navigate to the product directory:"
echo -e "     ${BLUE}cd $PRODUCT_DIR${NC}"
echo ""
echo -e "  2. Configure environment (if not already done):"
echo -e "     ${BLUE}cp .env.example .env${NC}"
echo -e "     ${BLUE}# Edit .env with your API keys${NC}"
echo ""
echo -e "  3. Start Claude Code:"
echo -e "     ${BLUE}claude${NC}"
echo ""
echo -e "  4. Run the factory initialization:"
echo -e "     ${BLUE}/factory-init${NC}"
echo ""
echo -e "  5. Follow the governed command flow:"
echo -e "     ${BLUE}/spec -> /arch -> /implement -> /check -> /review -> /approve -> /release${NC}"
echo ""
echo -e "${BOLD}Governance rules are active.${NC} All work must follow:"
echo -e "  - BMAD (Business, Market, Architecture, Delivery)"
echo -e "  - SPARC (Specification, Pseudocode, Architecture, Refinement, Completion)"
echo -e "  - TDD (Test-Driven Development, 80% minimum coverage)"
echo -e "  - No Ticket No Work"
echo -e "  - Maker-Checker-Reviewer-Approver"
echo ""
echo -e "${BOLD}Happy building.${NC}"
