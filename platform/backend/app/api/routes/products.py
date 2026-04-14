"""Products router — PRJ0-42.

Endpoints:
  POST /api/v1/products/bootstrap   — create isolated product git repo + DB record
  GET  /api/v1/products             — list all products
  GET  /api/v1/products/{id}        — get single product
"""

from __future__ import annotations

import uuid as _uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.product import Product
from app.services.product_bootstrap import bootstrap_product_repo

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class BootstrapRequest(BaseModel):
    product_name: str
    repo_path: str
    jira_project_key: str = ""
    github_url: str = ""
    confluence_url: str = ""


class ProductRead(BaseModel):
    id: str
    name: str
    repo_path: str
    jira_project_key: str | None
    github_url: str | None
    confluence_url: str | None
    created_at: str

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/bootstrap", status_code=201)
async def bootstrap(req: BootstrapRequest, db: AsyncSession = Depends(get_db)):
    """Create an isolated git repo for a new product and register it in the Brain."""
    # Check name uniqueness
    result = await db.execute(select(Product).where(Product.name == req.product_name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Product '{req.product_name}' already exists")

    try:
        scaffold = bootstrap_product_repo(req.product_name, req.repo_path, req.jira_project_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Bootstrap failed: {exc}")

    product = Product(
        name=req.product_name,
        repo_path=scaffold["repo_path"],
        jira_project_key=req.jira_project_key or None,
        github_url=req.github_url or None,
        confluence_url=req.confluence_url or None,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)

    return {
        "id": str(product.id),
        "name": product.name,
        "repo_path": product.repo_path,
        "jira_project_key": product.jira_project_key,
        "files_created": scaffold["files_created"],
    }


@router.get("", response_model=list[ProductRead])
async def list_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).order_by(Product.created_at.desc()))
    products = result.scalars().all()
    return [
        ProductRead(
            id=str(p.id),
            name=p.name,
            repo_path=p.repo_path,
            jira_project_key=p.jira_project_key,
            github_url=p.github_url,
            confluence_url=p.confluence_url,
            created_at=p.created_at.isoformat(),
        )
        for p in products
    ]


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: str, db: AsyncSession = Depends(get_db)):
    try:
        uid = _uuid.UUID(product_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid product ID")
    result = await db.execute(select(Product).where(Product.id == uid))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductRead(
        id=str(p.id),
        name=p.name,
        repo_path=p.repo_path,
        jira_project_key=p.jira_project_key,
        github_url=p.github_url,
        confluence_url=p.confluence_url,
        created_at=p.created_at.isoformat(),
    )
