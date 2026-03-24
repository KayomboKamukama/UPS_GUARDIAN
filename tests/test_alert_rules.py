from ups_guardian.core.models import Device
from ups_guardian.services.alerts import AlertRulesEngine
from ups_guardian.services.mock_snmp import MockSNMPResult


def _device() -> Device:
    return Device(
        id=1,
        ups_name="UKYL-3KVA-001",
        station="Kyaliwajjala",
        location_code="KYL",
        vendor="Generic",
        model="UPS",
        capacity_kva="3KVA",
        ip_address="10.0.0.1",
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
        notes=None,
    )


def test_alert_engine_triggers_multiple_rules():
    engine = AlertRulesEngine()
    result = MockSNMPResult(
        communication_status="online",
        battery_status="low",
        battery_capacity=40,
        runtime_remaining_minutes=5,
        load_percentage=70,
        temperature_c=31,
        input_voltage=220,
        output_voltage=230,
        general_alarm=True,
        battery_disconnected=False,
        on_battery=True,
        overload=False,
        replace_battery=True,
    )
    alerts = engine.evaluate(_device(), result)
    alert_types = {a.alert_type for a in alerts}
    assert "low_runtime" in alert_types
    assert "high_temperature" in alert_types
    assert "on_battery" in alert_types
