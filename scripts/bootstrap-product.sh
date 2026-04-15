#!/usr/bin/env bash
# =============================================================================
# bootstrap-product.sh — ProjectZeroFactory product bootstrapper
#
# Greenfield:  creates GitHub repo, JIRA project, Confluence space, clones
#              into sibling directory, injects scaffold, writes .env, pushes.
#
# Brownfield:  connects to existing resources, injects scaffold into existing
#              repo, audits codebase.
#
# Usage:
#   ./scripts/bootstrap-product.sh
#   ./scripts/bootstrap-product.sh --name i-comply
#   ./scripts/bootstrap-product.sh --name i-comply --description "Compliance platform"
#   ./scripts/bootstrap-product.sh --brownfield --name my-app --github=org/my-app --jira=MYAPP
#   ./scripts/bootstrap-product.sh --name i-comply --skip=temporal,confluence
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FACTORY_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

ok()    { echo -e "${GREEN}✓${RESET}  $*"; }
warn()  { echo -e "${YELLOW}⚠${RESET}  $*"; }
err()   { echo -e "${RED}✗${RESET}  $*"; exit 1; }
info()  { echo -e "${CYAN}→${RESET}  $*"; }
step()  { echo -e "\n${BOLD}── $* ──${RESET}"; }
ask()   { echo -en "${CYAN}?${RESET}  $* "; }

# ── Parse flags ───────────────────────────────────────────────────────────────
MODE="greenfield"
PRODUCT_NAME=""
PRODUCT_DESC=""
PRODUCT_ROOT_OVERRIDE=""
GITHUB_EXISTING=""
GITHUB_ORG_OVERRIDE=""
OPEN_AFTER=true
JIRA_EXISTING=""
CONFLUENCE_EXISTING=""
TEMPORAL_QUEUE_EXISTING=""
PRD_PATH=""
SKIP_STEPS=""

while [[ $# -gt 0 ]]; do
  arg="$1"
  case "$arg" in
    --brownfield|--partial)   MODE="brownfield";          shift ;;
    --name=*)                 PRODUCT_NAME="${arg#*=}";   shift ;;
    --name)                   PRODUCT_NAME="${2:-}";      shift 2 ;;
    --description=*)          PRODUCT_DESC="${arg#*=}";   shift ;;
    --description)            PRODUCT_DESC="${2:-}";      shift 2 ;;
    --root=*)                 PRODUCT_ROOT_OVERRIDE="${arg#*=}"; shift ;;
    --root)                   PRODUCT_ROOT_OVERRIDE="${2:-}"; shift 2 ;;
    --github=*)               GITHUB_EXISTING="${arg#*=}"; shift ;;
    --github)                 GITHUB_EXISTING="${2:-}";   shift 2 ;;
    --org=*)                  GITHUB_ORG_OVERRIDE="${arg#*=}"; shift ;;
    --org)                    GITHUB_ORG_OVERRIDE="${2:-}"; shift 2 ;;
    --no-open)                OPEN_AFTER=false; shift ;;
    --jira=*)                 JIRA_EXISTING="${arg#*=}";  shift ;;
    --jira)                   JIRA_EXISTING="${2:-}";     shift 2 ;;
    --confluence=*)           CONFLUENCE_EXISTING="${arg#*=}"; shift ;;
    --confluence)             CONFLUENCE_EXISTING="${2:-}"; shift 2 ;;
    --temporal-queue=*)       TEMPORAL_QUEUE_EXISTING="${arg#*=}"; shift ;;
    --temporal-queue)         TEMPORAL_QUEUE_EXISTING="${2:-}"; shift 2 ;;
    --prd=*)                  PRD_PATH="${arg#*=}";       shift ;;
    --prd)                    PRD_PATH="${2:-}";          shift 2 ;;
    --skip=*)                 SKIP_STEPS="${arg#*=}";     shift ;;
    --skip)                   SKIP_STEPS="${2:-}";        shift 2 ;;
    --help|-h)
      echo "Usage: ./scripts/bootstrap-product.sh [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --name=NAME              Product name (lowercase, hyphens)"
      echo "  --description=DESC       One-line product description"
      echo "  --brownfield             Connect to existing resources"
      echo "  --root=PATH              Custom PRODUCT_ROOT (default: sibling of factory)"
      echo "  --github=ORG/REPO        Existing GitHub repo (brownfield)"
      echo "  --jira=KEY               Existing JIRA project key (brownfield)"
      echo "  --confluence=KEY         Existing Confluence space key (brownfield)"
      echo "  --temporal-queue=NAME    Existing Temporal queue (brownfield)"
      echo "  --prd=PATH               Path to PRD/BMAD doc"
      echo "  --skip=STEPS             Comma-separated: github,jira,confluence,temporal,prd"
      echo "  --skip=all-integrations  Skip all external integrations"
      echo ""
      echo "Examples:"
      echo "  ./scripts/bootstrap-product.sh --name i-comply"
      echo "  ./scripts/bootstrap-product.sh --brownfield --name my-app --github=org/my-app --skip=confluence"
      exit 0
      ;;
    -*)
      err "Unknown flag: $arg"
      ;;
    *)
      [[ -z "$PRODUCT_NAME" ]] && PRODUCT_NAME="$arg"
      shift
      ;;
  esac
done

# Brownfield auto-detect: if --github provided, assume brownfield
if [[ -n "$GITHUB_EXISTING" && "$MODE" == "greenfield" ]]; then
  MODE="brownfield"
fi

# Stash CLI values so load_env cannot overwrite them
_CLI_PRODUCT_NAME="$PRODUCT_NAME"
_CLI_PRODUCT_DESC="$PRODUCT_DESC"
_CLI_MODE="$MODE"

# Skip helpers
skip() { echo "$SKIP_STEPS" | tr ',' '\n' | grep -qx "$1" || [[ "$SKIP_STEPS" == "all-integrations" ]]; }

# ── Load env ──────────────────────────────────────────────────────────────────
# Safely parse only KEY=VALUE lines — skip comments, blank lines, bare words
load_env() {
  local env_file
  for env_file in "$FACTORY_ROOT/.env" "$FACTORY_ROOT/platform/backend/.env"; do
    [[ -f "$env_file" ]] || continue
    while IFS= read -r line; do
      # Skip comments and blank lines
      [[ "$line" =~ ^[[:space:]]*# ]] && continue
      [[ -z "${line// }" ]] && continue
      # Only process KEY=VALUE lines
      [[ "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]] || continue
      export "$line" 2>/dev/null || true
    done < "$env_file"
  done
}

# ── GitHub token: .env → keychain fallback ───────────────────────────────────
resolve_github_token() {
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    echo "$GITHUB_TOKEN"; return
  fi
  # Keychain fallback (macOS)
  local creds
  creds=$(git credential fill <<< $'protocol=https\nhost=github.com\n' 2>/dev/null || true)
  echo "$creds" | grep '^password=' | cut -d= -f2-
}

# ── GitHub API helper ─────────────────────────────────────────────────────────
gh_api() {
  local method="$1" path="$2" data="${3:-}"
  local token
  token=$(resolve_github_token)
  if [[ -z "$token" ]]; then
    warn "No GitHub token found. Set GITHUB_TOKEN in .env or run: gh auth login"
    return 1
  fi
  if [[ -n "$data" ]]; then
    curl -sf -X "$method" \
      -H "Authorization: token $token" \
      -H "Accept: application/vnd.github.v3+json" \
      -H "Content-Type: application/json" \
      "https://api.github.com$path" \
      -d "$data"
  else
    curl -sf -X "$method" \
      -H "Authorization: token $token" \
      -H "Accept: application/vnd.github.v3+json" \
      "https://api.github.com$path"
  fi
}

# ── Jira/Confluence auth ──────────────────────────────────────────────────────
atlassian_auth() {
  echo -n "${JIRA_USER_EMAIL:-}:${JIRA_API_TOKEN:-}" | base64
}

jira_api() {
  local method="$1" path="$2" data="${3:-}"
  local base="${JIRA_BASE_URL:-}"
  [[ -z "$base" ]] && { warn "JIRA_BASE_URL not set"; return 1; }
  if [[ -n "$data" ]]; then
    curl -sf -X "$method" \
      -H "Authorization: Basic $(atlassian_auth)" \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      "$base$path" -d "$data"
  else
    curl -sf -X "$method" \
      -H "Authorization: Basic $(atlassian_auth)" \
      -H "Accept: application/json" \
      "$base$path"
  fi
}

confluence_api() {
  local method="$1" path="$2" data="${3:-}"
  local base="${CONFLUENCE_BASE_URL:-}"
  [[ -z "$base" ]] && { warn "CONFLUENCE_BASE_URL not set"; return 1; }
  local token="${CONFLUENCE_API_TOKEN:-${JIRA_API_TOKEN:-}}"
  local auth
  auth=$(echo -n "${JIRA_USER_EMAIL:-}:$token" | base64)
  if [[ -n "$data" ]]; then
    curl -sf -X "$method" \
      -H "Authorization: Basic $auth" \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      "$base$path" -d "$data"
  else
    curl -sf -X "$method" \
      -H "Authorization: Basic $auth" \
      -H "Accept: application/json" \
      "$base$path"
  fi
}

# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

# Load env first so args can override
load_env

# Re-apply CLI args over any .env values (args always win)
[[ -n "$_CLI_PRODUCT_NAME" ]]  && PRODUCT_NAME="$_CLI_PRODUCT_NAME"
[[ -n "$_CLI_PRODUCT_DESC" ]]  && PRODUCT_DESC="$_CLI_PRODUCT_DESC"
[[ -n "$_CLI_MODE" ]]          && MODE="$_CLI_MODE"

echo ""
echo -e "${BOLD}ProjectZeroFactory — Product Bootstrap${RESET}"
echo "════════════════════════════════════════"
echo -e "Mode: ${CYAN}${MODE}${RESET}"
echo ""

# ── Step 1: Validate factory ──────────────────────────────────────────────────
step "Step 1: Validate factory"

[[ -f "$FACTORY_ROOT/.claude/CLAUDE.md" ]]   || err "Not a valid factory: missing .claude/CLAUDE.md"
[[ -f "$FACTORY_ROOT/.claude/settings.json" ]] || err "Not a valid factory: missing .claude/settings.json"
[[ -d "$FACTORY_ROOT/.git" ]]                 || err "Factory is not a git repo"
ok "Factory validated: $FACTORY_ROOT"

# ── Step 2: Product identity ──────────────────────────────────────────────────
step "Step 2: Product identity"

if [[ -z "$PRODUCT_NAME" ]]; then
  ask "Product name (lowercase, hyphens, e.g. i-comply):"
  read -r PRODUCT_NAME
fi

[[ -z "$PRODUCT_NAME" ]] && err "Product name required"
[[ "$PRODUCT_NAME" =~ ^[a-z][a-z0-9-]*$ ]] || err "Invalid name '$PRODUCT_NAME' — lowercase letters, numbers, hyphens only"

if [[ -z "$PRODUCT_DESC" ]]; then
  ask "One-line description [press enter to skip]:"
  read -r PRODUCT_DESC
  PRODUCT_DESC="${PRODUCT_DESC:-${PRODUCT_NAME} — managed by ProjectZeroFactory}"
fi

# Derive JIRA key: uppercase, max 8 chars, letters only
JIRA_KEY_AUTO=$(echo "$PRODUCT_NAME" | tr -d '-' | tr '[:lower:]' '[:upper:]' | cut -c1-8)

ok "Name: $PRODUCT_NAME"
ok "Description: $PRODUCT_DESC"

# ── Step 3: Resolve PRODUCT_ROOT ─────────────────────────────────────────────
step "Step 3: Resolve PRODUCT_ROOT"

if [[ -n "$PRODUCT_ROOT_OVERRIDE" ]]; then
  PRODUCT_ROOT="$(realpath "$PRODUCT_ROOT_OVERRIDE" 2>/dev/null || echo "$PRODUCT_ROOT_OVERRIDE")"
else
  PRODUCT_ROOT="$(dirname "$FACTORY_ROOT")/$PRODUCT_NAME"
fi

info "Layout:"
info "  $(dirname "$FACTORY_ROOT")/"
info "  ├── $(basename "$FACTORY_ROOT")/   ← factory"
info "  └── $PRODUCT_NAME/                 ← PRODUCT_ROOT"
echo ""

# Safety: never operate in factory root
[[ "$PRODUCT_ROOT" == "$FACTORY_ROOT" ]] && err "PRODUCT_ROOT == FACTORY_ROOT — refusing to overwrite factory"

ok "PRODUCT_ROOT: $PRODUCT_ROOT"

# ── Step 4: GitHub ────────────────────────────────────────────────────────────
step "Step 4: GitHub"

GITHUB_REPO_FULL=""
GH_TOKEN=$(resolve_github_token)

if skip "github"; then
  warn "GitHub skipped — using PRODUCT_ROOT as-is"
  mkdir -p "$PRODUCT_ROOT"
  if [[ ! -d "$PRODUCT_ROOT/.git" ]]; then
    git -C "$PRODUCT_ROOT" init -b main
    ok "git init in $PRODUCT_ROOT"
  fi

elif [[ -n "$GITHUB_EXISTING" ]]; then
  info "Brownfield — cloning existing repo: $GITHUB_EXISTING"
  if [[ ! -d "$PRODUCT_ROOT" ]]; then
    git clone "https://${GH_TOKEN}@github.com/${GITHUB_EXISTING}.git" "$PRODUCT_ROOT"
  else
    warn "$PRODUCT_ROOT already exists — skipping clone"
  fi
  GITHUB_REPO_FULL="$GITHUB_EXISTING"
  ok "Cloned: $GITHUB_EXISTING → $PRODUCT_ROOT"

else
  # Greenfield — create or reuse repo
  if [[ -z "$GH_TOKEN" ]]; then
    err "No GitHub token. Set GITHUB_TOKEN in .env or run: gh auth login"
  fi

  GH_LOGIN=$(gh_api GET /user | python3 -c "import sys,json; print(json.load(sys.stdin)['login'])" 2>/dev/null || echo "")
  [[ -z "$GH_LOGIN" ]] && err "GitHub auth failed — check token"

  # Resolve owner: org flag > .env GITHUB_ORG > personal login
  GH_OWNER="${GITHUB_ORG_OVERRIDE:-${GITHUB_ORG:-$GH_LOGIN}}"
  # If owner == personal login, use /user/repos; else use /orgs/{org}/repos
  if [[ "$GH_OWNER" == "$GH_LOGIN" ]]; then
    GH_REPOS_ENDPOINT="/user/repos"
  else
    GH_REPOS_ENDPOINT="/orgs/$GH_OWNER/repos"
    info "Using org: $GH_OWNER"
  fi

  # Corner case: check if repo already exists before trying to create
  EXISTING_JSON=$(gh_api GET "/repos/$GH_OWNER/$PRODUCT_NAME" 2>/dev/null || echo "")

  if [[ -n "$EXISTING_JSON" ]]; then
    warn "GitHub repo already exists: $GH_OWNER/$PRODUCT_NAME"
    ask "Use existing repo? [Y/n]:"
    read -r USE_EXISTING
    if [[ "${USE_EXISTING:-Y}" =~ ^[Nn]$ ]]; then
      ask "New repo name:"
      read -r PRODUCT_NAME_NEW
      [[ -z "$PRODUCT_NAME_NEW" ]] && err "No name provided — aborting"
      PRODUCT_NAME="$PRODUCT_NAME_NEW"
      EXISTING_JSON=""
    else
      REPO_JSON="$EXISTING_JSON"
      ok "Using existing repo: $GH_OWNER/$PRODUCT_NAME"
    fi
  fi

  if [[ -z "${REPO_JSON:-}" ]]; then
    info "Creating repo: $GH_OWNER/$PRODUCT_NAME"
    REPO_JSON=$(gh_api POST "$GH_REPOS_ENDPOINT" "{
      \"name\": \"$PRODUCT_NAME\",
      \"description\": \"$PRODUCT_DESC\",
      \"private\": true,
      \"auto_init\": true
    }" 2>/dev/null || echo "")
    [[ -z "$REPO_JSON" ]] && err "Failed to create GitHub repo — check token scopes (needs 'repo' or org admin)"
    ok "Repo created: $GH_OWNER/$PRODUCT_NAME"
  fi

  GITHUB_REPO_FULL=$(echo "$REPO_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['full_name'])" 2>/dev/null || echo "")
  [[ -z "$GITHUB_REPO_FULL" ]] && err "Could not parse repo full_name from GitHub response"

  # Corner case: PRODUCT_ROOT dir already exists
  if [[ -d "$PRODUCT_ROOT" ]]; then
    if [[ -d "$PRODUCT_ROOT/.git" ]]; then
      warn "Directory already exists and is a git repo: $PRODUCT_ROOT"
      ask "Use it as-is (skip clone)? [Y/n]:"
      read -r SKIP_CLONE
      if [[ "${SKIP_CLONE:-Y}" =~ ^[Nn]$ ]]; then
        err "Aborting — remove $PRODUCT_ROOT manually and retry"
      fi
      ok "Using existing directory: $PRODUCT_ROOT"
    else
      warn "Directory exists but is NOT a git repo: $PRODUCT_ROOT"
      ask "Delete and re-clone? [y/N]:"
      read -r DO_DELETE
      if [[ "${DO_DELETE:-N}" =~ ^[Yy]$ ]]; then
        rm -rf "$PRODUCT_ROOT"
        git clone "https://${GH_TOKEN}@github.com/${GITHUB_REPO_FULL}.git" "$PRODUCT_ROOT"
        ok "Cloned fresh: $PRODUCT_ROOT"
      else
        err "Aborting — resolve directory conflict manually"
      fi
    fi
  else
    git clone "https://${GH_TOKEN}@github.com/${GITHUB_REPO_FULL}.git" "$PRODUCT_ROOT"
    ok "Cloned: github.com/$GITHUB_REPO_FULL → $PRODUCT_ROOT"
  fi
fi

# Validate PRODUCT_ROOT is a git repo
[[ -d "$PRODUCT_ROOT/.git" ]] || err "$PRODUCT_ROOT is not a git repo"
[[ -w "$PRODUCT_ROOT" ]]      || err "$PRODUCT_ROOT is not writable"

# ── Step 5: JIRA ──────────────────────────────────────────────────────────────
step "Step 5: JIRA"
JIRA_KEY=""

if skip "jira"; then
  warn "JIRA skipped — ticket tracking disabled"
  JIRA_ENABLED="false"

elif [[ -n "$JIRA_EXISTING" ]]; then
  info "Validating existing JIRA project: $JIRA_EXISTING"
  JIRA_RESP=$(jira_api GET "/rest/api/3/project/$JIRA_EXISTING" 2>/dev/null || echo "")
  if [[ -z "$JIRA_RESP" ]]; then
    warn "JIRA project $JIRA_EXISTING not found — skipping JIRA"
    JIRA_ENABLED="false"
  else
    JIRA_KEY="$JIRA_EXISTING"
    JIRA_ENABLED="true"
    ok "JIRA project validated: $JIRA_KEY"
  fi

else
  if [[ -z "${JIRA_BASE_URL:-}" ]]; then
    warn "JIRA_BASE_URL not set — skipping JIRA"
    JIRA_ENABLED="false"
  else
    # Get account ID for project lead
    ACCOUNT_ID=$(jira_api GET "/rest/api/3/myself" 2>/dev/null \
      | python3 -c "import sys,json; print(json.load(sys.stdin)['accountId'])" 2>/dev/null || echo "")

    if [[ -z "$ACCOUNT_ID" ]]; then
      warn "JIRA auth failed — skipping JIRA"
      JIRA_ENABLED="false"
    else
      # Corner case: JIRA key already taken
      JIRA_KEY_CHECK=$(jira_api GET "/rest/api/3/project/$JIRA_KEY_AUTO" 2>/dev/null || echo "")
      if [[ -n "$JIRA_KEY_CHECK" ]]; then
        warn "JIRA project key '$JIRA_KEY_AUTO' already exists"
        ask "Use existing project '$JIRA_KEY_AUTO'? [Y/n]:"
        read -r USE_JIRA_EXISTING
        if [[ "${USE_JIRA_EXISTING:-Y}" =~ ^[Nn]$ ]]; then
          ask "Enter a different JIRA key (max 8 uppercase letters):"
          read -r JIRA_KEY_AUTO
          JIRA_KEY_AUTO=$(echo "$JIRA_KEY_AUTO" | tr '[:lower:]' '[:upper:]' | tr -cd 'A-Z' | cut -c1-8)
          [[ -z "$JIRA_KEY_AUTO" ]] && { warn "Invalid key — skipping JIRA"; JIRA_ENABLED="false"; }
        else
          JIRA_KEY="$JIRA_KEY_AUTO"
          JIRA_ENABLED="true"
          ok "Using existing JIRA project: $JIRA_KEY"
        fi
      fi

      if [[ -z "${JIRA_KEY:-}" && "${JIRA_ENABLED:-}" != "false" ]]; then
        info "Creating JIRA project: $JIRA_KEY_AUTO"
        JIRA_RESP=$(jira_api POST "/rest/api/3/project" "{
          \"key\": \"$JIRA_KEY_AUTO\",
          \"name\": \"$PRODUCT_NAME\",
          \"description\": \"$PRODUCT_DESC\",
          \"projectTypeKey\": \"software\",
          \"leadAccountId\": \"$ACCOUNT_ID\",
          \"assigneeType\": \"UNASSIGNED\"
        }" 2>/dev/null || echo "")

        JIRA_KEY=$(echo "$JIRA_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('key',''))" 2>/dev/null || echo "")
        if [[ -n "$JIRA_KEY" ]]; then
          ok "JIRA project created: $JIRA_KEY"
          JIRA_ENABLED="true"
        else
          ERR_MSG=$(echo "$JIRA_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('errors',d.get('errorMessages','')))" 2>/dev/null || echo "$JIRA_RESP")
          warn "JIRA create failed: $ERR_MSG — skipping JIRA"
          JIRA_ENABLED="false"
        fi
      fi
    fi
  fi
fi

JIRA_KEY="${JIRA_KEY:-}"
JIRA_ENABLED="${JIRA_ENABLED:-false}"

# ── Step 6: Confluence ────────────────────────────────────────────────────────
step "Step 6: Confluence"
CONFLUENCE_KEY=""

if skip "confluence"; then
  warn "Confluence skipped — doc sync disabled"
  CONFLUENCE_ENABLED="false"

elif [[ -n "$CONFLUENCE_EXISTING" ]]; then
  info "Validating existing Confluence space: $CONFLUENCE_EXISTING"
  CONF_RESP=$(confluence_api GET "/rest/api/space/$CONFLUENCE_EXISTING" 2>/dev/null || echo "")
  if [[ -z "$CONF_RESP" ]]; then
    warn "Confluence space $CONFLUENCE_EXISTING not found — skipping"
    CONFLUENCE_ENABLED="false"
  else
    CONFLUENCE_KEY="$CONFLUENCE_EXISTING"
    CONFLUENCE_ENABLED="true"
    ok "Confluence space validated: $CONFLUENCE_KEY"
  fi

else
  if [[ -z "${CONFLUENCE_BASE_URL:-}" ]]; then
    warn "CONFLUENCE_BASE_URL not set — skipping Confluence"
    CONFLUENCE_ENABLED="false"
  else
    CONF_KEY_AUTO=$(echo "$JIRA_KEY_AUTO" | cut -c1-6)

    # Corner case: Confluence space key already taken
    CONF_CHECK=$(confluence_api GET "/rest/api/space/$CONF_KEY_AUTO" 2>/dev/null || echo "")
    if [[ -n "$CONF_CHECK" ]]; then
      warn "Confluence space '$CONF_KEY_AUTO' already exists"
      ask "Use existing space '$CONF_KEY_AUTO'? [Y/n]:"
      read -r USE_CONF_EXISTING
      if [[ "${USE_CONF_EXISTING:-Y}" =~ ^[Nn]$ ]]; then
        ask "Enter a different space key (max 6 uppercase letters):"
        read -r CONF_KEY_AUTO
        CONF_KEY_AUTO=$(echo "$CONF_KEY_AUTO" | tr '[:lower:]' '[:upper:]' | tr -cd 'A-Z0-9' | cut -c1-6)
        [[ -z "$CONF_KEY_AUTO" ]] && { warn "Invalid key — skipping Confluence"; CONFLUENCE_ENABLED="false"; }
      else
        CONFLUENCE_KEY="$CONF_KEY_AUTO"
        CONFLUENCE_ENABLED="true"
        ok "Using existing Confluence space: $CONFLUENCE_KEY"
      fi
    fi

    if [[ -z "${CONFLUENCE_KEY:-}" && "${CONFLUENCE_ENABLED:-}" != "false" ]]; then
      info "Creating Confluence space: $CONF_KEY_AUTO"
      CONF_RESP=$(confluence_api POST "/rest/api/space" "{
        \"key\": \"$CONF_KEY_AUTO\",
        \"name\": \"$PRODUCT_NAME\",
        \"description\": {
          \"plain\": {
            \"value\": \"$PRODUCT_DESC — ProjectZero governed product\",
            \"representation\": \"plain\"
          }
        },
        \"type\": \"global\"
      }" 2>/dev/null || echo "")

      CONFLUENCE_KEY=$(echo "$CONF_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('key',''))" 2>/dev/null || echo "")
      if [[ -n "$CONFLUENCE_KEY" ]]; then
        ok "Confluence space created: $CONFLUENCE_KEY"
        CONFLUENCE_ENABLED="true"
      else
        warn "Confluence create failed — skipping"
        CONFLUENCE_ENABLED="false"
      fi
    fi
  fi
fi

CONFLUENCE_KEY="${CONFLUENCE_KEY:-}"
CONFLUENCE_ENABLED="${CONFLUENCE_ENABLED:-false}"

# ── Step 7: Inject .claude scaffold ──────────────────────────────────────────
step "Step 7: Inject factory scaffold"

# Commands
mkdir -p "$PRODUCT_ROOT/.claude/commands"
cp "$FACTORY_ROOT/.claude/commands/"*.md "$PRODUCT_ROOT/.claude/commands/"
CMD_COUNT=$(ls "$PRODUCT_ROOT/.claude/commands/"*.md 2>/dev/null | wc -l | tr -d ' ')
ok "$CMD_COUNT slash commands injected → .claude/commands/"

# Hooks
mkdir -p "$PRODUCT_ROOT/.claude/hooks"
cp "$FACTORY_ROOT/.claude/hooks/"* "$PRODUCT_ROOT/.claude/hooks/" 2>/dev/null && \
  ok "Hooks copied → .claude/hooks/" || true

# Settings
cp "$FACTORY_ROOT/.claude/settings.json" "$PRODUCT_ROOT/.claude/settings.json"
ok "settings.json copied"

# Memory structure
mkdir -p "$PRODUCT_ROOT/.claude/memory"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

for f in session-log decisions blockers patterns learnings; do
  [[ -f "$PRODUCT_ROOT/.claude/memory/$f.md" ]] || {
    FTITLE="$(echo "$f" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2); print}')"
    printf '# %s — %s\n_Bootstrapped %s_\n' "$FTITLE" "$PRODUCT_NAME" "$TIMESTAMP" \
      > "$PRODUCT_ROOT/.claude/memory/$f.md"
  }
done
ok "Memory structure initialized"

# CLAUDE.md
if [[ ! -f "$PRODUCT_ROOT/CLAUDE.md" ]]; then
cat > "$PRODUCT_ROOT/CLAUDE.md" <<EOF
# $PRODUCT_NAME

$PRODUCT_DESC

## Factory
Parent: [ProjectZeroFactory](../ProjectZeroFactory)
Operating contract: \`.claude/\`

## Integrations
- GitHub:     ${GITHUB_REPO_FULL:-$PRODUCT_NAME}
- JIRA:       ${JIRA_KEY:-disabled}
- Confluence: ${CONFLUENCE_KEY:-disabled}

## Quick Start
Open in Claude Code and type \`/\` to access all factory commands.
Start with \`/spec\` or \`/vision-to-prd\`.
EOF
ok "CLAUDE.md written"
fi

# ── Step 8: Write product .env to PRODUCT_ROOT ───────────────────────────────
step "Step 8: Write product .env"

TEMPORAL_QUEUE="${TEMPORAL_QUEUE_EXISTING:-$PRODUCT_NAME-task-queue}"
TEMPORAL_ENABLED="false"
if ! skip "temporal" && [[ -n "${TEMPORAL_HOST:-}" ]]; then
  TEMPORAL_HOST_ONLY="${TEMPORAL_HOST%%:*}"
  TEMPORAL_PORT="${TEMPORAL_HOST##*:}"
  if python3 -c "
import socket
try:
    s=socket.create_connection(('$TEMPORAL_HOST_ONLY', int('${TEMPORAL_PORT:-7233}')), 2)
    s.close(); print('ok')
except: pass
" 2>/dev/null | grep -q ok; then
    TEMPORAL_ENABLED="true"
  fi
fi

cat > "$PRODUCT_ROOT/.env" <<EOF
# $PRODUCT_NAME — ProjectZero governed product
# Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
# DO NOT COMMIT

PRODUCT_NAME=$PRODUCT_NAME
PROJECT_MODE=$MODE
PRODUCT_ROOT=$PRODUCT_ROOT

# GitHub
GITHUB_REPO=${GITHUB_REPO_FULL:-$PRODUCT_NAME}
GITHUB_ORG=${GITHUB_ORG:-}
GITHUB_DEFAULT_BRANCH=${GITHUB_DEFAULT_BRANCH:-main}

# JIRA
JIRA_ENABLED=$JIRA_ENABLED
JIRA_PROJECT_KEY=${JIRA_KEY:-}
JIRA_BASE_URL=${JIRA_BASE_URL:-}
JIRA_API_TOKEN=${JIRA_API_TOKEN:-}
JIRA_USER_EMAIL=${JIRA_USER_EMAIL:-}

# Confluence
CONFLUENCE_ENABLED=$CONFLUENCE_ENABLED
CONFLUENCE_SPACE_KEY=${CONFLUENCE_KEY:-}
CONFLUENCE_BASE_URL=${CONFLUENCE_BASE_URL:-}
CONFLUENCE_API_TOKEN=${CONFLUENCE_API_TOKEN:-${JIRA_API_TOKEN:-}}

# AI
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
CLAUDE_MODEL=${CLAUDE_MODEL:-claude-sonnet-4-6}

# Database
DATABASE_URL=${DATABASE_URL:-}

# Temporal
TEMPORAL_ENABLED=$TEMPORAL_ENABLED
TEMPORAL_HOST=${TEMPORAL_HOST:-localhost:7233}
TEMPORAL_TASK_QUEUE=$TEMPORAL_QUEUE
EOF

# Ensure .env is gitignored
if ! grep -q '^\.env$' "$PRODUCT_ROOT/.gitignore" 2>/dev/null; then
  echo ".env" >> "$PRODUCT_ROOT/.gitignore"
fi
ok ".env written to $PRODUCT_ROOT/.env (gitignored)"

# ── Step 9: Brownfield codebase audit ────────────────────────────────────────
if [[ "$MODE" == "brownfield" ]]; then
  step "Step 9: Brownfield codebase audit"

  LANG="unknown"; FRAMEWORK="unknown"; TEST_FW="unknown"; CI="none"

  # Language detection
  [[ -f "$PRODUCT_ROOT/package.json" ]]     && LANG="Node.js/JavaScript"
  [[ -f "$PRODUCT_ROOT/tsconfig.json" ]]    && LANG="TypeScript"
  [[ -f "$PRODUCT_ROOT/requirements.txt" ]] && LANG="Python"
  [[ -f "$PRODUCT_ROOT/Pipfile" ]]          && LANG="Python"
  [[ -f "$PRODUCT_ROOT/go.mod" ]]           && LANG="Go"
  [[ -f "$PRODUCT_ROOT/pom.xml" ]]          && LANG="Java/Maven"
  [[ -f "$PRODUCT_ROOT/build.gradle" ]]     && LANG="Java/Gradle"

  # Framework
  if [[ -f "$PRODUCT_ROOT/package.json" ]]; then
    grep -q '"next"'    "$PRODUCT_ROOT/package.json" 2>/dev/null && FRAMEWORK="Next.js"
    grep -q '"react"'   "$PRODUCT_ROOT/package.json" 2>/dev/null && FRAMEWORK="React"
    grep -q '"vue"'     "$PRODUCT_ROOT/package.json" 2>/dev/null && FRAMEWORK="Vue"
    grep -q '"express"' "$PRODUCT_ROOT/package.json" 2>/dev/null && FRAMEWORK="Express"
    grep -q '"fastify"' "$PRODUCT_ROOT/package.json" 2>/dev/null && FRAMEWORK="Fastify"
  fi
  [[ -f "$PRODUCT_ROOT/manage.py" ]] && FRAMEWORK="Django"
  [[ -f "$PRODUCT_ROOT/app.py" ]]    && FRAMEWORK="Flask/FastAPI"

  # Test framework
  [[ -f "$PRODUCT_ROOT/jest.config.*" ]]    && TEST_FW="Jest"
  [[ -f "$PRODUCT_ROOT/vitest.config.*" ]]  && TEST_FW="Vitest"
  [[ -f "$PRODUCT_ROOT/pytest.ini" ]]       && TEST_FW="pytest"
  [[ -f "$PRODUCT_ROOT/setup.cfg" ]] && grep -q 'pytest' "$PRODUCT_ROOT/setup.cfg" 2>/dev/null && TEST_FW="pytest"

  # CI
  [[ -d "$PRODUCT_ROOT/.github/workflows" ]] && CI="GitHub Actions"
  [[ -f "$PRODUCT_ROOT/Jenkinsfile" ]]        && CI="Jenkins"
  [[ -f "$PRODUCT_ROOT/.gitlab-ci.yml" ]]     && CI="GitLab CI"
  [[ -f "$PRODUCT_ROOT/circle.yml" ]] || [[ -f "$PRODUCT_ROOT/.circleci/config.yml" ]] && CI="CircleCI"

  echo ""
  echo "Codebase Audit"
  echo "══════════════"
  echo "  Language:   $LANG"
  echo "  Framework:  $FRAMEWORK"
  echo "  Tests:      $TEST_FW"
  echo "  CI/CD:      $CI"

  # Write brownfield audit
  cat > "$PRODUCT_ROOT/.claude/memory/brownfield-audit.md" <<EOF
# Brownfield Audit — $PRODUCT_NAME
Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

## Codebase
- Language:   $LANG
- Framework:  $FRAMEWORK
- Tests:      $TEST_FW
- CI/CD:      $CI

## Coverage Gap
Baseline coverage unknown. Factory requires ≥80%. Create ticket to measure and close gap.

## Next Steps
- Run existing test suite to get coverage baseline
- Create ticket: "Raise test coverage to 80%"
- Map existing architecture before /arch
EOF
  ok "Brownfield audit written → .claude/memory/brownfield-audit.md"
fi

# ── Step 10: Commit + push ────────────────────────────────────────────────────
step "Step 10: Commit and push"

cd "$PRODUCT_ROOT"

git add .claude/ CLAUDE.md .gitignore 2>/dev/null || true
git add -u 2>/dev/null || true

if git diff --cached --quiet 2>/dev/null; then
  info "Nothing new to commit (scaffold already present)"
else
  git commit -m "chore: inject ProjectZero factory scaffold

Product:     $PRODUCT_NAME
Mode:        $MODE
JIRA:        ${JIRA_KEY:-disabled}
Confluence:  ${CONFLUENCE_KEY:-disabled}
Factory:     $FACTORY_ROOT"

  if [[ -n "${GITHUB_REPO_FULL:-}" ]]; then
    GH_TOKEN_PUSH=$(resolve_github_token)
    if [[ -n "$GH_TOKEN_PUSH" ]]; then
      REMOTE_URL="https://${GH_TOKEN_PUSH}@github.com/${GITHUB_REPO_FULL}.git"
      git remote set-url origin "$REMOTE_URL" 2>/dev/null || git remote add origin "$REMOTE_URL"
      # Pull remote first (handles auto_init divergence), then push
      git pull origin main --rebase --allow-unrelated-histories -q 2>/dev/null || true
      git push origin main 2>&1 | grep -v "^remote:" || true
      ok "Pushed to github.com/$GITHUB_REPO_FULL"
    else
      warn "No token for push — committed locally only"
    fi
  else
    info "No remote configured — committed locally"
  fi
fi

cd "$FACTORY_ROOT"

# ── Step 11: Report ───────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}Bootstrap Complete${RESET}"
echo "══════════════════════════════════════"
echo -e "  Mode:        ${CYAN}$MODE${RESET}"
echo -e "  PRODUCT_ROOT: $PRODUCT_ROOT"
echo ""
printf "  %-14s %s\n" "GitHub:" "${GITHUB_REPO_FULL:-skipped}"
printf "  %-14s %s\n" "JIRA:" "${JIRA_KEY:-skipped} (${JIRA_ENABLED})"
printf "  %-14s %s\n" "Confluence:" "${CONFLUENCE_KEY:-skipped} (${CONFLUENCE_ENABLED})"
printf "  %-14s %s\n" "Temporal:" "$TEMPORAL_QUEUE (${TEMPORAL_ENABLED})"
printf "  %-14s %s\n" "Commands:" "$CMD_COUNT slash commands"
echo ""
echo -e "  Layout:"
echo -e "    $(dirname "$FACTORY_ROOT")/"
echo -e "    ├── $(basename "$FACTORY_ROOT")/"
echo -e "    └── $PRODUCT_NAME/   ← open this in Claude Code"
echo ""
if [[ -n "$PRD_PATH" ]]; then
  echo -e "  PRD: $PRD_PATH (run /spec to generate stories)"
else
  echo -e "  Next: /vision-to-prd  (no PRD) or /spec (have PRD)"
fi
echo ""

# ── Post-bootstrap: create workspace + open alongside factory ────────────────
# Workspace file named after parent directory — works for any org/folder setup
PARENT_DIR="$(dirname "$FACTORY_ROOT")"
WORKSPACE_NAME="$(basename "$PARENT_DIR" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"
WORKSPACE_FILE="$PARENT_DIR/${WORKSPACE_NAME}.code-workspace"

# ── Create standard project placeholder directories ───────────────────────────
step "Step 11: Create project structure"

PLACEHOLDERS=(
  "src"
  "tests"
  "docs"
  ".github/workflows"
)

for dir in "${PLACEHOLDERS[@]}"; do
  if [[ ! -d "$PRODUCT_ROOT/$dir" ]]; then
    mkdir -p "$PRODUCT_ROOT/$dir"
    # .gitkeep so empty dirs are tracked
    touch "$PRODUCT_ROOT/$dir/.gitkeep"
  fi
done

# Stub docs/PRD.md if no PRD loaded yet
if [[ -z "$PRD_PATH" && ! -f "$PRODUCT_ROOT/docs/PRD.md" ]]; then
cat > "$PRODUCT_ROOT/docs/PRD.md" <<EOF
# $PRODUCT_NAME — Product Requirements Document

> Stub created by /bootstrap-product. Replace with actual PRD or run /vision-to-prd.

## Problem Statement
<!-- What problem does this solve? -->

## Target Users
<!-- Who uses this? -->

## Key Features
<!-- What does it do? -->

## Success Metrics
<!-- How do we know it's working? -->
EOF
fi

ok "Project structure created: src/ tests/ docs/ .github/workflows/"

# ── Create/update multi-root VS Code workspace ────────────────────────────────
python3 - <<PYEOF
import json, os

ws_file = "$WORKSPACE_FILE"
factory = "$FACTORY_ROOT"
product = "$PRODUCT_ROOT"
product_name = os.path.basename(product)
jira_key = "$JIRA_KEY"
jira_enabled = "$JIRA_ENABLED"
confluence_key = "$CONFLUENCE_KEY"
confluence_enabled = "$CONFLUENCE_ENABLED"
jira_base = "${JIRA_BASE_URL:-}"
confluence_base = "${CONFLUENCE_BASE_URL:-}"

# Load existing workspace or start fresh
if os.path.exists(ws_file):
    with open(ws_file) as f:
        ws = json.load(f)
else:
    ws = {"folders": [], "settings": {}}

folders = ws.get("folders", [])
paths_present = [f["path"] for f in folders]

# ── Factory (always first) ────────────────────────────────────────────────────
if factory not in paths_present:
    folders.insert(0, {"name": "⚙ ProjectZeroFactory", "path": factory})

# ── Product root ──────────────────────────────────────────────────────────────
if product not in paths_present:
    folders.append({"name": f"📦 {product_name}", "path": product})

# ── Product subfolders as workspace entries ───────────────────────────────────
sub_folders = [
    ("src",              f"  └ {product_name}/src"),
    ("tests",            f"  └ {product_name}/tests"),
    ("docs",             f"  └ {product_name}/docs"),
    (".github/workflows",f"  └ {product_name}/.github/workflows"),
    (".claude/memory",   f"  └ {product_name}/.claude/memory"),
]

for rel, label in sub_folders:
    full_path = os.path.join(product, rel)
    if os.path.isdir(full_path) and full_path not in paths_present:
        folders.append({"name": label, "path": full_path})

ws["folders"] = folders

# ── Workspace settings ────────────────────────────────────────────────────────
parent_name = os.path.basename(os.path.dirname(factory))
ws["settings"] = {
    "window.title": f"{parent_name} — ${{activeEditorShort}}",
    "editor.formatOnSave": True,
    "explorer.sortOrder": "type",
    "files.exclude": {
        "**/__pycache__": True,
        "**/.pytest_cache": True,
        "**/node_modules": True,
        "**/*.pyc": True,
    }
}

# ── Task shortcuts for the product ───────────────────────────────────────────
tasks = ws.get("tasks", {"version": "2.0.0", "tasks": []})
existing_labels = [t.get("label","") for t in tasks.get("tasks",[])]

new_tasks = [
    {
        "label": f"{product_name}: /spec",
        "type": "shell",
        "command": f"claude --print '/spec' --cwd {product}",
        "group": "build",
        "detail": "Run /spec in Claude Code for this product"
    },
    {
        "label": f"{product_name}: /implement",
        "type": "shell",
        "command": f"claude --print '/implement' --cwd {product}",
        "group": "build",
        "detail": "Run /implement in Claude Code for this product"
    },
    {
        "label": f"{product_name}: /check",
        "type": "shell",
        "command": f"claude --print '/check' --cwd {product}",
        "group": "test",
        "detail": "Run quality gates for this product"
    }
]

for t in new_tasks:
    if t["label"] not in existing_labels:
        tasks["tasks"].append(t)

ws["tasks"] = tasks

with open(ws_file, "w") as f:
    json.dump(ws, f, indent=2)

print(f"Workspace: {ws_file}")
print(f"Folders ({len(folders)}):")
for f in folders:
    print(f"  {f['name']}")
PYEOF

if [[ "$OPEN_AFTER" == "true" ]]; then
  echo ""
  info "Opening both folders alongside each other..."

  # Add product folder to the existing VS Code window (no close/reopen)
  VS_CODE_CLI=""
  [[ -x "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code" ]] \
    && VS_CODE_CLI="/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
  command -v code   &>/dev/null && VS_CODE_CLI="code"
  command -v cursor &>/dev/null && VS_CODE_CLI="cursor"

  if [[ -n "$VS_CODE_CLI" ]]; then
    # --add injects the folder into the active window without closing it
    "$VS_CODE_CLI" --add "$PRODUCT_ROOT"
    ok "Added '$PRODUCT_NAME' to current VS Code workspace (no restart)"
    info "Workspace file updated: $WORKSPACE_FILE"
  elif [[ -d "/Applications/Cursor.app" ]]; then
    open -a "Cursor" --args --add "$PRODUCT_ROOT"
    ok "Added '$PRODUCT_NAME' to current Cursor workspace"
  else
    warn "VS Code CLI not found — install it:"
    echo "  Open VS Code → Cmd+Shift+P → 'Shell Command: Install code in PATH'"
    echo "  Then re-run: code --add $PRODUCT_ROOT"
  fi

  echo ""
  info "To open in Claude Code (separate window per project):"
  echo "    claude $PRODUCT_ROOT"
fi
