# GAIA-APP Windows Build Guide

> Phase 1 of the Windows Dev Build Roadmap — complete setup instructions for building GAIA on Windows.

---

## System Requirements

| Requirement | Minimum | Recommended |
|---|---|---|
| OS | Windows 10 21H2 | Windows 11 23H2 |
| RAM | 8 GB | 16 GB |
| Disk | 10 GB free | 20 GB free |
| CPU | x86_64 (Intel/AMD) | x86_64 multi-core |

---

## 1. Install Rust

```powershell
# Download and run rustup installer
winget install Rustlang.Rustup

# OR download from https://rustup.rs and run rustup-init.exe

# After install, add Windows MSVC target
rustup target add x86_64-pc-windows-msvc

# Verify
rustc --version
cargo --version
```

> **Important:** Rust on Windows requires the **MSVC build tools**.
> Install Visual Studio Build Tools 2022 with the "Desktop development with C++" workload:
> https://visualstudio.microsoft.com/visual-cpp-build-tools/

---

## 2. Install Node.js

```powershell
# Install Node.js 20 LTS via winget
winget install OpenJS.NodeJS.LTS

# Verify
node --version   # should be >= 20
npm --version
```

---

## 3. Install Python

```powershell
# Install Python 3.11+ via winget
winget install Python.Python.3.11

# Verify
python --version
pip --version
```

---

## 4. Install WebView2 Runtime

WebView2 is required by Tauri on Windows. It is pre-installed on Windows 11.
For Windows 10, download the Evergreen Bootstrapper:
https://developer.microsoft.com/en-us/microsoft-edge/webview2/

```powershell
# Check if already installed (Windows 11 has it by default)
Get-Package -Name "Microsoft Edge WebView2 Runtime" -ErrorAction SilentlyContinue
```

---

## 5. Clone the Repository

```powershell
git clone https://github.com/R0GV3TheAlchemist/GAIA-APP.git
cd GAIA-APP
```

---

## 6. Install Frontend Dependencies

```powershell
npm install

# Verify Tauri CLI is available
npx tauri --version
```

---

## 7. Install Python Dependencies

```powershell
# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 8. Run Development Build

```powershell
# Activate Python venv first
.venv\Scripts\activate

# Run GAIA in development mode (hot reload)
npm run tauri dev
```

This will:
1. Start the Vite dev server on `localhost:1420`
2. Compile the Rust backend via Cargo
3. Launch the GAIA desktop window

---

## 9. Build Windows Installer

```powershell
# Activate Python venv first
.venv\Scripts\activate

# Build production Windows installer
npm run tauri build
```

### Output Artifacts

After a successful build, find your installers at:

```
src-tauri/target/release/bundle/
  msi/        -> GAIA_0.1.0_x64_en-US.msi
  nsis/       -> GAIA_0.1.0_x64-setup.exe
```

---

## 10. Verify the Build

1. Locate `GAIA_0.1.0_x64_en-US.msi` in the bundle output
2. Double-click to install on Windows
3. Launch GAIA from Start Menu
4. Confirm window opens at 1200x800
5. Confirm title bar reads **GAIA**

---

## Troubleshooting

### `error: linker 'link.exe' not found`
Install Visual Studio Build Tools 2022 with the "Desktop development with C++" workload.

### `WebView2 not found`
Download and install WebView2 Runtime from Microsoft:
https://developer.microsoft.com/en-us/microsoft-edge/webview2/

### `error[E0463]: can't find crate for ...`
Run `rustup update stable` and try again.

### `npm install` fails with peer dependency errors
Run `npm install --legacy-peer-deps`

### Python `pip install` fails on a package
Check `requirements.txt` for Linux-only packages. Document any Windows-incompatible packages below.

#### Known Windows-Incompatible Packages
| Package | Issue | Windows Alternative |
|---|---|---|
| *(none documented yet)* | — | — |

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```powershell
copy .env.example .env
notepad .env
```

---

## Quick Reference Commands

```powershell
# Dev mode
npm run tauri dev

# Production build
npm run tauri build

# Run Python tests
.venv\Scripts\activate
pytest tests/

# TypeScript type check
npm run build

# Update Rust dependencies
cargo update
```

---

*Last updated: 2026-04-20 — Phase 1 Windows Build Roadmap*
