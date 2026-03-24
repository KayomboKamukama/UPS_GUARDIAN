"""Filesystem path helpers for development and frozen builds."""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "UPS_Guardian"


def bundled_root() -> Path:
    """Return root for bundled resources (PyInstaller) or project root in dev."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path.cwd()


def user_data_dir() -> Path:
    """Return writable app data directory."""
    if os.name == "nt":
        base = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path.home() / ".local" / "share"
    path = base / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def user_config_path() -> Path:
    path = user_data_dir() / "app_config.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def bundled_config_schema_path() -> Path:
    return bundled_root() / "config" / "schema.sql"


def bundled_seed_csv_path() -> Path:
    return bundled_root() / "config" / "sample_devices.csv"


def bundled_profiles_dir() -> Path:
    return bundled_root() / "profiles"
