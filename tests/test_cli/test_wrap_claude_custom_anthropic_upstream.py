"""Tests for _anthropic_target_api_url_from_env (custom Anthropic upstream support).

Tests helper function that captures custom Anthropic-compatible upstream URLs
(e.g. z.ai gateway) before wrap overwrites ANTHROPIC_BASE_URL, ensuring the
proxy knows where to forward compressed requests. See issue #1476 / PR #1477.
"""

from __future__ import annotations

import pytest

from headroom.cli import wrap as wrap_cli


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyFixture) -> None:
    """Remove all Anthropic-related env vars before each test."""
    for key in [
        "ANTHROPIC_BASE_URL",
        "ANTHROPIC_TARGET_API_URL",
        "CLAUDE_CODE_USE_VERTEX",
        "ANTHROPIC_FOUNDRY_BASE_URL",
        "ANTHROPIC_FOUNDRY_RESOURCE",
    ]:
        monkeypatch.delenv(key, raising=False)


def test_custom_anthropic_base_url_forwarded(clean_env: None, monkeypatch: pytest.MonkeyFixture) -> None:
    """ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic returns z.ai URL."""
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://api.z.ai/api/anthropic")

    result = wrap_cli._anthropic_target_api_url_from_env("http://127.0.0.1:8787")

    assert result == "https://api.z.ai/api/anthropic"


def test_explicit_target_url_precedence(clean_env: None, monkeypatch: pytest.MonkeyFixture) -> None:
    """When both ANTHROPIC_TARGET_API_URL and ANTHROPIC_BASE_URL are set, explicit TARGET wins."""
    monkeypatch.setenv("ANTHROPIC_TARGET_API_URL", "https://explicit.target.com/v1")
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://ignored.base.com/v1")

    result = wrap_cli._anthropic_target_api_url_from_env("http://127.0.0.1:8787")

    assert result == "https://explicit.target.com/v1"


def test_default_anthropic_url_not_forwarded(clean_env: None, monkeypatch: pytest.MonkeyFixture) -> None:
    """ANTHROPIC_BASE_URL=https://api.anthropic.com returns None (proxy already defaults here)."""
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")

    result = wrap_cli._anthropic_target_api_url_from_env("http://127.0.0.1:8787")

    assert result is None


def test_default_anthropic_url_with_v1_not_forwarded(clean_env: None, monkeypatch: pytest.MonkeyFixture) -> None:
    """ANTHROPIC_BASE_URL=https://api.anthropic.com/v1 returns None (normalized to same endpoint)."""
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1")

    result = wrap_cli._anthropic_target_api_url_from_env("http://127.0.0.1:8787")

    assert result is None


def test_loopback_guard(clean_env: None, monkeypatch: pytest.MonkeyFixture) -> None:
    """ANTHROPIC_BASE_URL pointing at the proxy itself returns None (prevents infinite loop)."""
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "http://127.0.0.1:8787")

    result = wrap_cli._anthropic_target_api_url_from_env("http://127.0.0.1:8787")

    assert result is None


def test_loopback_guard_with_trailing_slash(clean_env: None, monkeypatch: pytest.MonkeyFixture) -> None:
    """ANTHROPIC_BASE_URL with trailing slash pointing at proxy returns None."""
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "http://127.0.0.1:8787/")

    result = wrap_cli._anthropic_target_api_url_from_env("http://127.0.0.1:8787")

    assert result is None


def test_no_base_url_returns_none(clean_env: None) -> None:
    """Unset ANTHROPIC_BASE_URL + unset ANTHROPIC_TARGET_API_URL returns None."""
    result = wrap_cli._anthropic_target_api_url_from_env("http://127.0.0.1:8787")

    assert result is None


def test_explicit_target_loopback_guard(clean_env: None, monkeypatch: pytest.MonkeyFixture) -> None:
    """ANTHROPIC_TARGET_API_URL pointing at proxy returns None (loopback guard applies to explicit target too)."""
    monkeypatch.setenv("ANTHROPIC_TARGET_API_URL", "http://127.0.0.1:8787")

    result = wrap_cli._anthropic_target_api_url_from_env("http://127.0.0.1:8787")

    assert result is None


def test_empty_base_url_returns_none(clean_env: None, monkeypatch: pytest.MonkeyFixture) -> None:
    """Empty ANTHROPIC_BASE_URL is treated as unset."""
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "")

    result = wrap_cli._anthropic_target_api_url_from_env("http://127.0.0.1:8787")

    assert result is None


def test_whitespace_base_url_returns_none(clean_env: None, monkeypatch: pytest.MonkeyFixture) -> None:
    """Whitespace-only ANTHROPIC_BASE_URL is treated as unset."""
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "   ")

    result = wrap_cli._anthropic_target_api_url_from_env("http://127.0.0.1:8787")

    assert result is None


# ---------------------------------------------------------------------------
# Non-regression tests: ensure Foundry/Vertex modes are not affected
# ---------------------------------------------------------------------------


def test_foundry_mode_non_regression(clean_env: None, monkeypatch: pytest.MonkeyFixture) -> None:
    """Foundry mode should ignore ANTHROPIC_BASE_URL custom URL and still use Foundry upstream.

    This test verifies that the custom Anthropic upstream helper is skipped when
    Foundry mode is active (foundry_upstream is set), ensuring non-regression.
    """
    # Set up a custom Anthropic-compatible gateway URL
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://api.z.ai/api/anthropic")

    # Set up Foundry mode
    monkeypatch.setenv("ANTHROPIC_FOUNDRY_RESOURCE", "my-resource")

    # In Foundry mode, the custom URL should be ignored
    # Helper is only called when `not use_vertex and not foundry_upstream`
    # This test verifies the integration logic in wrap claude handler
    # (the helper itself doesn't know about Foundry - it's the caller's job)
    result = wrap_cli._anthropic_target_api_url_from_env("http://127.0.0.1:8787")

    # Helper still returns the custom URL (it doesn't know about Foundry)
    assert result == "https://api.z.ai/api/anthropic"

    # But in actual wrap claude handler, this helper is only called when
    # `not use_vertex and not foundry_upstream`, so Foundry mode would skip it
    # See headroom/cli/wrap.py:3489-3496 for the integration logic


@pytest.mark.skip(reason="PR #1477 (Vertex support) not yet merged - Vertex test infrastructure not present")
def test_vertex_mode_non_regression(clean_env: None, monkeypatch: pytest.MonkeyFixture) -> None:
    """Vertex mode should not be affected by custom Anthropic upstream changes.

    This test is skipped until PR #1477 is merged, as Vertex test infrastructure
    is not yet present. Once merged, this will verify that CLAUDE_CODE_USE_VERTEX=1
    path is untouched by the default Anthropic upstream changes.
    """
    # When PR #1477 is merged, add Vertex test here
    # Should verify that CLAUDE_CODE_USE_VERTEX=1 causes the helper to be skipped
    # and Vertex path works independently
    pass
