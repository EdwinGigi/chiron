import structlog
from pydantic import BaseModel

logger = structlog.get_logger("chiron.remediation.patch")


class PatchBlock(BaseModel):
    """A search/replace block for modifying code."""

    search: str
    replace: str


def apply_patch(original_content: str, blocks: list[PatchBlock]) -> str:
    """Apply a list of search/replace blocks to the original content."""
    content = original_content
    for block in blocks:
        # Normalize line endings to avoid \r\n vs \n mismatch issues
        search_normalized = block.search.replace("\r\n", "\n")
        content_normalized = content.replace("\r\n", "\n")

        if search_normalized not in content_normalized:
            logger.warning("Search block not found in content, skipping patch.")
            raise ValueError(f"Could not find block:\n{block.search}")

        content = content_normalized.replace(
            search_normalized, block.replace.replace("\r\n", "\n"), 1
        )
    return content
