#!/bin/bash
# Confluence Integration — Post build progress and documentation

CONF_URL="https://isourceinnovation.atlassian.net/wiki"
CONF_SPACE="PR"
CONF_USER="dandawate.y@isourceinfosystems.com"
CONF_TOKEN="${CONFLUENCE_API_TOKEN}"

# Create/update build status page
post_build_status() {
    local title="$1"
    local content="$2"
    local parent_page_id="3571713"

    curl -s -X POST \
        -H "Authorization: Bearer $CONF_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"type\":\"page\",
            \"title\":\"$title\",
            \"spaceId\":\"$CONF_SPACE\",
            \"parentId\":\"$parent_page_id\",
            \"body\":{\"storage\":{\"value\":\"$content\",\"representation\":\"storage\"}}
        }" \
        "$CONF_URL/api/v2/pages" \
        > /dev/null

    echo "✅ Confluence updated: $title"
}

# Post ticket completion to Confluence
ticket_completed_doc() {
    local ticket="$1"
    local name="$2"
    local tests="$3"
    local coverage="$4"
    local timestamp=$(date)

    content="<h2>$ticket: $name</h2>
<p><strong>Completed:</strong> $timestamp</p>
<ul>
<li>Tests: $tests passing</li>
<li>Coverage: $coverage%</li>
<li>Status: Ready for merge</li>
</ul>"

    post_build_status "$ticket - $name" "$content"
}

case "${1:-help}" in
    "status")
        post_build_status "$2" "$3"
        ;;
    "ticket-done")
        ticket_completed_doc "$2" "$3" "$4" "$5"
        ;;
    *)
        echo "Usage: $0 {status|ticket-done} ..."
        ;;
esac
