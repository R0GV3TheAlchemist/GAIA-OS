# GAIA Performance & Startup Guide

> **Phase 6.3** — Performance & Startup  
> Target: cold start (double-click → fully interactive UI) under 3 seconds on a mid-range machine.

---

## Cold-Start Sequence

```
User double-clicks GAIA.exe
        │
        ▼
   Tauri runtime init
   Window created — hidden (visible: false)
        │
        ▼
   start_python_sidecar() called
   gaia-backend.exe spawns in background
        │
        ▼
   /health polled (exponential back-off, 300 ms → 3 s, max 30 s)
        │
        ├── 200 OK ──▶  emit sidecar:ready
        │                window.show() + window.set_focus()
        │                ← USER SEES FULLY LOADED UI ✓
        │
        └── timeout ──▶  emit sidecar:error
                         window.show() with error overlay
```

The key insight: **the window is never shown until the UI is ready to render.**  
This eliminates the blank white flash that plagues most Electron/Tauri apps on cold start.

---

## Rust Release Profile

Defined in `src-tauri/Cargo.toml`:

```toml
[profile.release]
opt-level     = 3       # Maximum LLVM optimisation
lto           = "thin"  # Cross-crate dead-code elimination
codegen-units = 1       # Single codegen unit — best inlining
strip         = "symbols" # Strip debug symbols (~30% smaller binary)
panic         = "abort" # No unwinding tables
```

### Why Each Setting Matters

| Setting | Effect | Trade-off |
|---------|--------|-----------|
| `opt-level = 3` | Fastest runtime execution | Slightly longer compile time |
| `lto = "thin"` | Removes dead code across all crates | Longer CI compile (~2–4 min extra) |
| `codegen-units = 1` | Best inlining — LLVM sees all code | Longest compile, most impactful |
| `strip = "symbols"` | ~30% smaller `.exe` — faster load from disk | No symbols in crash reports (use `.pdb` separately) |
| `panic = "abort"` | No unwinding machinery linked in | Panics cannot be caught with `std::panic::catch_unwind` |

---

## Frontend Performance

### Lazy-Load Dev Panels

Dev-only panels (diagnostics, logs, quantum canvas) should be dynamically imported and never bundled into the main chunk:

```ts
// Good — only loads when the panel is opened
const DevPanel = lazy(() => import('./panels/DevPanel'))

// Bad — always in the main bundle
import DevPanel from './panels/DevPanel'
```

### Vite Bundle Config

In `vite.config.ts`, ensure dev-only code is tree-shaken in production:

```ts
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        vendor: ['react', 'react-dom'],
        tauri:  ['@tauri-apps/api'],
      }
    }
  }
}
```

### Asset Optimisation

- All images should be WebP or AVIF (not PNG/JPEG)
- Fonts loaded with `font-display: swap` to avoid FOIT
- CSS inlined for above-the-fold content

---

## Python Backend (gaia-backend)

### Startup Time Budget

The PyInstaller binary has a ~1–2 s decompression cost on first run (bootloader extracts to a temp dir). Subsequent runs use the OS file cache and start faster.

To minimise this:
- Keep `gaia-backend.spec` imports tight — only import what the startup path needs
- Use lazy imports inside route handlers for heavy libraries (e.g., `import torch` only when an AI route is first called)
- The `/health` endpoint should **not** import heavy modules — it must respond in < 50 ms

```python
# Good — /health is instant
@app.get("/health")
def health():
    return {"status": "ok"}

# Bad — importing torch at module level delays all startup
import torch  # moves this inside the route that needs it
```

---

## Measuring Cold Start

To benchmark on your machine:

```powershell
# PowerShell — time from launch to first HTTP 200 on /health
$start = Get-Date
Start-Process .\src-tauri\target\release\gaia.exe
do { Start-Sleep -Milliseconds 100 } until (
    try { (Invoke-WebRequest http://127.0.0.1:8008/health -TimeoutSec 1).StatusCode -eq 200 } catch { $false }
)
$elapsed = (Get-Date) - $start
Write-Host "Cold start: $($elapsed.TotalSeconds)s"
```

**Target:** < 3.0 s on a mid-range machine (i5 / Ryzen 5, SSD, 16 GB RAM).

---

## Monitoring in Production

The frontend should record and surface startup timing:

```ts
// Listen for the sidecar:ready event and log the elapsed time
const t0 = performance.now()
await listen('sidecar:ready', () => {
  const elapsed = ((performance.now() - t0) / 1000).toFixed(2)
  console.info(`[GAIA] Cold start: ${elapsed}s`)
})
```

This data can feed into the GAIA diagnostics panel in a future release.

---

*Last updated: Phase 6.3 — April 2026*
