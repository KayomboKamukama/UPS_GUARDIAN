"""Diagnostics tools page (not in default sidebar for phase 1)."""

from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget

from ups_guardian.data.device_repository import DeviceRepository
from ups_guardian.services.polling import PollingEngine


class DiagnosticsPage(QWidget):
    """Simple diagnostics using mock poller for Phase 1."""

    def __init__(self, device_repo: DeviceRepository, poller: PollingEngine):
        super().__init__()
        self.device_repo = device_repo
        self.poller = poller

        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        top.addWidget(QLabel("Device"))
        self.device_combo = QComboBox()
        top.addWidget(self.device_combo)

        test_btn = QPushButton("Test Poll")
        test_btn.clicked.connect(self._test_poll)
        top.addWidget(test_btn)

        self.output = QTextEdit()
        self.output.setReadOnly(True)

        layout.addLayout(top)
        layout.addWidget(self.output)
        self._reload_devices()

    def _reload_devices(self) -> None:
        self.devices = self.device_repo.list_devices()
        self.device_combo.clear()
        for d in self.devices:
            self.device_combo.addItem(f"{d.ups_name} ({d.ip_address})", d)

    def _test_poll(self) -> None:
        self._reload_devices()
        idx = self.device_combo.currentIndex()
        if idx < 0:
            self.output.append("No device available")
            return
        device = self.device_combo.itemData(idx)
        result = self.poller.poll_one(device)
        self.output.append(
            f"[{device.ups_name}] comm={result.communication_status}, battery={result.battery_capacity}%, load={result.load_percentage}%"
        )
