"""Qt application bootstrap."""

from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication

from ups_guardian.core.config import AppConfig, load_config, save_config
from ups_guardian.core.logging_config import setup_logging
from ups_guardian.data.db import init_schema
from ups_guardian.data.device_repository import DeviceRepository
from ups_guardian.data.telemetry_repository import TelemetryRepository
from ups_guardian.services.alerts import AlertRulesEngine
from ups_guardian.services.mock_snmp import MockSNMPAdapter
from ups_guardian.services.polling import PollingEngine
from ups_guardian.ui.main_window import MainWindow
from ups_guardian.utils.paths import (
    bundled_config_schema_path,
    bundled_seed_csv_path,
    user_config_path,
)

logger = logging.getLogger(__name__)


def run_app() -> int:
    """Initialize dependencies and show main window."""
    cfg_path = user_config_path()
    config = load_config(cfg_path)
    _ensure_output_dirs(config)

    setup_logging(config.log_path)
    logger.info("UPS Guardian startup")
    init_schema(config.database_path, str(bundled_config_schema_path()))

    device_repo = DeviceRepository(config.database_path)
    telemetry_repo = TelemetryRepository(config.database_path)
    poller = PollingEngine(
        device_repo,
        telemetry_repo,
        MockSNMPAdapter(),
        AlertRulesEngine(
            temperature_threshold=config.temperature_threshold_c,
            load_threshold=config.load_threshold_percent,
            capacity_threshold=config.capacity_threshold_percent,
            runtime_threshold=config.runtime_threshold_min,
        ),
    )

    if not device_repo.list_devices() and bundled_seed_csv_path().exists():
        device_repo.import_csv(str(bundled_seed_csv_path()))

    app = QApplication(sys.argv)
    window = MainWindow(config, device_repo, telemetry_repo, poller, str(cfg_path))
    window.show()
    rc = app.exec()
    logger.info("UPS Guardian shutdown")
    return rc


def _ensure_output_dirs(config: AppConfig) -> None:
    """Ensure writable output folders exist and persist normalized config."""
    from pathlib import Path

    Path(config.log_path).parent.mkdir(parents=True, exist_ok=True)
    Path(config.export_folder).mkdir(parents=True, exist_ok=True)
    Path(config.database_path).parent.mkdir(parents=True, exist_ok=True)
    save_config(user_config_path(), config)
