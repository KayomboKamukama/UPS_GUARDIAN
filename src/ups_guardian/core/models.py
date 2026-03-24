"""Domain models for UPS Guardian."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Device:
    """Represents a UPS device record."""

    id: Optional[int]
    ups_name: str
    station: str
    location_code: str
    vendor: str
    model: str
    capacity_kva: str
    ip_address: str
    snmp_version: str
    snmp_port: int
    community_or_username: Optional[str]
    auth_protocol: Optional[str]
    priv_protocol: Optional[str]
    web_url: Optional[str]
    serial_number: Optional[str]
    install_date: Optional[str]
    monitoring_enabled: bool
    current_status: str
    oid_profile_name: str
    notes: Optional[str]


@dataclass(slots=True)
class PollSample:
    """Represents a sampled UPS metrics row."""

    device_id: int
    sampled_at: datetime
    battery_status: str
    battery_capacity: float
    runtime_remaining_minutes: float
    load_percentage: float
    temperature_c: float
    input_voltage: float
    output_voltage: float
    communication_status: str
    on_battery: bool
    overload: bool
    battery_disconnected: bool
    replace_battery: bool
    general_alarm: bool


@dataclass(slots=True)
class Alert:
    """Represents an alert event for a device."""

    device_id: int
    alert_type: str
    severity: str
    message: str
    first_seen: datetime
    last_seen: datetime
    active: bool = True
    occurrences: int = 1
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    comment: Optional[str] = None
