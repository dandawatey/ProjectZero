"""
Tenant Isolation Module: RLS, tenant context, audit logging.

PRJ0-98: Tenant Isolation Framework
- Extract tenant_id from JWT claims
- Inject into request context (thread-local)
- Enforce RLS on all queries
- Log all data access to audit table
"""

import logging
import uuid
from datetime import datetime
from contextvars import ContextVar
from typing import Optional, Dict, Any
from dataclasses import dataclass

import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID


logger = logging.getLogger(__name__)


# ============================================================================
# TENANT CONTEXT: Thread-safe, request-scoped
# ============================================================================

_tenant_context: ContextVar[Optional['TenantContext']] = ContextVar('tenant_context', default=None)


@dataclass
class TenantContext:
    """Request-scoped tenant context extracted from JWT."""
    tenant_id: str
    user_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    @classmethod
    def from_jwt(cls, claims: Dict[str, Any], ip: str, user_agent: str) -> 'TenantContext':
        """Extract tenant context from JWT claims."""
        tenant_id = claims.get("tenant_id")
        user_id = claims.get("sub")

        if not tenant_id or not user_id:
            raise ValueError("JWT must contain 'tenant_id' and 'sub' claims")

        return cls(
            tenant_id=tenant_id,
            user_id=user_id,
            ip_address=ip,
            user_agent=user_agent,
        )

    @staticmethod
    def get() -> Optional['TenantContext']:
        """Get current tenant context (thread-safe, request-scoped)."""
        return _tenant_context.get()

    @staticmethod
    def set(context: 'TenantContext') -> None:
        """Set current tenant context."""
        _tenant_context.set(context)

    @staticmethod
    def clear() -> None:
        """Clear tenant context (call after request ends)."""
        _tenant_context.set(None)


# ============================================================================
# AUDIT LOG TABLE
# ============================================================================

class AuditLog:
    """Immutable audit log table (append-only, never truncate/delete)."""

    # SQL DDL for audit log table
    DDL = """
    CREATE TABLE IF NOT EXISTS audit_logs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        tenant_id VARCHAR(255) NOT NULL,
        user_id VARCHAR(255) NOT NULL,
        action VARCHAR(50) NOT NULL,  -- SELECT, INSERT, UPDATE, DELETE
        resource_type VARCHAR(255) NOT NULL,  -- table name
        resource_id VARCHAR(255),  -- row ID accessed (optional)
        timestamp TIMESTAMP DEFAULT NOW(),
        ip_address VARCHAR(45),  -- IPv4 or IPv6
        user_agent TEXT,
        reason TEXT,  -- optional: why accessed?
        hmac_signature VARCHAR(256) NOT NULL,  -- HMAC-SHA256 for integrity
        created_at TIMESTAMP DEFAULT NOW(),
        CONSTRAINT audit_logs_action_check CHECK (action IN ('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'TOKEN_REFRESH')),
        INDEX idx_audit_tenant_id (tenant_id),
        INDEX idx_audit_user_id (user_id),
        INDEX idx_audit_action (action),
        INDEX idx_audit_timestamp (timestamp)
    );

    -- RLS POLICY: User can only READ logs for their tenant
    CREATE POLICY audit_logs_rls_select ON audit_logs FOR SELECT
    USING (tenant_id = current_setting('app.current_tenant_id')::VARCHAR);

    -- RLS POLICY: RESTRICT DELETE (only super-admin via explicit grant)
    CREATE POLICY audit_logs_rls_delete ON audit_logs FOR DELETE
    USING (false);  -- Block all DELETEs by default

    -- RLS POLICY: RESTRICT TRUNCATE (not allowed for any role)
    ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY;
    ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
    REVOKE TRUNCATE ON audit_logs FROM public;
    """

    @staticmethod
    def create_entry(
        db: Session,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        """Create audit log entry."""
        context = TenantContext.get()
        if not context:
            logger.warning("No tenant context available for audit logging")
            return

        # Calculate HMAC signature (prove audit log wasn't tampered with)
        import hmac
        import hashlib
        signature_data = f"{context.tenant_id}|{context.user_id}|{action}|{resource_type}|{datetime.utcnow().isoformat()}"
        hmac_sig = hmac.new(
            key=b"audit-log-signing-key",  # TODO: Load from KMS
            msg=signature_data.encode(),
            digestmod=hashlib.sha256,
        ).hexdigest()

        # Build audit log entry
        entry = {
            "tenant_id": context.tenant_id,
            "user_id": context.user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "timestamp": datetime.utcnow(),
            "ip_address": context.ip_address,
            "user_agent": context.user_agent,
            "reason": reason,
            "hmac_signature": hmac_sig,
        }

        # Insert into audit_logs table
        # In production: use raw SQL insert to bypass ORM filters
        query = sa.text("""
            INSERT INTO audit_logs (tenant_id, user_id, action, resource_type, resource_id, timestamp, ip_address, user_agent, reason, hmac_signature)
            VALUES (:tenant_id, :user_id, :action, :resource_type, :resource_id, :timestamp, :ip_address, :user_agent, :reason, :hmac_signature)
        """)
        db.execute(query, entry)
        db.commit()

        logger.info(f"Audit log: {context.tenant_id} | {action} | {resource_type} | {context.user_id}")

    @staticmethod
    def verify_integrity(db: Session, log_id: str) -> bool:
        """Verify audit log entry hasn't been tampered with (HMAC check)."""
        query = sa.text("SELECT * FROM audit_logs WHERE id = :log_id")
        row = db.execute(query, {"log_id": log_id}).first()

        if not row:
            return False

        # Recalculate HMAC
        import hmac
        import hashlib
        signature_data = f"{row['tenant_id']}|{row['user_id']}|{row['action']}|{row['resource_type']}|{row['timestamp'].isoformat()}"
        calculated_hmac = hmac.new(
            key=b"audit-log-signing-key",
            msg=signature_data.encode(),
            digestmod=hashlib.sha256,
        ).hexdigest()

        return calculated_hmac == row['hmac_signature']


# ============================================================================
# RLS POLICY ENFORCEMENT
# ============================================================================

class RLSEnforcer:
    """Apply RLS policies to queries (tenant_id filtering)."""

    @staticmethod
    def apply_tenant_filter(query: sa.sql.Select) -> sa.sql.Select:
        """Filter query to include only rows matching current tenant."""
        context = TenantContext.get()
        if not context:
            raise PermissionError("No tenant context available; query blocked")

        # Assume all tables have tenant_id column
        # Add WHERE clause: tenant_id = current_tenant
        return query.where(sa.column("tenant_id") == context.tenant_id)

    @staticmethod
    def enforce_insert_tenant(table: sa.Table, values: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce INSERT can only set tenant_id to current tenant."""
        context = TenantContext.get()
        if not context:
            raise PermissionError("No tenant context available; INSERT blocked")

        # If tenant_id provided, must match current context
        if "tenant_id" in values and values["tenant_id"] != context.tenant_id:
            raise PermissionError(f"Cannot INSERT row for tenant {values['tenant_id']}; not authorized")

        # Set tenant_id to current context
        values["tenant_id"] = context.tenant_id
        return values


# ============================================================================
# MIDDLEWARE: Extract JWT → Inject Context
# ============================================================================

def tenant_context_middleware(request: Any, jwt_claims: Dict[str, Any]) -> None:
    """Middleware: extract tenant_id from JWT, set TenantContext."""
    try:
        ip = request.client.host if hasattr(request, 'client') else "0.0.0.0"
        user_agent = request.headers.get("user-agent", "") if hasattr(request, 'headers') else ""

        context = TenantContext.from_jwt(jwt_claims, ip, user_agent)
        TenantContext.set(context)

        logger.debug(f"Tenant context set: {context.tenant_id}")
    except ValueError as e:
        logger.error(f"Failed to set tenant context: {e}")
        raise


# ============================================================================
# HELPER: Query Builder with RLS
# ============================================================================

class TenantQuery:
    """Query builder that automatically applies RLS filters."""

    @staticmethod
    def select_with_rls(db: Session, table: sa.Table) -> sa.sql.Select:
        """Build SELECT query with tenant filtering applied."""
        context = TenantContext.get()
        if not context:
            raise PermissionError("No tenant context; query blocked")

        query = sa.select(table).where(table.c.tenant_id == context.tenant_id)

        # Log the SELECT
        AuditLog.create_entry(
            db=db,
            action="SELECT",
            resource_type=table.name,
            reason="Query via TenantQuery.select_with_rls()",
        )

        return query

    @staticmethod
    def insert_with_rls(db: Session, table: sa.Table, values: Dict[str, Any]) -> None:
        """Build INSERT query with tenant enforcement."""
        context = TenantContext.get()
        if not context:
            raise PermissionError("No tenant context; INSERT blocked")

        values = RLSEnforcer.enforce_insert_tenant(table, values)

        db.execute(sa.insert(table).values(**values))
        db.commit()

        # Log the INSERT
        AuditLog.create_entry(
            db=db,
            action="INSERT",
            resource_type=table.name,
            reason="Insert via TenantQuery.insert_with_rls()",
        )
