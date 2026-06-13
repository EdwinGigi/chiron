from typing import Literal

from pydantic import BaseModel


class TriageResult(BaseModel):
    category: Literal["docs_only", "trivial", "standard", "complex"]
    reasoning: str


def get_triage_prompt(pr_title: str, pr_body: str, changed_files: list[str]) -> str:
    """Generate the system prompt for PR triage."""
    files_list = "\n".join(changed_files)
    return f"""You are an AI code reviewer assessing a pull request to determine if it requires a
deep code review.
    
PR Title: {pr_title}
PR Body: {pr_body or "No description provided."}
Files Changed:
{files_list}

Classify this PR into one of the following categories:
- docs_only: Only documentation, markdown, text, or non-code configuration files changed.
- trivial: Very minor code changes (e.g., typos, simple renames, formatting).
- standard: Normal code changes that require review.
- complex: Large, risky, or architecturally significant changes.

Provide your feedback as a structured JSON object containing `category` and `reasoning`.
"""
