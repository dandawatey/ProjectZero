"""Pydantic schemas for Organization API."""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid


class TierType(str, Enum):
    """Subscription tiers."""
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class RoleType(str, Enum):
    """User roles."""
    OWNER = "Owner"
    ENGINEER = "Engineer"
    REVIEWER = "Reviewer"


class OrganizationCreate(BaseModel):
    """POST /organizations request."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    region: str = Field("us-east-1", max_length=50)
    billing_contact_email: Optional[EmailStr] = None


class OrganizationUpdate(BaseModel):
    """PATCH /organizations/{org_id} request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    region: Optional[str] = Field(None, max_length=50)
    billing_contact_email: Optional[EmailStr] = None
    logo_url: Optional[str] = Field(None, max_length=500)


class OrganizationResponse(BaseModel):
    """Organization response."""
    id: uuid.UUID
    name: str
    description: Optional[str]
    tier: TierType
    region: str
    billing_contact_email: Optional[str]
    logo_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrganizationDetailResponse(OrganizationResponse):
    """Detailed org response with stats."""
    member_count: int = 0
    workspace_count: int = 0
    storage_gb: int = 0


class UserOrganizationCreate(BaseModel):
    """POST /organizations/{org_id}/members request."""
    email: EmailStr
    role: RoleType = RoleType.ENGINEER


class UserOrganizationResponse(BaseModel):
    """Member response."""
    user_id: uuid.UUID
    email: str
    role: RoleType
    invited_at: datetime
    joined_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserOrganizationUpdate(BaseModel):
    """PATCH /organizations/{org_id}/members/{user_id} request."""
    role: RoleType


class WorkspaceCreate(BaseModel):
    """POST /organizations/{org_id}/workspaces request."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    region: Optional[str] = Field("us-east-1", max_length=50)
    github_repo_url: Optional[str] = Field(None, max_length=500)


class WorkspaceResponse(BaseModel):
    """Workspace response."""
    id: uuid.UUID
    org_id: uuid.UUID
    name: str
    description: Optional[str]
    region: str
    github_repo_url: Optional[str]
    storage_gb: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    """Audit log entry."""
    id: int
    org_id: uuid.UUID
    actor_id: Optional[uuid.UUID]
    resource_type: str
    resource_id: uuid.UUID
    action: str
    changes: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class BillingSubscriptionResponse(BaseModel):
    """Subscription response."""
    id: uuid.UUID
    org_id: uuid.UUID
    tier: TierType
    status: str
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
