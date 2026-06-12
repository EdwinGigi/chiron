from typing import Literal, Optional
from pydantic import BaseModel, Field


class DiffHunkLine(BaseModel):
    line_number: Optional[int]
    content: str
    type: Literal["added", "removed", "context"]


class DiffHunk(BaseModel):
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    lines: list[DiffHunkLine]


class DiffFile(BaseModel):
    path: str
    old_path: Optional[str] = None
    status: Literal["added", "modified", "deleted", "renamed"]
    hunks: list[DiffHunk] = Field(default_factory=list)
    language: Optional[str] = None


class PRInfo(BaseModel):
    owner: str
    repo: str
    number: int
    title: str
    body: Optional[str]
    head_sha: str
    head_ref: str
    base_ref: str
    author: str


class ReviewComment(BaseModel):
    path: str
    line: int
    body: str
    severity: Literal["critical", "warning", "suggestion", "nitpick"]
    suggested_fix: Optional[str] = None


class ReviewResult(BaseModel):
    summary: str
    comments: list[ReviewComment] = Field(default_factory=list)
    overall_assessment: Literal["approve", "request_changes", "comment"]


class FixResult(BaseModel):
    success: bool
    patch: Optional[str] = None
    message: str
    attempts: int


class FailureReport(BaseModel):
    failure_type: Literal["test", "lint", "build", "type", "timeout", "flaky"]
    raw_logs: str
    parsed_failures: list[str] = Field(default_factory=list)


class Diagnosis(BaseModel):
    root_cause: str
    affected_files: list[str]
    confidence: float
    suggested_approach: str
    failure_type: Literal["test", "lint", "build", "type", "timeout", "flaky"]
