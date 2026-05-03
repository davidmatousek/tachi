"""Smoke test: verify the conftest importlib shim correctly loads scripts."""


def test_extract_infographic_data_module_loads(extract_infographic_data):
    """Phase 0 gate: confirm the hyphenated-name script loads via importlib shim."""
    assert extract_infographic_data is not None
    # Verify at least one attribute exists on the loaded module
    # (don't make claims about specific functions — the module may change)
    assert hasattr(extract_infographic_data, "__file__")
