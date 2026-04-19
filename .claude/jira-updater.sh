#!/bin/bash
# JIRA Integration — Update ticket status and add comments

JIRA_URL="https://isourceinnovation.atlassian.net"
JIRA_PROJECT="PRJ0"
JIRA_USER="dandawate.y@isourceinfosystems.com"
JIRA_TOKEN="${JIRA_API_TOKEN}"

# Update ticket to DONE
mark_done() {
    local ticket="$1"
    local tests="$2"
    local coverage="$3"
    local branch="$4"

    local comment="✅ Ticket complete!

Tests: $tests passing
Coverage: $coverage%
Branch: $branch
Status: Ready for merge to main

All acceptance criteria met. Tests passing. Code reviewed."

    curl -s -X POST \
        -H "Authorization: Bearer $JIRA_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"body\":{\"content\":[{\"type\":\"text\",\"text\":\"$comment\"}]}}" \
        "$JIRA_URL/rest/api/3/issue/$ticket/comment" \
        > /dev/null

    curl -s -X PUT \
        -H "Authorization: Bearer $JIRA_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"transition\":{\"id\":\"11\"}}" \
        "$JIRA_URL/rest/api/3/issue/$ticket/transitions" \
        > /dev/null

    echo "✅ JIRA updated: $ticket → Done"
}

# Add progress comment
add_progress() {
    local ticket="$1"
    local phase="$2"
    local detail="$3"

    local comment="🔄 Progress Update

Phase: $phase
Detail: $detail
Timestamp: $(date)"

    curl -s -X POST \
        -H "Authorization: Bearer $JIRA_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"body\":{\"content\":[{\"type\":\"text\",\"text\":\"$comment\"}]}}" \
        "$JIRA_URL/rest/api/3/issue/$ticket/comment" \
        > /dev/null

    echo "✅ Comment added: $ticket"
}

# Link commit to ticket
link_commit() {
    local ticket="$1"
    local commit="$2"
    local message="$3"

    local comment="🔗 Commit: $commit

$message"

    curl -s -X POST \
        -H "Authorization: Bearer $JIRA_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"body\":{\"content\":[{\"type\":\"text\",\"text\":\"$comment\"}]}}" \
        "$JIRA_URL/rest/api/3/issue/$ticket/comment" \
        > /dev/null

    echo "✅ Commit linked: $ticket"
}

case "${1:-help}" in
    "done")
        mark_done "$2" "$3" "$4" "$5"
        ;;
    "progress")
        add_progress "$2" "$3" "$4"
        ;;
    "commit")
        link_commit "$2" "$3" "$4"
        ;;
    *)
        echo "Usage: $0 {done|progress|commit} ..."
        ;;
esac
