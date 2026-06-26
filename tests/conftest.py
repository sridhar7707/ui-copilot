"""
Pytest configuration and shared fixtures.
Plain factory functions stay in fixtures.py; this file wraps them as
injectable pytest fixtures so tests can declare them as parameters.
"""
from __future__ import annotations

import pytest

from tests.fixtures import bad_page as _bad_page
from tests.fixtures import clean_page as _clean_page


@pytest.fixture
def clean():
    """Near-perfect ParsedPage — should trigger zero issues."""
    return _clean_page()


@pytest.fixture
def bad():
    """Poorly designed ParsedPage — should trigger issues in every category."""
    return _bad_page()
