# Release Checklist — Neo Dashboard Tools

A practical pre-release checklist. Tick everything before tagging a release.

> **Release target:** a stable companion version aligned with Neo Dashboard Kit's
> `v1.0.0`. Document clear compatibility in the release notes.

---

## HACS

- [ ] Installable via HACS as a **custom repository** (category **Integration**)
- [ ] Fresh installation works after a Home Assistant restart
- [ ] Update from a previous version works
- [ ] Logo/icon checked — inline `custom_components/neo_dashboard_tools/brand/`
      assets render in **Settings → Devices & Services** and the config-flow
      dialog (HACS download panel may still show "icon not available" — known
      HACS bug, see [`BRANDING.md`](BRANDING.md))

---

## Integration setup

- [ ] Integration appears under **Settings → Devices & Services → Add integration**
- [ ] Config flow completes and creates the entry
- [ ] `config/neo_dashboard_modules/` is created automatically

---

## WebSocket API

- [ ] `neo_dashboard_tools/list` returns stored modules `{ modules: [{name, code}] }`
- [ ] `neo_dashboard_tools/save` writes a module (admin only; >1 MiB rejected)
- [ ] `neo_dashboard_tools/delete` removes a module (admin only)
- [ ] `neo_dashboard_tools/fetch` loads the store index + module `.js` (scoped)
- [ ] Foreign host/path rejected (`host_not_allowed` / `path_not_allowed`)
- [ ] Non-admin cannot save/delete

---

## Storage

- [ ] Saved modules live under `config/neo_dashboard_modules/<name>.js`
- [ ] Filenames are sanitised (no path traversal)

---

## Sensors & cleanup

- [ ] **"Modules"** summary sensor: state = count, attributes = full module list
- [ ] **"Version"** sensor shows the installed integration version
- [ ] Old per-module diagnostic entities (≤ v0.3.0) are removed automatically on
      load (stale-entity cleanup)

---

## Docs & metadata

- [ ] `README.md` is a current bilingual landing page
- [ ] `docs/de/README.md` and `docs/en/README.md` are complete and equivalent
- [ ] `SECURITY.md` present and accurate
- [ ] `manifest.json` version bumped and consistent with the release tag
- [ ] No outdated version numbers in docs/badges
- [ ] No dead links

---

## Validation

- [ ] `python -m compileall custom_components/neo_dashboard_tools`
- [ ] `manifest.json` is valid JSON with the required keys
- [ ] CI workflow green
