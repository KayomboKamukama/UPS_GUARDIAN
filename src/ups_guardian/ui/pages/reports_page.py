"""Basic reporting page for phase 1."""

from __future__ import annotations

from datetime import datetime

from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QMessageBox, QPushButton, QTextEdit, QVBoxLayout, QWidget

from ups_guardian.data.device_repository import DeviceRepository
from ups_guardian.data.telemetry_repository import TelemetryRepository


class ReportsPage(QWidget):
    """Generates local CSV exports for inventory, active alerts and status summary."""

    def __init__(self, device_repo: DeviceRepository, telemetry_repo: TelemetryRepository):
        super().__init__()
        self.device_repo = device_repo
        self.telemetry_repo = telemetry_repo

        layout = QVBoxLayout(self)
        actions = QHBoxLayout()
        inventory_btn = QPushButton("Export UPS Inventory CSV")
        inventory_btn.clicked.connect(self._export_inventory)
        alerts_btn = QPushButton("Export Active Alerts CSV")
        alerts_btn.clicked.connect(self._export_alerts)
        summary_btn = QPushButton("Export Latest Status CSV")
        summary_btn.clicked.connect(self._export_summary)

        for b in [inventory_btn, alerts_btn, summary_btn]:
            actions.addWidget(b)
        actions.addStretch(1)

        self.info = QTextEdit()
        self.info.setReadOnly(True)
        self.info.setPlainText("Phase 1 local reporting exports UPS inventory, active alerts, and latest device status.")

        layout.addLayout(actions)
        layout.addWidget(self.info)

    def _save_path(self, default_name: str) -> str:
        path, _ = QFileDialog.getSaveFileName(self, "Save report", default_name, "CSV Files (*.csv)")
        return path

    def _export_inventory(self) -> None:
        path = self._save_path("ups_inventory.csv")
        if not path:
            return
        self.device_repo.export_csv(path)
        self._notify(path)

    def _export_alerts(self) -> None:
        path = self._save_path("ups_active_alerts.csv")
        if not path:
            return
        rows = self.telemetry_repo.list_active_alerts()
        headers = ["id", "ups_name", "station", "alert_type", "severity", "message", "first_seen", "last_seen", "acknowledged"]
        self.telemetry_repo.export_rows_to_csv(path, headers, rows)
        self._notify(path)

    def _export_summary(self) -> None:
        path = self._save_path("ups_latest_status_summary.csv")
        if not path:
            return
        rows = []
        latest = self.telemetry_repo.recent_samples(limit=500)
        seen: set[int] = set()
        for sample in latest:
            if sample["device_id"] in seen:
                continue
            seen.add(sample["device_id"])
            rows.append(sample)
        headers = [
            "device_id", "ups_name", "station", "vendor", "ip_address", "sampled_at", "communication_status",
            "battery_capacity", "load_percentage", "temperature_c", "runtime_remaining_minutes",
        ]
        self.telemetry_repo.export_rows_to_csv(path, headers, rows)
        self._notify(path)

    def _notify(self, path: str) -> None:
        QMessageBox.information(self, "Report", f"CSV exported at {datetime.now().isoformat(timespec='seconds')}\n{path}")
