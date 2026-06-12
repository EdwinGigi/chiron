from unittest.mock import AsyncMock, patch

import pytest

from chiron.ai.prompts.triage import TriageResult
from chiron.analysis.triage import analyze_pr_diff, triage_pr
from chiron.models import DiffFile, PRInfo, ReviewResult


@pytest.fixture
def sample_pr_info():
    return PRInfo(
        owner="test-owner",
        repo="test-repo",
        number=1,
        title="Test PR",
        body="Test Body",
        head_sha="sha1",
        head_ref="branch1",
        base_ref="main",
        author="test-user",
    )


@pytest.fixture
def sample_files():
    return [DiffFile(path="test.py", old_path="test.py", status="modified", hunks=[])]


@pytest.mark.asyncio
@patch("chiron.analysis.triage.GeminiClient")
async def test_triage_pr(mock_gemini_client_class, sample_pr_info, sample_files):
    mock_client = AsyncMock()
    mock_gemini_client_class.return_value = mock_client

    mock_client.generate_structured.return_value = TriageResult(
        category="standard", reasoning="Has code changes"
    )

    result = await triage_pr(sample_pr_info, sample_files)

    assert result.category == "standard"
    mock_client.generate_structured.assert_called_once()


@pytest.mark.asyncio
@patch("chiron.analysis.triage.GeminiClient")
async def test_analyze_pr_diff(mock_gemini_client_class, sample_pr_info, sample_files):
    mock_client = AsyncMock()
    mock_gemini_client_class.return_value = mock_client

    mock_client.generate_structured.return_value = ReviewResult(
        summary="Looks good", overall_assessment="approve", comments=[]
    )

    result = await analyze_pr_diff(sample_pr_info, "diff text", sample_files)

    assert result.overall_assessment == "approve"
    mock_client.generate_structured.assert_called_once()
