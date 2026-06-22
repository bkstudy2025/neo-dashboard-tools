# Neo Dashboard Tools — Dokumentation (Deutsch)

> 🇬🇧 English version: [`docs/en/README.md`](../en/README.md)

Companion-Integration für das
[Neo Dashboard Kit](https://github.com/bkstudy2025/neo-dashboard-kit).
Speichert Dashboard-**Module** (kleine JS-Karten, z. B. Premium-Karten)
**dateibasiert auf dem Server** unter `config/neo_dashboard_modules/` und stellt
sie dem Frontend über eine WebSocket-API bereit.

## Inhalt

- [Warum braucht man Tools?](#warum-braucht-man-tools)
- [Installation](#installation)
- [Einrichtung in Home Assistant](#einrichtung-in-home-assistant)
- [Übersicht in Geräte & Dienste](#übersicht-in-geräte--dienste)
- [Module verwalten](#module-verwalten)
- [Speicherort der Module](#speicherort-der-module)
- [WebSocket-API](#websocket-api)
- [Sicherheitsmodell](#sicherheitsmodell)
- [Fehlerbehebung](#fehlerbehebung)
- [Verhältnis zum Neo Dashboard Kit](#verhältnis-zum-neo-dashboard-kit)
- [Logo & Icon in HACS](#logo--icon-in-hacs)

---

## Warum braucht man Tools?

Das Neo Dashboard Kit kann **Module** (zusätzliche JS-Karten) laden. Ohne diese
Integration müsste der JS-Code direkt in die Dashboard-/Lovelace-Konfiguration
eingebettet werden. Das hat Nachteile:

- Die Karten-/Dashboard-Config wird mit großen JS-Blobs unübersichtlich.
- Module müssten auf jedem Dashboard erneut gepflegt werden.
- Updates wären mühsam (an mehreren Stellen ändern).

**Mit Neo Dashboard Tools:**

- ✅ Die Karten-/Dashboard-Config bleibt **sauber** (kein JS-Blob im YAML).
- ✅ Module sind **geräteübergreifend** verfügbar.
- ✅ **Zentrale Aktualisierung** an einer Stelle.

> **Hinweis:** Die Integration ist **optional**. Die Karten von Neo Dashboard Kit
> (Neo Control, Neo Display, Neo Header) funktionieren auch ohne Tools. Erst für
> server-seitig gespeicherte Module/Premium-Karten wird die Integration
> empfohlen.

---

## Installation

1. **HACS → Integrationen → ⋮ (oben rechts) → Benutzerdefinierte Repositories**
2. Repository: `https://github.com/bkstudy2025/neo-dashboard-tools`
   — Kategorie **Integration**
3. **Neo Dashboard Tools** herunterladen → **Home Assistant neu starten**

---

## Einrichtung in Home Assistant

1. **Einstellungen → Geräte & Dienste → Integration hinzufügen**
2. Nach **„Neo Dashboard Tools"** suchen und auswählen.
3. Bestätigen — die Integration legt automatisch das Verzeichnis
   `config/neo_dashboard_modules/` an.

Danach erkennt das Neo Dashboard Kit die Integration automatisch und speichert
Module über sie (statt im YAML).

---

## Übersicht in Geräte & Dienste

Die Integration legt ein Gerät **Neo Dashboard Tools** mit **zwei**
zusammengefassten Diagnose-Sensoren an:

| Sensor | Bedeutung |
|---|---|
| **„Module"** | Status = Anzahl installierter Module · Attribute = vollständige Liste (`type`, `name`, `version`, `author`, `file` je Modul) |
| **„Version"** | installierte Integrations-Version |

> **Hinweis (ab v0.3.1):** Frühere Versionen legten **eine Diagnose-Entity pro
> Karte/Modul** an. Das wurde durch die beiden Summary-Sensoren ersetzt. Alte,
> nicht mehr gültige Entitäten (z. B. „Neo Klima", „Neo Kamera", „Neo Kalender" …)
> werden beim Laden der Integration **automatisch aus der Entity-Registry
> entfernt** — einmal **Integration neu laden** bzw. **Home Assistant neu
> starten** genügt, kein manuelles Aufräumen nötig.

---

## Module verwalten

**Konfigurieren** (am Gerät/Eintrag) → Menü:

- **Neues Modul hinzufügen** — Code einfügen
- **Modul bearbeiten** — vorhandenen Code ansehen/ändern (wird vorgeladen)
- **Modul entfernen**

In der Praxis werden Module meist über den **Store**/**„Code einfügen"** im
Karten-Editor des Neo Dashboard Kit gespeichert — die Integration ist die
Server-Seite dahinter.

---

## Speicherort der Module

```
config/
└── neo_dashboard_modules/
    ├── <name>.js
    └── …
```

- Jedes Modul ist eine eigene `.js`-Datei.
- Der Dateiname wird auf sichere Zeichen reduziert (`a–z`, `0–9`, `-`, `_`,
  max. 64 Zeichen).
- Die Dateien sind reines, vom Frontend ausgeliefertes JavaScript — sie werden
  **serverseitig nicht ausgeführt**.

---

## WebSocket-API

Alle Befehle laufen über die Home-Assistant-WebSocket-Verbindung.

| Befehl | Beschreibung | Rechte |
|---|---|---|
| `neo_dashboard_tools/list` | Alle Module abrufen `{ modules: [{name, code}] }` | – |
| `neo_dashboard_tools/save` | Modul speichern/überschreiben `{name, code}` | **Admin** |
| `neo_dashboard_tools/delete` | Modul löschen `{name}` | **Admin** |
| `neo_dashboard_tools/fetch` | Server-seitig eine erlaubte https-URL laden `{url}` (umgeht Browser-CORS) | – |

Der `fetch`-Befehl ist **kein allgemeiner Proxy** — siehe
[Sicherheitsmodell](#sicherheitsmodell).

---

## Sicherheitsmodell

Die Integration ist bewusst eng abgesichert:

**Speichern (`save`):**
- Erfordert **Admin-Rechte**.
- Dateiname wird bereinigt (`_safe_name`): nur `a–z`, `0–9`, `-`, `_`, max. 64
  Zeichen — verhindert Path-Traversal.
- Maximale Modulgröße **1 MiB**.

**Löschen (`delete`):** erfordert **Admin-Rechte**.

**Fetch-Proxy (`fetch`):** existiert ausschließlich, um den **kuratierten
Store-Index** und **Modul-/Karten-Dateien** für das Frontend zu laden (umgeht
Browser-CORS). Er ist so eng begrenzt, dass er **nicht als SSRF-Proxy**
missbraucht werden kann:

- **Nur https**, keine Redirects (`allow_redirects=False`).
- **Host-Allowlist:** `raw.githubusercontent.com`, `cdn.jsdelivr.net`,
  `api.github.com`.
- **Pfad-Allowlist pro Host** — fest auf dieses Projekt eingegrenzt:
  - `api.github.com` → nur der Store-Index
    (`/repos/bkstudy2025/neo-dashboard-kit/contents/store/index.json`)
  - `raw.githubusercontent.com` → nur der Store-Index (Fallback)
  - `cdn.jsdelivr.net` → nur `store/modules/*.js` dieses Repos (beliebige Ref,
    z. B. ein gepinnter Commit-SHA)
- **Content-Type-Prüfung** (`text/*`, JSON, JavaScript).
- **Größenlimit 1 MiB** für die Antwort, Timeout 15 s.

**Generell:**
- ❌ Keine externen Tracking-Skripte.
- ❌ Keine Tokens oder Secrets im Repo.
- ✅ Gespeicherte Module werden **nur ausgeliefert**, nicht auf dem Server
  ausgeführt.

Siehe auch [`SECURITY.md`](../../SECURITY.md).

---

## Fehlerbehebung

| Symptom | Ursache / Lösung |
|---|---|
| Integration erscheint nicht unter „Integration hinzufügen" | HACS-Download abgeschlossen? **Home Assistant neu gestartet**? |
| Alte „Neo …"-Diagnose-Entitäten noch sichtbar | **Integration neu laden** bzw. HA neu starten — die Cleanup-Logik (ab v0.3.1) entfernt sie automatisch. |
| Store/Module laden nicht | Prüfe Internetzugang zu `raw.githubusercontent.com` / `cdn.jsdelivr.net` / `api.github.com`. Fremde Hosts/Pfade werden bewusst mit `host_not_allowed` / `path_not_allowed` abgelehnt. |
| Modul speichern schlägt fehl | Admin-Rechte nötig; Code darf **1 MiB** nicht überschreiten. |
| HACS zeigt „icon not available" | Bekanntes HACS-Verhalten — siehe [Logo & Icon in HACS](#logo--icon-in-hacs). |

---

## Verhältnis zum Neo Dashboard Kit

- **Neo Dashboard Kit** = die **Frontend-Karten** (HACS · *Lovelace/Frontend*).
- **Neo Dashboard Tools** = die **Server-Integration** (HACS · *Integration*),
  die Module dateibasiert speichert und ausliefert.

Beide werden getrennt über HACS installiert. Das Kit funktioniert eigenständig;
Tools ergänzt die server-seitige Modulspeicherung. Empfohlene Kombination:
gleiche bzw. klar kompatible Release-Stände (siehe Release-Notes der Repos).

---

## Logo & Icon in HACS

Seit **Home Assistant 2026.3** liefern Integrationen ihr Marken-Icon **inline**
unter `custom_components/neo_dashboard_tools/brand/` mit. Details und der bekannte
HACS-Anzeigefehler ([hacs/integration#5223](https://github.com/hacs/integration/issues/5223))
sind in [`BRANDING.md`](../../BRANDING.md) dokumentiert.

---

## Lizenz

[MIT](../../LICENSE)
