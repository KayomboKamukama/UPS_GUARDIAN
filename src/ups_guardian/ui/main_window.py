"""Main window and navigation."""

from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ups_guardian.core.config import AppConfig
from ups_guardian.data.device_repository import DeviceRepository
from ups_guardian.data.telemetry_repository import TelemetryRepository
from ups_guardian.services.polling import PollingEngine
from ups_guardian.ui.pages.about_page import AboutPage
from ups_guardian.ui.pages.alerts_page import AlertsPage
from ups_guardian.ui.pages.dashboard_page import DashboardPage
from ups_guardian.ui.pages.devices_page import DevicesPage
from ups_guardian.ui.pages.reports_page import ReportsPage
from ups_guardian.ui.pages.settings_page import SettingsPage


class MainWindow(QMainWindow):
    """Main desktop shell with sidebar navigation."""

    def __init__(
        self,
        config: AppConfig,
        device_repo: DeviceRepository,
        telemetry_repo: TelemetryRepository,
        poller: PollingEngine,
        config_path: str,
    ):
        super().__init__()
        self.setWindowTitle("UPS Guardian")
        self.resize(1360, 820)

        self.dashboard_page = DashboardPage(device_repo, telemetry_repo)
        self.devices_page = DevicesPage(device_repo, self.dashboard_page.refresh)
        self.alerts_page = AlertsPage(telemetry_repo)
        self.reports_page = ReportsPage(device_repo, telemetry_repo)
        self.settings_page = SettingsPage(config, config_path)
        self.about_page = AboutPage()

        self.stack = QStackedWidget()
        pages = [
            self.dashboard_page,
            self.devices_page,
            self.alerts_page,
            self.reports_page,
            self.settings_page,
            self.about_page,
        ]
        for page in pages:
            self.stack.addWidget(page)

        container = QWidget()
        root_layout = QVBoxLayout(container)

        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("UPS Guardian — UPS Monitoring for Multi-Station ICT Environments"))
        top_bar.addStretch(1)
        poll_btn = QPushButton("Poll Now")
        poll_btn.clicked.connect(self._poll_now)
        top_bar.addWidget(poll_btn)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.nav = QListWidget()
        for name in ["Dashboard", "Devices", "Alerts", "Reports", "Settings", "About"]:
            QListWidgetItem(name, self.nav)
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.setCurrentRow(0)

        splitter.addWidget(self.nav)
        splitter.addWidget(self.stack)
        splitter.setSizes([220, 1000])

        root_layout.addLayout(top_bar)
        root_layout.addWidget(splitter)
        self.setCentralWidget(container)

        self.poller = poller
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._poll_now)
        self.poll_timer.start(max(5, config.poll_interval_sec) * 1000)

    def _poll_now(self) -> None:
        devices, alerts = self.poller.poll_all()
        self.dashboard_page.refresh()
        self.alerts_page.refresh()
        if self.isActiveWindow():
            QMessageBox.information(self, "Polling Complete", f"Polled {devices} devices. Active alerts: {alerts}")
