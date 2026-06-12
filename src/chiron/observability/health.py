import time

from pydantic import BaseModel


class HealthStatus(BaseModel):
    status: str
    version: str
    uptime_seconds: float
    reviews_completed: int = 0
    fixes_applied: int = 0


_START_TIME = time.time()
_REVIEWS_COMPLETED = 0
_FIXES_APPLIED = 0


def get_health() -> HealthStatus:
    """Get the current health and metrics of the application."""
    return HealthStatus(
        status="healthy",
        version="0.1.0",
        uptime_seconds=time.time() - _START_TIME,
        reviews_completed=_REVIEWS_COMPLETED,
        fixes_applied=_FIXES_APPLIED,
    )


def record_review_completed():
    """Increment the completed reviews counter."""
    global _REVIEWS_COMPLETED
    _REVIEWS_COMPLETED += 1


def record_fix_applied():
    """Increment the applied fixes counter."""
    global _FIXES_APPLIED
    _FIXES_APPLIED += 1
