"""Device CRUD repository."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from ups_guardian.core.models import Device
from ups_guardian.data.db import get_conn


class DeviceRepository:
    """Persistence operations for devices."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def list_devices(self, search: str = "", station: str = "", vendor: str = "") -> list[Device]:
        where = ["1=1"]
        params: list[str] = []
        if search:
            where.append("(ups_name LIKE ? OR ip_address LIKE ? OR model LIKE ?)")
            like = f"%{search}%"
            params.extend([like, like, like])
        if station:
            where.append("station = ?")
            params.append(station)
        if vendor:
            where.append("vendor = ?")
            params.append(vendor)

        with get_conn(self.db_path) as conn:
            rows = conn.execute(
                f"SELECT * FROM devices WHERE {' AND '.join(where)} ORDER BY ups_name",
                params,
            ).fetchall()
        return [self._row_to_device(r) for r in rows]

    def add_device(self, device: Device) -> int:
        self._ensure_unique(device)
        fields = self._device_fields(device)
        columns = ", ".join(fields.keys())
        placeholders = ", ".join([":" + k for k in fields])
        with get_conn(self.db_path) as conn:
            cur = conn.execute(
                f"INSERT INTO devices ({columns}) VALUES ({placeholders})",
                fields,
            )
            conn.commit()
            return int(cur.lastrowid)

    def update_device(self, device: Device) -> None:
        if device.id is None:
            raise ValueError("device.id is required for update")
        self._ensure_unique(device)
        fields = self._device_fields(device)
        sets = ", ".join([f"{k}=:{k}" for k in fields])
        params = dict(fields)
        params["id"] = device.id
        with get_conn(self.db_path) as conn:
            conn.execute(f"UPDATE devices SET {sets}, updated_at=datetime('now') WHERE id=:id", params)
            conn.commit()

    def delete_device(self, device_id: int) -> None:
        with get_conn(self.db_path) as conn:
            conn.execute("DELETE FROM devices WHERE id=?", (device_id,))
            conn.commit()

    def import_csv(self, csv_path: str) -> int:
        rows_added = 0
        with Path(csv_path).open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                device = Device(
                    id=None,
                    ups_name=row["ups_name"],
                    station=row["station"],
                    location_code=row["location_code"],
                    vendor=row.get("vendor", "Generic"),
                    model=row.get("model", "Unknown"),
                    capacity_kva=row.get("capacity_kva") or row.get("capacity", "3KVA"),
                    ip_address=row["ip_address"],
                    snmp_version=row.get("snmp_version", "v2c"),
                    snmp_port=int(row.get("snmp_port", 161)),
                    community_or_username=row.get("community_or_username") or row.get("community") or None,
                    auth_protocol=row.get("auth_protocol") or None,
                    priv_protocol=row.get("priv_protocol") or None,
                    web_url=row.get("web_url") or None,
                    serial_number=row.get("serial_number") or None,
                    install_date=row.get("install_date") or None,
                    monitoring_enabled=(row.get("monitoring_enabled") or row.get("enabled") or "1") == "1",
                    current_status=row.get("current_status") or row.get("status") or "unknown",
                    oid_profile_name=row.get("oid_profile_name") or row.get("oid_profile") or "generic_ups",
                    notes=row.get("notes") or None,
                )
                self.add_device(device)
                rows_added += 1
        return rows_added

    def export_csv(self, csv_path: str, devices: Iterable[Device] | None = None) -> None:
        data = list(devices) if devices is not None else self.list_devices()
        fields = [
            "ups_name", "station", "location_code", "vendor", "model", "capacity_kva", "ip_address",
            "snmp_version", "snmp_port", "community_or_username", "auth_protocol", "priv_protocol",
            "web_url", "serial_number", "install_date", "monitoring_enabled", "current_status",
            "oid_profile_name", "notes",
        ]
        with Path(csv_path).open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            for d in data:
                writer.writerow({
                    "ups_name": d.ups_name,
                    "station": d.station,
                    "location_code": d.location_code,
                    "vendor": d.vendor,
                    "model": d.model,
                    "capacity_kva": d.capacity_kva,
                    "ip_address": d.ip_address,
                    "snmp_version": d.snmp_version,
                    "snmp_port": d.snmp_port,
                    "community_or_username": d.community_or_username or "",
                    "auth_protocol": d.auth_protocol or "",
                    "priv_protocol": d.priv_protocol or "",
                    "web_url": d.web_url or "",
                    "serial_number": d.serial_number or "",
                    "install_date": d.install_date or "",
                    "monitoring_enabled": 1 if d.monitoring_enabled else 0,
                    "current_status": d.current_status,
                    "oid_profile_name": d.oid_profile_name,
                    "notes": d.notes or "",
                })

    def _ensure_unique(self, device: Device) -> None:
        with get_conn(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT id, ups_name, ip_address FROM devices
                WHERE (ups_name=? OR ip_address=?)
                """,
                (device.ups_name, device.ip_address),
            ).fetchone()
        if row and int(row["id"]) != (device.id or -1):
            if row["ups_name"] == device.ups_name:
                raise ValueError(f"Duplicate UPS name detected: {device.ups_name}")
            raise ValueError(f"Duplicate IP address detected: {device.ip_address}")

    @staticmethod
    def _device_fields(device: Device) -> dict[str, object]:
        return {
            "ups_name": device.ups_name,
            "station": device.station,
            "location_code": device.location_code,
            "vendor": device.vendor,
            "model": device.model,
            "capacity_kva": device.capacity_kva,
            "ip_address": device.ip_address,
            "snmp_version": device.snmp_version,
            "snmp_port": device.snmp_port,
            "community_or_username": device.community_or_username,
            "auth_protocol": device.auth_protocol,
            "priv_protocol": device.priv_protocol,
            "web_url": device.web_url,
            "serial_number": device.serial_number,
            "install_date": device.install_date,
            "monitoring_enabled": int(device.monitoring_enabled),
            "current_status": device.current_status,
            "oid_profile_name": device.oid_profile_name,
            "notes": device.notes,
        }

    @staticmethod
    def _row_to_device(row) -> Device:
        return Device(
            id=int(row["id"]),
            ups_name=row["ups_name"],
            station=row["station"],
            location_code=row["location_code"],
            vendor=row["vendor"],
            model=row["model"],
            capacity_kva=row["capacity_kva"],
            ip_address=row["ip_address"],
            snmp_version=row["snmp_version"],
            snmp_port=int(row["snmp_port"]),
            community_or_username=row["community_or_username"],
            auth_protocol=row["auth_protocol"],
            priv_protocol=row["priv_protocol"],
            web_url=row["web_url"],
            serial_number=row["serial_number"],
            install_date=row["install_date"],
            monitoring_enabled=bool(row["monitoring_enabled"]),
            current_status=row["current_status"],
            oid_profile_name=row["oid_profile_name"],
            notes=row["notes"],
        )
