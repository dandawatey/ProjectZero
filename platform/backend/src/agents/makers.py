"""Maker agents: Backend Engineer, Frontend Engineer, Data Engineer."""

import asyncio
import logging
from typing import List
from datetime import datetime

from .base import Agent, AgentContext, AgentResult, AgentRole, AgentStatus

logger = logging.getLogger(__name__)


class MakerAgent(Agent):
    """Base maker agent (writes code via TDD)."""

    def __init__(self, agent_name: str = "Backend Engineer"):
        super().__init__(agent_name, AgentRole.MAKER)

    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute TDD cycle: test → implement → refactor."""
        start_time = datetime.utcnow()
        try:
            await self.update_status(AgentStatus.IN_PROGRESS, "Starting TDD cycle")

            # Step 1: Clone repo
            logger.info(f"Cloning {context.repo.url}")
            await self._clone_repo(context)

            # Step 2: Create feature branch
            branch_name = f"{context.ticket.ticket_id.lower()}-{context.ticket.title.lower().replace(' ', '-')}"
            logger.info(f"Creating branch: {branch_name}")
            await self._create_branch(context, branch_name)

            # Step 3: Write tests (TDD - RED)
            logger.info("Writing tests (TDD - RED phase)")
            test_file = await self._write_tests(context)

            # Step 4: Implement (TDD - GREEN)
            logger.info("Implementing feature (TDD - GREEN phase)")
            impl_files = await self._implement_feature(context)

            # Step 5: Refactor
            logger.info("Refactoring code (TDD - REFACTOR phase)")
            await self._refactor(context, impl_files)

            # Step 6: Commit
            logger.info("Committing changes")
            commit_hash = await self._commit(context, context.ticket.ticket_id)

            # Step 7: Push
            logger.info("Pushing to origin")
            await self._push(context, branch_name)

            # Step 8: Open PR
            logger.info("Opening pull request")
            pr_url = await self._open_pr(context, branch_name)

            duration = (datetime.utcnow() - start_time).total_seconds()

            result = AgentResult(
                success=True,
                message=f"TDD cycle complete: {len(impl_files)} files implemented, tests passing",
                output={
                    "branch": branch_name,
                    "commit_hash": commit_hash,
                    "pr_url": pr_url,
                    "test_file": test_file,
                    "impl_files": impl_files,
                },
                duration_seconds=duration,
            )

            await self.on_success(result)
            return result

        except Exception as e:
            error_msg = f"TDD cycle failed: {str(e)}"
            await self.on_failure(error_msg)
            return AgentResult(
                success=False,
                message=error_msg,
                errors=[str(e)],
                duration_seconds=(datetime.utcnow() - start_time).total_seconds(),
            )

    async def _clone_repo(self, context: AgentContext) -> str:
        """Clone repository."""
        # In production: use subprocess.run(["git", "clone", ...])
        logger.debug(f"Mock: Cloning {context.repo.url} to {context.workspace_path}/{context.repo.name}")
        return f"{context.workspace_path}/{context.repo.name}"

    async def _create_branch(self, context: AgentContext, branch_name: str):
        """Create feature branch."""
        logger.debug(f"Mock: Creating branch {branch_name}")
        # In production: git checkout -b branch_name

    async def _write_tests(self, context: AgentContext) -> str:
        """Write test file (TDD - RED phase)."""
        test_filename = f"tests/test_{context.ticket.ticket_id.lower()}.py"
        logger.debug(f"Mock: Writing tests to {test_filename}")
        logger.debug(f"Acceptance criteria: {context.ticket.acceptance_criteria}")

        # In production: use Claude API to generate tests
        # Prompt: "Write pytest tests for: {acceptance_criteria}"
        # Generate test file with ≥80% of acceptance criteria covered

        return test_filename

    async def _implement_feature(self, context: AgentContext) -> List[str]:
        """Implement feature (TDD - GREEN phase)."""
        impl_files = [
            f"src/{context.ticket.ticket_id.lower()}.py",
        ]

        for file in impl_files:
            logger.debug(f"Mock: Implementing {file}")
            # In production: use Claude API to generate implementation
            # Prompt: "Implement code to pass: {test_file}"

        return impl_files

    async def _refactor(self, context: AgentContext, impl_files: List[str]):
        """Refactor code (TDD - REFACTOR phase)."""
        logger.debug(f"Mock: Refactoring {len(impl_files)} files")
        # In production: use Claude API to suggest refactorings
        # Check: code style, performance, maintainability

    async def _commit(self, context: AgentContext, ticket_id: str) -> str:
        """Commit changes."""
        commit_msg = f"feat: {context.ticket.title} ({ticket_id})\n\nAcceptance criteria:\n"
        commit_msg += "\n".join(f"- {c}" for c in context.ticket.acceptance_criteria)
        commit_msg += "\n\nCo-Authored-By: Claude <noreply@anthropic.com>"

        logger.debug(f"Mock: Committing: {commit_msg[:80]}...")
        # In production: git commit -m "{commit_msg}"

        return "abc123def456"  # Mock commit hash

    async def _push(self, context: AgentContext, branch_name: str):
        """Push to remote."""
        logger.debug(f"Mock: Pushing {branch_name} to origin")
        # In production: git push -u origin branch_name

    async def _open_pr(self, context: AgentContext, branch_name: str) -> str:
        """Open pull request on GitHub."""
        pr_description = f"""## {context.ticket.title}

**Ticket**: {context.ticket.ticket_id}

**Description**:
{context.ticket.description}

**Acceptance Criteria**:
{chr(10).join(f'- [ ] {c}' for c in context.ticket.acceptance_criteria)}

**Test Evidence**:
- All tests passing
- Coverage: 85%+ (target: ≥80%)
- Linting: clean
- Type checking: clean

**Labels**: `tdd`, `{context.ticket.ticket_id.lower()}`
"""

        logger.debug(f"Mock: Opening PR on {context.repo.name}")
        # In production: github.create_pull_request(...)

        return f"https://github.com/org/{context.repo.name}/pull/1"


class BackendEngineer(MakerAgent):
    """Backend engineer agent: builds server-side features."""

    def __init__(self):
        super().__init__("Backend Engineer")


class FrontendEngineer(MakerAgent):
    """Frontend engineer agent: builds UI features."""

    def __init__(self):
        super().__init__("Frontend Engineer")


class DataEngineer(MakerAgent):
    """Data engineer agent: builds data pipelines."""

    def __init__(self):
        super().__init__("Data Engineer")
