"""Polling engine for device telemetry collection."""

from __future__ import annotations

import logging
from datetime import datetime

from ups_guardian.core.models import Device, PollSample
from ups_guardian.data.device_repository import DeviceRepository
from ups_guardian.data.telemetry_repository import TelemetryRepository
from ups_guardian.services.alerts import AlertRulesEngine
from ups_guardian.services.mock_snmp import MockSNMPAdapter, MockSNMPResult

logger = logging.getLogger(__name__)


class PollingEngine:
    """Poll enabled UPS devices and store readings/alerts."""

    def __init__(
        self,
        device_repo: DeviceRepository,
        telemetry_repo: TelemetryRepository,
        snmp_adapter: MockSNMPAdapter,
        alert_engine: AlertRulesEngine,
    ):
        self.device_repo = device_repo
        self.telemetry_repo = telemetry_repo
        self.snmp_adapter = snmp_adapter
        self.alert_engine = alert_engine

    def poll_all(self) -> tuple[int, int]:
        devices = [d for d in self.device_repo.list_devices() if d.monitoring_enabled]
        alerts_count = 0
        for device in devices:
            result = self.poll_one(device)
            alerts = self.alert_engine.evaluate(device, result)
            for alert in alerts:
                self.telemetry_repo.upsert_alert(alert)
                self.telemetry_repo.add_event(device.id, "alert_triggered", f"{alert.severity}:{alert.message}")
            self.telemetry_repo.clear_absent_alerts(device.id or 0, {a.alert_type for a in alerts})
            alerts_count += len(alerts)
        logger.info("Polling cycle complete. devices=%s alerts=%s", len(devices), alerts_count)
        return len(devices), alerts_count

    def poll_one(self, device: Device) -> MockSNMPResult:
        result = self.snmp_adapter.poll_device(device)
        status = "unreachable" if result.communication_status == "unreachable" else self._derive_status(result)
        sample = PollSample(
            device_id=device.id or 0,
            sampled_at=datetime.now(),
            battery_status=result.battery_status,
            battery_capacity=result.battery_capacity,
            runtime_remaining_minutes=result.runtime_remaining_minutes,
            load_percentage=result.load_percentage,
            temperature_c=result.temperature_c,
            input_voltage=result.input_voltage,
            output_voltage=result.output_voltage,
            communication_status=status,
            on_battery=result.on_battery,
            overload=result.overload,
            battery_disconnected=result.battery_disconnected,
            replace_battery=result.replace_battery,
            general_alarm=result.general_alarm,
        )
        self.telemetry_repo.insert_sample(sample)
        self.telemetry_repo.add_event(device.id, "polling", f"Polling state: {status}")
        return result

    @staticmethod
    def _derive_status(result: MockSNMPResult) -> str:
        if result.overload or result.general_alarm or result.battery_disconnected:
            return "critical"
        if result.on_battery or result.replace_battery or result.load_percentage >= 50 or result.temperature_c >= 25:
            return "warning"
        return "normal"
