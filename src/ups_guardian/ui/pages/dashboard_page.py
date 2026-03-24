"""Dashboard page."""

from __future__ import annotations

from collections import Counter

from PySide6.QtWidgets import QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from ups_guardian.data.device_repository import DeviceRepository
from ups_guardian.data.telemetry_repository import TelemetryRepository


STATUS_COLORS = {
    "normal": "#2e7d32",
    "warning": "#f9a825",
    "critical": "#c62828",
    "unreachable": "#757575",
}


class DashboardPage(QWidget):
    """UPS status overview and latest telemetry table."""

    def __init__(self, device_repo: DeviceRepository, telemetry_repo: TelemetryRepository):
        super().__init__()
        self.device_repo = device_repo
        self.telemetry_repo = telemetry_repo

        layout = QVBoxLayout(self)

        self.summary_labels = {key: QLabel() for key in ["total", "normal", "warning", "critical", "unreachable"]}
        summary = QHBoxLayout()
        for key, label in self.summary_labels.items():
            color = STATUS_COLORS.get(key, "#455a64")
            label.setStyleSheet(f"padding: 6px; border: 1px solid {color}; border-radius: 6px;")
            summary.addWidget(label)
        summary.addStretch(1)

        self.table = QTableWidget(0, 12)
        self.table.setHorizontalHeaderLabels(
            [
                "UPS Name",
                "Station",
                "Vendor",
                "IP",
                "Status",
                "Battery %",
                "Load %",
                "Temp °C",
                "Input V",
                "Output V",
                "Runtime",
                "Last Poll",
            ]
        )

        layout.addLayout(summary)
        layout.addWidget(self.table)
        self.refresh()

    def refresh(self) -> None:
        devices = self.device_repo.list_devices()
        samples = self.telemetry_repo.recent_samples(limit=500)
        latest_per_device: dict[int, dict] = {}
        for sample in samples:
            latest_per_device.setdefault(sample["device_id"], sample)

        status_count = Counter(d.current_status for d in devices)
        self.summary_labels["total"].setText(f"Total: {len(devices)}")
        self.summary_labels["normal"].setText(f"Normal: {status_count.get('normal', 0)}")
        self.summary_labels["warning"].setText(f"Warning: {status_count.get('warning', 0)}")
        self.summary_labels["critical"].setText(f"Critical: {status_count.get('critical', 0)}")
        self.summary_labels["unreachable"].setText(f"Unreachable: {status_count.get('unreachable', 0)}")

        self.table.setRowCount(len(devices))
        for idx, device in enumerate(devices):
            sample = latest_per_device.get(device.id or -1, {})
            status = sample.get("communication_status", device.current_status)
            values = [
                device.ups_name,
                device.station,
                device.vendor,
                device.ip_address,
                status,
                str(sample.get("battery_capacity", "-")),
                str(sample.get("load_percentage", "-")),
                str(sample.get("temperature_c", "-")),
                str(sample.get("input_voltage", "-")),
                str(sample.get("output_voltage", "-")),
                str(sample.get("runtime_remaining_minutes", "-")),
                sample.get("sampled_at", "-"),
            ]
            for col, value in enumerate(values):
                self.table.setItem(idx, col, QTableWidgetItem(value))
