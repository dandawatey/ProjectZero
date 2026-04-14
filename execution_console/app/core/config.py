"""Central configuration — reads from env vars / .env — PRJ0-56."""
from __future__ import annotations
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent.parent / ".env")
except ImportError:
    pass


class Config:
    # Console backend
    EXECUTION_CONSOLE_URL: str = os.getenv("EXECUTION_CONSOLE_URL", "http://localhost:8001")
    CONSOLE_DB_PATH: str = os.getenv("CONSOLE_DB_PATH", str(Path.home() / ".projectzero" / "console.db"))
    CONSOLE_LOG_PATH: str = os.getenv("CONSOLE_LOG_PATH", str(Path.home() / ".projectzero" / "events.jsonl"))
    CONSOLE_REFRESH_SECONDS: float = float(os.getenv("CONSOLE_REFRESH_SECONDS", "2.0"))

    # JIRA
    JIRA_BASE_URL: str = os.getenv("JIRA_BASE_URL", "")
    JIRA_USER_EMAIL: str = os.getenv("JIRA_USER_EMAIL", "")
    JIRA_API_TOKEN: str = os.getenv("JIRA_API_TOKEN", "")
    JIRA_PROJECT_KEY: str = os.getenv("JIRA_PROJECT_KEY", "PRJ0")

    # Temporal
    TEMPORAL_HOST: str = os.getenv("TEMPORAL_HOST", "localhost:7233")
    TEMPORAL_NAMESPACE: str = os.getenv("TEMPORAL_NAMESPACE", "default")
    TEMPORAL_UI_URL: str = os.getenv("TEMPORAL_UI_URL", "http://localhost:8233")

    # ProjectZero platform backend
    PROJECTZERO_BASE_URL: str = os.getenv("PROJECTZERO_BASE_URL", "http://localhost:8000")
    PROJECTZERO_TOKEN: str = os.getenv("PROJECTZERO_TOKEN", "")

    # Claude Code hook integration
    CLAUDE_CURRENT_TICKET: str = os.getenv("CLAUDE_CURRENT_TICKET", "")
    CLAUDE_AGENT_NAME: str = os.getenv("CLAUDE_AGENT_NAME", "claude")

    # OTel
    OTEL_ENABLED: bool = os.getenv("OTEL_ENABLED", "false").lower() == "true"
    OTEL_ENDPOINT: str = os.getenv("OTEL_ENDPOINT", "http://localhost:4317")
    OTEL_SERVICE_NAME: str = os.getenv("OTEL_SERVICE_NAME", "execution-console")

    @classmethod
    def jira_configured(cls) -> bool:
        return bool(cls.JIRA_BASE_URL and cls.JIRA_USER_EMAIL and cls.JIRA_API_TOKEN)

    @classmethod
    def temporal_configured(cls) -> bool:
        return cls.TEMPORAL_HOST != "localhost:7233" or os.getenv("TEMPORAL_HOST")

    @classmethod
    def jira_issue_url(cls, issue_key: str) -> str:
        if cls.JIRA_BASE_URL:
            return f"{cls.JIRA_BASE_URL}/browse/{issue_key}"
        return f"https://jira.atlassian.net/browse/{issue_key}"

    @classmethod
    def temporal_workflow_url(cls, workflow_id: str, run_id: str = "") -> str:
        base = f"{cls.TEMPORAL_UI_URL}/namespaces/{cls.TEMPORAL_NAMESPACE}/workflows/{workflow_id}"
        return f"{base}/{run_id}" if run_id else base


cfg = Config()
