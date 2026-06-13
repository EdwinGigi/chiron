from pydantic import BaseModel

from chiron.models import ReviewComment


class CIDiagnosisResult(BaseModel):
    """Result of analyzing a failed CI workflow log."""

    explanation: str
    diagnosed_comments: list[ReviewComment]


def get_ci_diagnosis_prompt(log_content: str, recent_commits: str) -> str:
    """Generate the prompt to diagnose a CI failure."""
    return f"""You are an expert DevOps and Software Engineer analyzing a failed CI/CD pipeline.

A GitHub Actions workflow has failed. Your task is to diagnose the root cause of the failure from the provided logs and map it to specific files and line numbers if possible.

Recent Commits (to give context on what might have broken it):
{recent_commits}

Failed Workflow Logs:
```
{log_content[-10000:]}  # Truncated to last 10k characters for context window
```

Analyze the logs carefully.
Look for:
- Python Tracebacks
- Syntax Errors
- Linting Errors (Ruff, Flake8)
- Type Checking Errors (MyPy)
- Test Failures (Pytest)

Output a `CIDiagnosisResult` containing an explanation of the failure, and a list of `ReviewComment` objects.
For each comment, specify the EXACT file path and line number where the fix needs to be applied, and describe what the fix should be.
If the log does not clearly indicate a specific file/line (e.g., a network timeout or infrastructure failure), return an empty list of comments.
"""
