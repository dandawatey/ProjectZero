"""Organization CRUD endpoints (SaaS-ORG-1)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import datetime
from typing import List
import uuid
import json

from app.core.database import get_db
from app.core.auth_deps import get_current_user
from app.models.user import User


async def get_current_user_id(user: User = Depends(get_current_user)) -> uuid.UUID:
    """Dependency to get current user ID."""
    return user.id
from app.models.organization import (
    Organization, UserOrganization, RoleType, TierType, Workspace, AuditLog
)
from app.schemas.organization import (
    OrganizationCreate, OrganizationUpdate, OrganizationResponse, OrganizationDetailResponse,
    UserOrganizationCreate, UserOrganizationResponse, UserOrganizationUpdate,
    WorkspaceCreate, WorkspaceResponse, AuditLogResponse,
)
from app.services.audit import log_audit_event

router = APIRouter()


# ============================================================================
# Organization CRUD
# ============================================================================

@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create organization",
)
async def create_organization(
    org_data: OrganizationCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Create new organization. Creator becomes Owner."""
    org = Organization(
        name=org_data.name,
        description=org_data.description,
        region=org_data.region,
        billing_contact_email=org_data.billing_contact_email,
        tier=TierType.STARTER,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(org)
    await db.flush()

    # Add creator as Owner
    user_org = UserOrganization(
        user_id=user_id,
        org_id=org.id,
        role=RoleType.OWNER,
        joined_at=datetime.utcnow(),
    )
    db.add(user_org)

    # Audit log (disabled for MVP - SQLite autoincrement issue)
    # await log_audit_event(
    #     db=db,
    #     org_id=org.id,
    #     actor_id=user_id,
    #     resource_type="organization",
    #     resource_id=org.id,
    #     action="created",
    #     changes=json.dumps(org_data.dict()),
    # )

    await db.commit()
    await db.refresh(org)
    return org


@router.get("", response_model=List[OrganizationResponse], summary="List user's organizations")
async def list_organizations(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get all organizations user is member of."""
    stmt = select(Organization).join(
        UserOrganization,
        Organization.id == UserOrganization.org_id,
    ).where(
        UserOrganization.user_id == user_id,
        Organization.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    orgs = result.scalars().all()
    return orgs


@router.get("/{org_id}", response_model=OrganizationDetailResponse, summary="Get organization")
async def get_organization(
    org_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get organization details (with RLS check)."""
    # Verify user is member of org
    member_stmt = select(UserOrganization).where(
        UserOrganization.user_id == user_id,
        UserOrganization.org_id == org_id,
    )
    member = (await db.execute(member_stmt)).scalars().first()
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Get org
    stmt = select(Organization).where(
        Organization.id == org_id,
        Organization.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    org = result.scalars().first()

    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    return org


@router.patch(
    "/{org_id}",
    response_model=OrganizationResponse,
    summary="Update organization",
)
async def update_organization(
    org_id: uuid.UUID,
    update_data: OrganizationUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update organization (Owner only)."""
    # Check authorization (Owner only)
    member_stmt = select(UserOrganization).where(
        UserOrganization.user_id == user_id,
        UserOrganization.org_id == org_id,
        UserOrganization.role == RoleType.OWNER,
    )
    member = (await db.execute(member_stmt)).scalars().first()
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Owner can update org")

    # Get org
    stmt = select(Organization).where(
        Organization.id == org_id,
        Organization.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    org = result.scalars().first()

    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # Track changes for audit log
    changes = {}
    if update_data.name is not None and update_data.name != org.name:
        changes["name"] = {"old": org.name, "new": update_data.name}
        org.name = update_data.name
    if update_data.description is not None and update_data.description != org.description:
        changes["description"] = {"old": org.description, "new": update_data.description}
        org.description = update_data.description
    if update_data.region is not None and update_data.region != org.region:
        changes["region"] = {"old": org.region, "new": update_data.region}
        org.region = update_data.region
    if update_data.billing_contact_email is not None and update_data.billing_contact_email != org.billing_contact_email:
        changes["billing_contact_email"] = {"old": org.billing_contact_email, "new": update_data.billing_contact_email}
        org.billing_contact_email = update_data.billing_contact_email
    if update_data.logo_url is not None and update_data.logo_url != org.logo_url:
        changes["logo_url"] = {"old": org.logo_url, "new": update_data.logo_url}
        org.logo_url = update_data.logo_url

    org.updated_at = datetime.utcnow()

    # Audit log (disabled for MVP)
    # if changes:
    #     await log_audit_event(
    #         db=db,
    #         org_id=org.id,
    #         actor_id=user_id,
    #         resource_type="organization",
    #         resource_id=org.id,
    #         action="updated",
    #         changes=json.dumps(changes),
    #     )

    await db.commit()
    await db.refresh(org)
    return org


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete organization")
async def delete_organization(
    org_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete organization (Owner only)."""
    # Check authorization
    member_stmt = select(UserOrganization).where(
        UserOrganization.user_id == user_id,
        UserOrganization.org_id == org_id,
        UserOrganization.role == RoleType.OWNER,
    )
    member = (await db.execute(member_stmt)).scalars().first()
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Owner can delete org")

    # Get org
    stmt = select(Organization).where(
        Organization.id == org_id,
        Organization.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    org = result.scalars().first()

    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # Soft delete
    org.deleted_at = datetime.utcnow()

    # Audit log (disabled for MVP)
    # await log_audit_event(
    #     db=db,
    #     org_id=org.id,
    #     actor_id=user_id,
    #     resource_type="organization",
    #     resource_id=org.id,
    #     action="deleted",
    #     changes=None,
    # )

    await db.commit()


# ============================================================================
# Member Management
# ============================================================================

@router.post(
    "/{org_id}/members",
    response_model=UserOrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invite member",
)
async def invite_member(
    org_id: uuid.UUID,
    member_data: UserOrganizationCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Invite user to organization (Owner/Admin only)."""
    # Check authorization
    auth_stmt = select(UserOrganization).where(
        UserOrganization.user_id == user_id,
        UserOrganization.org_id == org_id,
        UserOrganization.role.in_([RoleType.OWNER]),
    )
    auth_member = (await db.execute(auth_stmt)).scalars().first()
    if not auth_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Owner can invite members")

    # Find user by email
    user_stmt = select(User).where(User.email == member_data.email)
    target_user = (await db.execute(user_stmt)).scalars().first()

    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check if already member
    existing = await db.execute(
        select(UserOrganization).where(
            UserOrganization.user_id == target_user.id,
            UserOrganization.org_id == org_id,
        )
    )
    if existing.scalars().first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already member")

    # Add member
    user_org = UserOrganization(
        user_id=target_user.id,
        org_id=org_id,
        role=member_data.role,
    )
    db.add(user_org)

    # Audit log (disabled for MVP)
    # await log_audit_event(
    #     db=db,
    #     org_id=org_id,
    #     actor_id=user_id,
    #     resource_type="user",
    #     resource_id=target_user.id,
    #     action="invited",
    #     changes=json.dumps({"role": member_data.role.value}),
    # )

    # TODO: Send invite email with verification link

    await db.commit()
    await db.refresh(user_org)

    return {
        "user_id": user_org.user_id,
        "email": target_user.email,
        "role": user_org.role,
        "invited_at": user_org.invited_at,
        "joined_at": user_org.joined_at,
    }


@router.get("/{org_id}/members", response_model=List[UserOrganizationResponse], summary="List members")
async def list_members(
    org_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List organization members."""
    # Check user is member of org
    check_stmt = select(UserOrganization).where(
        UserOrganization.user_id == user_id,
        UserOrganization.org_id == org_id,
    )
    if not (await db.execute(check_stmt)).scalars().first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Get members with eager-loaded User relationship
    stmt = select(UserOrganization).where(
        UserOrganization.org_id == org_id,
    ).options(selectinload(UserOrganization.user))
    result = await db.execute(stmt)
    members = result.scalars().all()

    # Convert to response schema with email from related user
    return [
        {
            "user_id": m.user_id,
            "email": m.user.email,
            "role": m.role,
            "invited_at": m.invited_at,
            "joined_at": m.joined_at,
        }
        for m in members
    ]


@router.patch(
    "/{org_id}/members/{target_user_id}",
    response_model=UserOrganizationResponse,
    summary="Update member role",
)
async def update_member_role(
    org_id: uuid.UUID,
    target_user_id: uuid.UUID,
    update_data: UserOrganizationUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update member role (Owner only)."""
    # Check authorization
    auth_stmt = select(UserOrganization).where(
        UserOrganization.user_id == user_id,
        UserOrganization.org_id == org_id,
        UserOrganization.role == RoleType.OWNER,
    )
    if not (await db.execute(auth_stmt)).scalars().first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Owner can update roles")

    # Get member with eager-loaded user
    member_stmt = select(UserOrganization).where(
        UserOrganization.org_id == org_id,
        UserOrganization.user_id == target_user_id,
    ).options(selectinload(UserOrganization.user))
    member = (await db.execute(member_stmt)).scalars().first()

    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    # Update role
    old_role = member.role
    member.role = update_data.role
    member.updated_at = datetime.utcnow()

    # Audit log (disabled for MVP)
    # await log_audit_event(
    #     db=db,
    #     org_id=org_id,
    #     actor_id=user_id,
    #     resource_type="user",
    #     resource_id=target_user_id,
    #     action="role_updated",
    #     changes=json.dumps({"old": old_role.value, "new": update_data.role.value}),
    # )

    await db.commit()
    await db.refresh(member)

    return {
        "user_id": member.user_id,
        "email": member.user.email,
        "role": member.role,
        "invited_at": member.invited_at,
        "joined_at": member.joined_at,
    }


@router.delete("/{org_id}/members/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove member")
async def remove_member(
    org_id: uuid.UUID,
    target_user_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Remove member from organization (Owner only)."""
    # Check authorization
    auth_stmt = select(UserOrganization).where(
        UserOrganization.user_id == user_id,
        UserOrganization.org_id == org_id,
        UserOrganization.role == RoleType.OWNER,
    )
    if not (await db.execute(auth_stmt)).scalars().first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Owner can remove members")

    # Get member
    member_stmt = select(UserOrganization).where(
        UserOrganization.org_id == org_id,
        UserOrganization.user_id == target_user_id,
    )
    member = (await db.execute(member_stmt)).scalars().first()

    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    # Prevent removing last Owner
    if member.role == RoleType.OWNER:
        other_owners = await db.execute(
            select(UserOrganization).where(
                UserOrganization.org_id == org_id,
                UserOrganization.role == RoleType.OWNER,
                UserOrganization.user_id != target_user_id,
            )
        )
        if not other_owners.scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove last Owner")

    # Remove member
    await db.delete(member)

    # Audit log (disabled for MVP)
    # await log_audit_event(
    #     db=db,
    #     org_id=org_id,
    #     actor_id=user_id,
    #     resource_type="user",
    #     resource_id=target_user_id,
    #     action="removed",
    #     changes=None,
    # )

    await db.commit()


# ============================================================================
# Workspaces
# ============================================================================

@router.post(
    "/{org_id}/workspaces",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create workspace",
)
async def create_workspace(
    org_id: uuid.UUID,
    ws_data: WorkspaceCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Create workspace (repo) in organization."""
    # Check user is member of org
    member_stmt = select(UserOrganization).where(
        UserOrganization.user_id == user_id,
        UserOrganization.org_id == org_id,
    )
    if not (await db.execute(member_stmt)).scalars().first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Get org tier + count existing workspaces
    org_stmt = select(Organization).where(Organization.id == org_id)
    org = (await db.execute(org_stmt)).scalars().first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # Check quota
    ws_count = (await db.execute(
        select(Workspace).where(
            Workspace.org_id == org_id,
            Workspace.deleted_at.is_(None),
        )
    )).scalars().all()

    quota_limits = {
        TierType.STARTER: 1,
        TierType.PROFESSIONAL: 10,
        TierType.ENTERPRISE: 999999,
    }
    limit = quota_limits.get(org.tier, 1)
    if len(ws_count) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Workspace quota exceeded for {org.tier} tier",
        )

    # Create workspace
    ws = Workspace(
        org_id=org_id,
        name=ws_data.name,
        description=ws_data.description,
        region=ws_data.region or "us-east-1",
        github_repo_url=ws_data.github_repo_url,
    )
    db.add(ws)

    # Audit log (disabled for MVP)
    # await log_audit_event(
    #     db=db,
    #     org_id=org_id,
    #     actor_id=user_id,
    #     resource_type="workspace",
    #     resource_id=ws.id,
    #     action="created",
    #     changes=json.dumps(ws_data.dict()),
    # )

    await db.commit()
    await db.refresh(ws)
    return ws


@router.get("/{org_id}/workspaces", response_model=List[WorkspaceResponse], summary="List workspaces")
async def list_workspaces(
    org_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List organization workspaces."""
    # Check user is member
    if not (await db.execute(
        select(UserOrganization).where(
            UserOrganization.user_id == user_id,
            UserOrganization.org_id == org_id,
        )
    )).scalars().first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Get workspaces
    stmt = select(Workspace).where(
        Workspace.org_id == org_id,
        Workspace.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalars().all()
