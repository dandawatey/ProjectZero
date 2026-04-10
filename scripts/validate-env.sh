#!/usr/bin/env bash
# =============================================================================
# validate-env.sh
# Validates that the .env file contains all required keys with non-empty values.
#
# Usage:
#   bash scripts/validate-env.sh                  # Validate factory .env
#   bash scripts/validate-env.sh /path/to/.env    # Validate specific .env file
#   bash scripts/validate-env.sh --strict          # Fail on optional keys too
#
# Exit codes:
#   0 - All required keys present and non-empty
#   1 - One or more required keys missing or empty
#   2 - .env file not found
# =============================================================================

set -euo pipefail

# --- Color Output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# --- Determine paths ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FACTORY_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# --- Parse arguments ---
ENV_FILE=""
STRICT_MODE=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --strict)
      STRICT_MODE=true
      shift
      ;;
    --help|-h)
      echo "Usage: bash scripts/validate-env.sh [OPTIONS] [ENV_FILE_PATH]"
      echo ""
      echo "Options:"
      echo "  --strict    Also validate optional keys (JIRA, Confluence, etc.)"
      echo "  --help      Show this help message"
      echo ""
      echo "If no ENV_FILE_PATH is provided, validates \$FACTORY_ROOT/.env"
      exit 0
      ;;
    *)
      ENV_FILE="$1"
      shift
      ;;
  esac
done

if [[ -z "$ENV_FILE" ]]; then
  ENV_FILE="$FACTORY_ROOT/.env"
fi

# =============================================================================
# Required Keys -- these must be present and non-empty for the factory to work
# =============================================================================
REQUIRED_KEYS=(
  "ANTHROPIC_API_KEY"
  "GITHUB_TOKEN"
  "GITHUB_ORG"
  "GITHUB_DEFAULT_BRANCH"
  "CLAUDE_MODEL"
)

# =============================================================================
# Optional Keys -- validated only in strict mode
# =============================================================================
OPTIONAL_KEYS=(
  "JIRA_BASE_URL"
  "JIRA_API_TOKEN"
  "JIRA_USER_EMAIL"
  "JIRA_PROJECT_KEY"
  "CONFLUENCE_BASE_URL"
  "CONFLUENCE_API_TOKEN"
  "CONFLUENCE_SPACE_KEY"
  "OPENAI_API_KEY"
  "REDIS_URL"
  "DATABASE_URL"
  "DAGSTER_HOME"
  "SENTRY_DSN"
  "DATADOG_API_KEY"
)

# =============================================================================
# Integration Groups -- validated together (if one is set, all must be set)
# =============================================================================
declare -A INTEGRATION_GROUPS
INTEGRATION_GROUPS=(
  ["JIRA"]="JIRA_BASE_URL JIRA_API_TOKEN JIRA_USER_EMAIL JIRA_PROJECT_KEY"
  ["CONFLUENCE"]="CONFLUENCE_BASE_URL CONFLUENCE_API_TOKEN CONFLUENCE_SPACE_KEY"
  ["REDIS"]="REDIS_URL"
  ["DATABASE"]="DATABASE_URL"
  ["DAGSTER"]="DAGSTER_HOME DAGSTER_HOST DAGSTER_PORT"
)

# =============================================================================
# Validation Functions
# =============================================================================

check_file_exists() {
  if [[ ! -f "$ENV_FILE" ]]; then
    echo -e "${RED}[ERROR]${NC} .env file not found at: $ENV_FILE"
    echo ""
    if [[ -f "$FACTORY_ROOT/.env.example" ]]; then
      echo -e "Create one from the example:"
      echo -e "  ${BLUE}cp $FACTORY_ROOT/.env.example $ENV_FILE${NC}"
    else
      echo -e "No .env.example found either. The factory repository may be incomplete."
    fi
    exit 2
  fi
}

get_env_value() {
  local key="$1"
  local value
  # Read value, handling keys that may appear multiple times (take last occurrence)
  value=$(grep "^${key}=" "$ENV_FILE" 2>/dev/null | tail -1 | cut -d'=' -f2-)
  # Trim whitespace
  value=$(echo "$value" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
  # Remove surrounding quotes if present
  value=$(echo "$value" | sed "s/^['\"]//;s/['\"]$//")
  echo "$value"
}

validate_keys() {
  local -n keys=$1
  local label="$2"
  local is_required="$3"
  local missing=()
  local present=()

  for key in "${keys[@]}"; do
    local value
    value=$(get_env_value "$key")
    if [[ -z "$value" ]]; then
      missing+=("$key")
    else
      present+=("$key")
    fi
  done

  if [[ ${#present[@]} -gt 0 ]]; then
    for key in "${present[@]}"; do
      echo -e "  ${GREEN}[OK]${NC}   $key"
    done
  fi

  if [[ ${#missing[@]} -gt 0 ]]; then
    for key in "${missing[@]}"; do
      if [[ "$is_required" == "true" ]]; then
        echo -e "  ${RED}[MISSING]${NC} $key"
      else
        echo -e "  ${YELLOW}[EMPTY]${NC}  $key"
      fi
    done
  fi

  # Return count of missing keys
  echo "${#missing[@]}" > /tmp/validate_env_missing_count
}

validate_integration_groups() {
  local warnings=0

  for group_name in "${!INTEGRATION_GROUPS[@]}"; do
    local keys_str="${INTEGRATION_GROUPS[$group_name]}"
    local -a keys=($keys_str)
    local has_any=false
    local missing_in_group=()

    for key in "${keys[@]}"; do
      local value
      value=$(get_env_value "$key")
      if [[ -n "$value" ]]; then
        has_any=true
      else
        missing_in_group+=("$key")
      fi
    done

    if [[ "$has_any" == "true" && ${#missing_in_group[@]} -gt 0 ]]; then
      echo -e "\n  ${YELLOW}[WARN]${NC} $group_name integration is partially configured."
      echo -e "  The following keys are set, but these are missing:"
      for key in "${missing_in_group[@]}"; do
        echo -e "    ${YELLOW}- $key${NC}"
      done
      warnings=$((warnings + 1))
    fi
  done

  return $warnings
}

# =============================================================================
# Main Validation
# =============================================================================

echo -e "\n${BOLD}ProjectZeroFactory -- Environment Validation${NC}"
echo -e "File: $ENV_FILE"
echo -e "Mode: $(if $STRICT_MODE; then echo 'Strict'; else echo 'Standard'; fi)"
echo ""

check_file_exists

# --- Check for secrets safety ---
echo -e "${BOLD}Security Check:${NC}"
# Verify .env is in .gitignore
if [[ -f "$FACTORY_ROOT/.gitignore" ]]; then
  if grep -q "^\.env$" "$FACTORY_ROOT/.gitignore" 2>/dev/null; then
    echo -e "  ${GREEN}[OK]${NC}   .env is in .gitignore"
  else
    echo -e "  ${RED}[WARN]${NC} .env is NOT in .gitignore -- secrets may be committed!"
  fi
else
  echo -e "  ${YELLOW}[WARN]${NC} No .gitignore found"
fi
echo ""

# --- Validate required keys ---
echo -e "${BOLD}Required Keys:${NC}"
REQUIRED_MISSING=0
for key in "${REQUIRED_KEYS[@]}"; do
  value=$(get_env_value "$key")
  if [[ -z "$value" ]]; then
    echo -e "  ${RED}[MISSING]${NC} $key"
    REQUIRED_MISSING=$((REQUIRED_MISSING + 1))
  else
    # Mask the value for display
    masked="${value:0:4}****"
    echo -e "  ${GREEN}[OK]${NC}   $key = $masked"
  fi
done
echo ""

# --- Validate optional keys (strict mode) ---
if $STRICT_MODE; then
  echo -e "${BOLD}Optional Keys (strict mode):${NC}"
  OPTIONAL_MISSING=0
  for key in "${OPTIONAL_KEYS[@]}"; do
    value=$(get_env_value "$key")
    if [[ -z "$value" ]]; then
      echo -e "  ${YELLOW}[EMPTY]${NC}  $key"
      OPTIONAL_MISSING=$((OPTIONAL_MISSING + 1))
    else
      masked="${value:0:4}****"
      echo -e "  ${GREEN}[OK]${NC}   $key = $masked"
    fi
  done
  echo ""
fi

# --- Validate integration groups ---
echo -e "${BOLD}Integration Groups:${NC}"
validate_integration_groups
INTEGRATION_WARNINGS=$?
echo ""

# --- Feature flags check ---
echo -e "${BOLD}Feature Flags:${NC}"
for flag in ENABLE_LOCAL_FALLBACK ENABLE_MEMORY_PERSISTENCE ENABLE_PIPELINE_MODE; do
  value=$(get_env_value "$flag")
  if [[ -n "$value" ]]; then
    echo -e "  ${BLUE}[SET]${NC}  $flag = $value"
  else
    echo -e "  ${YELLOW}[DEFAULT]${NC} $flag (not set, will use defaults)"
  fi
done
echo ""

# --- Summary ---
echo -e "${BOLD}Summary:${NC}"
if [[ $REQUIRED_MISSING -eq 0 ]]; then
  echo -e "  ${GREEN}All required keys are present.${NC}"
else
  echo -e "  ${RED}$REQUIRED_MISSING required key(s) missing.${NC}"
  echo -e "  The factory will not operate correctly until these are set."
fi

if [[ $INTEGRATION_WARNINGS -gt 0 ]]; then
  echo -e "  ${YELLOW}$INTEGRATION_WARNINGS integration group(s) partially configured.${NC}"
fi

echo ""

# --- Exit code ---
if [[ $REQUIRED_MISSING -gt 0 ]]; then
  echo -e "${RED}Validation FAILED.${NC} Set the missing required keys in $ENV_FILE"
  exit 1
else
  echo -e "${GREEN}Validation PASSED.${NC}"
  exit 0
fi
