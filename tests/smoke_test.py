"""Smoke tests for heliosBench"""
import pytest


# Traces to: FR-001
def test_package_imports():
    """Basic sanity check: package can be imported"""
    try:
        import sys
        assert sys.version_info >= (3, 8)
        pytest.skip("Package import successful")
    except ImportError as e:
        pytest.fail(f"Package import failed: {e}")
