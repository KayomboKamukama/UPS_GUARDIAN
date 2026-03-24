"""Telemetry and alert persistence."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from ups_guardian.core.models import Alert, PollSample
from ups_guardian.data.db import get_conn


class TelemetryRepository:
    """Store readings, events, alerts and exports."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def insert_sample(self, sample: PollSample) -> None:
        with get_conn(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO device_readings (
                    device_id, sampled_at, battery_status, battery_capacity, runtime_remaining_minutes,
                    load_percentage, temperature_c, input_voltage, output_voltage, communication_status,
                    on_battery, overload, battery_disconnected, replace_battery, general_alarm
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    sample.device_id,
                    sample.sampled_at.isoformat(timespec="seconds"),
                    sample.battery_status,
                    sample.battery_capacity,
                    sample.runtime_remaining_minutes,
                    sample.load_percentage,
                    sample.temperature_c,
                    sample.input_voltage,
                    sample.output_voltage,
                    sample.communication_status,
                    int(sample.on_battery),
                    int(sample.overload),
                    int(sample.battery_disconnected),
                    int(sample.replace_battery),
                    int(sample.general_alarm),
                ),
            )
            conn.execute(
                "UPDATE devices SET last_poll_at=?, current_status=?, updated_at=datetime('now') WHERE id=?",
                (sample.sampled_at.isoformat(timespec="seconds"), sample.communication_status, sample.device_id),
            )
            conn.commit()

    def recent_samples(self, limit: int = 100) -> list[dict]:
        with get_conn(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT r.*, d.ups_name, d.station, d.vendor, d.ip_address
                FROM device_readings r
                JOIN devices d ON d.id = r.device_id
                ORDER BY sampled_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def upsert_alert(self, alert: Alert) -> int:
        now = alert.last_seen.isoformat(timespec="seconds")
        first = alert.first_seen.isoformat(timespec="seconds")
        with get_conn(self.db_path) as conn:
            existing = conn.execute(
                "SELECT * FROM alerts WHERE device_id=? AND alert_type=? AND active=1",
                (alert.device_id, alert.alert_type),
            ).fetchone()
            if existing:
                severity = self._max_severity(existing["severity"], alert.severity)
                conn.execute(
                    """
                    UPDATE alerts
                    SET last_seen=?, occurrences=occurrences+1, severity=?, message=?, acknowledged=0,
                        acknowledged_by=NULL, acknowledged_at=NULL, comment=NULL
                    WHERE id=?
                    """,
                    (now, severity, alert.message, existing["id"]),
                )
                alert_id = int(existing["id"])
            else:
                cur = conn.execute(
                    """
                    INSERT INTO alerts (
                        device_id, alert_type, severity, message, first_seen, last_seen, active,
                        occurrences, acknowledged, acknowledged_by, acknowledged_at, comment
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        alert.device_id,
                        alert.alert_type,
                        alert.severity,
                        alert.message,
                        first,
                        now,
                        int(alert.active),
                        alert.occurrences,
                        int(alert.acknowledged),
                        alert.acknowledged_by,
                        alert.acknowledged_at.isoformat(timespec="seconds") if alert.acknowledged_at else None,
                        alert.comment,
                    ),
                )
                alert_id = int(cur.lastrowid)
            conn.commit()
            return alert_id

    def clear_absent_alerts(self, device_id: int, active_types: set[str]) -> None:
        with get_conn(self.db_path) as conn:
            if active_types:
                placeholders = ",".join("?" for _ in active_types)
                conn.execute(
                    f"UPDATE alerts SET active=0 WHERE device_id=? AND active=1 AND alert_type NOT IN ({placeholders})",
                    (device_id, *active_types),
                )
            else:
                conn.execute("UPDATE alerts SET active=0 WHERE device_id=? AND active=1", (device_id,))
            conn.commit()

    def acknowledge_alert(self, alert_id: int, operator: str, comment: str) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        with get_conn(self.db_path) as conn:
            conn.execute(
                """
                UPDATE alerts
                SET acknowledged=1, acknowledged_by=?, acknowledged_at=?, comment=?
                WHERE id=?
                """,
                (operator, now, comment, alert_id),
            )
            conn.commit()

    def add_event(self, device_id: int | None, event_type: str, message: str) -> None:
        with get_conn(self.db_path) as conn:
            conn.execute(
                "INSERT INTO events (device_id, event_type, message, created_at) VALUES (?, ?, ?, ?)",
                (device_id, event_type, message, datetime.now().isoformat(timespec="seconds")),
            )
            conn.commit()

    def list_active_alerts(self) -> list[dict]:
        with get_conn(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT a.*, d.ups_name, d.station
                FROM alerts a
                JOIN devices d ON d.id = a.device_id
                WHERE a.active = 1
                ORDER BY CASE a.severity WHEN 'critical' THEN 1 WHEN 'warning' THEN 2 ELSE 3 END, a.last_seen DESC
                """
            ).fetchall()
        return [dict(r) for r in rows]

    def export_rows_to_csv(self, csv_path: str, headers: list[str], rows: list[dict]) -> None:
        path = Path(csv_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=headers)
            writer.writeheader()
            for row in rows:
                writer.writerow({h: row.get(h, "") for h in headers})

    @staticmethod
    def _max_severity(current: str, new: str) -> str:
        rank = {"info": 1, "warning": 2, "critical": 3}
        return current if rank.get(current, 0) >= rank.get(new, 0) else new
