"""Gemeinsame Fixtures für die Neo-Dashboard-Tools-Tests."""
import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """custom_components/ im Test-HA auffindbar machen (für alle Tests)."""
    yield
