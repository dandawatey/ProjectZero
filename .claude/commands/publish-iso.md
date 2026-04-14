# /publish-iso

Publish the ISO Audit Documentation Hub to Confluence (master page + 12 sub-pages).

## Usage
/publish-iso

## Steps
1. BASE_URL=${PROJECTZERO_BASE_URL:-http://localhost:8000}
2. TOKEN=$(cat ~/.projectzero_token 2>/dev/null || echo $PROJECTZERO_TOKEN)
3. curl -s -X POST "$BASE_URL/api/v1/confluence/publish-iso" \
     -H "Authorization: Bearer $TOKEN"
4. Display: master page URL + list of 12 sub-page URLs created
