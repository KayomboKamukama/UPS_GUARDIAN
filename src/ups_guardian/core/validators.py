"""Validation and naming utilities."""

from __future__ import annotations

import re

NAME_PATTERN = re.compile(r"^[A-Z]{4}-\d+KVA-\d{3}$")


def validate_ups_name(name: str) -> tuple[bool, str]:
    """Validate UPS naming convention e.g. UKYL-3KVA-001."""
    cleaned = name.strip().upper()
    if not cleaned:
        return False, "UPS name is required."
    if not NAME_PATTERN.fullmatch(cleaned):
        return False, "Use format [Country+Location]-[Capacity]-[Seq], e.g. UKYL-3KVA-001"
    return True, "OK"


def is_valid_ups_name(name: str) -> bool:
    """Boolean compatibility helper for existing checks."""
    return validate_ups_name(name)[0]


def generate_ups_name(country_initial: str, location_code: str, capacity: str, sequence: int) -> str:
    """Generate UPS name by convention."""
    return f"{country_initial.upper()}{location_code.upper()}-{capacity.upper()}-{sequence:03d}"
