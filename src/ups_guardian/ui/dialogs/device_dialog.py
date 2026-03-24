"""Device add/edit dialog."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from ups_guardian.core.models import Device
from ups_guardian.core.validators import generate_ups_name, is_valid_ups_name
from ups_guardian.services.oid_profiles import OIDProfileManager
from ups_guardian.utils.paths import bundled_profiles_dir


class DeviceDialog(QDialog):
    """Input form for UPS inventory entries."""

    def __init__(self, parent=None, device: Device | None = None):
        super().__init__(parent)
        self.setWindowTitle("UPS Device")
        self.resize(560, 520)

        self.name_edit = QLineEdit()
        self.station_edit = QLineEdit()
        self.location_edit = QLineEdit()
        self.vendor_edit = QLineEdit("Generic")
        self.model_edit = QLineEdit("UPS")
        self.capacity_edit = QLineEdit("3KVA")
        self.ip_edit = QLineEdit()
        self.snmp_version = QComboBox()
        self.snmp_version.addItems(["v2c", "v3"])
        self.snmp_port = QSpinBox()
        self.snmp_port.setRange(1, 65535)
        self.snmp_port.setValue(161)
        self.community_edit = QLineEdit("public")
        self.auth_protocol_edit = QLineEdit()
        self.priv_protocol_edit = QLineEdit()
        self.web_url_edit = QLineEdit()
        self.serial_edit = QLineEdit()
        self.install_edit = QLineEdit()
        self.profile_combo = QComboBox()
        profiles = OIDProfileManager(str(bundled_profiles_dir())).list_profiles()
        self.profile_combo.addItems(profiles or ["generic_ups"])
        self.enabled_check = QCheckBox("Monitoring enabled")
        self.enabled_check.setChecked(True)
        self.notes_edit = QLineEdit()

        gen_row = QHBoxLayout()
        self.country_initial_edit = QLineEdit("U")
        self.country_initial_edit.setFixedWidth(40)
        self.sequence_edit = QSpinBox()
        self.sequence_edit.setRange(1, 999)
        self.sequence_edit.setValue(1)
        gen_btn = QPushButton("Generate")
        gen_btn.clicked.connect(self._generate_name)
        gen_row.addWidget(self.country_initial_edit)
        gen_row.addWidget(self.sequence_edit)
        gen_row.addWidget(gen_btn)

        form = QFormLayout()
        form.addRow("UPS Name", self.name_edit)
        form.addRow("Name helper", gen_row)
        form.addRow("Station", self.station_edit)
        form.addRow("Location code", self.location_edit)
        form.addRow("Vendor", self.vendor_edit)
        form.addRow("Model", self.model_edit)
        form.addRow("Capacity", self.capacity_edit)
        form.addRow("IP Address", self.ip_edit)
        form.addRow("SNMP Version", self.snmp_version)
        form.addRow("SNMP Port", self.snmp_port)
        form.addRow("Community/User", self.community_edit)
        form.addRow("Auth Protocol", self.auth_protocol_edit)
        form.addRow("Priv Protocol", self.priv_protocol_edit)
        form.addRow("Web URL", self.web_url_edit)
        form.addRow("Serial", self.serial_edit)
        form.addRow("Install date", self.install_edit)
        form.addRow("OID Profile", self.profile_combo)
        form.addRow("Notes", self.notes_edit)
        form.addRow("Monitoring", self.enabled_check)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        self.device_id = None
        self.current_status = "unknown"
        if device:
            self._load_device(device)

    def _generate_name(self) -> None:
        self.name_edit.setText(
            generate_ups_name(
                self.country_initial_edit.text()[:1],
                self.location_edit.text()[:3],
                self.capacity_edit.text(),
                self.sequence_edit.value(),
            )
        )

    def _load_device(self, d: Device) -> None:
        self.device_id = d.id
        self.current_status = d.current_status
        self.name_edit.setText(d.ups_name)
        self.station_edit.setText(d.station)
        self.location_edit.setText(d.location_code)
        self.vendor_edit.setText(d.vendor)
        self.model_edit.setText(d.model)
        self.capacity_edit.setText(d.capacity_kva)
        self.ip_edit.setText(d.ip_address)
        self.snmp_version.setCurrentText(d.snmp_version)
        self.snmp_port.setValue(d.snmp_port)
        self.community_edit.setText(d.community_or_username or "")
        self.auth_protocol_edit.setText(d.auth_protocol or "")
        self.priv_protocol_edit.setText(d.priv_protocol or "")
        self.web_url_edit.setText(d.web_url or "")
        self.serial_edit.setText(d.serial_number or "")
        self.install_edit.setText(d.install_date or "")
        self.profile_combo.setCurrentText(d.oid_profile_name)
        self.enabled_check.setChecked(d.monitoring_enabled)
        self.notes_edit.setText(d.notes or "")

    def to_device(self) -> Device:
        name = self.name_edit.text().strip().upper()
        if not is_valid_ups_name(name):
            raise ValueError("Invalid UPS name. Use format like UKYL-3KVA-001.")
        if not self.ip_edit.text().strip():
            raise ValueError("IP address is required.")
        return Device(
            id=self.device_id,
            ups_name=name,
            station=self.station_edit.text().strip(),
            location_code=self.location_edit.text().strip().upper(),
            vendor=self.vendor_edit.text().strip(),
            model=self.model_edit.text().strip(),
            capacity_kva=self.capacity_edit.text().strip().upper(),
            ip_address=self.ip_edit.text().strip(),
            snmp_version=self.snmp_version.currentText(),
            snmp_port=self.snmp_port.value(),
            community_or_username=self.community_edit.text().strip() or None,
            auth_protocol=self.auth_protocol_edit.text().strip() or None,
            priv_protocol=self.priv_protocol_edit.text().strip() or None,
            web_url=self.web_url_edit.text().strip() or None,
            serial_number=self.serial_edit.text().strip() or None,
            install_date=self.install_edit.text().strip() or None,
            monitoring_enabled=self.enabled_check.isChecked(),
            current_status=self.current_status,
            oid_profile_name=self.profile_combo.currentText(),
            notes=self.notes_edit.text().strip() or None,
        )
