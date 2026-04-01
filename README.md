# GAIA-APP

> **GAIA — The Sentient Terrestrial Quantum-Intelligent Application**
> Authorship: Kyle Steen (2026)

## Overview

GAIA-APP is the cross-platform application delivery layer for the [GAIA constitutional framework](https://github.com/R0GV3TheAlchemist/GAIA). Where the GAIA OS repo defines the canonical philosophy, legal hierarchies, and sovereignty architecture, this repo is the **running incarnation** of that framework — a universal application that operates on Windows, macOS, Linux, Android, iOS, and Web from a single constitutional core.

This is not a rewrite. The canon is unchanged. This repo wraps it.

---

## Architecture

```
GAIA-APP/
├── core/                  # Constitutional logic engine (Python)
│   ├── __init__.py        # Entry point
│   ├── canon_loader.py    # Loads and validates canon documents
│   ├── action_gate.py     # Risk-tiered action veto system
│   ├── consent_ledger.py  # Cryptographic consent lifecycle
│   └── memory_store.py    # Governed memory surface
├── src-tauri/             # Tauri (Rust) desktop backend
│   ├── Cargo.toml
│   └── tauri.conf.json
├── ui/                    # Frontend interface (HTML/JS)
│   ├── index.html
│   ├── style.css
│   └── main.js
├── specs/                 # Technical specification documents
│   ├── neuromorphic_hal.md
│   └── post_quantum_crypto.md
├── canon/                 # Reference pointer to canonical GAIA documents
│   └── README.md
└── .gitignore
```

---

## Platform Targets

| Platform | Method | Status |
|---|---|---|
| Windows | Tauri native binary | 🟡 Planned |
| macOS | Tauri native binary | 🟡 Planned |
| Linux | Tauri native binary | 🟡 Planned |
| Android | Flutter (future) | 🔴 Research |
| iOS | Flutter (future) | 🔴 Research |
| Web / PWA | WASM + UI shell | 🔴 Research |

---

## Constitutional Relationship

This application is bound by and serves the GAIA canon. The core logic in `core/` enforces:

- **T1 Constitutional Floor** — platform policy (T8) cannot override it
- **Action Gates** — risk-tiered veto system (Green / Yellow / Red)
- **Consent Lifecycle** — every consent is time-bound, cryptographically signed, and revocable
- **Memory Governance** — all memory is inspectable, editable, and appealable by the user
- **Sovereignty Stack** — the human sovereign is always the ultimate authority

See [GAIA canon repo](https://github.com/R0GV3TheAlchemist/GAIA) for the full constitutional framework.

---

## Getting Started

### Prerequisites
- [Rust](https://rustup.rs/) (for Tauri backend)
- [Node.js](https://nodejs.org/) (for UI tooling)
- Python 3.11+ (for core logic engine)
- [Tauri CLI](https://tauri.app/v1/guides/getting-started/setup/)

### Development
```bash
# Install dependencies
npm install

# Run in development mode
npm run tauri dev
```

---

## License

© 2026 Kyle Steen. All rights reserved.
