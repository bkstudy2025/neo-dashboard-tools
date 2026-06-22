# Neo Dashboard Tools — Documentation (English)

> 🇩🇪 Deutsche Version: [`docs/de/README.md`](../de/README.md)

Companion integration for the
[Neo Dashboard Kit](https://github.com/bkstudy2025/neo-dashboard-kit).
Stores dashboard **modules** (small JS cards, e.g. Premium cards) **as files on
the server** under `config/neo_dashboard_modules/` and serves them to the
frontend over a WebSocket API.

## Contents

- [Why are Tools needed?](#why-are-tools-needed)
- [Installation](#installation)
- [Setup in Home Assistant](#setup-in-home-assistant)
- [Overview in Devices & Services](#overview-in-devices--services)
- [Managing modules](#managing-modules)
- [Module storage location](#module-storage-location)
- [WebSocket API](#websocket-api)
- [Security model](#security-model)
- [Troubleshooting](#troubleshooting)
- [Relationship to Neo Dashboard Kit](#relationship-to-neo-dashboard-kit)
- [Logo & icon in HACS](#logo--icon-in-hacs)

---

## Why are Tools needed?

Neo Dashboard Kit can load **modules** (extra JS cards). Without this
integration, the JS code would have to be embedded directly in the
dashboard/Lovelace configuration. That has drawbacks:

- The card/dashboard config gets cluttered with large JS blobs.
- Modules would need to be re-added on every dashboard.
- Updates would be tedious (change in multiple places).

**With Neo Dashboard Tools:**

- ✅ The card/dashboard config stays **clean** (no JS blob in YAML).
- ✅ Modules are available **across devices**.
- ✅ **Central updates** in one place.

> **Note:** The integration is **optional**. The Neo Dashboard Kit cards
> (Neo Control, Neo Display, Neo Header) work without Tools. The integration is
> recommended only for server-side stored modules / Premium cards.

---

## Installation

1. **HACS → Integrations → ⋮ (top right) → Custom repositories**
2. Repository: `https://github.com/bkstudy2025/neo-dashboard-tools`
   — category **Integration**
3. Download **Neo Dashboard Tools** → **restart Home Assistant**

---

## Setup in Home Assistant

1. **Settings → Devices & Services → Add integration**
2. Search for **"Neo Dashboard Tools"** and select it.
3. Confirm — the integration automatically creates the
   `config/neo_dashboard_modules/` directory.

Neo Dashboard Kit then detects the integration automatically and stores modules
through it (instead of in YAML).

---

## Overview in Devices & Services

The integration creates a **Neo Dashboard Tools** device with **two**
consolidated diagnostic sensors:

| Sensor | Meaning |
|---|---|
| **"Modules"** | State = number of installed modules · attributes = full list (`type`, `name`, `version`, `author`, `file` per module) |
| **"Version"** | installed integration version |

> **Note (since v0.3.1):** Earlier versions created **one diagnostic entity per
> card/module**. That was replaced by the two summary sensors. Old, no-longer-valid
> entities (e.g. "Neo Climate", "Neo Camera", "Neo Calendar" …) are **removed
> automatically from the entity registry** when the integration loads — a single
> **reload integration** / **restart Home Assistant** is enough, no manual cleanup
> required.

---

## Managing modules

**Configure** (on the device/entry) → menu:

- **Add new module** — paste code
- **Edit module** — view/change existing code (pre-loaded)
- **Remove module**

In practice, modules are usually saved via the **Store** / **"Paste code"** in
the Neo Dashboard Kit card editor — this integration is the server side behind it.

---

## Module storage location

```
config/
└── neo_dashboard_modules/
    ├── <name>.js
    └── …
```

- Each module is its own `.js` file.
- The filename is reduced to safe characters (`a–z`, `0–9`, `-`, `_`, max. 64
  characters).
- The files are plain JavaScript served to the frontend — they are **not
  executed on the server**.

---

## WebSocket API

All commands run over the Home Assistant WebSocket connection.

| Command | Description | Rights |
|---|---|---|
| `neo_dashboard_tools/list` | Get all modules `{ modules: [{name, code}] }` | – |
| `neo_dashboard_tools/save` | Save/overwrite a module `{name, code}` | **Admin** |
| `neo_dashboard_tools/delete` | Delete a module `{name}` | **Admin** |
| `neo_dashboard_tools/fetch` | Fetch an allowed https URL server-side `{url}` (avoids browser CORS) | – |

The `fetch` command is **not a generic proxy** — see
[Security model](#security-model).

---

## Security model

The integration is deliberately tightly scoped:

**Save (`save`):**
- Requires **admin rights**.
- Filename is sanitised (`_safe_name`): only `a–z`, `0–9`, `-`, `_`, max. 64
  characters — prevents path traversal.
- Maximum module size **1 MiB**.

**Delete (`delete`):** requires **admin rights**.

**Fetch proxy (`fetch`):** exists solely to load the **curated store index** and
**module/card files** for the frontend (avoids browser CORS). It is scoped so
tightly that it **cannot be misused as an SSRF proxy**:

- **https only**, no redirects (`allow_redirects=False`).
- **Host allowlist:** `raw.githubusercontent.com`, `cdn.jsdelivr.net`,
  `api.github.com`.
- **Per-host path allowlist** — fixed to this project:
  - `api.github.com` → store index only
    (`/repos/bkstudy2025/neo-dashboard-kit/contents/store/index.json`)
  - `raw.githubusercontent.com` → store index only (fallback)
  - `cdn.jsdelivr.net` → only `store/modules/*.js` of this repo (any ref, e.g. a
    pinned commit SHA)
- **Content-type check** (`text/*`, JSON, JavaScript).
- **1 MiB response size limit**, 15 s timeout.

**General:**
- ❌ No external tracking scripts.
- ❌ No tokens or secrets in the repo.
- ✅ Stored modules are **only served**, never executed on the server.

See also [`SECURITY.md`](../../SECURITY.md).

---

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Integration doesn't appear under "Add integration" | HACS download finished? **Home Assistant restarted?** |
| Old "Neo …" diagnostic entities still visible | **Reload integration** / restart HA — the cleanup logic (since v0.3.1) removes them automatically. |
| Store/modules don't load | Check internet access to `raw.githubusercontent.com` / `cdn.jsdelivr.net` / `api.github.com`. Foreign hosts/paths are rejected on purpose with `host_not_allowed` / `path_not_allowed`. |
| Saving a module fails | Admin rights required; code must not exceed **1 MiB**. |
| HACS shows "icon not available" | Known HACS behaviour — see [Logo & icon in HACS](#logo--icon-in-hacs). |

---

## Relationship to Neo Dashboard Kit

- **Neo Dashboard Kit** = the **frontend cards** (HACS · *Lovelace/Frontend*).
- **Neo Dashboard Tools** = the **server integration** (HACS · *Integration*)
  that stores and serves modules file-based.

Both are installed separately via HACS. The Kit works standalone; Tools adds the
server-side module storage. Recommended combination: matching or clearly
compatible release levels (see each repo's release notes).

> **Current compatibility:** Tools `v1.0.0-rc.1` ↔ Kit `v1.0.0-rc.1`.

---

## Logo & icon in HACS

Since **Home Assistant 2026.3**, integrations ship their brand icon **inline**
under `custom_components/neo_dashboard_tools/brand/`. Details and the known HACS
display bug ([hacs/integration#5223](https://github.com/hacs/integration/issues/5223))
are documented in [`BRANDING.md`](../../BRANDING.md).

---

## License

[MIT](../../LICENSE)
