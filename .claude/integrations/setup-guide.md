# Integration Setup Guide

## JIRA
1. Create a JIRA project (Scrum or Kanban board)
2. Note the project key (e.g., HEALTH)
3. Generate API token: https://id.atlassian.com/manage-profile/security/api-tokens
4. Set in .env: JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USER_EMAIL, JIRA_PROJECT_KEY
5. Update .claude/integrations/config.json: set jira.enabled = true, jira.projectKey
6. Run /factory-init to validate

## Confluence
1. Create a Confluence space for the project
2. Note the space key
3. Use same API token as JIRA (same Atlassian account)
4. Set in .env: CONFLUENCE_BASE_URL, CONFLUENCE_API_TOKEN, CONFLUENCE_SPACE_KEY
5. Update config.json: set confluence.enabled = true, confluence.spaceKey
6. Run /factory-init to validate

## GitHub
1. Create a repository for the product
2. Generate personal access token (fine-grained, repo scope)
3. Set in .env: GITHUB_TOKEN, GITHUB_ORG
4. Update config.json: set github.owner, github.repo
5. Run /factory-init to validate

## Slack (Optional)
1. Create incoming webhook for a channel
2. Set in .env: SLACK_WEBHOOK
3. Update config.json: set slack.enabled = true
4. Factory will send status notifications to Slack

## Local-First Mode
If no integrations configured, factory operates fully locally:
- Tickets in .claude/delivery/jira/issues/
- Docs in .claude/delivery/confluence/pages/
- Git operations are always local-first
