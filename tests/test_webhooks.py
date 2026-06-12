import hashlib
import hmac

import pytest

from chiron.github.webhooks import WebhookRouter, parse_webhook_event, verify_signature


def test_verify_signature_valid(sample_settings):
    payload = b'{"hello": "world"}'
    secret = sample_settings.github_webhook_secret

    mac = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    signature = f"sha256={mac}"

    assert verify_signature(payload, signature, secret) is True


def test_verify_signature_invalid(sample_settings):
    payload = b'{"hello": "world"}'
    secret = sample_settings.github_webhook_secret

    signature = "sha256=invalid_hash"

    assert verify_signature(payload, signature, secret) is False


def test_verify_signature_missing(sample_settings):
    payload = b'{"hello": "world"}'
    assert verify_signature(payload, "", sample_settings.github_webhook_secret) is False
    assert verify_signature(payload, "dummy", sample_settings.github_webhook_secret) is False


def test_parse_webhook_event(sample_webhook_headers, sample_webhook_payload):
    event_type, action, payload = parse_webhook_event(
        sample_webhook_headers, sample_webhook_payload
    )

    assert event_type == "pull_request"
    assert action == "opened"
    assert payload["number"] == 42


@pytest.mark.asyncio
async def test_webhook_router_routes_correctly():
    router = WebhookRouter()

    called = []

    @router.on("pull_request", "opened")
    async def handle_pr_opened(payload):
        called.append("pr_opened")
        return {"status": "ok"}

    @router.on("pull_request")
    async def handle_pr_general(payload):
        called.append("pr_general")
        return {"status": "ok"}

    result1 = await router.route("pull_request", "opened", {})
    assert "pr_opened" in called
    assert result1["status"] == "ok"

    called.clear()

    result2 = await router.route("pull_request", "closed", {})
    assert "pr_general" in called
    assert result2["status"] == "ok"

    result3 = await router.route("issues", "opened", {})
    assert result3["status"] == "ignored"
