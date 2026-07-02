# Security Policy — Neo Dashboard Tools

## Reporting a vulnerability

Please report security issues **privately** via
[GitHub Security Advisories](https://github.com/bkstudy2025/neo-dashboard-tools/security/advisories/new)
or by opening a minimal issue **without exploit details** and asking for a
private channel. Do **not** disclose exploit details publicly before a fix is
available.

## Security model (summary)

This integration is deliberately tightly scoped. Full details:
[🇩🇪 Sicherheitsmodell](docs/de/README.md#sicherheitsmodell) ·
[🇬🇧 Security model](docs/en/README.md#security-model).

- **Admin-only writes:** `save` and `delete` WebSocket commands require admin
  rights. Filenames are sanitised (`a–z`, `0–9`, `-`, `_`, max 64 chars) to
  prevent path traversal. Saved modules are capped at **1 MiB**.
- **`list` is read-only and available to every logged-in user** (by design:
  every dashboard user needs the module code to render the cards). Do not
  store secrets in module files — treat them as visible to all HA users.
- **Stored modules are never executed on the server** — they are plain JS files
  served to the frontend.
- **The `fetch` proxy is not a general-purpose proxy.** It is restricted to:
  - https only, **no redirects**;
  - a **host allowlist** (`raw.githubusercontent.com`, `cdn.jsdelivr.net`,
    `api.github.com`);
  - a **per-host path allowlist** pinned to this project's store index and
    `store/modules/*.js`;
  - content-type validation and a **1 MiB** response cap with a 15 s timeout.

  This prevents the proxy from being abused for SSRF against internal hosts.

## What this integration does **not** do

- ❌ No external tracking or analytics scripts.
- ❌ No tokens, API keys or secrets stored in the repository.
- ❌ No server-side execution of stored module code.

## Supported versions

The latest released version receives security fixes. Please update before
reporting.
