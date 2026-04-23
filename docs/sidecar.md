# GAIA Sidecar Architecture

> **Phase 3 reference doc** — explains how the Python backend is bundled, launched, and managed inside the Tauri Windows app.

---

## Overview

GAIA's Python backend (FastAPI + Uvicorn) runs as a **Tauri sidecar** — a bundled subprocess that launches automatically when the desktop app starts and shuts down when it closes. End-users need **no Python installation**.

```
┌──────────────────────────────────────────────────┐
│  GAIA Desktop App (Tauri / Rust)                 │
│                                                  │
│  ┌──────────────┐    IPC/HTTP    ┌─────────────┐ │
│  │  Frontend    │ ◄────────────► │  Sidecar    │ │
│  │  (TypeScript)│ localhost:8008 │  (Python)   │ │
│  └──────────────┘                └─────────────┘ │
└──────────────────────────────────────────────────┘
```

---

## Building the Sidecar

### 1. Install PyInstaller

```bash
pip install pyinstaller
```

### 2. Build the frozen executable

From the repo root:

```bash
pyinstaller gaia-backend.spec
```

This produces `dist/gaia-backend.exe` — a fully self-contained Windows executable with all Python dependencies bundled inside.

### 3. Copy to Tauri binaries directory

Tauri requires the sidecar to be named with the target triple:

```bash
copy dist\gaia-backend.exe src-tauri\binaries\gaia-backend-x86_64-pc-windows-msvc.exe
```

This step is automated in the CI workflow (`.github/workflows/build-windows.yml`).

---

## Tauri Configuration

### `tauri.conf.json`

The `externalBin` field tells Tauri to include the sidecar in the installer bundle:

```json
"bundle": {
  "externalBin": ["binaries/gaia-backend"]
}
```

### `capabilities/default.json`

The `shell:allow-execute` permission allows Rust to spawn the sidecar:

```json
"permissions": [
  "shell:allow-execute",
  ...
]
```

---

## Lifecycle in Rust (`src-tauri/src/lib.rs`)

### Startup

On app boot, `start_python_sidecar()` is called from `.setup()`. It:

1. Spawns `gaia-backend` via `ShellExt::sidecar()`
2. Stores the `CommandChild` handle in `Arc<Mutex<Option<CommandChild>>>`
3. Polls `http://127.0.0.1:8008/health` with exponential backoff (300 ms → 3 s, max 20 attempts ≈ 30 s)
4. Logs `[GAIA] Python backend ready` on success

### Graceful Shutdown

The child process is killed in two places:

- **Window close event** (`on_window_event` → `CloseRequested`)
- **Tray "Quit" menu item**

Both retrieve the `SidecarHandle` from Tauri state, lock the mutex, call `child.kill()`, and clear the handle.

### Restart Command

The Tauri command `restart_backend` (invocable from the frontend) kills the existing process and spawns a fresh one:

```typescript
import { invoke } from '@tauri-apps/api/core';
await invoke('restart_backend');
```

---

## Frontend Health-Check (`src/sidecar.ts`)

Before the GAIA UI mounts, `initSidecar()` is called from `src/main.ts`. It:

1. Shows a full-screen loading overlay (`#gaia-loading-overlay`)
2. Polls `/health` with exponential backoff (up to 40 attempts ≈ 30 s)
3. On success → removes overlay, mounts UI
4. On failure → invokes `restart_backend` and retries (max 3 auto-retries)
5. After all retries exhausted → shows a dismissible error state and unmounts after 6 s

---

## Windows Data Paths

| Purpose      | Path                                      |
|--------------|-------------------------------------------|
| Config       | `%APPDATA%\com.rogve.gaia\config\`         |
| Logs         | `%APPDATA%\com.rogve.gaia\logs\`           |
| Canon docs   | `%APPDATA%\com.rogve.gaia\canon\`          |

These directories are created on first launch by `ensureAppDataDirs()` in `src/app.ts`. Canon docs are seeded from the bundled `resources/canon/` directory if the destination is empty.

---

## Testing

Sidecar tests live in `tests/test_sidecar.py`. They require the frozen exe to exist:

```bash
# Build first
pyinstaller gaia-backend.spec

# Run sidecar tests
pytest tests/test_sidecar.py -v
```

| Test | Assertion |
|------|-----------|
| `test_starts_within_10_seconds` | Backend HTTP-ready in < 10 s cold start |
| `test_health_returns_ok` | `/health` returns `{status: ok}` |
| `test_state_endpoint_returns_valid_shape` | `/api/state` has all engine keys |
| `test_stable_30_minutes` | No failures over 30 min (skipped in CI) |

---

## CI Integration

In GitHub Actions (`.github/workflows/build-windows.yml`), the sidecar build is automated:

```yaml
- name: Build Python sidecar
  run: |
    pip install pyinstaller
    pyinstaller gaia-backend.spec
    copy dist\gaia-backend.exe src-tauri\binaries\gaia-backend-x86_64-pc-windows-msvc.exe
```

This runs **before** `npm run tauri build` so the real binary is in place when Tauri bundles the installer.
