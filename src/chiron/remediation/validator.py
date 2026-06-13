import ast
import os
import subprocess
import sys
import tempfile

import structlog

logger = structlog.get_logger("chiron.remediation.validator")


def validate_python_syntax(code: str) -> bool:
    """Check if the code has valid Python syntax."""
    try:
        ast.parse(code)
        return True
    except SyntaxError as e:
        logger.warning("Syntax validation failed", error=str(e))
        return False


def validate_with_ruff(code: str) -> bool:
    """Run ruff check on the code."""
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as f:
        f.write(code)
        temp_path = f.name

    try:
        # Run ruff check
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", temp_path], capture_output=True, text=True
        )
        if result.returncode != 0:
            logger.warning("Ruff validation failed", output=result.stdout)
            return False
        return True
    except Exception as e:
        logger.error("Failed to run ruff", error=str(e))
        return False
    finally:
        os.unlink(temp_path)


def validate_patch(new_content: str, filename: str) -> bool:
    """Run all pre-commit validations for a file."""
    if filename.endswith(".py"):
        if not validate_python_syntax(new_content):
            return False
        if not validate_with_ruff(new_content):
            return False

    # For non-python files, or if all checks passed
    return True
