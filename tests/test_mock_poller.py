from ups_guardian.core.models import Device
from ups_guardian.services.mock_snmp import MockSNMPAdapter


def test_mock_poller_output_structure():
    device = Device(
        id=1,
        ups_name="UMKN-5KVA-001",
        station="Mukono",
        location_code="MKN",
        vendor="Huawei",
        model="UPS5000",
        capacity_kva="5KVA",
        ip_address="10.0.12.31",
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
        oid_profile_name="huawei_placeholder",
        notes=None,
    )
    result = MockSNMPAdapter().poll_device(device)
    assert hasattr(result, "battery_capacity")
    assert hasattr(result, "runtime_remaining_minutes")
    assert result.output_voltage >= 0
