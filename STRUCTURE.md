# Projekt-Struktur — Neo Dashboard Tools

Home-Assistant-Integration, die als **Speicher-Backend + CORS-Proxy** für
das Modul-System von Neo Dashboard Kit dient. Diese Datei hält das
verbindliche Layout und die Konventionen fest.

## Das Ökosystem (2 Repos)

| Repo | Rolle | Installation in HA |
|------|-------|--------------------|
| **neo-dashboard-kit** | Frontend: Karten + Modul-System **und** Store-Katalog (`store/`) | HACS → Lovelace-Resource |
| **neo-dashboard-tools** (dieses Repo) | Integration: Modul-Persistenz + CORS-Proxy | HACS → `custom_components/` |

> Der Store-Katalog (`store/index.json` + Module) liegt **im Kit-Repo** und wird
> über jsDelivr/`raw.githubusercontent.com` geladen — es gibt **kein** separates
> `neo-modules`-Repo (siehe STRUCTURE.md im Kit).

## Repo-Layout

```
custom_components/neo_dashboard_tools/   ← die Integration (HA-Standard)
  __init__.py          Setup + WebSocket-API (list / save / delete / fetch)
  config_flow.py       UI-Einrichtung (config entry)
  const.py             DOMAIN, MODULES_DIR, Signale
  sensor.py            Status-/Info-Sensor
  manifest.json        Integration-Metadaten + Version
  strings.json         UI-Texte (Quelle)
  translations/        Übersetzungen (en.json, …)
tests/                 Smoke-Tests (pytest-homeassistant-custom-component)
  conftest.py          aktiviert custom_components/ im Test-HA
  test_smoke.py        Config-Flow · WS-Roundtrip · fetch-Allowlist
pytest.ini             pytest-Konfiguration (asyncio_mode = auto)
requirements-test.txt  Test-Abhängigkeiten (CI + lokal)
hacs.json              HACS-Metadaten
icon.png / logo.png    Branding
README.md / STRUCTURE.md
.gitignore             hält __pycache__/*.pyc draußen
```

> Konvention HA/HACS: Der **gesamte** Integrations-Code liegt unter
> `custom_components/<domain>/`. Der Ordnername muss exakt der `domain`
> aus `manifest.json` entsprechen (`neo_dashboard_tools`).

## Laufzeit-Struktur in Home Assistant

Die Integration legt gespeicherte Module unter dem HA-Konfig-Verzeichnis ab:

```
<config>/neo_dashboard_modules/<id>.js      (MODULES_DIR in const.py)
```

- Eine Datei pro Modul, Dateiname = Modul-`id` (über `_safe_name` bereinigt).
- Sichtbar & sicherbar (Teil von HA-Backups), vom Nutzer einsehbar.
- Beim Start liest das Frontend diese Liste über die WebSocket-API.

## WebSocket-API (Namespace `neo_dashboard_tools/…`)

| Befehl | Zweck | Rechte |
|--------|-------|--------|
| `list` | alle gespeicherten Module `[{name, code}]` | alle |
| `save` | Modul anlegen/überschreiben | admin |
| `delete` | Modul löschen | admin |
| `fetch` | https-URL serverseitig laden (umgeht Browser-CORS) | admin |

## Konventionen

- **Keine** generierten Artefakte committen (`__pycache__/`, `*.pyc` — via
  `.gitignore` ausgeschlossen).
- Version wird in `manifest.json` gepflegt; ein Git-Tag löst den Release aus.
- Neue UI-Texte zuerst in `strings.json`, dann in `translations/` spiegeln.
