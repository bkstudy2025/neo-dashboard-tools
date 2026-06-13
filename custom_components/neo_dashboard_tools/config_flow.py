"""Config flow for Neo Dashboard Tools (single instance, no options).

Module management happens in the dashboard (Neo Card editor → "Module
verwalten"); this integration only stores files and exposes sensors.
"""
from __future__ import annotations

from homeassistant import config_entries

from .const import DOMAIN


class NeoDashboardToolsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Single-instance config flow — just creates the entry."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title="Neo Dashboard Tools", data={})
