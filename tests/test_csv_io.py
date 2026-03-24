from pathlib import Path

from ups_guardian.data.db import init_schema
from ups_guardian.data.device_repository import DeviceRepository


def test_csv_import_export_roundtrip(tmp_path: Path):
    db = tmp_path / "test.db"
    init_schema(str(db), "config/schema.sql")
    repo = DeviceRepository(str(db))

    csv_in = Path("config/sample_devices.csv")
    imported = repo.import_csv(str(csv_in))
    assert imported >= 7

    csv_out = tmp_path / "out.csv"
    repo.export_csv(str(csv_out))
    assert csv_out.exists()
    content = csv_out.read_text(encoding="utf-8")
    assert "ups_name" in content
    assert "UKYL-3KVA-001" in content
