import httpx
from typing import Any

from chiron.models import ReviewResult


class GitHubAPI:
    """Wrapper for GitHub REST and GraphQL APIs."""

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.base_url = "https://api.github.com"

    async def _get(self, endpoint: str, **kwargs) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}{endpoint}", headers=self.headers, **kwargs
            )
            response.raise_for_status()
            return response.json()

    async def _post(self, endpoint: str, json: dict, **kwargs) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}{endpoint}", headers=self.headers, json=json, **kwargs
            )
            response.raise_for_status()
            return response.json()

    async def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """Fetch the unified diff of a pull request."""
        headers = self.headers.copy()
        headers["Accept"] = "application/vnd.github.v3.diff"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}",
                headers=headers,
            )
            response.raise_for_status()
            return response.text

    async def get_pr_files(self, owner: str, repo: str, pr_number: int) -> list[dict]:
        """Fetch the list of files changed in a pull request."""
        return await self._get(f"/repos/{owner}/{repo}/pulls/{pr_number}/files")

    async def get_file_contents(self, owner: str, repo: str, path: str, ref: str) -> str:
        """Fetch the raw contents of a file at a specific commit ref."""
        headers = self.headers.copy()
        headers["Accept"] = "application/vnd.github.v3.raw"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/contents/{path}?ref={ref}",
                headers=headers,
            )
            response.raise_for_status()
            return response.text

    async def post_review(self, owner: str, repo: str, pr_number: int, review: ReviewResult) -> dict:
        """Post a batched review on a pull request."""
        from chiron.github.reviews import format_review_for_github
        
        payload = format_review_for_github(review)
        return await self._post(f"/repos/{owner}/{repo}/pulls/{pr_number}/reviews", json=payload)

    async def post_comment(self, owner: str, repo: str, issue_number: int, body: str) -> dict:
        """Post a general issue/PR comment."""
        return await self._post(f"/repos/{owner}/{repo}/issues/{issue_number}/comments", json={"body": body})

    async def push_commit(
        self, owner: str, repo: str, branch: str, expected_head_oid: str, file_changes: list[dict], message: str
    ) -> dict:
        """Push a commit using the GraphQL API."""
        from chiron.github.commits import format_commit_mutation
        
        query, variables = format_commit_mutation(owner, repo, branch, expected_head_oid, file_changes, message)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/graphql",
                headers=self.headers,
                json={"query": query, "variables": variables}
            )
            response.raise_for_status()
            return response.json()

    async def get_workflow_run_logs(self, owner: str, repo: str, run_id: int) -> str:
        """Fetch the raw logs of a workflow run."""
        # Note: This endpoint redirects to a signed URL to download a zip file,
        # which requires handling redirects and extracting the zip.
        # A simpler approach for the prototype might be to fetch job logs.
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/actions/runs/{run_id}/logs",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.text
