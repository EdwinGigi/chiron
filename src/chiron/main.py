from typing import Any

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from chiron.analysis.triage import analyze_pr_diff, triage_pr
from chiron.config import get_settings
from chiron.github.api import GitHubAPI
from chiron.github.app import GitHubAppAuth
from chiron.github.diff import parse_diff
from chiron.github.webhooks import WebhookRouter, parse_webhook_event, verify_signature
from chiron.models import PRInfo
from chiron.observability.health import get_health, record_review_completed
from chiron.observability.logger import configure_logging
from chiron.remediation.ci_agent import process_failed_workflow
from chiron.remediation.loop import process_remediation

settings = get_settings()
configure_logging(settings.log_level)
logger = structlog.get_logger("chiron.main")

app = FastAPI(
    title="Chiron", description="Autonomous CI/CD Code Review & Remediation Agent", version="0.1.0"
)

router: WebhookRouter = WebhookRouter()


@router.on("pull_request", "opened")
@router.on("pull_request", "synchronize")
async def handle_pull_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Handle new or updated pull requests."""
    pr_data = payload.get("pull_request", {})
    repo_data = payload.get("repository", {})
    owner = repo_data.get("owner", {}).get("login")
    repo = repo_data.get("name")
    installation_id = payload.get("installation", {}).get("id")

    if not all([pr_data, owner, repo, installation_id]):
        return {"status": "skipped", "reason": "Missing required payload data"}

    pr_info = PRInfo(
        owner=owner,
        repo=repo,
        number=pr_data.get("number"),
        title=pr_data.get("title", ""),
        body=pr_data.get("body"),
        head_sha=pr_data.get("head", {}).get("sha", ""),
        head_ref=pr_data.get("head", {}).get("ref", ""),
        base_ref=pr_data.get("base", {}).get("ref", ""),
        author=pr_data.get("user", {}).get("login", ""),
    )

    auth = GitHubAppAuth(settings.github_app_id, settings.github_private_key_path)
    token = await auth.get_installation_token(installation_id)
    api = GitHubAPI(token)

    diff_text = await api.get_pr_diff(owner, repo, pr_info.number)
    files = parse_diff(diff_text)

    if not files:
        return {"status": "skipped", "reason": "No files changed or unable to parse diff"}

    triage_result = await triage_pr(pr_info, files)

    if triage_result.category in ["docs_only", "trivial"]:
        logger.info("Skipping full review based on triage", category=triage_result.category)
        return {"status": "skipped", "reason": f"Triaged as {triage_result.category}"}

    review_result = await analyze_pr_diff(pr_info, diff_text, files)

    await api.post_review(owner, repo, pr_info.number, review_result)

    # Trigger Remediation Loop
    # We do this asynchronously/await it. In production, this might be sent
    # to a task queue (like arq) but for Phase 3 we'll await it directly.
    await process_remediation(api, pr_info, review_result)

    record_review_completed()

    return {"status": "reviewed", "comments_posted": len(review_result.comments)}


@router.on("workflow_run", action="completed")
async def handle_workflow_run_completed(payload: dict[str, Any]) -> dict[str, Any]:
    """Handle completed CI workflow runs."""
    if not settings.ci_monitoring:
        logger.info("CI monitoring is disabled")
        return {"status": "skipped", "reason": "ci_monitoring disabled"}

    workflow_run = payload.get("workflow_run", {})
    conclusion = workflow_run.get("conclusion")

    if conclusion != "failure":
        logger.info("Workflow completed without failure, skipping", conclusion=conclusion)
        return {"status": "skipped", "reason": f"conclusion is {conclusion}"}

    installation_id = payload.get("installation", {}).get("id")
    if not installation_id:
        return {"status": "error", "message": "No installation ID"}

    token = await auth.get_installation_token(installation_id)
    api = GitHubAPI(token)

    # Process the failed workflow
    await process_failed_workflow(api, payload)

    return {"status": "processed_workflow_failure"}


@app.post("/webhooks/github")
async def github_webhook(request: Request) -> JSONResponse:
    """Receive GitHub webhooks."""
    payload = await request.body()
    signature = request.headers.get("x-hub-signature-256", "")

    if not verify_signature(payload, signature, settings.github_webhook_secret):
        logger.warning("Invalid webhook signature", signature=signature)
        raise HTTPException(status_code=401, detail="Invalid signature")

    event_type, action, event_payload = parse_webhook_event(
        dict(request.headers), await request.json()
    )
    logger.info("Received webhook", event_type=event_type, action=action)

    try:
        result = await router.route(event_type, action, event_payload)
        return JSONResponse(content={"status": "processed", "result": result})
    except Exception as e:
        logger.exception("Error processing webhook", event_type=event_type, error=str(e))
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.get("/health")
async def health_check() -> Any:
    """Health check endpoint for Cloud Run."""
    return get_health()


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint info."""
    return {
        "name": "Chiron",
        "version": "0.1.0",
        "description": "Autonomous CI/CD Code Review & Remediation Agent",
    }


def main() -> None:
    """Run the application locally."""
    uvicorn.run("chiron.main:app", host="0.0.0.0", port=settings.port, reload=True)


if __name__ == "__main__":
    main()
