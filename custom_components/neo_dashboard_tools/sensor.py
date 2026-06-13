"""Sensor exposing the installed Neo Dashboard modules."""
from __future__ import annotations

import re

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import _read_all
from .const import DOMAIN, SIGNAL_UPDATE

_RE_REGISTER = re.compile(r"""registerCard\(\s*["'`]([\w-]+)["'`]""")
_RE_NAME = re.compile(r"""name\s*:\s*["'`]([^"'`]+)["'`]""")
_RE_VERSION = re.compile(r"""version\s*:\s*["'`]([^"'`]+)["'`]""")
_RE_AUTHOR = re.compile(r"""author\s*:\s*["'`]([^"'`]+)["'`]""")


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([NeoModulesSensor(hass, entry)])


class NeoModulesSensor(SensorEntity):
    """Shows how many Neo Dashboard modules are installed + their details."""

    _attr_has_entity_name = True
    _attr_name = "Module"
    _attr_icon = "mdi:puzzle"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self._attr_unique_id = f"{entry.entry_id}_modules"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Neo Dashboard Tools",
            "manufacturer": "Neo Dashboard Kit",
        }
        self._modules: list[dict] = []

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE, self._handle_update)
        )
        await self._scan()

    @callback
    def _handle_update(self) -> None:
        self.hass.async_create_task(self._scan())

    async def _scan(self) -> None:
        raw = await self.hass.async_add_executor_job(_read_all, self.hass)
        modules = []
        for m in raw:
            code = m.get("code", "")
            types = _RE_REGISTER.findall(code)
            name_match = _RE_NAME.search(code)
            ver_match = _RE_VERSION.search(code)
            author_match = _RE_AUTHOR.search(code)
            modules.append(
                {
                    "name": name_match.group(1) if name_match else m["name"],
                    "type": types[0] if types else m["name"],
                    "version": ver_match.group(1) if ver_match else None,
                    "author": author_match.group(1) if author_match else None,
                    "file": f"{m['name']}.js",
                }
            )
        self._modules = modules
        self.async_write_ha_state()

    @property
    def native_value(self) -> int:
        return len(self._modules)

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "count": len(self._modules),
            "modules": self._modules,
            "names": [m["name"] for m in self._modules],
        }
