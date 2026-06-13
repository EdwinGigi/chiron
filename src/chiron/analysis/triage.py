import structlog

from chiron.ai.gemini import GeminiClient
from chiron.ai.prompts.review import get_review_prompt
from chiron.ai.prompts.triage import TriageResult, get_triage_prompt
from chiron.models import DiffFile, PRInfo, ReviewResult

logger = structlog.get_logger("chiron.analysis.triage")


async def triage_pr(pr_info: PRInfo, files: list[DiffFile]) -> TriageResult:
    """Quickly assess if a PR needs a full review."""
    logger.info("Triaging PR", pr_number=pr_info.number)
    file_paths = [f.path for f in files]

    prompt = get_triage_prompt(pr_info.title, pr_info.body or "", file_paths)
    client = GeminiClient()

    # Use flash model for fast triage
    result = await client.generate_structured(prompt, TriageResult, model="gemini-2.5-flash")
    logger.info("PR triaged", category=result.category, reasoning=result.reasoning)
    return result


async def analyze_pr_diff(pr_info: PRInfo, diff_text: str, files: list[DiffFile]) -> ReviewResult:
    """Analyze a PR diff using Gemini and return a structured review."""
    logger.info("Analyzing PR diff", pr_number=pr_info.number, files_count=len(files))

    pr_context = f"Title: {pr_info.title}\nDescription: {pr_info.body}\n"
    prompt = get_review_prompt(pr_context, diff_text)

    client = GeminiClient()
    # Use Pro model for deep code review
    review = await client.generate_structured(prompt, ReviewResult, model="gemini-2.5-flash")

    logger.info(
        "Generated review",
        assessment=review.overall_assessment,
        comments_count=len(review.comments),
    )
    return review
