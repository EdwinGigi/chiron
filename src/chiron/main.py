from typing import Any

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from chiron.config import get_settings
from chiron.github.webhooks import WebhookRouter, parse_webhook_event, verify_signature
from chiron.observability.health import get_health
from chiron.observability.logger import configure_logging

settings = get_settings()
configure_logging(settings.log_level)
logger = structlog.get_logger("chiron.main")

app = FastAPI(
    title="Chiron", description="Autonomous CI/CD Code Review & Remediation Agent", version="0.1.0"
)

router: WebhookRouter = WebhookRouter()


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
