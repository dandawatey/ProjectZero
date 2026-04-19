"""
SaaS-ORG-1: Organization CRUD Endpoints Tests (TDD)

Tests for organization CRUD endpoints with RLS + RBAC + quota enforcement.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from datetime import datetime
import uuid

from app.models.organization import Organization, UserOrganization, RoleType
from app.models.user import User
from app.core.database import async_session
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def test_org_data():
    """Test org creation payload."""
    return {
        "name": "Test Corp",
        "description": "Test organization",
        "region": "us-east-1",
        "billing_contact_email": "billing@testcorp.com",
    }


async def _create_test_user(db: AsyncSession, email: str) -> str:
    """Helper: create a test user in DB. Returns user_id as string."""
    user_id = uuid.uuid4()
    user = User(
        id=str(user_id),  # Convert to string for SQLite
        email=email,
        hashed_password="dummy_hash",  # not used in tests
        role="developer",
        is_active=True,
    )
    db.add(user)
    await db.flush()
    return str(user_id)


@pytest_asyncio.fixture
async def test_user_1_id(app):
    """Create first test user in DB."""
    async with async_session() as db:
        unique_id = str(uuid.uuid4())[:8]
        user_id = await _create_test_user(db, f"testuser1-{unique_id}@example.com")
        await db.commit()
        return user_id


@pytest_asyncio.fixture
async def test_user_2_id(app):
    """Create second test user in DB (for RBAC/RLS tests)."""
    async with async_session() as db:
        unique_id = str(uuid.uuid4())[:8]
        user_id = await _create_test_user(db, f"testuser2-{unique_id}@example.com")
        await db.commit()
        return user_id


@pytest_asyncio.fixture
async def test_user_3_id(app):
    """Create third test user in DB (for isolation tests)."""
    async with async_session() as db:
        unique_id = str(uuid.uuid4())[:8]
        user_id = await _create_test_user(db, f"testuser3-{unique_id}@example.com")
        await db.commit()
        return user_id


@pytest_asyncio.fixture
async def auth_headers(test_user_1_id):
    """Auth headers for first test user."""
    from app.core.security import create_access_token
    from app.core.config import get_settings

    settings = get_settings()
    token = create_access_token(
        data={"sub": str(test_user_1_id)},
        secret=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        expires_minutes=60,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def auth_headers_engineer(test_user_2_id):
    """Auth headers for second test user (engineer)."""
    from app.core.security import create_access_token
    from app.core.config import get_settings

    settings = get_settings()
    token = create_access_token(
        data={"sub": str(test_user_2_id)},
        secret=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        expires_minutes=60,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def auth_headers_other_user(test_user_3_id):
    """Auth headers for third test user (RLS isolation test)."""
    from app.core.security import create_access_token
    from app.core.config import get_settings

    settings = get_settings()
    token = create_access_token(
        data={"sub": str(test_user_3_id)},
        secret=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        expires_minutes=60,
    )
    return {"Authorization": f"Bearer {token}"}


class TestOrgCRUD:
    """Organization CRUD endpoint tests."""

    @pytest.mark.asyncio
    async def test_create_organization(self, client: AsyncClient, test_org_data, auth_headers):
        """Test POST /api/v1/organizations creates org."""
        response = await client.post(
            "/api/v1/organizations",
            json=test_org_data,
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == test_org_data["name"]
        assert data["region"] == test_org_data["region"]
        assert data["tier"] == "starter"
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_organization_sets_creator_as_owner(
        self, client: AsyncClient, test_org_data, auth_headers
    ):
        """Test that org creator is automatically assigned as Owner."""
        response = await client.post(
            "/api/v1/organizations",
            json=test_org_data,
            headers=auth_headers,
        )
        assert response.status_code == 201
        org_id = response.json()["id"]

        # Verify user is Owner in users_orgs table
        members_resp = await client.get(
            f"/api/v1/organizations/{org_id}/members",
            headers=auth_headers,
        )
        assert members_resp.status_code == 200
        members = members_resp.json()
        assert len(members) >= 1
        assert any(m["role"] == "Owner" for m in members)

    @pytest.mark.asyncio
    async def test_list_organizations(self, client: AsyncClient, test_org_data, auth_headers):
        """Test GET /api/v1/organizations lists user's orgs."""
        # Create org first
        create_resp = await client.post(
            "/api/v1/organizations",
            json=test_org_data,
            headers=auth_headers,
        )
        org_id = create_resp.json()["id"]

        # List orgs
        response = await client.get(
            "/api/v1/organizations",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(org["id"] == org_id for org in data)

    @pytest.mark.asyncio
    async def test_get_organization(self, client: AsyncClient, test_org_data, auth_headers):
        """Test GET /api/v1/organizations/{org_id} retrieves org."""
        # Create org
        create_resp = await client.post(
            "/api/v1/organizations",
            json=test_org_data,
            headers=auth_headers,
        )
        org_id = create_resp.json()["id"]

        # Get org
        response = await client.get(
            f"/api/v1/organizations/{org_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == org_id
        assert data["name"] == test_org_data["name"]
        assert data["region"] == test_org_data["region"]

    @pytest.mark.asyncio
    async def test_get_organization_not_found(self, client: AsyncClient, auth_headers):
        """Test GET unknown org returns 403 (access denied, don't leak existence)."""
        fake_id = uuid.uuid4()
        response = await client.get(
            f"/api/v1/organizations/{fake_id}",
            headers=auth_headers,
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_organization(
        self, client: AsyncClient, test_org_data, auth_headers
    ):
        """Test PATCH /api/v1/organizations/{org_id} updates org."""
        # Create org
        create_resp = await client.post(
            "/api/v1/organizations",
            json=test_org_data,
            headers=auth_headers,
        )
        org_id = create_resp.json()["id"]

        # Update org
        update_data = {
            "name": "Updated Corp",
            "region": "eu-west-1",
            "billing_contact_email": "new@testcorp.com",
        }
        response = await client.patch(
            f"/api/v1/organizations/{org_id}",
            json=update_data,
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Corp"
        assert data["region"] == "eu-west-1"
        assert data["billing_contact_email"] == "new@testcorp.com"

    @pytest.mark.asyncio
    async def test_delete_organization(self, client: AsyncClient, test_org_data, auth_headers):
        """Test DELETE /api/v1/organizations/{org_id} soft-deletes org."""
        # Create org
        create_resp = await client.post(
            "/api/v1/organizations",
            json=test_org_data,
            headers=auth_headers,
        )
        org_id = create_resp.json()["id"]

        # Delete org
        response = await client.delete(
            f"/api/v1/organizations/{org_id}",
            headers=auth_headers,
        )
        assert response.status_code == 204

        # Verify org is hidden (RLS should hide it)
        get_resp = await client.get(
            f"/api/v1/organizations/{org_id}",
            headers=auth_headers,
        )
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_rls_user_cannot_access_other_org(
        self, client: AsyncClient, test_org_data, auth_headers, auth_headers_other_user
    ):
        """Test Row-Level Security: user X cannot read org Y."""
        # User 1 creates org
        create_resp = await client.post(
            "/api/v1/organizations",
            json=test_org_data,
            headers=auth_headers,
        )
        org_id = create_resp.json()["id"]

        # User 2 tries to access org → should fail
        response = await client.get(
            f"/api/v1/organizations/{org_id}",
            headers=auth_headers_other_user,
        )
        assert response.status_code in [403, 404]

    @pytest.mark.asyncio
    async def test_quota_enforcement_starter_tier(
        self, client: AsyncClient, auth_headers, test_org_data
    ):
        """Test Starter tier quota: max 1 workspace."""
        # Create org (Starter tier)
        create_resp = await client.post(
            "/api/v1/organizations",
            json=test_org_data,
            headers=auth_headers,
        )
        org_id = create_resp.json()["id"]

        # Create 1st workspace → should succeed
        ws_resp_1 = await client.post(
            f"/api/v1/organizations/{org_id}/workspaces",
            json={"name": "Workspace 1"},
            headers=auth_headers,
        )
        assert ws_resp_1.status_code == 201

        # Create 2nd workspace → should fail (quota exceeded)
        ws_resp_2 = await client.post(
            f"/api/v1/organizations/{org_id}/workspaces",
            json={"name": "Workspace 2"},
            headers=auth_headers,
        )
        assert ws_resp_2.status_code == 429  # Too Many Requests

    @pytest.mark.asyncio
    async def test_create_organization_requires_auth(self, client: AsyncClient, test_org_data):
        """Test unauthenticated request returns 401."""
        response = await client.post(
            "/api/v1/organizations",
            json=test_org_data,
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_only_owner_can_update_org(
        self, client: AsyncClient, test_org_data, auth_headers, auth_headers_engineer
    ):
        """Test only Owner role can update org settings."""
        # Owner creates org
        create_resp = await client.post(
            "/api/v1/organizations",
            json=test_org_data,
            headers=auth_headers,
        )
        org_id = create_resp.json()["id"]

        # Invite engineer as member
        await client.post(
            f"/api/v1/organizations/{org_id}/members",
            json={"email": "engineer@example.com", "role": "Engineer"},
            headers=auth_headers,
        )

        # Engineer tries to update org → should fail
        update_data = {"name": "Hacked Name"}
        response = await client.patch(
            f"/api/v1/organizations/{org_id}",
            json=update_data,
            headers=auth_headers_engineer,
        )
        assert response.status_code == 403
