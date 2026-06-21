"""Neo Dashboard Tools — file-based module storage for Neo Dashboard Kit.

Stores frontend "modules" (small JS files, e.g. premium cards) on the server
under <config>/neo_dashboard_modules/ and exposes them to the frontend via
WebSocket commands so the dashboard config stays clean.
"""
from __future__ import annotations

import asyncio
import glob
import logging
import os
from urllib.parse import urlparse

import aiohttp
import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, MODULES_DIR, SIGNAL_UPDATE

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

# --- Server-side fetch/save safety limits ----------------------------------
# The fetch proxy only exists to load the curated store index + module/card
# files from GitHub for the frontend (avoids browser CORS). Keep it tightly
# scoped so it cannot be used as a generic SSRF proxy.
MAX_FETCH_SIZE = 1_048_576  # 1 MiB — store index / module file response cap
MAX_MODULE_SIZE = 1_048_576  # 1 MiB — saved module/card code cap
ALLOWED_FETCH_HOSTS = frozenset({"raw.githubusercontent.com", "cdn.jsdelivr.net"})
# Exact content-types accepted in addition to any "text/*" type.
ALLOWED_CONTENT_TYPES = frozenset(
    {
        "application/json",
        "application/javascript",
        "application/x-javascript",
        "text/javascript",
    }
)


def _content_type_allowed(content_type: str) -> bool:
    ctype = (content_type or "").split(";", 1)[0].strip().lower()
    return ctype.startswith("text/") or ctype in ALLOWED_CONTENT_TYPES

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
    """Set up via UI config entry — register WS API and the sensors."""
    _register_ws(hass)
    _cleanup_stale_entities(hass, entry)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


def _cleanup_stale_entities(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove orphaned entity-registry entries from older versions.

    Bis v0.3.0 wurde EINE Diagnose-Entity pro installiertem Modul/Karte angelegt
    (unique_id '<entry>_mod_<datei>'). Diese alten Einträge (z. B. „Neo Klima",
    „Neo Kamera", …) bleiben sonst als verwaiste Registry-Einträge sichtbar.
    Wir behalten nur die aktuellen Summary-Sensoren und entfernen den Rest —
    automatisch beim Laden der Integration, ohne manuelles Aufräumen.
    """
    registry = er.async_get(hass)
    valid = {f"{entry.entry_id}_modules", f"{entry.entry_id}_version"}
    for ent in er.async_entries_for_config_entry(registry, entry.entry_id):
        if ent.unique_id not in valid:
            _LOGGER.info("Removing stale Neo diagnostic entity: %s", ent.entity_id)
            registry.async_remove(ent.entity_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


def _register_ws(hass: HomeAssistant) -> None:
    if hass.data.get(f"{DOMAIN}_ws"):
        return
    hass.data[f"{DOMAIN}_ws"] = True
    websocket_api.async_register_command(hass, ws_list)
    websocket_api.async_register_command(hass, ws_save)
    websocket_api.async_register_command(hass, ws_delete)
    websocket_api.async_register_command(hass, ws_fetch)


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

    if len(code.encode("utf-8")) > MAX_MODULE_SIZE:
        connection.send_error(
            msg["id"], "too_large", f"Modul-Code überschreitet {MAX_MODULE_SIZE} Bytes."
        )
        return

    def _write() -> None:
        with open(os.path.join(_modules_dir(hass), f"{name}.js"), "w", encoding="utf-8") as fh:
            fh.write(code)

    await hass.async_add_executor_job(_write)
    async_dispatcher_send(hass, SIGNAL_UPDATE)
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
    async_dispatcher_send(hass, SIGNAL_UPDATE)
    connection.send_result(msg["id"], {})


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/fetch", vol.Required("url"): str}
)
@websocket_api.async_response
async def ws_fetch(hass, connection, msg):
    """Fetch text from an allowed https URL server-side (avoids browser CORS).

    Used by the store to load the index + card/module code from GitHub
    (raw.githubusercontent.com) and jsDelivr. Tightly scoped: https only,
    host allowlist, no redirects, content-type and size limits — so it cannot
    be misused as a generic proxy.
    """
    url = msg["url"]
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        connection.send_error(msg["id"], "invalid_url", "Nur https-URLs erlaubt.")
        return
    if parsed.hostname not in ALLOWED_FETCH_HOSTS:
        connection.send_error(
            msg["id"], "host_not_allowed", f"Host nicht erlaubt: {parsed.hostname}"
        )
        return
    try:
        session = async_get_clientsession(hass)
        async with session.get(
            url,
            timeout=aiohttp.ClientTimeout(total=15),
            allow_redirects=False,
        ) as resp:
            if resp.status != 200:
                connection.send_error(msg["id"], "fetch_failed", f"HTTP {resp.status}")
                return
            if not _content_type_allowed(resp.headers.get("Content-Type", "")):
                connection.send_error(
                    msg["id"],
                    "invalid_content_type",
                    f"Content-Type nicht erlaubt: {resp.headers.get('Content-Type', '')}",
                )
                return
            raw = await resp.content.read(MAX_FETCH_SIZE + 1)
            if len(raw) > MAX_FETCH_SIZE:
                connection.send_error(
                    msg["id"], "too_large", f"Antwort überschreitet {MAX_FETCH_SIZE} Bytes."
                )
                return
            content = raw.decode("utf-8", errors="replace")
        connection.send_result(msg["id"], {"content": content})
    except (aiohttp.ClientError, asyncio.TimeoutError) as err:
        connection.send_error(msg["id"], "fetch_failed", str(err))
