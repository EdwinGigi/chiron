from unidiff import PatchSet
from typing import List

from chiron.models import DiffFile, DiffHunk, DiffHunkLine


def parse_diff(diff_text: str) -> List[DiffFile]:
    """Parse a unified diff string into structured DiffFile objects."""
    if not diff_text.strip():
        return []
        
    try:
        patch_set = PatchSet(diff_text)
    except Exception as e:
        # Handle unidiff parsing errors gracefully
        return []
        
    files = []
    
    for patched_file in patch_set:
        status = "modified"
        if patched_file.is_added_file:
            status = "added"
        elif patched_file.is_removed_file:
            status = "deleted"
        elif patched_file.is_rename:
            status = "renamed"
            
        path = patched_file.path
        # Clean paths (unidiff sometimes leaves a/ or b/ prefixes depending on version/format)
        if path.startswith('b/'):
            path = path[2:]
            
        old_path = patched_file.source_file if status == "renamed" else None
        if old_path and old_path.startswith('a/'):
            old_path = old_path[2:]
            
        hunks = []
        for hunk in patched_file:
            lines = []
            for line in hunk:
                line_type = "context"
                if line.is_added:
                    line_type = "added"
                elif line.is_removed:
                    line_type = "removed"
                    
                lines.append(
                    DiffHunkLine(
                        line_number=line.target_line_no if line.is_added else (line.source_line_no if line.is_removed else line.target_line_no),
                        content=line.value,
                        type=line_type
                    )
                )
                
            hunks.append(
                DiffHunk(
                    old_start=hunk.source_start,
                    old_count=hunk.source_length,
                    new_start=hunk.target_start,
                    new_count=hunk.target_length,
                    lines=lines
                )
            )
            
        files.append(
            DiffFile(
                path=path,
                old_path=old_path,
                status=status,
                hunks=hunks
            )
        )
        
    return files
