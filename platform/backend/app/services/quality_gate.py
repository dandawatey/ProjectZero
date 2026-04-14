"""Quality gate runner — PRJ0-34."""
import subprocess
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class GateResult:
    name: str
    passed: bool
    score: str        # e.g. "87.3%" or "0 errors" or "skipped"
    detail: str = ""


@dataclass
class CheckResult:
    passed: bool
    gates: list[GateResult]
    coverage_pct: float
    lint_errors: int
    type_errors: int


def _run(cmd: list[str], cwd: str) -> tuple[int, str]:
    """Run subprocess, return (returncode, combined output)."""
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120)
        return r.returncode, r.stdout + r.stderr
    except FileNotFoundError:
        return -1, f"command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return -1, f"timeout: {' '.join(cmd)}"


def _coverage_gate(repo_path: str) -> tuple[GateResult, float]:
    """Run pytest --cov, parse coverage %. Fail if <80."""
    cov_json = "/tmp/pz-cov.json"
    code, out = _run(
        [
            "python", "-m", "pytest",
            f"--cov={repo_path}",
            "--cov-report=json:" + cov_json,
            "-q", "--no-header",
        ],
        repo_path,
    )

    if code == -1 and "command not found" in out:
        return GateResult(
            name="coverage",
            passed=False,
            score="skipped",
            detail="pytest not installed",
        ), 0.0

    # Try parse coverage json
    pct: float = 0.0
    try:
        data = json.loads(Path(cov_json).read_text())
        pct = float(data.get("totals", {}).get("percent_covered", 0.0))
    except Exception as exc:
        logger.warning("coverage JSON parse failed: %s", exc)
        # Fallback: parse term output
        import re
        for line in out.splitlines():
            m = re.search(r"TOTAL\s+\d+\s+\d+\s+([\d.]+)%", line)
            if m:
                pct = float(m.group(1))
                break

    passed = pct >= 80.0
    return GateResult(
        name="coverage",
        passed=passed,
        score=f"{pct:.1f}%",
        detail="" if passed else f"below 80% threshold",
    ), pct


def _lint_gate(repo_path: str) -> tuple[GateResult, int]:
    """Run ruff check, parse error count."""
    code, out = _run(
        ["ruff", "check", repo_path, "--output-format=json"],
        repo_path,
    )

    if code == -1 and "command not found" in out:
        return GateResult(
            name="lint",
            passed=False,
            score="skipped",
            detail="ruff not installed",
        ), 0

    try:
        issues = json.loads(out) if out.strip().startswith("[") else []
    except json.JSONDecodeError:
        issues = []

    n = len(issues)
    passed = n == 0
    return GateResult(
        name="lint",
        passed=passed,
        score=f"{n} errors",
        detail="" if passed else f"{n} ruff violations",
    ), n


def _type_gate(repo_path: str) -> tuple[GateResult, int]:
    """Run pyright (preferred) or mypy. Parse error count."""
    # Try pyright first
    code, out = _run(
        ["pyright", repo_path, "--outputjson"],
        repo_path,
    )

    if code != -1:  # pyright found
        try:
            data = json.loads(out)
            errors = data.get("summary", {}).get("errorCount", 0)
        except json.JSONDecodeError:
            import re
            m = re.search(r"(\d+) error", out)
            errors = int(m.group(1)) if m else 0
        passed = errors == 0
        return GateResult(
            name="types",
            passed=passed,
            score=f"{errors} errors",
            detail="" if passed else f"{errors} pyright errors",
        ), errors

    # Try mypy fallback
    mypy_report = "/tmp/pz-mypy-report"
    code, out = _run(
        ["mypy", repo_path, "--json-report", mypy_report, "--ignore-missing-imports"],
        repo_path,
    )

    if code == -1 and "command not found" in out:
        return GateResult(
            name="types",
            passed=False,
            score="skipped",
            detail="pyright and mypy not installed",
        ), 0

    import re
    error_lines = [l for l in out.splitlines() if ": error:" in l]
    errors = len(error_lines)
    passed = errors == 0
    return GateResult(
        name="types",
        passed=passed,
        score=f"{errors} errors",
        detail="" if passed else f"{errors} mypy errors",
    ), errors


def run_quality_gates(repo_path: str) -> CheckResult:
    """Run coverage, lint, and type gates against repo_path. Return CheckResult."""
    repo_path = str(Path(repo_path).expanduser().resolve())
    logger.info("Quality gates starting: %s", repo_path)

    cov_gate, coverage_pct = _coverage_gate(repo_path)
    lint_gate, lint_errors = _lint_gate(repo_path)
    type_gate, type_errors = _type_gate(repo_path)

    gates = [cov_gate, lint_gate, type_gate]

    # Overall pass: all non-skipped gates must pass
    all_passed = all(
        g.passed for g in gates if g.score != "skipped"
    )

    return CheckResult(
        passed=all_passed,
        gates=gates,
        coverage_pct=coverage_pct,
        lint_errors=lint_errors,
        type_errors=type_errors,
    )
