from pathlib import Path

import pytest

from ups_guardian.core.models import Device
from ups_guardian.data.db import init_schema
from ups_guardian.data.device_repository import DeviceRepository


def _device(**kwargs) -> Device:
    base = dict(
        id=None,
        ups_name="UKYL-3KVA-001",
        station="Kyaliwajjala",
        location_code="KYL",
        vendor="Generic",
        model="UPS",
        capacity_kva="3KVA",
        ip_address="10.0.1.1",
        snmp_version="v2c",
        snmp_port=161,
        community_or_username="public",
        auth_protocol=None,
        priv_protocol=None,
        web_url=None,
        serial_number=None,
        install_date=None,
        monitoring_enabled=True,
        current_status="unknown",
        oid_profile_name="generic_ups",
        notes="test",
    )
    base.update(kwargs)
    return Device(**base)


def test_device_crud_and_duplicate_detection(tmp_path: Path):
    db = tmp_path / "test.db"
    init_schema(str(db), "config/schema.sql")
    repo = DeviceRepository(str(db))

    did = repo.add_device(_device())
    rows = repo.list_devices()
    assert len(rows) == 1
    assert rows[0].id == did

    with pytest.raises(ValueError):
        repo.add_device(_device(ups_name="UKYL-3KVA-001", ip_address="10.0.1.9"))

    with pytest.raises(ValueError):
        repo.add_device(_device(ups_name="UMKN-5KVA-001", ip_address="10.0.1.1"))

    updated = rows[0]
    updated.station = "Mukono"
    repo.update_device(updated)
    assert repo.list_devices()[0].station == "Mukono"

    repo.delete_device(did)
    assert repo.list_devices() == []
