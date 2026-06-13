"""Sensors for Neo Dashboard Tools.

- One summary sensor: number of installed modules.
- One diagnostic sensor per module: shows version + type/author/file.
"""
from __future__ import annotations

import re

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import _read_all
from .const import DOMAIN, SIGNAL_UPDATE

# Capture the registerCard(...) call WITH its meta object so we read the real
# card name/version/author — not some unrelated `name:` field elsewhere in code.
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
    async_add_entities([NeoModulesSensor(hass, entry)])
    manager = _ModuleEntityManager(hass, entry, async_add_entities)
    await manager.async_refresh()
    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_UPDATE, manager.schedule_refresh)
    )


class NeoModulesSensor(SensorEntity):
    """Summary: how many modules are installed (with the full list as attributes)."""

    _attr_has_entity_name = True
    _attr_name = "Module"
    _attr_icon = "mdi:puzzle"

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


class NeoModuleSensor(SensorEntity):
    """One per module — state = version, attributes = details."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:puzzle-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, meta: dict) -> None:
        self.hass = hass
        self._file = meta["file"]
        self._meta = meta
        self._attr_unique_id = f"{entry.entry_id}_mod_{meta['file']}"
        self._attr_name = meta["name"]
        self._attr_device_info = _device_info(entry)

    def update_meta(self, meta: dict) -> None:
        self._meta = meta
        self._attr_name = meta["name"]
        self.async_write_ha_state()

    @property
    def native_value(self) -> str:
        return self._meta.get("version") or "installiert"

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "type": self._meta.get("type"),
            "author": self._meta.get("author"),
            "version": self._meta.get("version"),
            "file": f"{self._meta.get('file')}.js",
        }


class _ModuleEntityManager:
    """Creates/updates/removes a sensor per installed module."""

    def __init__(self, hass, entry, async_add_entities) -> None:
        self.hass = hass
        self.entry = entry
        self._add = async_add_entities
        self._entities: dict[str, NeoModuleSensor] = {}

    @callback
    def schedule_refresh(self) -> None:
        self.hass.async_create_task(self.async_refresh())

    async def async_refresh(self) -> None:
        raw = await self.hass.async_add_executor_job(_read_all, self.hass)
        current = {m["name"]: _parse(m) for m in raw}

        # Add new + update existing
        new_entities = []
        for file, meta in current.items():
            ent = self._entities.get(file)
            if ent is None:
                ent = NeoModuleSensor(self.hass, self.entry, meta)
                self._entities[file] = ent
                new_entities.append(ent)
            else:
                ent.update_meta(meta)
        if new_entities:
            self._add(new_entities)

        # Remove modules that no longer exist
        for file in list(self._entities):
            if file not in current:
                ent = self._entities.pop(file)
                await ent.async_remove(force_remove=True)
