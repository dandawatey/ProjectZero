# Checklist: mem-search

## Before searching
- [ ] Always start with Layer 1 (search) — never jump to fetch
- [ ] Show token cost estimate before fetching more

## After Layer 1
- [ ] Results presented as numbered list with ID | timestamp | snippet | score
- [ ] If worker down: show start command (`npx claude-mem start`)

## After Layer 2
- [ ] Timeline shows window context (N before, target, N after)
- [ ] Center observation clearly marked

## After Layer 3
- [ ] Only fetched IDs explicitly requested by user
- [ ] Did NOT fetch all memories at once
- [ ] Citations use format [obs:id]

## Quality
- [ ] Error messages are actionable (include start command + port hint)
- [ ] Private observations excluded (worker handles this automatically)
