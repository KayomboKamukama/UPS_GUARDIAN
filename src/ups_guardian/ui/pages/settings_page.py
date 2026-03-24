"""Settings page."""

from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget

from ups_guardian.core.config import AppConfig, save_config


class SettingsPage(QWidget):
    """Configurable phase-1 settings persisted to JSON."""

    def __init__(self, config: AppConfig, config_path: str):
        super().__init__()
        self.config = config
        self.config_path = config_path

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.poll_interval = QLineEdit(str(config.poll_interval_sec))
        self.poll_timeout = QLineEdit(str(config.poll_timeout_sec))
        self.export_folder = QLineEdit(config.export_folder)
        self.log_path = QLineEdit(config.log_path)
        self.runtime_threshold = QLineEdit(str(config.runtime_threshold_min))
        self.temp_threshold = QLineEdit(str(config.temperature_threshold_c))
        self.load_threshold = QLineEdit(str(config.load_threshold_percent))
        self.capacity_threshold = QLineEdit(str(config.capacity_threshold_percent))
        self.startup = QLineEdit(config.startup_behavior)
        self.theme = QLineEdit(config.theme)

        form.addRow("Polling interval (sec)", self.poll_interval)
        form.addRow("Poll timeout (sec)", self.poll_timeout)
        form.addRow("Export folder", self.export_folder)
        form.addRow("Log file", self.log_path)
        form.addRow("Runtime threshold (min)", self.runtime_threshold)
        form.addRow("Temperature threshold (°C)", self.temp_threshold)
        form.addRow("Load threshold (%)", self.load_threshold)
        form.addRow("Capacity threshold (%)", self.capacity_threshold)
        form.addRow("Startup behavior", self.startup)
        form.addRow("Theme", self.theme)

        save_btn = QPushButton("Save settings")
        save_btn.clicked.connect(self._save)

        layout.addLayout(form)
        layout.addWidget(save_btn)

    def _save(self) -> None:
        try:
            self.config.poll_interval_sec = max(5, int(self.poll_interval.text()))
            self.config.poll_timeout_sec = max(1, int(self.poll_timeout.text()))
            self.config.export_folder = self.export_folder.text().strip()
            self.config.log_path = self.log_path.text().strip()
            self.config.runtime_threshold_min = max(1, int(self.runtime_threshold.text()))
            self.config.temperature_threshold_c = float(self.temp_threshold.text())
            self.config.load_threshold_percent = float(self.load_threshold.text())
            self.config.capacity_threshold_percent = float(self.capacity_threshold.text())
            self.config.startup_behavior = self.startup.text().strip() or "normal"
            self.config.theme = self.theme.text().strip() or "light"
        except ValueError:
            QMessageBox.warning(self, "Settings", "Invalid numeric value in settings form.")
            return

        save_config(self.config_path, self.config)
        QMessageBox.information(self, "Settings", "Settings saved. Restart app to apply fully.")
