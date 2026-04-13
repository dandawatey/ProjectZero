"""Temporal worker — registers all workflows and activities, connects to the server.

Usage:
    cd platform/temporal
    python -m workers.main

Environment variables:
    TEMPORAL_ADDRESS    — Temporal server address (default: localhost:7233)
    TEMPORAL_NAMESPACE  — Temporal namespace (default: default)
    TEMPORAL_TASK_QUEUE — Task queue name (default: projectzero-factory)
"""

from __future__ import annotations

import asyncio
import os
import sys

from temporalio.client import Client
from temporalio.worker import Worker

# Workflows
from workflows.feature_development import (
    FeatureDevelopmentWorkflow,
    MakerCheckerReviewerWorkflow,
)
from workflows.bug_fix import BugFixWorkflow
from workflows.qa_validation import QAValidationWorkflow
from workflows.deployment_readiness import DeploymentReadinessWorkflow
from workflows.release_governance import ReleaseGovernanceWorkflow

# Activities
from activities.core import (
    sync_workflow_state,
    record_step,
    request_approval,
    execute_stage,
    assign_agent,
    generate_artifact,
    create_audit_log,
    validate_input,
    finalize_workflow,
)

TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")
TASK_QUEUE = os.getenv("TEMPORAL_TASK_QUEUE", "projectzero-factory")

ALL_WORKFLOWS = [
    FeatureDevelopmentWorkflow,
    MakerCheckerReviewerWorkflow,
    BugFixWorkflow,
    QAValidationWorkflow,
    DeploymentReadinessWorkflow,
    ReleaseGovernanceWorkflow,
]

ALL_ACTIVITIES = [
    sync_workflow_state,
    record_step,
    request_approval,
    execute_stage,
    assign_agent,
    generate_artifact,
    create_audit_log,
    validate_input,
    finalize_workflow,
]


async def run_worker() -> None:
    """Connect to Temporal and run the worker until interrupted."""
    print(f"Connecting to Temporal at {TEMPORAL_ADDRESS} (namespace={TEMPORAL_NAMESPACE})")
    client = await Client.connect(
        TEMPORAL_ADDRESS,
        namespace=TEMPORAL_NAMESPACE,
    )

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=ALL_WORKFLOWS,
        activities=ALL_ACTIVITIES,
    )

    print(f"Worker started on queue: {TASK_QUEUE}")
    print(f"  Workflows:  {[w.__name__ for w in ALL_WORKFLOWS]}")
    print(f"  Activities: {[a.__name__ for a in ALL_ACTIVITIES]}")

    await worker.run()


def main() -> None:
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        print("\nWorker stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
