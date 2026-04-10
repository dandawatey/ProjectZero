# Usage: Git Worktrees

## How to Invoke
Activate this skill when its trigger conditions are met (see triggers.md).

## Process
1. Create worktree: git worktree add ../feature-branch feature-branch. 2. Work in isolation: Changes in worktree don't affect main tree. 3. Test independently: Run tests in worktree. 4. Merge back: Merge feature branch to develop. 5. Clean up: git worktree remove ../feature-branch.

## Expected Output
Completed work following the methodology above, with quality validated against checklist.md.
