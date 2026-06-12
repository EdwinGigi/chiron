from typing import Any
from chiron.models import ReviewResult

def format_review_for_github(review: ReviewResult) -> dict[str, Any]:
    """Convert ReviewResult model into GitHub API format."""
    comments = []
    
    for comment in review.comments:
        gh_comment: dict[str, Any] = {
            "path": comment.path,
            "line": comment.line,
            "body": f"**{comment.severity.upper()}**: {comment.body}"
        }
        if comment.suggested_fix:
            gh_comment["body"] += f"\n\n```suggestion\n{comment.suggested_fix}\n```"
        comments.append(gh_comment)
        
    event_map = {
        "approve": "APPROVE",
        "request_changes": "REQUEST_CHANGES",
        "comment": "COMMENT"
    }
    
    return {
        "body": review.summary,
        "event": event_map.get(review.overall_assessment, "COMMENT"),
        "comments": comments
    }
