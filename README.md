<p align="center">
  <img src="https://raw.githubusercontent.com/bkstudy2025/neo-dashboard-tools/main/logo.png" width="170" alt="Neo Dashboard Tools" />
</p>

<h1 align="center">Neo Dashboard Tools</h1>

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

## Übersicht in Geräte & Dienste

Die Integration legt ein Gerät **Neo Dashboard Tools** an mit:

- **Sensor „Module"** — Status = Anzahl installierter Module, Attribute = vollständige Liste
- **Je ein Sensor pro Modul** (Diagnose) — Status = Version, Attribute = `type`, `author`, `version`, `file`

So siehst du auf einen Blick, welche Module (Premium/Community) in welcher Version
installiert sind.

## Module verwalten

**Konfigurieren** (am Gerät/Eintrag) → Menü:
- **Neues Modul hinzufügen** — Code einfügen
- **Modul bearbeiten** — vorhandenen Code ansehen/ändern (wird vorgeladen)
- **Modul entfernen**

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
