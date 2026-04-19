# JIRA ↔ GitHub Integration Setup
**Status**: Ready to configure  
**Sync Type**: Bidirectional (commits ↔ tickets, PRs ↔ status)

---

## Step 1: Get JIRA API Token

1. Log in to JIRA: https://jira.yourcompany.com
2. Go to **Settings** → **Personal Settings** → **Security** → **Create API Token**
3. Name: `ProjectZero-GithubSync`
4. Copy token (you'll only see it once)

---

## Step 2: Get GitHub Personal Access Token

1. Go to GitHub: https://github.com/settings/tokens
2. Click **Generate new token (classic)**
3. Scopes needed:
   - `repo` (full control of private repositories)
   - `workflow` (GitHub Actions)
4. Name: `ProjectZero-JIRA-Sync`
5. Copy token

---

## Step 3: Configure Environment Variables

Add to your shell profile (`~/.zshrc`, `~/.bashrc`):

```bash
# JIRA Integration
export JIRA_HOST="jira.yourcompany.com"
export JIRA_PROJECT="PRJ0"
export JIRA_API_TOKEN="your_jira_token_here"

# GitHub Integration
export GITHUB_REPO="yourorgname/ProjectZeroFactory"
export GITHUB_TOKEN="your_github_token_here"
```

Then reload:
```bash
source ~/.zshrc  # or ~/.bashrc
```

---

## Step 4: Test Sync Script

Make script executable:
```bash
chmod +x .claude/jira-sync.sh
```

Test with existing ticket (SaaS-AUTH-2):
```bash
.claude/jira-sync.sh PRJ0-121 sync
```

Expected output:
```
✓ Syncing PRJ0-121 with git history...
✓ Found commits:
34b6529 feat(SaaS-AUTH-2): JWT auth endpoints
✓ Linking commit 34b6529: feat(SaaS-AUTH-2): JWT auth endpoints → PRJ0-121
✓ Commit 34b6529 linked to JIRA
✓ Checking PR status for PRJ0-121...
✓ Setting JIRA status to: Done
✓ JIRA ticket PRJ0-121 synced
```

---

## Step 5: Configure GitHub Actions

Create `.github/workflows/jira-sync.yml`:

```yaml
name: JIRA Sync

on:
  push:
    branches:
      - main
      - feature/**
  pull_request:
    types: [opened, closed, synchronize]

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Parse commit for JIRA ticket
        id: ticket
        run: |
          TICKET=$(git log -1 --pretty=%B | grep -o 'PRJ0-[0-9]*' | head -1 || echo "")
          echo "ticket=$TICKET" >> $GITHUB_OUTPUT

      - name: Sync to JIRA
        if: steps.ticket.outputs.ticket != ''
        env:
          JIRA_HOST: ${{ secrets.JIRA_HOST }}
          JIRA_API_TOKEN: ${{ secrets.JIRA_API_TOKEN }}
          GITHUB_REPO: ${{ github.repository }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          bash .claude/jira-sync.sh ${{ steps.ticket.outputs.ticket }} sync

      - name: Update PR with JIRA link
        if: github.event_name == 'pull_request' && steps.ticket.outputs.ticket != ''
        run: |
          echo "🔗 Linked to JIRA: [${{ steps.ticket.outputs.ticket }}](https://jira.yourcompany.com/browse/${{ steps.ticket.outputs.ticket }})" >> $GITHUB_STEP_SUMMARY
```

---

## Step 6: Add Secrets to GitHub

1. Go to your repo: **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:
   - `JIRA_HOST`: `jira.yourcompany.com`
   - `JIRA_API_TOKEN`: (from Step 1)
   - `GITHUB_TOKEN`: Already available (GitHub Secrets)

---

## Manual Sync Commands

Once configured, you can manually sync tickets:

```bash
# Sync all commits for a ticket
.claude/jira-sync.sh PRJ0-124 sync

# Check ticket status
.claude/jira-sync.sh PRJ0-124 status

# Link specific commit
.claude/jira-sync.sh PRJ0-124 link abc1234

# Close ticket when done
.claude/jira-sync.sh PRJ0-124 close
```

---

## Current Ticket Sync Status

| Ticket | Status | Last Sync | Commits |
|--------|--------|-----------|---------|
| PRJ0-120 (ORG-1) | Done | 21:47 | 66488bd |
| PRJ0-121 (AUTH-2) | Done | 21:47 | 34b6529 |
| PRJ0-122 (BILL-2) | Done | 21:47 | d6f225e |
| PRJ0-123 (FE-1) | Done | 21:47 | TBD |
| PRJ0-124 (ORG-2) | In Progress | 21:45 | TBD |
| PRJ0-125 (DASH-1) | In Progress | 21:45 | TBD |

---

## Troubleshooting

**Error: "401 Unauthorized"**
- Check JIRA_API_TOKEN is correct
- Verify JIRA_HOST is correct (no https:// prefix)

**Error: "Cannot find PR"**
- Commit message must include `PRJ0-XXX`
- PR must mention ticket in title or description

**Commits not linking**
- Run: `.claude/jira-sync.sh PRJ0-XXX sync`
- Check GITHUB_TOKEN has `repo` scope

**JIRA status not updating**
- Verify JIRA workflow allows status transitions
- Manual update: log in to JIRA and change status directly

---

## Bi-Directional Sync (Optional)

For full bi-directional sync (JIRA → GitHub):

```bash
# When JIRA ticket status changes to "In Code Review":
# → Auto-create PR with JIRA ticket link

# When PR is merged:
# → Auto-update JIRA ticket to "Done"
```

This requires additional GitHub Actions and JIRA webhooks. See `JIRA_WEBHOOKS_SETUP.md`.

---

## Next Steps

1. ✅ Configure environment variables (Step 3)
2. ✅ Test sync script (Step 4)
3. ✅ Set up GitHub Actions (Step 5)
4. ✅ Add GitHub Secrets (Step 6)
5. Run sync for all Sprint 1 tickets:
   ```bash
   for ticket in PRJ0-120 PRJ0-121 PRJ0-122 PRJ0-123 PRJ0-124 PRJ0-125; do
     .claude/jira-sync.sh $ticket sync
   done
   ```
6. Verify JIRA tickets updated in browser

---

**Status**: Ready to implement  
**Estimated Setup Time**: 15 minutes  
**Impact**: Full audit trail (commits ↔ tickets ↔ PRs)
