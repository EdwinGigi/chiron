import structlog
from pydantic import BaseModel

from chiron.ai.gemini import GeminiClient
from chiron.models import ReviewComment

logger = structlog.get_logger("chiron.remediation.fix_generator")


class GeneratedFix(BaseModel):
    """Structured response from Gemini containing a code fix."""

    explanation: str
    search: str
    replace: str


def get_fix_prompt(file_content: str, comments: list[ReviewComment]) -> str:
    """Generate the prompt for the LLM to create a fix."""
    comments_str = "\n".join([f"- Line {c.line} ({c.severity}): {c.body}" for c in comments])
    return f"""You are an autonomous AI code remediation agent.
    
The following file has been reviewed and needs to be fixed.

File Content:
```
{file_content}
```

Review Comments to Fix:
{comments_str}

Generate a fix for this file. Provide a precise `search` block containing the EXACT lines from 
the original file that need to be replaced, and a `replace` block containing the new code.
The `search` block must match the file content exactly, including whitespace and indentation.
Try to include enough context lines in your search block so it is unique.
Do not include markdown code block backticks in your search/replace strings.
"""


async def generate_fix_for_file(file_content: str, comments: list[ReviewComment]) -> GeneratedFix:
    """Generate a fix for a specific file based on review comments."""
    prompt = get_fix_prompt(file_content, comments)
    client = GeminiClient()

    # We use Pro for generating actual code
    return await client.generate_structured(prompt, GeneratedFix, model="gemini-2.5-pro")
