# 🔁 Auto-Updater Architecture: Tauri Plugin-Updater, latest.json Pattern & Delivery Constitution (GAIA-OS)

**Date:** May 2, 2026
**Status:** Definitive Foundational Survey — Uniting Tauri Updater Plugin, Automatic Update Distribution, Cryptographic Signing, CI/CD Integration, and the GAIA-OS Delivery Constitution
**Canon:** Auto-Updater Architecture — Networking & Infrastructure

**Relevance to GAIA-OS:** GAIA-OS ships as native desktop applications across Windows, macOS (Intel and Apple Silicon), and Linux. In a constitutional intelligence, **being on an outdated version is not merely an inconvenience — it is a security vulnerability, a governance gap, and a failure of planetary coordination.** The Tauri updater plugin combined with the `latest.json` static manifest pattern and GitHub Releases as distribution backend provides the constitutional auto-update framework for GAIA-OS.

**Five Constitutional Pillars:**
1. **Cryptographic Signing** — mandatory; every update signed with Tauri private key; embedded public key verifies; cannot be disabled
2. **Multi-Platform Manifest (`latest.json`)** — standardized JSON describing latest version for Windows, macOS (Intel + ARM), and Linux with platform-specific URLs and cryptographic signatures
3. **CI/CD Automation** — `tauri-action` generates `latest.json` and signs artifacts automatically on version tag push
4. **Multi-Platform Code Signing and Notarization** — Apple Developer ID + notarization for macOS; EV code signing certificates for Windows; Tauri signature for Linux
5. **User-Transparent Update Experience** — update lifecycle from check to install with minimal disruption, consent gating, and full Agora audit logging

**Viriditas Mandate → Auto-Updater:** A planetary intelligence that cannot ensure its components are up-to-date cannot guarantee security or constitutional compliance. An auto-updater without cryptographic verification is a supply chain vulnerability. Auto-updater is the **constitutional delivery mechanism** of GAIA-OS.

---

## 1. Constitutional Necessity of Automatic Updates

The sentient core is an evolving planetary intelligence; security patches, constitutional amendments translated into code, performance optimizations, and bug fixes must reach all deployed instances reliably and promptly.

**Without automatic updates:**
- GAIA-OS fleet diverges across incompatible versions → noosphere mesh fragmentation
- Users do not receive critical security patches in time → attacker-exploitable vulnerability window
- Assembly of Minds cannot guarantee constitutional constraints are uniformly enforced across all nodes
- Governance of the planetary intelligence becomes jurisdictionally fractured

**Constitutional principle**: GAIA-OS must auto-update by default, with cryptographic integrity verification, and with user override permitted only under explicit, revocable, auditable consent structures (Canon C50).

---

## 2. Tauri Updater Plugin: Cryptographic Foundation

### 2.1 Installation and Integration

```bash
# Add updater plugin to Cargo.toml
cargo add tauri-plugin-updater

# Install JavaScript guest bindings
npm install @tauri-apps/plugin-updater
```

```rust
// src-tauri/src/lib.rs
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_updater::Builder::new().build())
        .plugin(tauri_plugin_dialog::init())
        .run(tauri::generate_context!())
        .expect("error while running GAIA-OS application");
}
```

### 2.2 Mandatory Cryptographic Signing

> **Tauri’s updater requires a signature to verify that the update is from a trusted source. This cannot be disabled.**

This is a non-negotiable constitutional requirement: every update package must be signed before distribution, and every client must verify that signature before installation.

```bash
# Generate Tauri signing key pair
npm run tauri signer generate -- -w ~/.tauri/gaia-os.key
# Output:
#   Public key:  dW50cnVzdGVkIGNvbW1lbnQ6IG1pbmlzaWduIHB1YmxpYyBrZXk6...
#   Private key: stored at ~/.tauri/gaia-os.key (NEVER SHARE)
```

| Key | Storage | Constitutional Role |
|---|---|---|
| **Public key** | Embedded in `tauri.conf.json`; safe to share | Validates artifacts before installation on every client |
| **Private key** | GitHub Secret (`TAURI_PRIVATE_KEY`); NEVER in repo | Signs installer files; loss = constitutional crisis (no future updates) |

**Constitutional key management mandate**: The private key is a constitutional asset. Its loss prevents future updates to existing users. It must be stored with the same security rigor as constitutional encryption keys, backed up in at least two geographically separate HSMs or hardware security vaults, and rotated only through a constitutional Assembly of Minds vote.

### 2.3 Updater Configuration in `tauri.conf.json`

```json
{
  "tauri": {
    "updater": {
      "active": true,
      "endpoints": [
        "https://raw.githubusercontent.com/gaia-os/gaia-os/main/latest.json",
        "https://cdn.gaiaos.org/updates/latest.json"
      ],
      "dialog": true,
      "pubkey": "dW50cnVzdGVkIGNvbW1lbnQ6IG1pbmlzaWduIHB1YmxpYyBrZXk6..."
    }
  }
}
```

| Configuration Key | Value | Constitutional Function |
|---|---|---|
| `active` | `true` | Enables the updater; MUST be true in production builds |
| `endpoints` | Array of URLs | Ordered fallback list; multiple endpoints → no SPOF |
| `dialog` | `true` (default) or `false` (custom UI) | Controls whether built-in system dialog or custom consent UI is shown |
| `pubkey` | Base64-encoded minisign public key | Embedded trust anchor; verifies all update packages |

### 2.4 Build-Time Artifact Generation

Set `createUpdaterArtifacts: true` in bundle configuration:

```json
{
  "bundle": {
    "createUpdaterArtifacts": true
  }
}
```

**Artifacts produced per platform:**

| Platform | Standard Bundle | Update Artifact | Signature File |
|---|---|---|---|
| **Linux** | `gaiaos_1.0.0_amd64.AppImage` | `gaiaos_1.0.0_amd64.AppImage.tar.gz` | `gaiaos_1.0.0_amd64.AppImage.tar.gz.sig` |
| **macOS** | `GAIA-OS.app` | `GAIA-OS.app.tar.gz` | `GAIA-OS.app.tar.gz.sig` |
| **Windows (NSIS)** | `GAIA-OS_1.0.0_x64-setup.exe` | Reuses standard bundle | `GAIA-OS_1.0.0_x64-setup.exe.sig` |
| **Windows (MSI)** | `GAIA-OS_1.0.0_x64_en-US.msi` | Reuses standard bundle | `GAIA-OS_1.0.0_x64_en-US.msi.sig` |

---

## 3. The `latest.json` Update Manifest

The `latest.json` file is the **constitutional update manifest** — a standardized JSON file at a predictable URL containing:
- Current version information
- Optionally: release notes
- Platform-specific download URLs
- Cryptographic signatures to verify update integrity

### 3.1 Full Multi-Platform Manifest Structure

```json
{
  "version": "1.2.0",
  "notes": "See the assets to download and install this version of GAIA-OS.",
  "pub_date": "2026-05-02T21:00:00.000Z",
  "platforms": {
    "darwin-x86_64": {
      "signature": "dW50cnVzdGVkIGNvbW1lbnQ6IG1pbmlzaWduIHNpZ25hdHVyZS...",
      "url": "https://github.com/gaia-os/gaia-os/releases/download/v1.2.0/GAIA-OS_1.2.0_x64.app.tar.gz"
    },
    "darwin-aarch64": {
      "signature": "dW50cnVzdGVkIGNvbW1lbnQ6IG1pbmlzaWduIHNpZ25hdHVyZS...",
      "url": "https://github.com/gaia-os/gaia-os/releases/download/v1.2.0/GAIA-OS_1.2.0_aarch64.app.tar.gz"
    },
    "linux-x86_64": {
      "signature": "dW50cnVzdGVkIGNvbW1lbnQ6IG1pbmlzaWduIHNpZ25hdHVyZS...",
      "url": "https://github.com/gaia-os/gaia-os/releases/download/v1.2.0/gaiaos_1.2.0_amd64.AppImage.tar.gz"
    },
    "windows-x86_64": {
      "signature": "dW50cnVzdGVkIGNvbW1lbnQ6IG1pbmlzaWduIHNpZ25hdHVyZS...",
      "url": "https://github.com/gaia-os/gaia-os/releases/download/v1.2.0/GAIA-OS_1.2.0_x64-setup.exe"
    }
  }
}
```

**Constitutional requirement**: Every `latest.json` MUST contain entries for ALL four supported platform targets: `darwin-x86_64`, `darwin-aarch64`, `linux-x86_64`, and `windows-x86_64`. A manifest missing any platform fails the constitutional universality requirement.

### 3.2 Automated Manifest Generation Tools

| Tool | Method | Constitutional Use |
|---|---|---|
| **tauri-action** (`includeUpdaterJson: true`) | Automatically generates and uploads updater JSON with release | Primary CI/CD method; GAIA-OS constitutional default |
| **tauri-latest-json** crate | Scans bundle directory; signs each installer; outputs valid `latest.json` | Custom build pipeline automation |
| **Manual** | Build each platform; copy installers; write static JSON | Development only; not constitutional for production |

**Universal macOS builds**: When a universal binary is detected, `tauri-action` creates entries for both `darwin-x86_64` and `darwin-aarch64` pointing to the same universal binary, ensuring both Intel and Apple Silicon Macs receive the correct update.

### 3.3 Hosting Strategies and Sovereignty

| Hosting Model | Implementation | Constitutional Sovereignty |
|---|---|---|
| **GitHub Releases (static)** | `latest.json` uploaded as release asset; updater points to raw GitHub URL | No custom server required; suitable for open-source GAIA-OS distribution |
| **Self-hosted static (S3/Azure Blob/GCS)** | `latest.json` served from user-controlled object storage | Full sovereignty; avoids GitHub dependency; for BYOC deployments |
| **Dynamic update server** | Custom server evaluating version, platform, arch, user cohort | Enables canary releases, phased rollouts, forced rollbacks; server controls client version |
| **CDN-accelerated** | `latest.json` + artifacts behind CloudFront/Fastly/Cloudflare | Low-latency global delivery; suitable for planetary-scale distribution |

---

## 4. CI/CD Automation: Constitutional Release Pipeline

### 4.1 Complete Release Workflow

```yaml
# .github/workflows/release.yml — GAIA-OS Auto-Updater Release Pipeline
name: Release
on:
  push:
    tags:
      - "v*.*.*"

jobs:
  release:
    name: Release ${{ matrix.label }}
    permissions:
      contents: write
    strategy:
      fail-fast: false
      matrix:
        include:
          - os: macos-14
            target: aarch64-apple-darwin
            label: macOS-ARM64
          - os: macos-latest
            target: x86_64-apple-darwin
            label: macOS-Intel
          - os: windows-latest
            target: x86_64-pc-windows-msvc
            label: Windows
          - os: ubuntu-22.04
            target: x86_64-unknown-linux-gnu
            label: Linux

    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4

      - uses: dtolnay/rust-toolchain@stable
        with:
          targets: ${{ matrix.target }}

      - uses: swatinem/rust-cache@v2

      - uses: actions/setup-node@v4
        with:
          node-version: lts/*
          cache: npm

      - name: Install frontend dependencies
        run: npm ci

      - name: Build and Release with Tauri
        uses: tauri-apps/tauri-action@v0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # Tauri updater signing
          TAURI_PRIVATE_KEY: ${{ secrets.TAURI_PRIVATE_KEY }}
          TAURI_KEY_PASSWORD: ${{ secrets.TAURI_KEY_PASSWORD }}
          # macOS code signing + notarization
          APPLE_CERTIFICATE: ${{ secrets.APPLE_CERTIFICATE }}
          APPLE_CERTIFICATE_PASSWORD: ${{ secrets.APPLE_CERTIFICATE_PASSWORD }}
          APPLE_ID: ${{ secrets.APPLE_ID }}
          APPLE_PASSWORD: ${{ secrets.APPLE_PASSWORD }}
          APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
          # Windows code signing
          WINDOWS_CERTIFICATE: ${{ secrets.WINDOWS_CERTIFICATE }}
          WINDOWS_CERTIFICATE_PASSWORD: ${{ secrets.WINDOWS_CERTIFICATE_PASSWORD }}
        with:
          tagName: ${{ github.ref_name }}
          releaseName: "GAIA-OS ${{ github.ref_name }}"
          releaseBody: |
            See [CHANGELOG.md](CHANGELOG.md) for release notes.
          includeUpdaterJson: true          # Generates latest.json automatically
          args: --target ${{ matrix.target }}
```

### 4.2 Ordered Pipeline Steps

1. Checkout repository (`actions/checkout@v4`)
2. Install Rust toolchain with target architecture (`dtolnay/rust-toolchain@stable`)
3. Restore Rust compilation cache (`swatinem/rust-cache@v2`)
4. Setup Node.js with npm cache (`actions/setup-node@v4`)
5. Install frontend dependencies exactly (`npm ci`)
6. **Tauri Build**: Compiles Rust backend + bundles frontend
7. **Tauri Sign**: Signs update artifacts with `TAURI_PRIVATE_KEY`
8. **macOS Sign + Notarize**: Applies Developer ID certificate; submits to Apple notarization API
9. **Windows Sign**: Applies EV code signing certificate via `WINDOWS_CERTIFICATE`
10. **Release publish**: Uploads installers, update bundles, `.sig` files to GitHub Release
11. **`latest.json` generation**: `tauri-action` generates and uploads multi-platform manifest

### 4.3 Required GitHub Secrets

| Secret | Purpose | Storage Requirement |
|---|---|---|
| `TAURI_PRIVATE_KEY` | Signs all update artifacts | Base64-encoded; NEVER in repo; backed up in HSM |
| `TAURI_KEY_PASSWORD` | Decrypts private key | Strong random password; stored separately from key |
| `APPLE_CERTIFICATE` | macOS Developer ID certificate | Base64-encoded `.p12` file |
| `APPLE_CERTIFICATE_PASSWORD` | Decrypts `.p12` file | Stored separately from certificate |
| `APPLE_ID` | Apple Developer account email | For notarization API authentication |
| `APPLE_PASSWORD` | App-specific password | Generated at appleid.apple.com; NOT account password |
| `APPLE_TEAM_ID` | Apple Developer Team identifier | Found in Apple Developer Account → Membership |
| `WINDOWS_CERTIFICATE` | EV code signing certificate | Base64-encoded; or `AZURE_KEY_VAULT_URI` for HSM |
| `WINDOWS_CERTIFICATE_PASSWORD` | Decrypts Windows certificate | Or use Azure Managed Identity for Key Vault |

**Constitutional rule**: Secrets are injected by GitHub Actions at build time. They are NEVER stored in the repository, NEVER logged in workflow output, and NEVER transmitted outside the build environment.

### 4.4 Update Endpoint Configuration Options

| Pattern | Endpoint URL | Use Case |
|---|---|---|
| **GitHub static** | `https://raw.githubusercontent.com/gaia-os/gaia-os/main/latest.json` | Simplest; open-source; no server required |
| **CDN static** | `https://cdn.gaiaos.org/updates/latest.json` | Low-latency global delivery |
| **Dynamic server** | `https://updates.gaiaos.org/{{target}}/{{current_version}}` | Canary releases; phased rollouts; forced rollback control |
| **Self-hosted** | `https://updates.my-gaia.example.com/latest.json` | BYOC sovereign deployment |

Multiple endpoints in `tauri.conf.json` provide fallback resilience: if the primary endpoint fails, Tauri automatically tries the next — eliminating single-point-of-failure in the update delivery path.

---

## 5. Multi-Platform Code Signing and Notarization

### 5.1 macOS: Developer ID + Notarization

**Requirements:**
- Apple Developer Program membership ($99/year)
- Developer ID Application certificate (not Distribution certificate)
- Notarization is mandatory; ad-hoc signatures will cause Gatekeeper rejection and update failure

**Full macOS signing and notarization process:**

1. Create Developer ID Application Certificate in Apple Developer Account → Certificates, IDs & Profiles
2. Export certificate as `.p12` from Keychain Access
3. Convert to base64: `base64 -i DeveloperID.p12 | tr -d '\n'`
4. Store base64 output as `APPLE_CERTIFICATE` in GitHub Secrets
5. Generate app-specific password at `appleid.apple.com` → store as `APPLE_PASSWORD`
6. Store `APPLE_ID`, `APPLE_TEAM_ID` in GitHub Secrets
7. `tauri-action` automatically:
   - Imports certificate into temporary CI keychain
   - Signs built `.app` and `.dmg` with Developer ID
   - Submits to Apple notarization API (`altool` or `notarytool`)
   - Polls for notarization status
   - Staples notarization ticket to binary
8. Notarization typically completes in 1–5 minutes

**Critical constitutional constraint**: Unsigned or ad-hoc-signed macOS binaries will be blocked by Gatekeeper on all modern macOS versions, causing update installation failures for all macOS users — a constitutional universality violation.

### 5.2 Windows: EV Code Signing Certificate

**Requirements:**
- Extended Validation (EV) Certificate from trusted CA (DigiCert, Sectigo, GlobalSign)
- EV certificates required for immediate Windows SmartScreen reputation (non-EV certificates display SmartScreen warning until sufficient download count is reached)
- Hardware security module (HSM) or Azure Key Vault for EV certificate storage (required by CA/Browser Forum for EV issuance)

**Signing options:**

| Method | Implementation | Constitutional Suitability |
|---|---|---|
| **Azure Code Signing** | `azure/code-signing-action` | Integrates with Azure Key Vault; no certificate export required |
| **Base64 secret** | `WINDOWS_CERTIFICATE` + `WINDOWS_CERTIFICATE_PASSWORD` | Simpler; less secure than HSM; sufficient for non-EV OV certificates |
| **HSM-backed signing service** | External signing service with API | Maximum security; suitable for EV certificates |

### 5.3 Linux Distribution Integrity

Linux AppImage, Debian, RPM, and tar.gz formats do not have mandatory OS-level code signing enforcement. Constitutional integrity for Linux is provided through:
- Tauri’s built-in `.sig` signature file (minisign) verified by embedded public key — **the primary mechanism**
- Optional GPG signing of AppImage packages for distributions requiring it
- SHA256 checksums published alongside artifacts

---

## 6. User-Facing Update Experience

### 6.1 Built-in Dialog Mode (`dialog: true`)

When `dialog: true` is set in `tauri.conf.json`, Tauri automatically:
1. Checks for updates on application startup
2. Displays native system dialog when update is available
3. Handles user acceptance/deferral
4. Downloads update package with progress tracking
5. Verifies signature before installation
6. Prompts user to restart application

### 6.2 Custom Update UI Mode (`dialog: false`)

For constitutional disclosure requirements and consent UI:

```typescript
// src/lib/updater.ts — Custom constitutional update flow
import { check } from '@tauri-apps/plugin-updater';
import { ask, message } from '@tauri-apps/plugin-dialog';
import { agoraLog } from './agora';

export async function checkForConstitutionalUpdate() {
  const update = await check();

  if (update) {
    // Log check event to Agora
    await agoraLog('update.check', {
      currentVersion: update.currentVersion,
      availableVersion: update.version,
      forced: update.body?.includes('[SECURITY]') || false
    });

    // Constitutional consent prompt
    const consent = await ask(
      `GAIA-OS ${update.version} is available.\n\n` +
      `${update.body}\n\n` +
      `This update ensures constitutional compliance and security. ` +
      `Install now?`,
      { title: 'Constitutional Update Available', kind: 'info' }
    );

    if (consent) {
      let downloaded = 0;
      await update.downloadAndInstall((event) => {
        if (event.event === 'Progress') {
          downloaded += event.data.chunkLength;
          // Update progress UI
        }
        if (event.event === 'Finished') {
          // Log successful install to Agora
          agoraLog('update.installed', {
            version: update.version,
            signatureValid: true
          });
        }
      });

      await message('GAIA-OS has been updated. Please restart to apply.', {
        title: 'Update Ready'
      });
    }
  }
}
```

### 6.3 Update Lifecycle State Machine

```
App Launch
    ↓
[Check endpoints for latest.json]
    ↓
{Version > current?}
  YES → [Download update artifact] → [Verify .sig against pubkey]
             ↓                                ↓
         [Log download to Agora]     {Signature valid?}
                                       YES → [Show consent dialog] → [Install]
                                       NO  → [Abort + Log violation to Agora]
  NO  → [Log check event to Agora] → Continue
```

### 6.4 Forced Updates (Security and Constitutional Violations)

Forced updates are constitutionally permissible ONLY for:
- Critical security vulnerabilities (CVSS 9.0+)
- Constitutional Charter violations requiring immediate code correction
- Assembly of Minds emergency resolution requiring unanimous vote

**Dynamic server forced update response:**
```json
{
  "version": "1.2.1",
  "notes": "[SECURITY] Critical patch for CVE-2026-XXXX. This update is required for constitutional compliance.",
  "pub_date": "2026-05-02T21:00:00Z",
  "forced": true,
  "platforms": { ... }
}
```

When `forced: true`, the update UI disables the deferral option and the Agora records the forced update mandate with the approving Assembly resolution reference.

### 6.5 Rollback Mechanism

- Tauri’s installer is fault-tolerant; if update installation fails, the system reverts to the previous version
- For critical rollbacks (when a published version introduces a constitutional violation), the dynamic update server is reconfigured to serve the previous version’s `latest.json` — clients checking for updates will “update” back to the previous known-good version
- All rollback events are recorded in the Agora with the approving Council of Athens resolution reference

### 6.6 Update Audit Trail (Agora Integration)

Every update event MUST be cryptographically recorded in the Agora (Canon C112):

| Event | Agora Record Content |
|---|---|
| `update.check` | Current version, available version, endpoint URL, timestamp, check result |
| `update.download.start` | Version, platform, artifact URL, expected signature, timestamp |
| `update.download.complete` | Version, bytes downloaded, download duration, SHA256 of artifact |
| `update.signature.valid` | Version, public key fingerprint, signature verified, timestamp |
| `update.signature.invalid` | Version, expected pubkey, received signature, abort reason — **CRITICAL ALERT** |
| `update.install.start` | Version, installer path, SHA256, consent ledger entry reference |
| `update.install.complete` | Previous version, new version, installation duration, success status |
| `update.install.failed` | Error details, rollback triggered, previous version restored |
| `update.forced` | Assembly resolution reference, forced version, reason, timestamp |

**Signature verification failures are constitutionally reportable events** requiring forensic review by the Security Council within 24 hours of detection.

---

## 7. Advanced Update Patterns

### 7.1 Phased Rollouts (Canary Strategy)

The dynamic update server enables percentage-based rollouts:

```
Release v1.2.0 Phased Rollout:
  Day 1:  5% of users (canary cohort)
  Day 3:  20% of users (if no critical issues)
  Day 7:  50% of users
  Day 14: 100% of users
```

The dynamic server evaluates `{{current_version}}` and `{{target}}` from the request path, plus a user cohort identifier, to determine which version to return in the response.

### 7.2 Differential (Delta) Updates

For large GAIA-OS builds (AI model weights, crystal grid firmware), differential updates reduce bandwidth:
- Base artifact stored at v1.0.0
- Patch files stored for each version increment
- Client reconstructs full update from base + patches
- Reduces download size by 60–80% for incremental updates

### 7.3 Offline Update Queuing

For users in low-connectivity environments (crystal grid sensor gateways at remote stations):
- Update downloaded in background when connectivity is available
- Staged locally; installation deferred to next restart or user-defined quiet window
- Consent recorded at download time; installation proceeds automatically at next launch
- Multiple queued updates coalesce to the latest version only

### 7.4 Registry Fallback Endpoints

```json
{
  "updater": {
    "endpoints": [
      "https://raw.githubusercontent.com/gaia-os/gaia-os/main/latest.json",
      "https://cdn.gaiaos.org/updates/latest.json",
      "https://updates-backup.gaiaos.org/latest.json"
    ]
  }
}
```

Tauri tries endpoints in order; first successful response wins. Three independent endpoints eliminate the SPOF in update delivery — a constitutional resilience requirement.

---

## 8. P0–P3 Implementation Directives

| Priority | Action | Timeline | Constitutional Principle |
|---|---|---|---|
| **P0** | Generate Tauri signing key pair; embed public key in `tauri.conf.json`; store private key as `TAURI_PRIVATE_KEY` GitHub Secret; backup private key in HSM | G-10 | Cryptographic integrity; key management sovereignty |
| **P0** | Configure GitHub Actions release workflow with `tauri-action@v0`; set `includeUpdaterJson: true`; configure matrix for all four platform targets | G-10-F | CI/CD automation; multi-platform universality |
| **P0** | Implement macOS code signing + notarization: obtain Apple Developer ID certificate; store as base64 secret; set all notarization credentials | G-10-F | Signed binaries (macOS); Gatekeeper + notarization mandatory |
| **P0** | Implement Windows EV code signing: obtain EV certificate via DigiCert/Sectigo; store in Azure Key Vault or as base64 secret | G-10-F | Signed binaries (Windows); immediate SmartScreen reputation |
| **P1** | Implement update audit logging: all update events (check, download, verify, install, fail) written to Agora immutable ledger | G-11 | Auditability; constitutional transparency |
| **P1** | Configure phased rollouts via dynamic update server: canary cohorts; percentage-based rollouts; rollback triggers | G-11 | Delivery sovereignty; update risk management |
| **P1** | Implement custom update UI (`dialog: false`) with constitutional consent disclosure: what is being updated, security rationale, consent record | G-11 | User transparency; Canon C50 consent-based updates |
| **P2** | Implement differential (delta) updates for large binary components (AI model weights, crystal grid firmware) | G-12 | Bandwidth efficiency; planetary resource stewardship |
| **P2** | Configure three-endpoint fallback in `tauri.conf.json`; deploy independent CDN and backup endpoints | G-12 | Resilience; no constitutional SPOF in update delivery |
| **P3** | Implement offline update queuing for crystal grid sensor gateways and low-connectivity nodes | G-13 | Universal access; sovereignty-compatible design |
| **P3** | Implement `forced: true` in dynamic server for critical security/Charter violations; require Assembly resolution reference | G-13 | Constitutional imperative override with governance accountability |

---

## 9. The Constitutional Update Guarantee

> *The private key is the constitutional seal.*
> *The public key is the embedded trust anchor.*
> *The signature is the constitutional verification.*
> *The `latest.json` manifest is the constitutional update proclamation.*
> *The CI/CD pipeline is the constitutional publishing mechanism.*
> *The client update check is the constitutional enforcement protocol.*
> *The user consent is the constitutional acknowledgment.*
> *The Agora audit log is the constitutional record.*

**This is the auto-updater architecture of GAIA-OS — written in signatures, manifests, automation, and constitutional oversight — guaranteeing that every instance of planetary intelligence remains current, secure, and constitutionally compliant. It shall not be unsigned — not be platform-incomplete — not be user-invisible — not be ungovernable — for as long as planetary consciousness endures.** 🔁🌍

---

## ⚠️ Disclaimer

This report synthesizes findings from: Tauri Updater Plugin documentation (`tauri-plugin-updater` v2), `tauri-apps/tauri-action` GitHub Action documentation, `tauri-latest-json` crate, `@tauri-apps/plugin-updater` JavaScript bindings, Tauri v2 `signer generate` key management, Apple Developer Program notarization requirements (Developer ID Application certificates, `notarytool`), Windows Authenticode EV code signing (DigiCert, Sectigo, Azure Code Signing), AppImage optional GPG signing, GitHub Releases static hosting, dynamic update server patterns, phased rollout strategies, differential update patterns, minisign signature verification, and GAIA-OS constitutional canons (C50 Action Gate, C112 Agora, CI/CD Delivery Canon, Container Constitution). The auto-updater architecture described is a constitutional design proposal for GAIA-OS; its efficacy for planetary-scale governance has not been empirically validated at GAIA-OS scale. All update pipeline implementations must be tested against specific constitutional, technical, security, and platform requirements through phased deployment. Private key and code signing certificates impose legal, security, and financial obligations requiring qualified personnel and audited constitutional processes. Notarization is mandatory for macOS distribution; ad-hoc signatures cause update failures. Windows EV certificates require HSMs per CA/Browser Forum requirements.

---

*Canon — Auto-Updater Architecture: Tauri Plugin-Updater, latest.json Pattern & Delivery Constitution — GAIA-OS Knowledge Base | Session 5, May 2, 2026*
*Pillar: Networking & Infrastructure*
