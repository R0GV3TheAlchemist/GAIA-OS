# GAIA Auto-Updater Guide

> **Phase 6.4** — Auto-Updater  
> Documents the update check flow, `latest.json` format, endpoint config, and manual trigger.

---

## How It Works

```
App launches
    │
    ▼
sidecar:ready fires (backend healthy)
    │
    ▼  (2 s grace delay)
checkForUpdates() calls Tauri updater plugin
    │
    ├── No update available → silent, nothing shown
    │
    └── Update available  → update banner slides in (bottom-right)
            │
            ├── "Update & Restart" → download with progress bar → relaunch()
            │
            └── "Later" → banner dismissed, check again next launch
```

All update checks are **silent on failure** — if the endpoint is unreachable (offline, CDN down), GAIA starts normally with no error shown.

---

## Endpoint Configuration

Configured in `src-tauri/tauri.conf.json`:

```json
"plugins": {
  "updater": {
    "active": true,
    "dialog": false,
    "pubkey": "<minisign-public-key>",
    "endpoints": [
      "https://github.com/R0GV3TheAlchemist/GAIA-APP/releases/latest/download/latest.json"
    ],
    "windows": {
      "installMode": "passive"
    }
  }
}
```

> **`dialog: false`** — GAIA uses its own custom banner UI instead of Tauri's built-in dialog.

---

## `latest.json` Format

The `tauri-action` GitHub Action automatically generates `latest.json` and attaches it to every GitHub Release when `includeUpdaterJson: true` is set in `release.yml`.

Expected shape:

```json
{
  "version": "1.0.1",
  "notes": "Bug fixes and performance improvements.",
  "pub_date": "2026-04-24T00:00:00Z",
  "platforms": {
    "windows-x86_64": {
      "url": "https://github.com/R0GV3TheAlchemist/GAIA-APP/releases/download/v1.0.1/GAIA_1.0.1_x64-setup.exe",
      "signature": "<minisign-signature-of-the-installer>"
    }
  }
}
```

- `version` must be a valid semver string higher than the installed version
- `signature` is generated automatically by `tauri-action` using `TAURI_SIGNING_PRIVATE_KEY`
- The file must be served with `Content-Type: application/json`

---

## Release Workflow

To ship an update:

```bash
# 1. Bump version in src-tauri/tauri.conf.json and src-tauri/Cargo.toml
#    (both must match)

# 2. Commit and tag
git add src-tauri/tauri.conf.json src-tauri/Cargo.toml
git commit -m "chore: bump version to 1.0.1"
git tag v1.0.1
git push origin main --tags

# 3. GitHub Actions (release.yml) fires automatically:
#    - Builds the signed installer
#    - Creates a GitHub Release
#    - Attaches GAIA_1.0.1_x64-setup.exe + latest.json
#    - existing installs pick up the update on next launch
```

---

## Manual Update Trigger (Dev)

To test the updater UI without waiting for a real release, call from the browser console inside GAIA:

```ts
// In browser devtools console (Tauri devtools)
import { check } from '@tauri-apps/plugin-updater'
const u = await check()
console.log(u)  // null if no update, Update object if available
```

Or trigger the banner directly for UI testing:

```ts
// Temporarily lower the version in tauri.conf.json to force an update hit
// e.g., change "version": "0.0.1" → the live latest.json will always show an update
```

---

## Update Banner Behaviour

| State | UI |
|-------|-----------|
| No update | Nothing shown |
| Update available | Banner slides in from bottom-right after 2 s |
| Downloading | Progress bar replaces buttons, % shown |
| Installing | Bar fills to 100%, label says "Installing…" |
| Complete | "Restarting GAIA…" then `relaunch()` |
| Error | Buttons restored, error message shown for 3 s |
| Dismissed | Banner slides out, not shown again until next launch |

---

## Files

| File | Purpose |
|------|---------|
| `src/updater.ts` | Update check, banner injection, download + install logic |
| `src/updater.css` | Banner styles (dark theme, slide animation, progress bar) |
| `src/app.ts` | Wires `initUpdater()` into app startup via `sidecar:ready` |
| `src-tauri/tauri.conf.json` | Endpoint URL, public key, `dialog: false` |
| `.github/workflows/release.yml` | `includeUpdaterJson: true` generates `latest.json` per release |

---

*Last updated: Phase 6.4 — April 2026*
