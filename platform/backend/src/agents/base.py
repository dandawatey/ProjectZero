"""Base agent class and context management."""

import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Agent roles in MCRA workflow."""
    MAKER = "maker"  # Writes code (TDD)
    CHECKER = "checker"  # Validates quality gates
    REVIEWER = "reviewer"  # Reviews code
    APPROVER = "approver"  # Final sign-off


class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class JiraTicket:
    """JIRA ticket context."""
    ticket_id: str  # e.g., "ICOMPLY-1"
    title: str
    description: str
    acceptance_criteria: List[str]
    story_points: int
    assigned_to: Optional[str] = None
    status: str = "To Do"  # To Do, In Progress, In Review, Done


@dataclass
class GitRepo:
    """Git repository context."""
    url: str  # e.g., "https://github.com/org/i-comply.git"
    name: str  # e.g., "i-comply"
    branch: str = "main"
    clone_path: Optional[str] = None


@dataclass
class AgentResult:
    """Agent execution result."""
    success: bool
    message: str
    output: Optional[Dict[str, Any]] = None
    errors: List[str] = None
    duration_seconds: float = 0.0

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


@dataclass
class AgentContext:
    """Request-scoped context for agent execution."""
    ticket: JiraTicket
    repo: GitRepo
    agent_role: AgentRole
    agent_name: str
    user_id: str
    workspace_path: str  # Base path for agent work
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class Agent(ABC):
    """Base agent class for all MCRA agents."""

    def __init__(self, agent_name: str, role: AgentRole):
        self.agent_name = agent_name
        self.role = role
        self.status = AgentStatus.IDLE
        self.context: Optional[AgentContext] = None

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute agent work on ticket.

        Args:
            context: Agent context (ticket, repo, workspace)

        Returns:
            AgentResult with success/failure + output
        """
        pass

    async def set_context(self, context: AgentContext):
        """Set execution context."""
        self.context = context
        logger.info(f"Agent {self.agent_name} context set: {context.ticket.ticket_id}")

    async def update_status(self, status: AgentStatus, message: str = ""):
        """Update agent status."""
        self.status = status
        logger.info(f"Agent {self.agent_name} status: {status.value} - {message}")

    async def on_success(self, result: AgentResult):
        """Callback on successful execution."""
        logger.info(f"Agent {self.agent_name} succeeded: {result.message}")

    async def on_failure(self, error: str):
        """Callback on failed execution."""
        logger.error(f"Agent {self.agent_name} failed: {error}")

    def __str__(self):
        return f"{self.agent_name} ({self.role.value})"
