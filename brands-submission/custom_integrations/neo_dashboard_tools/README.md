# `home-assistant/brands` submission — Neo Dashboard Tools

These are the **ready-to-submit** brand assets for getting the Neo Dashboard
Tools icon to display in the **HACS store/list**.

> **Why this exists:** HACS resolves a repository's list icon from the Home
> Assistant *brands service*, keyed by the integration **domain**
> (`brands.home-assistant.io/_/neo_dashboard_tools/icon.png`) — **not** from this
> repo's root `icon.png`, the README image, `hacs.json`, or (yet) the inline
> `custom_components/neo_dashboard_tools/brand/` assets. So the icon only appears
> in HACS once `neo_dashboard_tools` exists in the brands service. See
> [`../../BRANDING.md`](../../BRANDING.md).

## Files in this folder

| File | Size | Notes |
|---|---|---|
| `icon.png` | 256×256 | square, PNG, transparent |
| `icon@2x.png` | 512×512 | hDPI (upscaled from the 256² source) |
| `logo.png` | 288×256 | landscape, shortest side 256 (spec: 128–256) |
| `logo@2x.png` | 365×325 | landscape hDPI, shortest side 325 (spec: 256–512) |

All are PNG with transparency. The folder path mirrors the brands repo layout
exactly, so you can copy it in directly.

## How to submit

1. Fork **https://github.com/home-assistant/brands**.
2. Copy this folder so the result is:
   ```
   custom_integrations/neo_dashboard_tools/
     ├── icon.png
     ├── icon@2x.png
     ├── logo.png
     └── logo@2x.png
   ```
3. Open a PR against `home-assistant/brands` (it still merges
   `custom_integrations/` submissions). Title e.g.
   *"Add Neo Dashboard Tools (neo_dashboard_tools) custom integration"*.
4. After it merges and the CDN propagates, HACS will resolve
   `https://brands.home-assistant.io/_/neo_dashboard_tools/icon.png` and the icon
   will appear in the HACS list.

> The `domain` **must** match `manifest.json` → `neo_dashboard_tools`.

## Regenerating these assets

From the repo root (requires Pillow):

```python
from PIL import Image
d = "brands-submission/custom_integrations/neo_dashboard_tools"
icon = Image.open("icon.png").convert("RGBA")
icon.save(f"{d}/icon.png", optimize=True)
icon.resize((512, 512), Image.LANCZOS).save(f"{d}/icon@2x.png", optimize=True)
logo = Image.open("logo.png").convert("RGBA")
w, h = logo.size; s = 256 / min(w, h)
logo.resize((round(w*s), round(h*s)), Image.LANCZOS).save(f"{d}/logo.png", optimize=True)
logo.save(f"{d}/logo@2x.png", optimize=True)
```
