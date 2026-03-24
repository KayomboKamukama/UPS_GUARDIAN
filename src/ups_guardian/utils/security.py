"""Lightweight local obfuscation utilities for sensitive fields.

Note: this is obfuscation, not strong encryption.
"""

from __future__ import annotations

import base64


def obfuscate(value: str | None) -> str | None:
    if not value:
        return value
    return base64.b64encode(value.encode("utf-8")).decode("ascii")


def deobfuscate(value: str | None) -> str | None:
    if not value:
        return value
    return base64.b64decode(value.encode("ascii")).decode("utf-8")
