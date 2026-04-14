"""ISO Audit Documentation publisher — PRJ0-48.

Creates/updates an ISO Audit Hub master page + 12 sub-pages in Confluence.
Uses ConfluenceClient.upsert_page (create-or-update) and find_page methods.
"""
from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

ISO_SUB_PAGES = [
    "Architecture & Design",
    "Deployment Architecture",
    "User Guide",
    "Security Controls",
    "Data Privacy & Protection",
    "Change Management",
    "Incident Management",
    "Business Continuity",
    "Risk Register",
    "Audit Trail & Logging",
    "Supplier Management",
    "Training & Competence",
]


def _sub_page_body(title: str) -> str:
    return f"""<h2>Purpose</h2>
<p>This page documents {title} controls and procedures for ISO audit compliance.</p>
<h2>Scope</h2>
<p>Applies to all ProjectZero Factory operations and products.</p>
<h2>Controls / Procedures</h2>
<p><em>Document specific controls, procedures, and references here.</em></p>
<h2>Evidence Links</h2>
<p><em>Link to supporting evidence, screenshots, or artefacts.</em></p>
<h2>Review History</h2>
<table>
<tbody>
<tr><th>Date</th><th>Reviewer</th><th>Changes</th><th>Status</th></tr>
<tr><td>-</td><td>-</td><td>Initial draft</td><td>Draft</td></tr>
</tbody>
</table>"""


def _master_page_body(sub_pages: list[dict]) -> str:
    rows = ""
    for sp in sub_pages:
        url = sp.get("url", "#")
        title = sp["title"]
        link = f'<a href="{url}">{title}</a>' if url and url != "#" else title
        rows += f"<tr><td>{link}</td><td>TBD</td><td>-</td><td>Draft</td></tr>"
    return f"""<h2>ISO Audit Compliance Hub</h2>
<p>Central documentation hub for ProjectZero Factory ISO audit compliance. All 12 control areas are linked below.</p>
<h2>Compliance Status</h2>
<table>
<tbody>
<tr><th>Control Area</th><th>Owner</th><th>Last Reviewed</th><th>Status</th></tr>
{rows}
</tbody>
</table>
<h2>How to Use</h2>
<p>Click each control area link to open the relevant documentation page. Update the page content, set the Owner, and change Status from Draft to In Review when ready for audit.</p>"""


def _page_url(page_id: str, base: str, space_key: str, title: str) -> str:
    """Build a Confluence page URL from page ID."""
    if not page_id:
        return ""
    # Strip /wiki suffix if present for URL building — Confluence Cloud URL pattern
    clean_base = base.rstrip("/")
    encoded_title = title.replace(" ", "+")
    return f"{clean_base}/wiki/spaces/{space_key}/pages/{page_id}"


async def publish_iso_hub(space_key: str = "PR", parent_title: str = "") -> dict:
    """Create or update ISO Audit Hub master page + 12 sub-pages in Confluence."""
    from app.services.confluence_client import ConfluenceClient

    client = ConfluenceClient()
    # Override space key if provided
    if space_key:
        client.space_key = space_key

    master_title = "ISO Audit Hub — ProjectZero"

    # Resolve parent page ID
    parent_id: str | None = None
    if parent_title:
        parent_page = await client.find_page(parent_title, space_key=space_key)
        if parent_page:
            parent_id = parent_page["id"]

    # Create master page first (sub-pages will be children of master)
    # Use placeholder body — will update after sub-pages are created
    placeholder_body = "<p>ISO Audit Hub — being initialised by ProjectZero Factory.</p>"
    master_id = await client.upsert_page(
        title=master_title,
        body=placeholder_body,
        parent_id=parent_id,
    )

    # Create sub-pages as children of master
    sub_pages: list[dict] = []
    for sp_title in ISO_SUB_PAGES:
        full_title = f"{master_title} — {sp_title}"
        try:
            sp_id = await client.upsert_page(
                title=full_title,
                body=_sub_page_body(sp_title),
                parent_id=master_id,
            )
            url = _page_url(sp_id or "", client.base, client.space_key, full_title) if sp_id else ""
            sub_pages.append({"title": sp_title, "url": url, "id": sp_id or ""})
            logger.info("Upserted sub-page: %s (id=%s)", sp_title, sp_id)
        except Exception as exc:
            logger.warning("Sub-page failed %s: %s", sp_title, exc)
            sub_pages.append({"title": sp_title, "url": "", "id": ""})

    # Update master page with real sub-page links
    if master_id:
        try:
            existing = await client.find_page(master_title, space_key=space_key)
            if existing:
                version = existing.get("version", {}).get("number", 1)
                await client._update_page(
                    master_id,
                    master_title,
                    _master_page_body(sub_pages),
                    version,
                )
        except Exception as exc:
            logger.warning("Master page update failed: %s", exc)

    master_url = _page_url(master_id or "", client.base, client.space_key, master_title) if master_id else ""

    return {
        "master_url": master_url,
        "master_id": master_id or "",
        "sub_pages": sub_pages,
    }
