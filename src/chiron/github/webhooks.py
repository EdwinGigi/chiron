import hashlib
import hmac
from collections.abc import Awaitable, Callable
from typing import Any


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify the GitHub webhook signature using HMAC SHA-256."""
    if not signature or not signature.startswith("sha256="):
        return False

    expected_mac = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

    return hmac.compare_digest(f"sha256={expected_mac}", signature)


def parse_webhook_event(headers: dict[str, Any], payload: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    """Parse the GitHub webhook headers and payload."""
    event_type = headers.get("x-github-event", "")
    action = payload.get("action", "")
    return event_type, action, payload


class WebhookRouter:
    """Routes GitHub webhook events to handler functions."""

    def __init__(self) -> None:
        self._handlers: dict[str, Callable[[dict[str, Any]], Awaitable[Any]]] = {}

    def add_handler(self, event_type: str, action: str, handler: Callable[[dict[str, Any]], Awaitable[Any]]) -> None:
        """Register a handler for a specific event and action."""
        key = f"{event_type}:{action}" if action else event_type
        self._handlers[key] = handler

    def on(self, event_type: str, action: str = "") -> Callable[[Callable[[dict[str, Any]], Awaitable[Any]]], Callable[[dict[str, Any]], Awaitable[Any]]]:
        """Decorator to register a handler."""

        def decorator(func: Callable[[dict[str, Any]], Awaitable[Any]]) -> Callable[[dict[str, Any]], Awaitable[Any]]:
            self.add_handler(event_type, action, func)
            return func

        return decorator

    async def route(self, event_type: str, action: str, payload: dict[str, Any]) -> Any:
        """Route the event to the appropriate handler."""
        key = f"{event_type}:{action}" if action else event_type
        handler = self._handlers.get(key)

        # Fallback to general event handler if specific action handler not found
        if not handler and action:
            handler = self._handlers.get(event_type)

        if handler:
            return await handler(payload)
        return {"status": "ignored", "reason": f"no handler for {key}"}
