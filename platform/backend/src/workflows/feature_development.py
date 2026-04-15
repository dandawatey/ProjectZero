"""Temporal workflow: Feature development (MCRA gates)."""

from datetime import timedelta
import logging
from typing import Optional

from temporalio import workflow
from temporalio.common import RetryPolicy

from ..agents.base import AgentContext, JiraTicket, GitRepo, AgentRole
from ..agents.makers import BackendEngineer
from ..agents.governance import Checker, Reviewer, Approver

logger = logging.getLogger(__name__)


@workflow.defn
class FeatureDevelopmentWorkflow:
    """Temporal workflow: Feature development with MCRA gates.

    Flow:
    1. Maker (Backend Engineer) writes code (TDD)
    2. Checker verifies quality gates (tests, coverage, lint, types)
    3. Reviewer approves code + architecture
    4. Approver gives final sign-off + merges
    """

    @workflow.run
    async def execute(
        self,
        ticket_id: str,
        product_name: str,
        product_repo_url: str,
        user_id: str,
        workspace_path: str,
    ) -> dict:
        """Execute feature development workflow.

        Args:
            ticket_id: JIRA ticket (e.g., "ICOMPLY-1")
            product_name: Product name (e.g., "i-comply")
            product_repo_url: Git repo URL
            user_id: User triggering workflow
            workspace_path: Base path for agent work

        Returns:
            Workflow result with final status
        """
        logger.info(f"Starting feature development workflow: {ticket_id}")

        # TODO: Fetch ticket details from JIRA
        ticket = JiraTicket(
            ticket_id=ticket_id,
            title=f"Feature {ticket_id}",
            description=f"Implement {ticket_id}",
            acceptance_criteria=[
                "Criterion 1",
                "Criterion 2",
                "Criterion 3",
            ],
            story_points=8,
        )

        repo = GitRepo(
            url=product_repo_url,
            name=product_name,
        )

        # Create agent context
        context = AgentContext(
            ticket=ticket,
            repo=repo,
            agent_role=AgentRole.MAKER,
            agent_name="Backend Engineer",
            user_id=user_id,
            workspace_path=workspace_path,
        )

        result = {
            "ticket_id": ticket_id,
            "product": product_name,
            "gates": {},
        }

        # ====================================================================
        # GATE 1: MAKER (Backend Engineer writes code via TDD)
        # ====================================================================
        logger.info(f"[GATE 1] MAKER: Backend Engineer starts TDD cycle")

        maker = BackendEngineer()
        await maker.set_context(context)
        maker_result = await maker.execute(context)

        result["gates"]["maker"] = {
            "success": maker_result.success,
            "message": maker_result.message,
            "output": maker_result.output,
        }

        if not maker_result.success:
            logger.error(f"Maker gate failed: {maker_result.message}")
            return {"success": False, "failed_gate": "maker", **result}

        logger.info(f"[GATE 1] MAKER ✓ PR opened: {maker_result.output.get('pr_url')}")

        # ====================================================================
        # GATE 2: CHECKER (Automated quality gates)
        # ====================================================================
        logger.info(f"[GATE 2] CHECKER: Running automated quality gates")

        checker = Checker()
        await checker.set_context(context)
        checker_result = await checker.execute(context)

        result["gates"]["checker"] = {
            "success": checker_result.success,
            "message": checker_result.message,
            "output": checker_result.output,
        }

        if not checker_result.success:
            logger.warning(f"Checker gate failed: {checker_result.errors}")
            logger.info(f"Requesting Maker fix issues and resubmit")
            # In production: loop back to Maker, request fixes
            # For MVP: return failure
            return {"success": False, "failed_gate": "checker", **result}

        logger.info(f"[GATE 2] CHECKER ✓ All quality gates passed")

        # ====================================================================
        # GATE 3: REVIEWER (Code + architecture review)
        # ====================================================================
        logger.info(f"[GATE 3] REVIEWER: Code and architecture review")

        reviewer = Reviewer()
        await reviewer.set_context(context)
        reviewer_result = await reviewer.execute(context)

        result["gates"]["reviewer"] = {
            "success": reviewer_result.success,
            "message": reviewer_result.message,
            "output": reviewer_result.output,
        }

        if not reviewer_result.success:
            logger.warning(f"Reviewer gate requested changes: {reviewer_result.errors}")
            # In production: loop back to Maker, request changes
            return {"success": False, "failed_gate": "reviewer", **result}

        logger.info(f"[GATE 3] REVIEWER ✓ Code approved")

        # ====================================================================
        # GATE 4: APPROVER (Final business sign-off + merge)
        # ====================================================================
        logger.info(f"[GATE 4] APPROVER: Final approval and merge")

        approver = Approver()
        await approver.set_context(context)
        approver_result = await approver.execute(context)

        result["gates"]["approver"] = {
            "success": approver_result.success,
            "message": approver_result.message,
            "output": approver_result.output,
        }

        if not approver_result.success:
            logger.error(f"Approver gate rejected: {approver_result.errors}")
            return {"success": False, "failed_gate": "approver", **result}

        logger.info(f"[GATE 4] APPROVER ✓ PR merged to main, ticket closed")

        # ====================================================================
        # WORKFLOW COMPLETE
        # ====================================================================
        result["success"] = True
        result["status"] = "DONE"
        logger.info(f"Feature development workflow complete: {ticket_id}")

        return result


@workflow.defn
class EnterpriseBootstrapWorkflow:
    """Temporal workflow: Bootstrap new product with enterprise agents + MCRA.

    Creates:
    1. New product git repo
    2. JIRA project + tickets (P0/P1/P2/P3)
    3. Agent team assignments
    4. MCRA automation setup
    5. Starts P0 feature development workflows in parallel
    """

    @workflow.run
    async def execute(
        self,
        product_name: str,
        enterprise_features: list[str],  # ["tenant-isolation", "multi-db", "encryption", ...]
        organization: str,
        team_members: dict,  # {"cto": "name", "engineering_lead": "name", ...}
    ) -> dict:
        """Bootstrap new product with enterprise capabilities.

        Args:
            product_name: New product name (e.g., "i-comply")
            enterprise_features: Features to include (e.g., ["tenant-isolation", "multi-db", "encryption"])
            organization: GitHub organization
            team_members: Team member assignments

        Returns:
            Bootstrap result with project details
        """
        logger.info(f"Bootstrapping product: {product_name}")

        result = {
            "product_name": product_name,
            "organization": organization,
            "features": enterprise_features,
            "setup": {},
        }

        # TODO: Implement bootstrap steps:
        # 1. Create GitHub repo
        # 2. Create JIRA project
        # 3. Generate JIRA tickets (map PRJ0-98..PRJ0-110 to product-specific)
        # 4. Assign agents to tickets
        # 5. Setup agent team configuration
        # 6. Create MCRA automation setup
        # 7. Start P0 workflows in parallel

        result["setup"]["github_repo"] = f"https://github.com/{organization}/{product_name}"
        result["setup"]["jira_project"] = f"{product_name.upper()}"
        result["setup"]["agents_ready"] = True
        result["setup"]["mcra_enabled"] = True

        logger.info(f"Product bootstrapped: {product_name}")
        return result
