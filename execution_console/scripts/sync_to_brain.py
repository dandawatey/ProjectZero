#!/usr/bin/env python3
"""
CLI: manually trigger claude-mem → Brain sync — PRJ0-75.

Usage:
    python execution_console/scripts/sync_to_brain.py
    python execution_console/scripts/sync_to_brain.py --dry-run
    python execution_console/scripts/sync_to_brain.py --threshold 0.5
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from execution_console.app.integrations.claude.mem_bridge import MemBridge
from execution_console.app.core.config import cfg


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync claude-mem memories to ProjectZero Brain")
    parser.add_argument("--dry-run", action="store_true", help="Show what would sync without writing")
    parser.add_argument("--threshold", type=float, default=cfg.CLAUDE_MEM_BRAIN_THRESHOLD,
                        help=f"Min score for promotion (default: {cfg.CLAUDE_MEM_BRAIN_THRESHOLD})")
    parser.add_argument("--mem-port", type=int, default=cfg.CLAUDE_MEM_PORT,
                        help=f"claude-mem worker port (default: {cfg.CLAUDE_MEM_PORT})")
    parser.add_argument("--brain-url", default=cfg.PROJECTZERO_BASE_URL,
                        help=f"Brain API base URL (default: {cfg.PROJECTZERO_BASE_URL})")
    args = parser.parse_args()

    bridge = MemBridge(
        mem_port=args.mem_port,
        brain_url=args.brain_url,
        brain_token=cfg.PROJECTZERO_TOKEN,
        threshold=args.threshold,
    )

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Syncing claude-mem → Brain")
    print(f"  Threshold : {args.threshold}")
    print(f"  mem port  : {args.mem_port}")
    print(f"  Brain URL : {args.brain_url}")
    print()

    result = bridge.sync(dry_run=args.dry_run)

    print(f"Results:")
    print(f"  Synced  : {result['synced']}")
    print(f"  Skipped : {result['skipped']} (already synced or below threshold)")
    print(f"  Errors  : {result['errors']}")
    if args.dry_run:
        print("\n[DRY RUN] No changes written.")


if __name__ == "__main__":
    main()
