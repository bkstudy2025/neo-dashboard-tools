"""Smoke-Tests für den Kern der Integration.

Abgedeckt: Config-Flow (Single-Instance), der save/list/delete-Roundtrip über
die WebSocket-API (inkl. Dateinamen-Sanitisierung) und die Schutzregeln des
fetch-Proxys (https-Pflicht, Host-/Pfad-Allowlist) — alles ohne Netzwerk.
"""
from homeassistant.setup import async_setup_component

from custom_components.neo_dashboard_tools.const import DOMAIN


async def test_config_flow_single_instance(hass):
    """Erste Instanz wird angelegt, eine zweite abgelehnt."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    assert result["type"] == "create_entry"
    assert result["title"] == "Neo Dashboard Tools"

    result2 = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    assert result2["type"] == "abort"
    assert result2["reason"] == "already_configured"


async def test_ws_save_list_delete_roundtrip(hass, hass_ws_client):
    """Modul speichern → listen → löschen → leere Liste."""
    assert await async_setup_component(hass, DOMAIN, {})
    client = await hass_ws_client(hass)

    await client.send_json(
        {"id": 1, "type": f"{DOMAIN}/save", "name": "demo-modul", "code": "// demo"}
    )
    msg = await client.receive_json()
    assert msg["success"]
    assert msg["result"]["name"] == "demo-modul"

    await client.send_json({"id": 2, "type": f"{DOMAIN}/list"})
    msg = await client.receive_json()
    assert msg["success"]
    assert msg["result"]["modules"] == [{"name": "demo-modul", "code": "// demo"}]

    await client.send_json({"id": 3, "type": f"{DOMAIN}/delete", "name": "demo-modul"})
    msg = await client.receive_json()
    assert msg["success"]

    await client.send_json({"id": 4, "type": f"{DOMAIN}/list"})
    msg = await client.receive_json()
    assert msg["success"]
    assert msg["result"]["modules"] == []


async def test_ws_save_sanitizes_filename(hass, hass_ws_client):
    """Pfad-Traversal im Namen wird zu einem harmlosen Dateinamen reduziert."""
    assert await async_setup_component(hass, DOMAIN, {})
    client = await hass_ws_client(hass)

    await client.send_json(
        {"id": 1, "type": f"{DOMAIN}/save", "name": "../../evil", "code": "// x"}
    )
    msg = await client.receive_json()
    assert msg["success"]
    assert msg["result"]["name"] == "evil"  # "." und "/" werden entfernt

    await client.send_json({"id": 2, "type": f"{DOMAIN}/delete", "name": "evil"})
    msg = await client.receive_json()
    assert msg["success"]


async def test_safe_name_distinct_symbol_names_do_not_collide():
    """Namen aus reinen Sonderzeichen kollidieren nicht mehr auf 'module'."""
    from custom_components.neo_dashboard_tools import _safe_name

    a = _safe_name("!!!")
    b = _safe_name("???")
    assert a != b  # früher beide → "module"
    assert a.startswith("module-") and b.startswith("module-")
    # Stabil (deterministisch) und für normale Slugs unverändert.
    assert _safe_name("!!!") == a
    assert _safe_name("neo-weather") == "neo-weather"


async def test_ws_save_rejects_oversized_code(hass, hass_ws_client):
    """Module über dem 1-MiB-Limit werden abgelehnt."""
    assert await async_setup_component(hass, DOMAIN, {})
    client = await hass_ws_client(hass)

    await client.send_json(
        {"id": 1, "type": f"{DOMAIN}/save", "name": "big", "code": "x" * (1_048_576 + 1)}
    )
    msg = await client.receive_json()
    assert not msg["success"]
    assert msg["error"]["code"] == "too_large"


async def test_ws_fetch_allowlist(hass, hass_ws_client):
    """Der fetch-Proxy lehnt fremde Hosts, http und fremde Pfade ab (ohne Netz)."""
    assert await async_setup_component(hass, DOMAIN, {})
    client = await hass_ws_client(hass)

    await client.send_json(
        {"id": 1, "type": f"{DOMAIN}/fetch", "url": "https://evil.example.com/x.js"}
    )
    msg = await client.receive_json()
    assert not msg["success"]
    assert msg["error"]["code"] == "host_not_allowed"

    await client.send_json(
        {"id": 2, "type": f"{DOMAIN}/fetch", "url": "http://raw.githubusercontent.com/x"}
    )
    msg = await client.receive_json()
    assert not msg["success"]
    assert msg["error"]["code"] == "invalid_url"

    await client.send_json(
        {
            "id": 3,
            "type": f"{DOMAIN}/fetch",
            "url": "https://raw.githubusercontent.com/other/repo/main/x.js",
        }
    )
    msg = await client.receive_json()
    assert not msg["success"]
    assert msg["error"]["code"] == "path_not_allowed"
