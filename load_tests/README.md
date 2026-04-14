# Load Tests — PRJ0-68

## Requirements
```bash
pip install locust
```

## Run
```bash
# Quick run (10 users, 30s)
locust -f load_tests/locustfile.py --headless -u 10 -r 5 --run-time 30s --host http://localhost:8000

# Full run (50 users, 60s) with HTML report
./load_tests/run_load_test.sh 50 10 60s

# Interactive UI
locust -f load_tests/locustfile.py --host http://localhost:8000
# Open http://localhost:8089
```

## Targets
- 50 concurrent users
- p95 latency < 500ms for read endpoints
- Failure rate < 1%

## Auth
Set env vars:
- LOAD_TEST_EMAIL (default: loadtest@example.com)
- LOAD_TEST_PASSWORD (default: LoadTest123!)
- LOAD_TEST_HOST (default: http://localhost:8000)
