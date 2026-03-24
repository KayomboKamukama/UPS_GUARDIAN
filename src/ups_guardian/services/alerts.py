"""Alert evaluation rules engine."""

from __future__ import annotations

from datetime import datetime

from ups_guardian.core.models import Alert, Device
from ups_guardian.services.mock_snmp import MockSNMPResult


class AlertRulesEngine:
    """Evaluate telemetry values and emit rule-based alerts."""

    def __init__(
        self,
        temperature_threshold: float = 25.0,
        load_threshold: float = 50.0,
        capacity_threshold: float = 50.0,
        runtime_threshold: float = 20.0,
    ):
        self.temperature_threshold = temperature_threshold
        self.load_threshold = load_threshold
        self.capacity_threshold = capacity_threshold
        self.runtime_threshold = runtime_threshold

    def evaluate(self, device: Device, result: MockSNMPResult) -> list[Alert]:
        alerts: list[Alert] = []
        now = datetime.now()

        if result.communication_status == "unreachable":
            alerts.append(self._build(device.id, "communication_failure", "critical", "UPS unreachable", now))
            return alerts

        if result.battery_disconnected:
            alerts.append(self._build(device.id, "battery_disconnected", "critical", "Battery disconnected", now))
        if result.on_battery:
            alerts.append(self._build(device.id, "on_battery", "warning", "UPS running on battery", now))
        if result.overload:
            alerts.append(self._build(device.id, "overload", "critical", "UPS overload detected", now))
        if result.battery_capacity <= self.capacity_threshold:
            alerts.append(self._build(device.id, "low_battery_capacity", "warning", f"Battery at {result.battery_capacity}%", now))
        if result.temperature_c >= self.temperature_threshold:
            alerts.append(self._build(device.id, "high_temperature", "warning", f"Temperature at {result.temperature_c}°C", now))
        if result.load_percentage >= self.load_threshold:
            alerts.append(self._build(device.id, "high_load", "warning", f"Load at {result.load_percentage}%", now))
        if result.runtime_remaining_minutes < self.runtime_threshold:
            alerts.append(self._build(device.id, "low_runtime", "warning", f"Runtime at {result.runtime_remaining_minutes} min", now))
        if result.replace_battery:
            alerts.append(self._build(device.id, "replace_battery", "warning", "Battery replacement advised", now))
        if result.general_alarm:
            alerts.append(self._build(device.id, "general_alarm", "critical", "General alarm active", now))

        return alerts

    @staticmethod
    def _build(device_id: int | None, alert_type: str, severity: str, message: str, now: datetime) -> Alert:
        return Alert(
            device_id=device_id or 0,
            alert_type=alert_type,
            severity=severity,
            message=message,
            first_seen=now,
            last_seen=now,
        )
