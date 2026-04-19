#!/bin/bash
# Voice Assistant for ProjectZero Build
# Natural, casual conversation with Soumya (Indian female voice)

VOICE="Soumya"
RATE="160"

speak() {
    say -v "$VOICE" -r "$RATE" "$1"
}

log_it() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> .claude/voice-assistant.log
}

# CASUAL, FRIENDLY ANNOUNCEMENTS

ticket_done() {
    local ticket="$1"
    local tests="$2"
    local name="$3"
    msg="Hey! Great news! The $name ticket is all done. Got $tests tests passing, everything's working perfectly, and it's ready to merge."
    speak "$msg"
    log_it "✅ DONE: $ticket - $name"
}

progress_update() {
    local ticket="$1"
    local phase="$2"
    local what="$3"
    msg="$ticket is moving along nicely. Right now in the $phase phase. $what. Keep an eye on this one."
    speak "$msg"
    log_it "🔄 PROGRESS: $ticket - $phase"
}

error_found() {
    local ticket="$1"
    local issue="$2"
    msg="Okay, so $ticket just hit a snag. $issue. Nothing we can't handle, but wanted to give you a heads up."
    speak "$msg"
    log_it "❌ ERROR: $ticket - $issue"
}

build_kick_off() {
    local count="$1"
    msg="Alright, let's get this going! Spinning up $count agents to work in parallel. I'll keep you in the loop as things wrap up."
    speak "$msg"
    log_it "🚀 BUILD_START: $count agents"
}

we_crushed_it() {
    msg="Yes! We absolutely crushed it! All tickets are complete, all tests passing, and we're totally ready to ship this thing."
    speak "$msg"
    log_it "🎉 ALL_COMPLETE"
}

quick_status() {
    local done="$1"
    local working="$2"
    local left="$3"
    msg="So here's where we're at: $done tickets knocked out, $working still cooking, and $left more in the queue. We're making solid progress!"
    speak "$msg"
    log_it "📊 STATUS"
}

say_hello() {
    msg="Hey there! I'm your build assistant. I'm gonna be your eyes and ears on this project, giving you friendly updates as things get done. No more boring technical logs, just real talk about what's happening."
    speak "$msg"
}

# MAIN
case "${1:-hello}" in
    "done")
        ticket_done "$2" "$3" "$4"
        ;;
    "progress")
        progress_update "$2" "$3" "$4"
        ;;
    "error")
        error_found "$2" "$3"
        ;;
    "build-start")
        build_kick_off "$2"
        ;;
    "crushed")
        we_crushed_it
        ;;
    "status")
        quick_status "$2" "$3" "$4"
        ;;
    "hello"|"hi"|"sample")
        say_hello
        ;;
    *)
        speak "$1"
        log_it "SPEAK: $1"
        ;;
esac
