from unittest.mock import AsyncMock, patch

import pytest

from chiron.ai.prompts.ci_diagnosis import CIDiagnosisResult
from chiron.models import ReviewComment
from chiron.remediation.ci_agent import process_failed_workflow


@pytest.fixture
def sample_workflow_payload():
    return {
        "action": "completed",
        "workflow_run": {
            "id": 12345,
            "head_branch": "test-branch",
            "head_sha": "abc123sha",
            "conclusion": "failure",
        },
        "repository": {"owner": {"login": "test-owner"}, "name": "test-repo"},
        "installation": {"id": 1},
    }


@pytest.mark.asyncio
@patch("chiron.remediation.ci_agent.GeminiClient")
@patch("chiron.remediation.ci_agent.process_remediation")
async def test_process_failed_workflow_with_fixes(
    mock_process_remediation, mock_gemini_client_class, sample_workflow_payload
):
    # Mock API
    mock_api = AsyncMock()
    mock_api._get.return_value = [
        {
            "number": 42,
            "title": "Test PR",
            "body": "Test body",
            "base": {"ref": "main"},
            "user": {"login": "test-user"},
        }
    ]
    mock_api.get_workflow_run_logs.return_value = "ERROR: file.py line 10 SyntaxError"

    # Mock Gemini
    mock_client = AsyncMock()
    mock_gemini_client_class.return_value = mock_client

    mock_client.generate_structured.return_value = CIDiagnosisResult(
        explanation="Syntax error found",
        diagnosed_comments=[
            ReviewComment(path="file.py", line=10, body="Fix syntax error", severity="critical")
        ],
    )

    await process_failed_workflow(mock_api, sample_workflow_payload)

    mock_api._get.assert_called_once()
    mock_api.get_workflow_run_logs.assert_called_once_with("test-owner", "test-repo", 12345)
    mock_client.generate_structured.assert_called_once()
    mock_process_remediation.assert_called_once()

    # Verify the created ReviewResult contains our comment
    args, _ = mock_process_remediation.call_args
    review_result = args[2]
    assert review_result.summary == "CI Failure Diagnosis: Syntax error found"
    assert len(review_result.comments) == 1
    assert review_result.comments[0].path == "file.py"


@pytest.mark.asyncio
@patch("chiron.remediation.ci_agent.GeminiClient")
@patch("chiron.remediation.ci_agent.process_remediation")
async def test_process_failed_workflow_no_fixes(
    mock_process_remediation, mock_gemini_client_class, sample_workflow_payload
):
    # Mock API
    mock_api = AsyncMock()
    mock_api._get.return_value = [
        {
            "number": 42,
            "title": "Test PR",
            "body": "Test body",
            "base": {"ref": "main"},
            "user": {"login": "test-user"},
        }
    ]
    mock_api.get_workflow_run_logs.return_value = "Network timeout"

    # Mock Gemini
    mock_client = AsyncMock()
    mock_gemini_client_class.return_value = mock_client

    mock_client.generate_structured.return_value = CIDiagnosisResult(
        explanation="Network timeout occurred", diagnosed_comments=[]
    )

    await process_failed_workflow(mock_api, sample_workflow_payload)

    mock_api.post_comment.assert_called_once()
    mock_process_remediation.assert_not_called()
