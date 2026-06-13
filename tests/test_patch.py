import pytest

from chiron.remediation.patch import PatchBlock, apply_patch


def test_apply_patch_success():
    original = "def foo():\n    return 1\n"
    blocks = [PatchBlock(search="    return 1\n", replace="    return 2\n")]
    result = apply_patch(original, blocks)
    assert result == "def foo():\n    return 2\n"


def test_apply_patch_not_found():
    original = "def foo():\n    return 1\n"
    blocks = [PatchBlock(search="return 3", replace="return 4")]
    with pytest.raises(ValueError, match="Could not find block"):
        apply_patch(original, blocks)


def test_apply_patch_multiple():
    original = "a = 1\nb = 2\nc = 3\n"
    blocks = [
        PatchBlock(search="a = 1\n", replace="a = 10\n"),
        PatchBlock(search="c = 3\n", replace="c = 30\n"),
    ]
    result = apply_patch(original, blocks)
    assert result == "a = 10\nb = 2\nc = 30\n"


def test_apply_patch_crlf_normalization():
    original = "def foo():\r\n    return 1\r\n"
    blocks = [PatchBlock(search="def foo():\n    return 1\n", replace="def bar():\n    return 2\n")]
    result = apply_patch(original, blocks)
    assert result == "def bar():\n    return 2\n"
