#!/usr/bin/env bash
# Google Stitch skill setup
# Symlinks skill into .claude/skills/ for Claude Code pickup

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$SCRIPT_DIR/../../../.claude/skills/google-stitch"

if [ -L "$TARGET_DIR" ]; then
  echo "Symlink already exists: $TARGET_DIR"
else
  ln -s "$SCRIPT_DIR" "$TARGET_DIR"
  echo "Linked: $TARGET_DIR → $SCRIPT_DIR"
fi
echo "google-stitch skill ready."
