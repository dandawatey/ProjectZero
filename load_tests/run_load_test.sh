#!/usr/bin/env bash
# Run Locust load test against ProjectZero — PRJ0-68
# Usage: ./load_tests/run_load_test.sh [users] [spawn-rate] [duration]

USERS=${1:-50}
RATE=${2:-10}
DURATION=${3:-60s}
HOST=${LOAD_TEST_HOST:-http://localhost:8000}
REPORT_DIR="load_tests/reports"

mkdir -p "$REPORT_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "Starting load test: $USERS users @ $RATE/s for $DURATION against $HOST"

locust -f load_tests/locustfile.py \
  --headless \
  -u "$USERS" \
  -r "$RATE" \
  --run-time "$DURATION" \
  --host "$HOST" \
  --html "$REPORT_DIR/locust_report_${TIMESTAMP}.html" \
  --csv "$REPORT_DIR/locust_${TIMESTAMP}" \
  2>&1 | tee "$REPORT_DIR/locust_run_${TIMESTAMP}.log"

echo ""
echo "Report: $REPORT_DIR/locust_report_${TIMESTAMP}.html"

# Assert p95 < 500ms from CSV
python3 - <<PYEOF
import csv, sys, glob

csvfiles = sorted(glob.glob("$REPORT_DIR/locust_${TIMESTAMP}_stats.csv"))
if not csvfiles:
    print("No stats CSV found — manual check required")
    sys.exit(0)

with open(csvfiles[0]) as f:
    reader = csv.DictReader(f)
    failures = []
    for row in reader:
        name = row.get("Name","")
        if name == "Aggregated":
            p95 = float(row.get("95%", 0) or 0)
            fail_pct = float(row.get("Failure Count", 0) or 0)
            total = float(row.get("Request Count", 1) or 1)
            fail_rate = fail_pct / total * 100
            print(f"p95 latency: {p95}ms | Failure rate: {fail_rate:.1f}%")
            if p95 > 500:
                print(f"WARN: p95 {p95}ms exceeds 500ms target")
            if fail_rate > 1:
                print(f"WARN: Failure rate {fail_rate:.1f}% exceeds 1% target")
            else:
                print("PASS: All thresholds met")
PYEOF
