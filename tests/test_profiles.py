import json

import pytest

from ups_guardian.services.oid_profiles import OIDProfileManager


def test_profile_loading_and_validation():
    manager = OIDProfileManager("profiles")
    profile = manager.get_profile("generic_ups")
    assert profile["profile_name"] == "generic_ups"


def test_profile_missing_required_keys(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text(json.dumps({"profile_name": "broken", "oids": {"battery_status": "1.2.3"}}), encoding="utf-8")
    manager = OIDProfileManager(str(tmp_path))
    with pytest.raises(ValueError):
        manager.get_profile("broken")
