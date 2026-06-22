# Branding & Icons — Neo Dashboard Tools

This repository ships its logo/icon in several places. Keep them consistent.

## Asset files

| File | Size | Purpose |
|---|---|---|
| `logo.png` | 365×325 | README header image (referenced via `raw.githubusercontent.com`) |
| `icon.png` | 256×256 | Square icon — source for the brand assets below and for a `home-assistant/brands` submission |
| `custom_components/neo_dashboard_tools/brand/icon.png` | 256×256 | **Inline brand icon** served by Home Assistant core |
| `custom_components/neo_dashboard_tools/brand/logo.png` | 288×256 | Inline brand logo (landscape, shortest side ≤ 256) |

When you update the logo, regenerate the `brand/` copies so all surfaces match.

## How the icon is resolved (researched, not guessed)

There are **two different consumers** of the icon, and they resolve it
**differently**:

### 1. Home Assistant core UI — uses the inline `brand/` assets ✅

Since **Home Assistant 2026.3**, custom integrations provide their brand icon
**inline** under `custom_components/<domain>/brand/`. HA core serves it through
the local brands proxy at `/api/brands/integration/neo_dashboard_tools/icon.png`.

This already works: **Settings → Devices & Services** and the **config-flow
dialog** render the inline Neo icon correctly.

### 2. The HACS store/list — uses the Home Assistant *brands service*, by domain ⚠️

The HACS frontend resolves a repository's list icon from the **Home Assistant
brands service, keyed by the integration domain** — roughly
`https://brands.home-assistant.io/_/neo_dashboard_tools/icon.png` (with HACS
metadata coming from `data-v2.hacs.xyz`). It does **not** read any of these from
the repo:

- ❌ root `icon.png` / `logo.png`
- ❌ the README header image
- ❌ a `hacs.json` field (HACS has **no** icon field)
- ❌ (currently) the inline `custom_components/<domain>/brand/` assets

Because there is **no `neo_dashboard_tools` entry in the brands service**, HACS
shows **"icon not available"**. HACS also does not yet fall back to HA core's
local brands proxy — that is a known HACS bug
([hacs/integration#5223](https://github.com/hacs/integration/issues/5223),
[hacs/integration#5171](https://github.com/hacs/integration/issues/5171)).

## How to make the HACS icon appear

The real fix is **not** a file in this repository — it is registering the icon
in the brands service:

1. **Submit to [`home-assistant/brands`](https://github.com/home-assistant/brands)**
   under `custom_integrations/neo_dashboard_tools/`. Despite the 2026.3 inline
   mechanism, this repo **still actively merges custom-integration brand
   submissions** (verified: merges through 2026). Provide:
   - `icon.png` — 256×256, square, PNG, trimmed, transparent (use this repo's
     `icon.png`)
   - `icon@2x.png` — 512×512 (optional hDPI)
   - `logo.png` — landscape, shortest side 128–256 (optional)

   Once merged and the CDN propagates, HACS resolves
   `https://brands.home-assistant.io/_/neo_dashboard_tools/icon.png` and the icon
   appears in the HACS list.

2. Or wait for HACS to ship the brands-proxy fallback (#5223 / #5171), after
   which the **inline** assets we already ship would be used directly.

Either way, we keep the inline `brand/` assets (they fix the **HA core** UI) and
keep `icon.png`/`logo.png` ready for the brands submission.

## Brand image guidelines (for reference)

- **Icon:** square (1:1), 256×256 (and optionally `icon@2x.png` at 512×512),
  PNG, trimmed, transparency preserved.
- **Logo:** landscape, shortest side between 128 and 256 px, PNG.

See the Home Assistant [brands repository](https://github.com/home-assistant/brands)
for the full specification.
