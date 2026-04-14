# /publish-hierarchy

Publish the JIRA Feature/Epic/Story hierarchy to a Confluence page.

## Usage
/publish-hierarchy

## Steps
1. BASE_URL=${PROJECTZERO_BASE_URL:-http://localhost:8000}
2. TOKEN=$(cat ~/.projectzero_token 2>/dev/null || echo $PROJECTZERO_TOKEN)
3. curl -s -X POST "$BASE_URL/api/v1/confluence/publish-jira-hierarchy" \
     -H "Authorization: Bearer $TOKEN"
4. Display the returned Confluence page URL
