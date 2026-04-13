"""Integration validation endpoints."""

from fastapi import APIRouter

from app.services.integration_service import validate_all, all_required_valid

router = APIRouter()


@router.get("/validate")
async def validate_integrations():
    """Validate all external integrations. Returns status per integration."""
    results = await validate_all()
    return {
        "integrations": [
            {"name": r.name, "status": r.status, "detail": r.detail, "required": r.required}
            for r in results
        ],
        "all_required_valid": all_required_valid(results),
        "total": len(results),
        "valid": sum(1 for r in results if r.status == "valid"),
        "failed": sum(1 for r in results if r.status != "valid" and r.required),
    }


@router.get("/validate/{integration_name}")
async def validate_single(integration_name: str):
    """Validate a single integration by name."""
    from app.services import integration_service

    validators = {
        "github": integration_service.validate_github,
        "jira": integration_service.validate_jira,
        "confluence": integration_service.validate_confluence,
        "temporal": integration_service.validate_temporal,
        "database": integration_service.validate_database,
        "redis": integration_service.validate_redis,
        "anthropic": integration_service.validate_anthropic,
    }
    validator = validators.get(integration_name.lower())
    if not validator:
        return {"error": f"Unknown integration: {integration_name}"}
    result = await validator()
    return {"name": result.name, "status": result.status, "detail": result.detail}
