from ups_guardian.core.validators import generate_ups_name, is_valid_ups_name, validate_ups_name


def test_name_validation():
    assert is_valid_ups_name("UKYL-3KVA-001")
    assert not is_valid_ups_name("bad-name")


def test_name_validation_message():
    ok, msg = validate_ups_name("bad")
    assert not ok
    assert "format" in msg.lower()


def test_name_generation():
    assert generate_ups_name("u", "kyl", "3kva", 1) == "UKYL-3KVA-001"
