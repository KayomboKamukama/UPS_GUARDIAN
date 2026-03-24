"""Configuration loading helpers."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ups_guardian.utils.paths import user_data_dir


@dataclass(slots=True)
class AppConfig:
    """Main application settings."""

    database_path: str = str(user_data_dir() / "ups_guardian.db")
    log_path: str = str(user_data_dir() / "logs" / "ups_guardian.log")
    export_folder: str = str(user_data_dir() / "exports")
    poll_interval_sec: int = 30
    poll_timeout_sec: int = 3
    retry_count: int = 2
    runtime_threshold_min: int = 20
    temperature_threshold_c: float = 25.0
    load_threshold_percent: float = 50.0
    capacity_threshold_percent: float = 50.0
    startup_behavior: str = "normal"
    theme: str = "light"
    default_profile: str = "generic_ups"

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "AppConfig":
        return cls(**{k: v for k, v in payload.items() if k in cls.__dataclass_fields__})

    def to_mapping(self) -> dict[str, Any]:
        return asdict(self)


def load_config(path: str | Path) -> AppConfig:
    """Load JSON settings into AppConfig, returning defaults on missing file."""
    path_obj = Path(path)
    if not path_obj.exists():
        cfg = AppConfig()
        save_config(path_obj, cfg)
        return cfg
    with path_obj.open("r", encoding="utf-8") as fh:
        data = json.load(fh) or {}
    return AppConfig.from_mapping(data)


def save_config(path: str | Path, config: AppConfig) -> None:
    """Persist configuration to JSON file."""
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    path_obj.write_text(json.dumps(config.to_mapping(), indent=2), encoding="utf-8")
