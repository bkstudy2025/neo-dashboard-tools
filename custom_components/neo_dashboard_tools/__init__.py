"""Neo Dashboard Tools — file-based module storage for Neo Dashboard Kit.

Stores frontend "modules" (small JS files, e.g. premium cards) on the server
under <config>/neo_dashboard_modules/ and exposes them to the frontend via
WebSocket commands so the dashboard config stays clean.
"""
from __future__ import annotations

import glob
import logging
import os

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, MODULES_DIR

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)


def _modules_dir(hass: HomeAssistant) -> str:
    path = hass.config.path(MODULES_DIR)
    os.makedirs(path, exist_ok=True)
    return path


def _safe_name(name: str) -> str:
    name = "".join(c for c in (name or "") if c.isalnum() or c in "-_")
    return (name or "module")[:64]


def _read_all(hass: HomeAssistant) -> list[dict]:
    out: list[dict] = []
    for path in sorted(glob.glob(os.path.join(_modules_dir(hass), "*.js"))):
        try:
            with open(path, encoding="utf-8") as fh:
                code = fh.read()
            out.append({"name": os.path.splitext(os.path.basename(path))[0], "code": code})
        except OSError as err:  # pragma: no cover
            _LOGGER.warning("Could not read module %s: %s", path, err)
    return out


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the WebSocket API once."""
    _register_ws(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up via UI config entry (no extra work needed)."""
    _register_ws(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return True


def _register_ws(hass: HomeAssistant) -> None:
    if hass.data.get(f"{DOMAIN}_ws"):
        return
    hass.data[f"{DOMAIN}_ws"] = True
    websocket_api.async_register_command(hass, ws_list)
    websocket_api.async_register_command(hass, ws_save)
    websocket_api.async_register_command(hass, ws_delete)


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/list"})
@websocket_api.async_response
async def ws_list(hass, connection, msg):
    """Return all stored modules: [{name, code}]."""
    modules = await hass.async_add_executor_job(_read_all, hass)
    connection.send_result(msg["id"], {"modules": modules})


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/save",
        vol.Required("name"): str,
        vol.Required("code"): str,
    }
)
@websocket_api.async_response
async def ws_save(hass, connection, msg):
    """Save (create/overwrite) a module file."""
    name = _safe_name(msg["name"])
    code = msg["code"]

    def _write() -> None:
        with open(os.path.join(_modules_dir(hass), f"{name}.js"), "w", encoding="utf-8") as fh:
            fh.write(code)

    await hass.async_add_executor_job(_write)
    connection.send_result(msg["id"], {"name": name})


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/delete", vol.Required("name"): str}
)
@websocket_api.async_response
async def ws_delete(hass, connection, msg):
    """Delete a module file."""
    name = _safe_name(msg["name"])

    def _rm() -> None:
        path = os.path.join(_modules_dir(hass), f"{name}.js")
        if os.path.exists(path):
            os.remove(path)

    await hass.async_add_executor_job(_rm)
    connection.send_result(msg["id"], {})
