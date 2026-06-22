# Branding & Icons — Neo Dashboard Tools

This repository ships its logo/icon in two places. Keep them consistent.

## Asset files

| File | Size | Purpose |
|---|---|---|
| `logo.png` | 365×325 | README header image (referenced via `raw.githubusercontent.com`) |
| `icon.png` | 256×256 | Square icon, source for the brand assets below |
| `custom_components/neo_dashboard_tools/brand/icon.png` | 256×256 | **Inline brand icon** served by Home Assistant |
| `custom_components/neo_dashboard_tools/brand/logo.png` | 288×256 | Inline brand logo (landscape, shortest side ≤ 256) |

When you update the logo, regenerate the `brand/` copies so all surfaces match.

## How Home Assistant & HACS resolve the icon

Since **Home Assistant 2026.3**, custom integrations provide their brand icon
**inline** under `custom_components/<domain>/brand/`. HA serves it through the
local brands proxy at `/api/brands/integration/neo_dashboard_tools/icon.png`.

- ✅ **Settings → Devices & Services** and the **config-flow dialog** render the
  inline icon correctly.
- ⚠️ The **HACS download panel** may still show *"icon not available"*. This is a
  known HACS bug ([hacs/integration#5223](https://github.com/hacs/integration/issues/5223)):
  HACS resolves repository icons via the old CDN (`brands.home-assistant.io`)
  instead of the local proxy. **This cannot be fixed from this repository.**

The `home-assistant/brands` repository **no longer accepts pull requests for
custom integrations** — the inline mechanism above is the supported path. We
therefore ship the best possible inline assets and document the HACS-side
limitation rather than chasing a fix that does not exist on the repo side.

## Brand image guidelines (for reference)

- **Icon:** square (1:1), 256×256 (and optionally `icon@2x.png` at 512×512),
  PNG, trimmed, transparency preserved.
- **Logo:** landscape, shortest side between 128 and 256 px, PNG.

See the Home Assistant [brands repository](https://github.com/home-assistant/brands)
for the full specification.
