"""Devices inventory page with CRUD and CSV import/export."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ups_guardian.data.device_repository import DeviceRepository
from ups_guardian.ui.dialogs.device_dialog import DeviceDialog


class DevicesPage(QWidget):
    """Manage UPS inventory."""

    def __init__(self, device_repo: DeviceRepository, refresh_callback):
        super().__init__()
        self.device_repo = device_repo
        self.refresh_callback = refresh_callback

        layout = QVBoxLayout(self)

        filters = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search UPS name / IP / model")
        self.station_filter = QLineEdit()
        self.station_filter.setPlaceholderText("Filter station")
        self.vendor_filter = QLineEdit()
        self.vendor_filter.setPlaceholderText("Filter vendor")
        apply_btn = QPushButton("Apply Filters")
        apply_btn.clicked.connect(self.refresh)

        for w in [self.search_box, self.station_filter, self.vendor_filter, apply_btn]:
            filters.addWidget(w)

        actions = QHBoxLayout()
        add_btn = QPushButton("Add")
        edit_btn = QPushButton("Edit")
        del_btn = QPushButton("Delete")
        import_btn = QPushButton("Import CSV")
        export_btn = QPushButton("Export CSV")

        add_btn.clicked.connect(self._add)
        edit_btn.clicked.connect(self._edit)
        del_btn.clicked.connect(self._delete)
        import_btn.clicked.connect(self._import_csv)
        export_btn.clicked.connect(self._export_csv)

        for b in [add_btn, edit_btn, del_btn, import_btn, export_btn]:
            actions.addWidget(b)
        actions.addStretch(1)

        self.table = QTableWidget(0, 11)
        self.table.setHorizontalHeaderLabels(
            ["ID", "UPS Name", "Station", "Vendor", "Model", "Capacity", "IP", "SNMP", "Profile", "Status", "Enabled"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addLayout(filters)
        layout.addLayout(actions)
        layout.addWidget(self.table)
        self.refresh()

    def refresh(self) -> None:
        self.devices = self.device_repo.list_devices(
            search=self.search_box.text().strip(),
            station=self.station_filter.text().strip(),
            vendor=self.vendor_filter.text().strip(),
        )
        self.table.setRowCount(len(self.devices))
        for i, d in enumerate(self.devices):
            row = [
                str(d.id), d.ups_name, d.station, d.vendor, d.model, d.capacity_kva, d.ip_address,
                d.snmp_version, d.oid_profile_name, d.current_status, "Yes" if d.monitoring_enabled else "No",
            ]
            for c, value in enumerate(row):
                self.table.setItem(i, c, QTableWidgetItem(value))

    def _selected_device(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.devices[row]

    def _add(self) -> None:
        dialog = DeviceDialog(self)
        if dialog.exec():
            try:
                self.device_repo.add_device(dialog.to_device())
                self.refresh()
                self.refresh_callback()
            except Exception as exc:
                QMessageBox.warning(self, "Validation", str(exc))

    def _edit(self) -> None:
        device = self._selected_device()
        if not device:
            return
        dialog = DeviceDialog(self, device)
        if dialog.exec():
            try:
                self.device_repo.update_device(dialog.to_device())
                self.refresh()
                self.refresh_callback()
            except Exception as exc:
                QMessageBox.warning(self, "Validation", str(exc))

    def _delete(self) -> None:
        device = self._selected_device()
        if not device:
            return
        self.device_repo.delete_device(device.id or 0)
        self.refresh()
        self.refresh_callback()

    def _import_csv(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Import UPS inventory", filter="CSV Files (*.csv)")
        if not path:
            return
        try:
            count = self.device_repo.import_csv(path)
            QMessageBox.information(self, "Import", f"Imported {count} devices")
            self.refresh()
            self.refresh_callback()
        except Exception as exc:
            QMessageBox.warning(self, "Import error", str(exc))

    def _export_csv(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export UPS inventory", "ups_inventory.csv", "CSV Files (*.csv)")
        if not path:
            return
        self.device_repo.export_csv(path, self.devices)
        QMessageBox.information(self, "Export", f"Exported inventory to {path}")
