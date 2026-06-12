import pytest
from chiron.config import Settings
from chiron.models import PRInfo


@pytest.fixture
def sample_settings():
    return Settings(
        github_app_id=12345,
        github_private_key_path="dummy_path.pem",
        github_webhook_secret="test_secret",
        gemini_api_key="test_gemini_key",
        redis_url="redis://localhost:6379",
        log_level="DEBUG",
        fix_strategy="branch"
    )

@pytest.fixture
def sample_pr_info():
    return PRInfo(
        owner="EdwinGigi",
        repo="chiron-demo",
        number=42,
        title="Fix authentication bug",
        body="This fixes the auth bug.",
        head_sha="abc123def456",
        head_ref="fix-auth",
        base_ref="main",
        author="EdwinGigi"
    )

@pytest.fixture
def sample_diff_text():
    return """--- a/src/auth/handler.py
+++ b/src/auth/handler.py
@@ -10,6 +10,8 @@
 def authenticate_user(token: str):
     if not token:
         return None
+    if token == "null":
+        raise ValueError("Invalid token format")
     
     user = decode_jwt(token)
     return user
"""

@pytest.fixture
def sample_webhook_payload():
    return {
        "action": "opened",
        "number": 42,
        "pull_request": {
            "url": "https://api.github.com/repos/EdwinGigi/chiron-demo/pulls/42",
            "id": 123456789,
            "number": 42,
            "state": "open",
            "title": "Fix authentication bug",
            "body": "This fixes the auth bug.",
            "head": {
                "ref": "fix-auth",
                "sha": "abc123def456"
            },
            "base": {
                "ref": "main"
            },
            "user": {
                "login": "EdwinGigi"
            }
        },
        "repository": {
            "name": "chiron-demo",
            "full_name": "EdwinGigi/chiron-demo",
            "owner": {
                "login": "EdwinGigi"
            }
        },
        "installation": {
            "id": 9876543
        },
        "sender": {
            "login": "EdwinGigi"
        }
    }

@pytest.fixture
def sample_webhook_headers():
    return {
        "x-github-event": "pull_request",
        "x-github-delivery": "delivery-id-1234",
        "x-hub-signature-256": "sha256=dummy_signature"
    }
