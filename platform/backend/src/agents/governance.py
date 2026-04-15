"""Governance agents: Checker, Reviewer, Approver."""

import logging
from typing import List, Dict, Any
from datetime import datetime

from .base import Agent, AgentContext, AgentResult, AgentRole, AgentStatus

logger = logging.getLogger(__name__)


class Checker(Agent):
    """Checker agent: automated quality gates."""

    def __init__(self):
        super().__init__("Checker", AgentRole.CHECKER)

    async def execute(self, context: AgentContext) -> AgentResult:
        """Run quality gates: tests, coverage, lint, types, security."""
        start_time = datetime.utcnow()
        try:
            await self.update_status(AgentStatus.IN_PROGRESS, "Running quality gates")

            checks = {}

            # 1. Run tests
            logger.info("Running pytest")
            checks["tests"] = await self._run_tests(context)

            # 2. Check coverage
            logger.info("Checking coverage ≥80%")
            checks["coverage"] = await self._check_coverage(context)

            # 3. Run linting
            logger.info("Running linting")
            checks["linting"] = await self._run_linting(context)

            # 4. Run type checking
            logger.info("Running type checking")
            checks["types"] = await self._run_types(context)

            # 5. Security scan
            logger.info("Running security scan")
            checks["security"] = await self._run_security_scan(context)

            # 6. Check ticket reference
            logger.info("Checking ticket references in commits")
            checks["ticket_ref"] = await self._check_ticket_reference(context)

            # Determine overall result
            all_passed = all(check["passed"] for check in checks.values())

            duration = (datetime.utcnow() - start_time).total_seconds()

            result = AgentResult(
                success=all_passed,
                message=f"Quality gates: {sum(1 for c in checks.values() if c['passed'])}/{len(checks)} passed",
                output=checks,
                errors=[f"{k}: {v['error']}" for k, v in checks.items() if not v["passed"] and v.get("error")],
                duration_seconds=duration,
            )

            if all_passed:
                await self.on_success(result)
            else:
                await self.on_failure(f"Quality gates failed: {result.errors}")

            return result

        except Exception as e:
            error_msg = f"Quality gates failed: {str(e)}"
            await self.on_failure(error_msg)
            return AgentResult(
                success=False,
                message=error_msg,
                errors=[str(e)],
                duration_seconds=(datetime.utcnow() - start_time).total_seconds(),
            )

    async def _run_tests(self, context: AgentContext) -> Dict[str, Any]:
        """Run pytest."""
        logger.debug("Mock: Running pytest tests/test_*.py -v")
        # In production: subprocess.run(["pytest", ...])
        return {"passed": True, "count": 42, "output": "42 passed"}

    async def _check_coverage(self, context: AgentContext) -> Dict[str, Any]:
        """Check test coverage ≥80%."""
        logger.debug("Mock: Checking coverage ≥80%")
        # In production: pytest --cov --cov-report=json
        coverage = 85
        passed = coverage >= 80
        return {"passed": passed, "coverage": coverage, "error": None if passed else f"Coverage {coverage}% < 80%"}

    async def _run_linting(self, context: AgentContext) -> Dict[str, Any]:
        """Run ruff linting."""
        logger.debug("Mock: Running ruff lint")
        # In production: subprocess.run(["ruff", "check", ...])
        return {"passed": True, "errors": 0}

    async def _run_types(self, context: AgentContext) -> Dict[str, Any]:
        """Run pyright type checking."""
        logger.debug("Mock: Running pyright")
        # In production: subprocess.run(["pyright", ...])
        return {"passed": True, "errors": 0}

    async def _run_security_scan(self, context: AgentContext) -> Dict[str, Any]:
        """Run OWASP ZAP security scan."""
        logger.debug("Mock: Running OWASP ZAP scan")
        # In production: subprocess.run(["zaproxy", ...])
        return {"passed": True, "issues": 0}

    async def _check_ticket_reference(self, context: AgentContext) -> Dict[str, Any]:
        """Check ticket reference in commit messages."""
        logger.debug(f"Mock: Checking commits reference {context.ticket.ticket_id}")
        # In production: git log --grep="ticket_id"
        return {"passed": True, "found": True}


class Reviewer(Agent):
    """Reviewer agent: code and architecture review."""

    def __init__(self, reviewer_name: str = "Code Reviewer"):
        super().__init__(reviewer_name, AgentRole.REVIEWER)

    async def execute(self, context: AgentContext) -> AgentResult:
        """Review PR: code quality, architecture, tests."""
        start_time = datetime.utcnow()
        try:
            await self.update_status(AgentStatus.IN_PROGRESS, "Reviewing code")

            reviews = {}

            # 1. Code review
            logger.info("Reviewing code quality")
            reviews["code"] = await self._review_code(context)

            # 2. Architecture review
            logger.info("Reviewing architecture")
            reviews["architecture"] = await self._review_architecture(context)

            # 3. Test review
            logger.info("Reviewing tests")
            reviews["tests"] = await self._review_tests(context)

            # Determine overall result
            all_approved = all(review["approved"] for review in reviews.values())

            duration = (datetime.utcnow() - start_time).total_seconds()

            result = AgentResult(
                success=all_approved,
                message=f"Code review: {'APPROVED' if all_approved else 'CHANGES REQUESTED'}",
                output=reviews,
                errors=[f"{k}: {v['comment']}" for k, v in reviews.items() if not v["approved"]],
                duration_seconds=duration,
            )

            if all_approved:
                await self.on_success(result)
            else:
                await self.on_failure(f"Code review requested changes")

            return result

        except Exception as e:
            error_msg = f"Code review failed: {str(e)}"
            await self.on_failure(error_msg)
            return AgentResult(
                success=False,
                message=error_msg,
                errors=[str(e)],
                duration_seconds=(datetime.utcnow() - start_time).total_seconds(),
            )

    async def _review_code(self, context: AgentContext) -> Dict[str, Any]:
        """Review code quality."""
        logger.debug("Mock: Reviewing code quality")
        # In production: use Claude API to review code
        return {"approved": True, "comment": "Code looks good. Well-structured."}

    async def _review_architecture(self, context: AgentContext) -> Dict[str, Any]:
        """Review architecture decisions."""
        logger.debug("Mock: Reviewing architecture")
        return {"approved": True, "comment": "Architecture matches ADR. Good design."}

    async def _review_tests(self, context: AgentContext) -> Dict[str, Any]:
        """Review test coverage and quality."""
        logger.debug("Mock: Reviewing tests")
        return {"approved": True, "comment": "Tests comprehensive, 85% coverage. Excellent."}


class Approver(Agent):
    """Approver agent: final business sign-off."""

    def __init__(self):
        super().__init__("Approver", AgentRole.APPROVER)

    async def execute(self, context: AgentContext) -> AgentResult:
        """Approve PR: business requirements, governance."""
        start_time = datetime.utcnow()
        try:
            await self.update_status(AgentStatus.IN_PROGRESS, "Approving PR")

            checks = {}

            # 1. Business requirements
            logger.info("Checking business requirements")
            checks["requirements"] = await self._check_requirements(context)

            # 2. Governance
            logger.info("Checking governance")
            checks["governance"] = await self._check_governance(context)

            # Determine overall result
            all_approved = all(check["approved"] for check in checks.values())

            if all_approved:
                logger.info("Merging PR to main")
                pr_url = await self._merge_pr(context)

                logger.info("Closing JIRA ticket")
                await self._close_jira_ticket(context)

            duration = (datetime.utcnow() - start_time).total_seconds()

            result = AgentResult(
                success=all_approved,
                message=f"Approver: {'APPROVED & MERGED' if all_approved else 'REJECTED'}",
                output=checks,
                errors=[f"{k}: {v['comment']}" for k, v in checks.items() if not v["approved"]],
                duration_seconds=duration,
            )

            if all_approved:
                await self.on_success(result)
            else:
                await self.on_failure(f"Approval failed")

            return result

        except Exception as e:
            error_msg = f"Approval failed: {str(e)}"
            await self.on_failure(error_msg)
            return AgentResult(
                success=False,
                message=error_msg,
                errors=[str(e)],
                duration_seconds=(datetime.utcnow() - start_time).total_seconds(),
            )

    async def _check_requirements(self, context: AgentContext) -> Dict[str, Any]:
        """Check business requirements met."""
        logger.debug("Mock: Checking business requirements")
        return {"approved": True, "comment": "Acceptance criteria met. ✓"}

    async def _check_governance(self, context: AgentContext) -> Dict[str, Any]:
        """Check governance rules."""
        logger.debug("Mock: Checking governance")
        return {"approved": True, "comment": "No governance issues. ✓"}

    async def _merge_pr(self, context: AgentContext) -> str:
        """Merge PR to main branch."""
        logger.debug("Mock: Merging PR to main")
        # In production: github.merge_pull_request(...)
        return "https://github.com/org/repo/pull/1"

    async def _close_jira_ticket(self, context: AgentContext):
        """Close JIRA ticket."""
        logger.debug(f"Mock: Closing {context.ticket.ticket_id}")
        # In production: jira.update_issue(ticket_id, status="Done")
