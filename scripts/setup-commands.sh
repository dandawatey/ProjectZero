#!/usr/bin/env bash
# setup-commands.sh — Register ProjectZero factory slash commands with Claude Code
#
# Usage:
#   ./scripts/setup-commands.sh              # project-level only (default)
#   ./scripts/setup-commands.sh --global     # also symlink to ~/.claude/commands/
#   ./scripts/setup-commands.sh --list       # list available commands, no changes
#   ./scripts/setup-commands.sh --uninstall  # remove global symlinks

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
FACTORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_COMMANDS_DIR="$FACTORY_ROOT/.claude/commands"
GLOBAL_COMMANDS_DIR="$HOME/.claude/commands"
MODE="${1:-}"

# ── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

ok()   { echo -e "${GREEN}✓${RESET} $*"; }
warn() { echo -e "${YELLOW}⚠${RESET} $*"; }
err()  { echo -e "${RED}✗${RESET} $*"; }
info() { echo -e "${CYAN}→${RESET} $*"; }

# ── Command groups ────────────────────────────────────────────────────────────
declare -A CMD_GROUPS=(
  ["Factory Setup"]="factory-init bootstrap-product factory-audit factory-upgrade"
  ["Planning"]="vision-to-prd spec arch business-docs sprint sprint-plan sprint-goal"
  ["Implementation"]="implement check ticket ticket-create story-create story-validate"
  ["Components"]="component-create component-review design-system-init"
  ["Release"]="review approve release publish-cxo publish-iso publish-hierarchy"
  ["Operations"]="monitor status resume pipeline-create setup"
  ["Recovery"]="recover-ticket recover-workflow"
  ["Reporting"]="agent-map console optimize ui-audit"
)

# ── List mode ─────────────────────────────────────────────────────────────────
list_commands() {
  echo ""
  echo -e "${BOLD}ProjectZero Factory — Slash Commands${RESET}"
  echo "══════════════════════════════════════"

  local total=0
  local missing=0

  for group in "Factory Setup" "Planning" "Implementation" "Components" "Release" "Operations" "Recovery" "Reporting"; do
    echo ""
    echo -e "${CYAN}${group}${RESET}"
    for cmd in ${CMD_GROUPS[$group]}; do
      local file="$PROJECT_COMMANDS_DIR/${cmd}.md"
      if [[ -f "$file" ]]; then
        # Extract purpose line
        local purpose
        purpose=$(grep -m1 "^## Purpose" -A1 "$file" 2>/dev/null | tail -1 | sed 's/^[[:space:]]*//' || echo "")
        printf "  ${GREEN}%-30s${RESET} %s\n" "/${cmd}" "$purpose"
        ((total++))
      else
        printf "  ${RED}%-30s${RESET} %s\n" "/${cmd}" "[MISSING]"
        ((missing++))
      fi
    done
  done

  echo ""
  echo "──────────────────────────────────────"
  echo -e "Total: ${BOLD}${total}${RESET} commands"
  if [[ $missing -gt 0 ]]; then
    warn "$missing command file(s) missing from $PROJECT_COMMANDS_DIR"
  fi

  echo ""
  echo -e "${BOLD}Scope:${RESET}"
  info "Project-level: available when Claude Code opens this directory"
  if [[ -d "$GLOBAL_COMMANDS_DIR" ]]; then
    local global_count
    global_count=$(find "$GLOBAL_COMMANDS_DIR" -name "*.md" -maxdepth 1 2>/dev/null | wc -l | tr -d ' ')
    info "Global install: $global_count command(s) in $GLOBAL_COMMANDS_DIR"
  else
    info "Global install: not configured (run with --global to install)"
  fi
  echo ""
}

# ── Validate project commands dir ─────────────────────────────────────────────
validate_project_commands() {
  echo ""
  echo -e "${BOLD}Validating project commands...${RESET}"

  if [[ ! -d "$PROJECT_COMMANDS_DIR" ]]; then
    err "Commands dir not found: $PROJECT_COMMANDS_DIR"
    echo "  Run from factory root or check directory structure."
    exit 1
  fi

  local found
  found=$(find "$PROJECT_COMMANDS_DIR" -name "*.md" -maxdepth 1 | wc -l | tr -d ' ')
  ok "$found command file(s) found in .claude/commands/"
}

# ── Install globally ──────────────────────────────────────────────────────────
install_global() {
  echo ""
  echo -e "${BOLD}Installing commands globally (~/.claude/commands/)...${RESET}"

  mkdir -p "$GLOBAL_COMMANDS_DIR"

  local installed=0
  local skipped=0

  for cmd_file in "$PROJECT_COMMANDS_DIR"/*.md; do
    local name
    name="$(basename "$cmd_file")"
    local target="$GLOBAL_COMMANDS_DIR/pzf-${name}"   # prefix to avoid collisions

    if [[ -L "$target" ]]; then
      # Already a symlink — update
      ln -sf "$cmd_file" "$target"
      ((skipped++))
    else
      ln -sf "$cmd_file" "$target"
      ok "  Linked /pzf-$(basename "$cmd_file" .md)"
      ((installed++))
    fi
  done

  if [[ $skipped -gt 0 ]]; then
    info "  $skipped existing symlink(s) refreshed"
  fi

  echo ""
  ok "Global install complete: $((installed + skipped)) command(s) in $GLOBAL_COMMANDS_DIR"
  info "Commands available as /pzf-<name> in any Claude Code project"
  warn "Prefix 'pzf-' used to avoid collisions with other project commands"
}

# ── Uninstall global symlinks ─────────────────────────────────────────────────
uninstall_global() {
  echo ""
  echo -e "${BOLD}Removing global symlinks from ~/.claude/commands/...${RESET}"

  if [[ ! -d "$GLOBAL_COMMANDS_DIR" ]]; then
    warn "Global commands dir does not exist: $GLOBAL_COMMANDS_DIR"
    return
  fi

  local removed=0
  for link in "$GLOBAL_COMMANDS_DIR"/pzf-*.md; do
    [[ -L "$link" ]] || continue
    rm "$link"
    ok "  Removed $(basename "$link")"
    ((removed++))
  done

  if [[ $removed -eq 0 ]]; then
    info "No pzf-* symlinks found to remove"
  else
    ok "$removed symlink(s) removed"
  fi
  echo ""
}

# ── Project-level registration check ──────────────────────────────────────────
check_project_registration() {
  echo ""
  echo -e "${BOLD}Project-level registration${RESET}"
  info "Commands in .claude/commands/ are auto-loaded by Claude Code"
  info "Open this directory in Claude Code → type / to see all commands"
  echo ""

  # Check if settings.json acknowledges commands
  local settings="$FACTORY_ROOT/.claude/settings.json"
  if [[ -f "$settings" ]]; then
    ok "settings.json present"
  else
    warn "settings.json missing — Claude Code may not load hooks correctly"
  fi
}

# ── Print summary ─────────────────────────────────────────────────────────────
print_summary() {
  echo ""
  echo -e "${BOLD}Setup Complete${RESET}"
  echo "══════════════"
  echo ""
  echo -e "Open this project in ${BOLD}Claude Code${RESET}, then type ${BOLD}/${RESET} to access:"
  echo ""
  echo "  /factory-init        ← start here (first run)"
  echo "  /bootstrap-product   ← create or connect product"
  echo "  /spec                ← write stories from PRD"
  echo "  /arch                ← design architecture"
  echo "  /implement           ← build features (TDD)"
  echo "  /check               ← run quality gates"
  echo "  /review              ← create PR"
  echo "  /approve             ← governance gate"
  echo "  /release             ← tag and ship"
  echo ""
  echo -e "  Run ${CYAN}./scripts/setup-commands.sh --list${RESET} for full command reference"
  echo ""
}

# ── Main ──────────────────────────────────────────────────────────────────────
main() {
  echo ""
  echo -e "${BOLD}ProjectZero Factory — Command Setup${RESET}"
  echo "════════════════════════════════════"

  case "$MODE" in
    --list)
      validate_project_commands
      list_commands
      ;;
    --global)
      validate_project_commands
      install_global
      check_project_registration
      list_commands
      print_summary
      ;;
    --uninstall)
      uninstall_global
      ;;
    "")
      validate_project_commands
      check_project_registration
      list_commands
      print_summary
      ;;
    *)
      err "Unknown flag: $MODE"
      echo "Usage: $0 [--list|--global|--uninstall]"
      exit 1
      ;;
  esac
}

main
