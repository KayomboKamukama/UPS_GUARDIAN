"""OID profile loading and validation."""

from __future__ import annotations

import json
from pathlib import Path

REQUIRED_OID_KEYS = {
    "battery_status",
    "battery_capacity",
    "runtime_remaining",
    "load_percentage",
    "temperature",
    "input_voltage",
    "output_voltage",
    "alarm_state",
    "battery_disconnected",
    "on_battery",
    "overload",
}


class OIDProfileManager:
    """Loads JSON OID profile files from a directory."""

    def __init__(self, profile_dir: str):
        self.profile_dir = Path(profile_dir)

    def list_profiles(self) -> list[str]:
        return sorted([p.stem for p in self.profile_dir.glob("*.json")])

    def get_profile(self, name: str) -> dict:
        path = self.profile_dir / f"{name}.json"
        if not path.exists():
            raise FileNotFoundError(f"OID profile not found: {name}")
        profile = json.loads(path.read_text(encoding="utf-8"))
        self.validate_profile(profile)
        return profile

    def validate_profile(self, profile: dict) -> None:
        missing = REQUIRED_OID_KEYS - set((profile.get("oids") or {}).keys())
        if missing:
            raise ValueError(f"Profile {profile.get('profile_name', '<unknown>')} missing OID keys: {sorted(missing)}")
