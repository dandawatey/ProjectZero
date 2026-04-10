# Environments

| Environment | Purpose | URL Pattern | Deploy Trigger |
|-------------|---------|-------------|---------------|
| Local | Development | localhost:3000 | Manual |
| Dev | Integration testing | dev.product.internal | Push to develop |
| Staging | Pre-production validation | staging.product.com | Push to release/* |
| Production | Live users | product.com | Manual (approved) |

## Configuration
- All config via environment variables
- Per-environment .env files (never committed)
- Same code artifact deployed to all environments
- Environment-specific config: URLs, credentials, feature flags

## Promotion Rules
- Local → Dev: automatic on push to develop
- Dev → Staging: automatic on release branch creation
- Staging → Production: manual, requires approval
- Hotfix: staging → production (expedited, still requires approval)
