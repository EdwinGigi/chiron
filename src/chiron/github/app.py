import time
import jwt
import httpx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


class GitHubAppAuth:
    """Manages GitHub App authentication (JWT and Installation tokens)."""

    def __init__(self, app_id: int, private_key_path: str):
        self.app_id = app_id
        with open(private_key_path, "rb") as f:
            private_key_bytes = f.read()

        self.private_key = serialization.load_pem_private_key(
            private_key_bytes, password=None, backend=default_backend()
        )
        self._tokens: dict[int, dict] = {}

    def _generate_jwt(self) -> str:
        """Generate a short-lived JWT for App authentication."""
        now = int(time.time())
        payload = {
            "iat": now - 60,  # 60s in the past to allow for clock drift
            "exp": now + (10 * 60),  # 10 minutes maximum
            "iss": str(self.app_id),
        }
        return jwt.encode(payload, self.private_key, algorithm="RS256")

    async def get_installation_token(self, installation_id: int) -> str:
        """Get an installation token, using cache if available and valid."""
        cached = self._tokens.get(installation_id)
        if cached and cached["expires_at"] > time.time() + 60:
            return cached["token"]

        jwt_token = self._generate_jwt()
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.github.com/app/installations/{installation_id}/access_tokens",
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            
            # Simple expiry parsing - GitHub returns ISO format, we'll just cache for 50 mins
            self._tokens[installation_id] = {
                "token": data["token"],
                "expires_at": time.time() + (50 * 60)
            }
            return data["token"]
