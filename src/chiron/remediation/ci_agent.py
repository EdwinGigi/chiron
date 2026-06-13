from typing import Any

import structlog

from chiron.ai.gemini import GeminiClient
from chiron.ai.prompts.ci_diagnosis import CIDiagnosisResult, get_ci_diagnosis_prompt
from chiron.github.api import GitHubAPI
from chiron.models import PRInfo, ReviewResult
from chiron.remediation.loop import process_remediation

logger = structlog.get_logger("chiron.remediation.ci_agent")


async def process_failed_workflow(api: GitHubAPI, payload: dict[str, Any]) -> None:
    """Diagnose a failed workflow and trigger remediation."""
    workflow_run = payload.get("workflow_run", {})
    run_id = workflow_run.get("id")
    head_branch = workflow_run.get("head_branch")
    head_sha = workflow_run.get("head_sha")
    repo = payload.get("repository", {})
    owner = repo.get("owner", {}).get("login")
    repo_name = repo.get("name")

    if not all([run_id, head_branch, head_sha, owner, repo_name]):
        logger.warning("Missing required workflow run data", run_id=run_id)
        return

    # Check if this branch has an open PR
    # For simplicity, we create a mock PRInfo. In reality, we'd query the PR via API
    # But since process_remediation takes a PRInfo, let's fetch the PR for this branch.
    prs = await api._get(f"/repos/{owner}/{repo_name}/pulls?state=open&head={owner}:{head_branch}")
    if not prs:
        logger.info(
            "No open PR found for failed workflow branch, skipping remediation", branch=head_branch
        )
        return

    pr_data = prs[0]
    pr_info = PRInfo(
        owner=owner,
        repo=repo_name,
        number=pr_data["number"],
        title=pr_data["title"],
        body=pr_data.get("body") or "",
        head_sha=head_sha,
        head_ref=head_branch,
        base_ref=pr_data["base"]["ref"],
        author=pr_data["user"]["login"],
    )

    logger.info("Fetching workflow logs", run_id=run_id)
    try:
        logs = await api.get_workflow_run_logs(owner, repo_name, run_id)
    except Exception as e:
        logger.error("Failed to fetch workflow logs", run_id=run_id, error=str(e))
        return

    # In a real scenario, we'd fetch recent commits. Here we use an empty string.
    recent_commits = ""

    logger.info("Diagnosing workflow failure with Gemini")
    prompt = get_ci_diagnosis_prompt(logs, recent_commits)
    client = GeminiClient()

    try:
        diagnosis = await client.generate_structured(
            prompt, CIDiagnosisResult, model="gemini-2.5-pro"
        )
    except Exception as e:
        logger.error("Failed to generate CI diagnosis", error=str(e))
        return

    if not diagnosis.diagnosed_comments:
        logger.info("No actionable code fixes found in workflow logs", run_id=run_id)
        # We could post the explanation as a general PR comment here
        await api.post_comment(
            owner, repo_name, pr_info.number, f"Chiron CI Diagnosis:\n{diagnosis.explanation}"
        )
        return

    logger.info(
        "Identified actionable fixes from CI logs", comments=len(diagnosis.diagnosed_comments)
    )

    # We map the diagnosis into a ReviewResult so we can feed it into our existing loop
    review_result = ReviewResult(
        summary=f"CI Failure Diagnosis: {diagnosis.explanation}",
        overall_assessment="request_changes",
        comments=diagnosis.diagnosed_comments,
    )

    # Trigger the remediation loop to fix the issues
    await process_remediation(api, pr_info, review_result)
