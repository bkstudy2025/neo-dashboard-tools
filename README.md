<p align="center">
  <img src="https://raw.githubusercontent.com/bkstudy2025/neo-dashboard-tools/main/logo.png" width="170" alt="Neo Dashboard Tools" />
</p>

<h1 align="center">Neo Dashboard Tools</h1>

<p align="center">
  Companion integration for the
  <a href="https://github.com/bkstudy2025/neo-dashboard-kit">Neo Dashboard Kit</a> —
  file-based, server-side storage for dashboard modules.<br>
  Companion-Integration für das
  <a href="https://github.com/bkstudy2025/neo-dashboard-kit">Neo Dashboard Kit</a> —
  dateibasierte, serverseitige Speicherung von Dashboard-Modulen.
</p>

<p align="center">
  <a href="docs/de/README.md"><b>🇩🇪 Deutsch</b></a> ·
  <a href="docs/en/README.md"><b>🇬🇧 English</b></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/HACS-Integration-blue.svg" alt="HACS">
  <img src="https://img.shields.io/github/v/release/bkstudy2025/neo-dashboard-tools?include_prereleases" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
</p>

---

## 📚 Documentation / Dokumentation

| | 🇩🇪 Deutsch | 🇬🇧 English |
|---|---|---|
| Full guide | [Dokumentation](docs/de/README.md) | [Documentation](docs/en/README.md) |
| Branding / Icons | [BRANDING.md](BRANDING.md) | [BRANDING.md](BRANDING.md) |
| Security | [SECURITY.md](SECURITY.md) | [SECURITY.md](SECURITY.md) |

---

## ⚡ TL;DR

**Neo Dashboard Tools** stores Neo Dashboard **modules** (small JS cards, e.g.
Premium cards) **as files on the server** under `config/neo_dashboard_modules/`
and serves them to the frontend over a tightly-scoped WebSocket API — so your
dashboard YAML stays clean and modules are available on every device.

**Neo Dashboard Tools** speichert Neo-Dashboard-**Module** (kleine JS-Karten,
z. B. Premium-Karten) **als Dateien auf dem Server** unter
`config/neo_dashboard_modules/` und stellt sie dem Frontend über eine eng
abgesicherte WebSocket-API bereit — so bleibt dein Dashboard-YAML sauber und
Module sind auf jedem Gerät verfügbar.

1. Install via HACS (custom repository → category **Integration**).
2. Restart Home Assistant, then add the integration via **Settings → Devices &
   Services**.
3. Neo Dashboard Kit detects it automatically and stores modules through it.

➡️ **Full guide:** [🇩🇪 Deutsch](docs/de/README.md) · [🇬🇧 English](docs/en/README.md)

---

## 📄 License

[MIT](LICENSE)
