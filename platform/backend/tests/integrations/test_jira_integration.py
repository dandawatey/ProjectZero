"""JIRA integration tests — PRJ0-66. Run with: pytest -m integration"""
import pytest
import os

pytestmark = pytest.mark.integration


@pytest.fixture
def jira_client():
    from app.services.jira_client import JiraClient
    try:
        return JiraClient()
    except RuntimeError:
        pytest.skip("JIRA not configured")


@pytest.mark.asyncio
async def test_jira_list_projects(jira_client):
    projects = await jira_client.list_projects()
    assert isinstance(projects, list)
    keys = [p["key"] for p in projects]
    assert "PRJ0" in keys


@pytest.mark.asyncio
async def test_jira_create_and_transition_issue(jira_client):
    import httpx
    # Create test issue
    result = await jira_client.create_issue(
        project_key="PRJ0",
        summary="[TEST] PRJ0-66 integration test — delete me",
        description_adf=jira_client._build_adf_paragraph(
            "Auto-created by PRJ0-66 integration test"
        ),
        issue_type="Task",
        priority="Low",
    )
    issue_key = result["key"]
    assert issue_key.startswith("PRJ0-")

    # Get transitions
    transitions = await jira_client.list_transitions_by_name(issue_key)
    assert "In Progress" in transitions or "Done" in transitions

    # Transition to Done
    done_id = transitions.get("Done", list(transitions.values())[-1])
    ok = await jira_client.transition_issue(issue_key, done_id)
    assert ok is True

    # Add comment
    async with httpx.AsyncClient() as c:
        await jira_client.add_comment(
            issue_key,
            jira_client._build_adf_paragraph(
                "Integration test complete — safe to delete"
            ),
        )


@pytest.mark.asyncio
async def test_jira_search(jira_client):
    import httpx
    async with httpx.AsyncClient() as c:
        issues = await jira_client.search(
            c,
            "project = PRJ0 AND status = Done ORDER BY key DESC",
            ["summary", "status"],
            max_results=5,
        )
    assert isinstance(issues, list)
    assert len(issues) > 0
