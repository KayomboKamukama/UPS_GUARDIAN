"""Mock polling adapter for lab/test mode without UPS hardware."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass

from ups_guardian.core.models import Device


@dataclass(slots=True)
class MockSNMPResult:
    """Simulated telemetry values from UPS."""

    communication_status: str
    battery_status: str
    battery_capacity: float
    runtime_remaining_minutes: float
    load_percentage: float
    temperature_c: float
    input_voltage: float
    output_voltage: float
    general_alarm: bool
    battery_disconnected: bool
    on_battery: bool
    overload: bool
    replace_battery: bool


class MockSNMPAdapter:
    """Produces realistic pseudo-random values for phase-1 development."""

    def poll_device(self, device: Device) -> MockSNMPResult:
        digest = hashlib.sha256(f"{device.ups_name}:{device.ip_address}".encode("utf-8")).hexdigest()
        seed = int(digest[:8], 16)
        rng = random.Random(seed + random.randint(1, 5000))

        if rng.random() < 0.07:
            return MockSNMPResult(
                communication_status="unreachable",
                battery_status="unknown",
                battery_capacity=0,
                runtime_remaining_minutes=0,
                load_percentage=0,
                temperature_c=0,
                input_voltage=0,
                output_voltage=0,
                general_alarm=True,
                battery_disconnected=False,
                on_battery=False,
                overload=False,
                replace_battery=False,
            )

        battery_capacity = max(12.0, min(100.0, rng.gauss(72, 20)))
        load = max(4.0, min(98.0, rng.gauss(45, 16)))
        temp = max(18.0, min(43.0, rng.gauss(27, 4)))
        runtime = max(2.0, min(240.0, battery_capacity * 1.5 - load * 0.8))
        on_battery = rng.random() < 0.12
        overload = load > 90
        battery_disconnected = rng.random() < 0.02
        replace_battery = battery_capacity < 30 and rng.random() < 0.35
        alarm = overload or replace_battery or temp > 35 or battery_disconnected

        return MockSNMPResult(
            communication_status="online",
            battery_status="normal" if battery_capacity >= 40 else "low",
            battery_capacity=round(battery_capacity, 2),
            runtime_remaining_minutes=round(runtime, 2),
            load_percentage=round(load, 2),
            temperature_c=round(temp, 2),
            input_voltage=round(max(180.0, min(260.0, rng.gauss(228, 8))), 2),
            output_voltage=230.0,
            general_alarm=alarm,
            battery_disconnected=battery_disconnected,
            on_battery=on_battery,
            overload=overload,
            replace_battery=replace_battery,
        )
