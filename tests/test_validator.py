from chiron.remediation.validator import validate_patch, validate_python_syntax, validate_with_ruff


def test_validate_python_syntax_valid():
    code = "def foo():\n    return 1"
    assert validate_python_syntax(code) is True


def test_validate_python_syntax_invalid():
    code = "def foo():\nreturn 1  # IndentationError"
    assert validate_python_syntax(code) is False


def test_validate_with_ruff_valid():
    code = "import os\n\n\ndef foo():\n    return os.name\n"
    assert validate_with_ruff(code) is True


def test_validate_with_ruff_invalid():
    # unused import
    code = "import sys\n\ndef foo():\n    return 1\n"
    assert validate_with_ruff(code) is False


def test_validate_patch():
    # Valid python file
    valid_code = "def foo():\n    return 1\n"
    assert validate_patch(valid_code, "test.py") is True

    # Invalid python file
    invalid_code = "def foo():\nreturn 1\n"
    assert validate_patch(invalid_code, "test.py") is False

    # Non-python file (should always return true)
    assert validate_patch("some invalid python syntax", "test.txt") is True
