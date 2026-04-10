# Skill: Git Worktrees

## Purpose
Parallel development using git worktrees for isolated work.

## Methodology
1. Create worktree: git worktree add ../feature-branch feature-branch. 2. Work in isolation: Changes in worktree don't affect main tree. 3. Test independently: Run tests in worktree. 4. Merge back: Merge feature branch to develop. 5. Clean up: git worktree remove ../feature-branch.

## Stage Mapping
Used during: Realization, Completion (unless otherwise noted)

## Integration
Available to all agents. Invoke when trigger conditions are met.
