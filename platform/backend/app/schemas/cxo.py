"""Pydantic schemas for CXO dashboard — PRJ0-21."""

from __future__ import annotations
from typing import Any
from pydantic import BaseModel


class VelocityPoint(BaseModel):
    sprint: str | None
    committed: float
    completed: float
    end_date: str | None


class BurndownPoint(BaseModel):
    date: str
    remaining: float


class Burndown(BaseModel):
    sprint: str | None
    total: float
    series: list[BurndownPoint]


class AssigneeTickets(BaseModel):
    assignee: str
    todo: int
    in_progress: int


class CycleTimePoint(BaseModel):
    key: str
    days: float


class IssueTypeCount(BaseModel):
    type: str
    count: int


class ThroughputPoint(BaseModel):
    date: str
    done: int


class ProjectSummary(BaseModel):
    key: str
    total: int
    done: int
    in_progress: int
    todo: int
    completion_pct: float


class ProjectMetrics(BaseModel):
    summary: ProjectSummary
    velocity: list[VelocityPoint]
    burndown: Burndown
    assignees: list[AssigneeTickets]
    cycle_time: list[CycleTimePoint]
    issue_types: list[IssueTypeCount]
    throughput: list[ThroughputPoint]
    cached: bool = False


class Portfolio(BaseModel):
    projects: list[ProjectSummary]
