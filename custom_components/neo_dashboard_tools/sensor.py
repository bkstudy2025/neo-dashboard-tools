"""Sensors for Neo Dashboard Tools.

Bewusst nur zwei zusammengefasste Diagnose-Sensoren — KEINE Entity pro Karte/
Modul mehr (das hat HA mit veralteten Einträgen zugemüllt, siehe Registry-Cleanup
in __init__.py):

- "Module": Anzahl installierter Store-Module (+ vollständige Liste als Attribute)
- "Version": installierte Integrations-Version
"""
from __future__ import annotations

import re

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.loader import async_get_integration

from . import _read_all
from .const import DOMAIN, SIGNAL_UPDATE

# registerCard(...) MIT Meta-Objekt → echter Karten-Name/-Version/-Autor.
_RE_REG_META = re.compile(
    r"""registerCard\(\s*["'`]([\w-]+)["'`]\s*,\s*[A-Za-z_$][\w$]*\s*,\s*\{([^{}]*)\}"""
)
_RE_REGISTER = re.compile(r"""registerCard\(\s*["'`]([\w-]+)["'`]""")


def _field(body: str, key: str):
    m = re.search(key + r"""\s*:\s*["'`]([^"'`]+)["'`]""", body)
    return m.group(1) if m else None


def _parse(module: dict) -> dict:
    """Extract metadata from a stored module {name(file), code}."""
    code = module.get("code", "")
    file = module["name"]
    meta = _RE_REG_META.search(code)
    if meta:
        typ, body = meta.group(1), meta.group(2)
        return {
            "file": file,
            "type": typ,
            "name": _field(body, "name") or typ,
            "version": _field(body, "version"),
            "author": _field(body, "author"),
        }
    fallback = _RE_REGISTER.search(code)
    typ = fallback.group(1) if fallback else file
    return {"file": file, "type": typ, "name": typ, "version": None, "author": None}


def _device_info(entry: ConfigEntry) -> dict:
    return {
        "identifiers": {(DOMAIN, entry.entry_id)},
        "name": "Neo Dashboard Tools",
        "manufacturer": "Neo Dashboard Kit",
    }


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    integration = await async_get_integration(hass, DOMAIN)
    async_add_entities(
        [
            NeoModulesSensor(hass, entry),
            NeoVersionSensor(entry, str(integration.version)),
        ]
    )


class NeoModulesSensor(SensorEntity):
    """Zusammenfassung: Anzahl installierter Store-Module (Liste als Attribute)."""

    _attr_has_entity_name = True
    _attr_name = "Module"
    _attr_icon = "mdi:puzzle"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self._attr_unique_id = f"{entry.entry_id}_modules"
        self._attr_device_info = _device_info(entry)
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
        self._modules = [_parse(m) for m in raw]
        self.async_write_ha_state()

    @property
    def native_value(self) -> int:
        return len(self._modules)

    @property
    def extra_state_attributes(self) -> dict:
        return {"count": len(self._modules), "modules": self._modules}


class NeoVersionSensor(SensorEntity):
    """Installierte Version der Integration (Diagnose)."""

    _attr_has_entity_name = True
    _attr_name = "Version"
    _attr_icon = "mdi:information-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry: ConfigEntry, version: str) -> None:
        self._attr_unique_id = f"{entry.entry_id}_version"
        self._attr_device_info = _device_info(entry)
        self._version = version

    @property
    def native_value(self) -> str:
        return self._version
