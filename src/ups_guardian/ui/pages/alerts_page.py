"""Alerts list and acknowledgement page."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QInputDialog,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ups_guardian.data.telemetry_repository import TelemetryRepository


class AlertsPage(QWidget):
    """Render current alerts with ack workflow and filters."""

    def __init__(self, telemetry_repo: TelemetryRepository):
        super().__init__()
        self.telemetry_repo = telemetry_repo

        layout = QVBoxLayout(self)
        toolbar = QHBoxLayout()
        self.severity_filter = QComboBox()
        self.severity_filter.addItems(["all", "critical", "warning", "info"])
        self.ack_filter = QComboBox()
        self.ack_filter.addItems(["all", "acknowledged", "unacknowledged"])
        self.device_filter = QLineEdit()
        self.device_filter.setPlaceholderText("Device filter")
        self.station_filter = QLineEdit()
        self.station_filter.setPlaceholderText("Station filter")

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        ack_btn = QPushButton("Acknowledge Selected")
        ack_btn.clicked.connect(self._ack_selected)

        for w in [self.severity_filter, self.ack_filter, self.device_filter, self.station_filter, refresh_btn, ack_btn]:
            toolbar.addWidget(w)
        toolbar.addStretch(1)

        self.table = QTableWidget(0, 10)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Device", "Station", "Type", "Severity", "Message", "First Seen", "Last Seen", "Ack", "Comment"]
        )

        layout.addLayout(toolbar)
        layout.addWidget(self.table)
        self.refresh()

    def refresh(self) -> None:
        rows = self.telemetry_repo.list_active_alerts()
        sev = self.severity_filter.currentText()
        ack = self.ack_filter.currentText()
        device_term = self.device_filter.text().strip().lower()
        station_term = self.station_filter.text().strip().lower()

        filtered = []
        for r in rows:
            if sev != "all" and r["severity"] != sev:
                continue
            if ack == "acknowledged" and not r["acknowledged"]:
                continue
            if ack == "unacknowledged" and r["acknowledged"]:
                continue
            if device_term and device_term not in r["ups_name"].lower():
                continue
            if station_term and station_term not in r["station"].lower():
                continue
            filtered.append(r)

        self.table.setRowCount(len(filtered))
        for i, r in enumerate(filtered):
            vals = [
                str(r["id"]), r["ups_name"], r["station"], r["alert_type"], r["severity"], r["message"],
                r["first_seen"], r["last_seen"], "Yes" if r["acknowledged"] else "No", r["comment"] or "",
            ]
            for c, v in enumerate(vals):
                self.table.setItem(i, c, QTableWidgetItem(str(v)))

    def _ack_selected(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            return
        alert_id = int(self.table.item(row, 0).text())
        operator, ok = QInputDialog.getText(self, "Acknowledge", "Operator name")
        if not ok or not operator:
            return
        comment, _ = QInputDialog.getText(self, "Acknowledge", "Comment")
        self.telemetry_repo.acknowledge_alert(alert_id, operator, comment)
        QMessageBox.information(self, "Alert", "Alert acknowledged")
        self.refresh()
