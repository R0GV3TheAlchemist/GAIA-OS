# GAIA Diagnostics & Crash Reporting Guide

> **Phase 6.5** — Crash Reporting & Diagnostics  
> Structured logging to disk, in-app diagnostics panel, log folder access.

---

## Log Files

### Location

| Platform | Path |
|----------|------|
| Windows  | `%APPDATA%\GAIA\logs\gaia-YYYY-MM-DD.log` |
| macOS    | `~/Library/Application Support/GAIA/logs/gaia-YYYY-MM-DD.log` |
| Linux    | `~/.local/share/GAIA/logs/gaia-YYYY-MM-DD.log` |

A new log file is created each day. Old files are not auto-rotated yet — clean manually if needed.

### Format

Each line is a JSON object (JSON-lines format):

```json
{"ts":"2026-04-24T14:32:01.123Z","level":"INFO","module":"updater","msg":"Update check skipped","data":"Network offline"}
```

| Field    | Type   | Description |
|----------|--------|-------------|
| `ts`     | string | ISO 8601 timestamp |
| `level`  | string | `DEBUG` / `INFO` / `WARN` / `ERROR` |
| `module` | string | Source module name |
| `msg`    | string | Human-readable message |
| `data`   | any    | Optional structured payload |

---

## Diagnostics Panel

Access via **Dev Suite → Bottom Panel → ⚙ Diagnostics tab**.

### KPI Cards

| Card | Description |
|------|-------------|
| App Version | Current GAIA semver |
| Sidecar | Live health check — online / degraded / offline |
| Cold Start | Time from page load to `sidecar:ready` (seconds) |
| Log Buffer | Number of entries in the in-memory ring buffer (max 500) |

### Log Tail

- Shows the last 100 log entries matching the selected level filter
- Filter: ALL / INFO / WARN / ERROR
- Auto-scrolls to newest entry
- "Clear" clears the view (not the file on disk)
- Auto-refreshes every 10 seconds

### Actions

| Button | Action |
|--------|--------|
| ↻ Refresh | Re-poll sidecar health and re-render log tail |
| 📁 Open Log Folder | Opens `%APPDATA%\GAIA\logs` in Explorer |
| 📋 Copy Report | Copies last 50 log entries as plain text to clipboard |

---

## Using the Logger in Code

```ts
import { logInfo, logWarn, logError } from '../diagnostics';

// Basic
logInfo('my-module', 'User opened settings');

// With structured data
logError('updater', 'Install failed', { reason: err.message, version: '1.0.1' });

// Warn with context
logWarn('sidecar', 'Health check slow', { attemptMs: 1850 });
```

All log calls:
1. Push to the in-memory ring buffer (max 500 entries, oldest dropped)
2. Mirror to the browser console
3. Append to today's log file on disk (best-effort — never throws)

---

## open_log_dir Command

The Rust command `open_log_dir` (registered in `src-tauri/src/lib.rs`) opens the log directory in the OS file explorer. It creates the directory if it doesn't exist yet.

Call from TypeScript:
```ts
import { invoke } from '@tauri-apps/api/core';
await invoke('open_log_dir');
```

---

## Crash Reporting Philosophy

GAIA does **not** phone home with crash data. All diagnostics are:
- Stored **locally** in AppData only
- Never transmitted without explicit user action
- Available to the user at any time via the diagnostics panel or log folder

This is by design — sovereign AI means sovereign data. 🌿

---

*Last updated: Phase 6.5 — April 2026*
