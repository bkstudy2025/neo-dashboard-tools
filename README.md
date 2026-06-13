# Neo Dashboard Tools

Companion-Integration für das [Neo Dashboard Kit](https://github.com/bkstudy2025/neo-dashboard-kit).

Speichert Dashboard-**Module** (kleine JS-Karten, z.B. Premium-Karten) **dateibasiert
auf dem Server** unter `config/neo_dashboard_modules/` und stellt sie dem Frontend
über eine WebSocket-API bereit.

**Vorteile gegenüber Code-in-Config:**
- Die Karten-/Dashboard-Config bleibt sauber (kein JS-Blob im YAML)
- Module sind **geräteübergreifend** verfügbar
- Zentrale Aktualisierung an einer Stelle

## Installation

1. HACS → Integrationen → ⋮ → Benutzerdefinierte Repositories
2. `https://github.com/bkstudy2025/neo-dashboard-tools` — Kategorie **Integration**
3. **Neo Dashboard Tools** installieren → Home Assistant neu starten
4. Einstellungen → Geräte & Dienste → **Integration hinzufügen** → „Neo Dashboard Tools"

Danach erkennt das Neo Dashboard Kit die Integration automatisch und speichert
Module über sie (statt im YAML).

## WebSocket-API

| Befehl | Beschreibung | Rechte |
|---|---|---|
| `neo_dashboard_tools/list` | Alle Module `[{name, code}]` | – |
| `neo_dashboard_tools/save` | Modul speichern `{name, code}` | Admin |
| `neo_dashboard_tools/delete` | Modul löschen `{name}` | Admin |

## Speicherort

`config/neo_dashboard_modules/<name>.js`

## Lizenz

MIT
