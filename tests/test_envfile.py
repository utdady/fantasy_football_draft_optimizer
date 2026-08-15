"""Tests for local .env loader (no secrets)."""

from __future__ import annotations

import os

from draftopt.envfile import load_dotenv


def test_load_dotenv_sets_missing_only(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("FANTASYPROS_API_KEY=from_file\nOTHER=1\n", encoding="utf-8")
    monkeypatch.delenv("FANTASYPROS_API_KEY", raising=False)
    monkeypatch.setenv("OTHER", "already")
    assert load_dotenv(env) == env
    assert os.environ["FANTASYPROS_API_KEY"] == "from_file"
    assert os.environ["OTHER"] == "already"


def test_load_dotenv_missing(tmp_path):
    assert load_dotenv(tmp_path / "nope.env") is None
