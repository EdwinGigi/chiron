from typing import Any


def format_commit_mutation(
    owner: str,
    repo: str,
    branch: str,
    expected_head_oid: str,
    file_changes: list[dict[str, Any]],
    message: str,
) -> tuple[str, dict[str, Any]]:
    """Format GraphQL mutation for createCommitOnBranch."""
    query = """
    mutation ($input: CreateCommitOnBranchInput!) {
      createCommitOnBranch(input: $input) {
        commit {
          url
          oid
        }
      }
    }
    """

    additions = []
    deletions = []

    for change in file_changes:
        if change.get("contents_base64"):
            additions.append({"path": change["path"], "contents": change["contents_base64"]})
        else:
            deletions.append({"path": change["path"]})

    variables: dict[str, Any] = {
        "input": {
            "branch": {"repositoryNameWithOwner": f"{owner}/{repo}", "branchName": branch},
            "message": {"headline": message},
            "fileChanges": {"additions": additions, "deletions": deletions},
            "expectedHeadOid": expected_head_oid,
        }
    }

    return query, variables
