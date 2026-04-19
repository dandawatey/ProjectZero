#!/bin/bash
# Voice Agent for ProjectZero Build Updates
# Uses macOS native text-to-speech (say command)

# Configuration
VOICE="Soumya"  # Indian female voice - natural, warm, conversational
RATE=160  # Words per minute (natural conversation pace)
PITCH=50  # Pitch adjustment

# Function to speak update
speak_update() {
    local message="$1"
    say -v "$VOICE" -r "$RATE" "$message"
}

# Function to log and speak
log_and_speak() {
    local level="$1"  # INFO, PROGRESS, COMPLETE, ERROR, WARNING
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Log to file
    echo "[$timestamp] [$level] $message" >> .claude/voice-agent.log

    # Speak to user
    case $level in
        "COMPLETE")
            speak_update "Complete. $message"
            ;;
        "ERROR")
            speak_update "Error. $message"
            ;;
        "WARNING")
            speak_update "Warning. $message"
            ;;
        "PROGRESS")
            speak_update "$message"
            ;;
        *)
            speak_update "$message"
            ;;
    esac
}

# Ticket completion announcements
announce_ticket_complete() {
    local ticket_id="$1"
    local ticket_name="$2"
    local test_count="$3"
    local coverage="$4"

    local message="Ticket $ticket_id, $ticket_name, is complete. $test_count tests passing. Coverage at $coverage percent. Ready for merge."
    log_and_speak "COMPLETE" "$message"
}

# Progress update
announce_progress() {
    local phase="$1"  # RED, GREEN, REFACTOR
    local ticket="$2"
    local detail="$3"

    local message="$ticket is in $phase phase. $detail"
    log_and_speak "PROGRESS" "$message"
}

# Error announcement
announce_error() {
    local ticket="$1"
    local error="$2"

    local message="$ticket encountered an error. $error"
    log_and_speak "ERROR" "$message"
}

# Start build
announce_build_start() {
    local count="$1"
    local message="Starting parallel build with $count agents"
    log_and_speak "PROGRESS" "$message"
}

# Merge announcement
announce_merge_complete() {
    local ticket="$1"
    local branch="$2"

    local message="$ticket merged to main from branch $branch"
    log_and_speak "COMPLETE" "$message"
}

# Interactive mode - speak whatever the user types
interactive_mode() {
    echo "Voice Agent Interactive Mode"
    echo "Type messages to speak (type 'exit' to quit):"
    while true; do
        read -p ">> " user_input
        if [ "$user_input" == "exit" ]; then
            speak_update "Exiting voice mode"
            break
        fi
        speak_update "$user_input"
    done
}

# Main CLI
case "${1:-help}" in
    "complete")
        announce_ticket_complete "$2" "$3" "$4" "$5"
        ;;
    "progress")
        announce_progress "$2" "$3" "$4"
        ;;
    "error")
        announce_error "$2" "$3"
        ;;
    "build-start")
        announce_build_start "$2"
        ;;
    "merge")
        announce_merge_complete "$2" "$3"
        ;;
    "interactive")
        interactive_mode
        ;;
    "speak")
        speak_update "$2"
        ;;
    "help")
        cat << 'EOF'
Voice Agent Commands:

./voice-agent.sh speak "message"
  - Speak a custom message

./voice-agent.sh progress RED ticket-name "details"
  - Announce phase progress

./voice-agent.sh complete ticket-id "ticket-name" test-count coverage-percent
  - Announce ticket completion

./voice-agent.sh error ticket-name "error description"
  - Announce error

./voice-agent.sh merge ticket-id branch-name
  - Announce merge complete

./voice-agent.sh build-start agent-count
  - Announce build start

./voice-agent.sh interactive
  - Interactive mode (type messages to speak)

Examples:
  ./voice-agent.sh speak "SaaS Auth two is complete"
  ./voice-agent.sh complete "PRJ0-49" "Auth Endpoints" "7" "85"
  ./voice-agent.sh progress "RED" "SaaS-FE-1" "Writing login form tests"
EOF
        ;;
    *)
        speak_update "Invalid command. Use help for options"
        ;;
esac
