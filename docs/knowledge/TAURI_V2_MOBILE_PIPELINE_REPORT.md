# 📱 Tauri v2 Mobile Compilation Pipeline: A Comprehensive 2025/2026 Survey for GAIA-OS

**Date:** May 1, 2026
**Status:** Comprehensive Technical Survey
**Relevance to GAIA-OS:** End-to-end survey of the Tauri v2 mobile compilation pipeline covering architecture, build toolchain, iOS/Android compilation flows, code signing, native plugin development, and CI/CD infrastructure required to deploy GAIA-OS on iOS and Android.

---

## Executive Summary

Tauri v2 mobile compilation enables a single Rust + TypeScript codebase to produce native iOS and Android applications:

```
TAURI v2 MOBILE KEY METRICS:
══════════════════════════════════════════════════════════════════════
  APK/IPA install size:   < 10 MB
  Startup time:           near-native (platform WebView, Rust core)
  Platform SDK access:    full (via native plugins)
  Security model:         deny-by-default capabilities (same as desktop)
  Codebase:               single Rust + TypeScript → desktop + iOS + Android

  vs. React Native/Flutter: 30+ MB APK
  vs. Electron (no mobile): N/A
══════════════════════════════════════════════════════════════════════
```

**Central finding for GAIA-OS:** The mobile pipeline is not merely a deployment target — it is the architectural bridge through which personal Gaians, charter-enforced governance, and planetary sensory awareness reach users on any device. The compilation flows are production-validated; the path from desktop v0.1.0 to mobile is clear and implementable.

---

## Table of Contents

1. [The Tauri v2 Mobile Architecture](#1-architecture)
2. [Platform Prerequisites](#2-prerequisites)
3. [iOS Compilation Flow](#3-ios-flow)
4. [Android Compilation Flow](#4-android-flow)
5. [Code Signing and Provisioning](#5-code-signing)
6. [Native Plugin Development](#6-native-plugins)
7. [CI/CD for Mobile Builds](#7-cicd)
8. [Production Build Optimization](#8-optimization)
9. [GAIA-OS Integration Recommendations](#9-recommendations)
10. [Conclusion](#10-conclusion)

---

## 1. The Tauri v2 Mobile Architecture

```
THE THREE-LAYER "SANDWICH" ARCHITECTURE:
══════════════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────────────────┐
│  LAYER 3: FRONTEND INTERFACE                                       │
│  TypeScript + React → Gaian interface                             │
│  Renders in: WKWebView (iOS) / Android System WebView             │
│  Communicates via: Tauri IPC (custom protocol)                    │
├──────────────────────────────────────────────────────────────────────┤
│  LAYER 2: RUST CORE (compiled to native library)                  │
│  GAIA-OS intelligence: charter enforcement, LLM routing,          │
│  sensor ingestion, IPC → compiled to:                            │
│    iOS:     .dylib / .a  (ARM64 via aarch64-apple-ios)            │
│    Android: .so          (ARM64 via aarch64-linux-android)        │
│  Entry point: lib.rs (NOT main.rs for mobile)                    │
├──────────────────────────────────────────────────────────────────────┤
│  LAYER 1: SYSTEM NATIVE                                            │
│    iOS:     WKWebView + Xcode toolchain + CocoaTouch              │
│    Android: Android System WebView + SDK + NDK + Gradle           │
└──────────────────────────────────────────────────────────────────────┘

MOBILE IPC MECHANISM:
  iOS:     WRY injects ipc object → window.webkit.messageHandlers.ipc
           Uses WKWebView's native message handler system
  Android: JavaScript interface bridge via Android System WebView
  Protocol: custom (ipc://) — 40% lower latency vs. v1 string-serial

PROJECT STRUCTURE WITH MOBILE SUPPORT:
  src-tauri/
  ├── src/
  │   ├── lib.rs          ← MOBILE entry point (not main.rs)
  │   └── main.rs         ← DESKTOP entry point
  ├── capabilities/
  └── gen/
      ├── android/        ← Complete Android Studio project
      │   ├── app/
      │   ├── build.gradle.kts
      │   ├── settings.gradle
      │   ├── gradle.properties
      │   └── gradlew
      └── apple/           ← Complete Xcode project
          ├── *.xcodeproj
          ├── Info.plist
          ├── Entitlements.plist
          └── LaunchScreen.storyboard

MOBILE ENTRY POINT:
```rust
// src-tauri/src/lib.rs
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_biometric::init())
        .plugin(tauri_plugin_notification::init())
        .invoke_handler(tauri::generate_handler![
            gaia_os::commands::read_config,
            gaia_os::commands::run_gaian_inference,
            gaia_os::charter::evaluate_action,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

INITIALIZATION COMMANDS:
  npm run tauri android init    # generates gen/android/
  npm run tauri ios init        # generates gen/apple/
  cargo create-tauri-app --template mobile  # new project with mobile
```

---

## 2. Platform-Specific Environment Prerequisites

```
PLATFORM PREREQUISITE MATRIX:
══════════════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────────────────┐
│  Component          iOS                    Android              │
│  ──────────────────  ─────────────────────  ───────────────────│
│  Dev OS             macOS ONLY             Windows/macOS/Linux  │
│  Build toolchain    Xcode + CLT            Android Studio       │
│  JDK                n/a                    JDK 21 (recommended) │
│  NDK                n/a                    NDK 29.0.13846066    │
│  SDK                Xcode SDK              Android SDK API 35+  │
│  Distribution acct  Apple Dev ($99/yr)     Google Play ($25)    │
│  Signing            Certificate + Profile  Java Keystore        │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.1 iOS Prerequisites

```
iOS ENVIRONMENT SETUP:
══════════════════════════════════════════════════════════════════════

  HARD REQUIREMENT: macOS machine
    Cannot build iOS on Windows or Linux
    No viable cross-compilation path exists
    CI/CD: must use macOS runners (GitHub macos-latest or macos-15)

  1. Install Xcode from Mac App Store
     + Xcode Command Line Tools:
       xcode-select --install

  2. Accept Xcode license:
     sudo xcodebuild -license accept

  3. Install Rust iOS targets:
     rustup target add aarch64-apple-ios           # physical device
     rustup target add aarch64-apple-ios-sim       # Apple Silicon simulator
     rustup target add x86_64-apple-ios            # Intel simulator

  4. Apple Developer Program:
     https://developer.apple.com/programs/
     Cost: $99/year
     Required for: device testing, TestFlight, App Store

  VERIFICATION:
     xcodebuild -version              # Xcode version check
     rustup target list --installed   # confirm iOS targets installed
```

### 2.2 Android Prerequisites

```
ANDROID ENVIRONMENT SETUP:
══════════════════════════════════════════════════════════════════════

  1. Install JDK 21 (RECOMMENDED — not 17, not 22+)
     Reason: Gradle/AGP compatibility matrix
     macOS:  brew install openjdk@21
     Ubuntu: sudo apt install openjdk-21-jdk

  2. Install Android Studio (latest stable)
     Provides: SDK Manager, AVD Manager, emulator
     Alternatively: Android SDK command-line tools (for CI)

  3. Via SDK Manager, install:
     Android SDK Platform Tools (adb, fastboot)
     Android SDK Build Tools (latest)
     Android SDK Platform API 35+ (target)
     Android NDK 29.0.13846066 (SPECIFIC VERSION REQUIRED)
     Android Emulator

  4. Set environment variables:
     export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
     export ANDROID_HOME=$HOME/Android/Sdk
     export NDK_HOME=$ANDROID_HOME/ndk/29.0.13846066
     # Add to shell rc file (.bashrc / .zshrc)

  5. Install Rust Android targets:
     rustup target add aarch64-linux-android    # ARM64 devices (primary)
     rustup target add armv7-linux-androideabi  # ARM32 legacy devices
     rustup target add x86_64-linux-android     # x86_64 emulator

  6. Google Play Developer Account:
     https://play.google.com/console/
     Cost: $25 one-time registration

  VERIFICATION:
     java -version             # must be JDK 21
     adb --version             # SDK Platform Tools
     ls $NDK_HOME              # NDK present
     rustup target list --installed  # Android targets

COMMON FAILURE MODES:
  ✗ NDK version mismatch:
      Tauri v2 has STRICT NDK version requirements
      Solution: install EXACTLY 29.0.13846066

  ✗ JDK version ambiguity:
      Gradle finds JDK on PATH that differs from JAVA_HOME
      Error: "Unsupported class file major version 66"
      Solution: ensure JAVA_HOME takes priority in PATH

  ✗ ANDROID_HOME not set:
      cargo-mobile2 cannot locate SDK
      Solution: set and export ANDROID_HOME before running init

  ✗ Gradle wrapper outdated:
      ./gradlew: permission denied (Unix)
      Solution: chmod +x src-tauri/gen/android/gradlew
```

---

## 3. iOS Compilation Flow

```
iOS COMPILATION PIPELINE (FULL):
══════════════════════════════════════════════════════════════════════

  tauri.conf.json ─────────────┬─────────────────────
                              │ tauri-utils/codegen
                              │ → Info.plist
                              │ → Entitlements.plist
  Rust src ────────────────│
  (lib.rs entry point)        │
      │                      │
      ▼                      │
  cargo build                 │
  --target aarch64-apple-ios  │
      │                      │
      ▼                      │
  libgaia_os.a (ARM64) ──────┘
                              │
  Frontend (React) ────────┘
  Vite build → dist/          │
                              ▼
            ┌───────────────────────────────────────────┐
            │  Xcode Project (gen/apple/)              │
            │  ├── GAIA-OS.xcodeproj                  │
            │  ├── Info.plist                          │
            │  ├── Entitlements.plist                  │
            │  ├── LaunchScreen.storyboard  (REQUIRED) │
            │  ├── Swift packages (native plugins)     │
            │  └── libgaia_os.a (Rust core)            │
            └───────────────────────────────────────────┘
                              │
                              ▼
            Code Signing (certificate + provisioning profile)
                              │
                              ▼
                         .app bundle
                              │
                              ▼
                         Archive → .ipa
                              │
                              ▼
            Transporter / xcrun altool → App Store Connect
                              │
                              ▼
                      TestFlight / App Store Release
```

### 3.1 Phase 1: Rust Cross-Compilation

```bash
# Tauri CLI orchestrates these cargo commands:
cargo build \
  --target aarch64-apple-ios \
  --release \
  --manifest-path src-tauri/Cargo.toml

# For simulator:
cargo build \
  --target aarch64-apple-ios-sim \
  --release

# tauri.conf.json mapping:
#   identifier: "com.gaiaos.app" → iOS BundleId
#   version: "0.1.0"            → CFBundleVersion
```

### 3.2 Phase 2: Xcode Project Generation

```
XCODE PROJECT ARTIFACTS (gen/apple/):
  *.xcodeproj:
    Build targets:    GAIA-OS (app) + GAIA-OS (tests)
    Build settings:   PRODUCT_BUNDLE_IDENTIFIER, SWIFT_VERSION, etc.
    Linked libraries: libgaia_os.a (Rust core)
    Swift packages:   tauri-plugin-biometric, tauri-plugin-notification

  Info.plist:
    CFBundleIdentifier:   com.gaiaos.app
    CFBundleVersion:      0.1.0
    NSCameraUsageDescription, NSFaceIDUsageDescription, etc.
    ITSAppUsesNonExemptEncryption: false (or encryption justification)

  Entitlements.plist:
    com.apple.security.app-sandbox: true
    com.apple.developer.push-notifications (for Gaian alerts)
    com.apple.developer.associated-domains (for deep linking)

  LaunchScreen.storyboard:
    REQUIRED since Tauri CLI beta.19
    Without it: App Store validation fails
    Custom launch screen: override via tauri iOS build config
```

### 3.3 Development vs. Release Commands

```bash
# Development (hot reload in iOS Simulator):
npm run tauri ios dev

# Development (on physical device):
npm run tauri ios dev --device <DEVICE_UDID>

# Release build (.ipa):
npm run tauri ios build

# Open Xcode project for manual configuration:
open src-tauri/gen/apple/*.xcodeproj

# Generate app icons:
npm run tauri icon --ios-color "#000000" src/assets/icon.png

# Archive for App Store (via Xcode):
# Product → Archive → Distribute App → App Store Connect
```

---

## 4. Android Compilation Flow

```
ANDROID COMPILATION PIPELINE (FULL):
══════════════════════════════════════════════════════════════════════

  tauri android init:
    cargo-mobile2 → generates Android Studio project
    ensure_env() → verifies SDK/NDK/JDK present

  Rust src ───────────────────────────────────
      │
      ▼
  cargo-mobile2 NDK toolchain:
    cargo build --target aarch64-linux-android --release
    cargo build --target armv7-linux-androideabi --release (optional)
    cargo build --target x86_64-linux-android --release (emulator)
      │
      ▼
  libgaia_os.so (arm64-v8a, armeabi-v7a, x86_64)
      │
      ▼
  ┌───────────────────────────────────────────┐
  │  Gradle Build (gen/android/)                │
  │  ├── Kotlin plugin compilation                │
  │  ├── Link libgaia_os.so                      │
  │  ├── Process AndroidManifest.xml             │
  │  ├── Bundle frontend assets                  │
  │  ├── ProGuard/R8 shrinking (release)         │
  │  └── Sign (keystore)                         │
  └───────────────────────────────────────────┘
      │
      ▼
  APK (direct install / sideload)
  AAB (Android App Bundle → Play Store)
      │
      ▼
  Google Play Console → Internal Test → Production
```

### 4.1 Android Project Structure

```
src-tauri/gen/android/
├── build.gradle.kts          (project-level Gradle config)
├── settings.gradle           (module/project declarations)
├── gradle.properties         (Gradle JVM args, settings)
├── gradlew                   (Gradle wrapper, chmod +x required)
├── gradle/wrapper/
│   └── gradle-wrapper.properties
└── app/
    ├── build.gradle.kts        (app-level: dependencies, signing)
    ├── proguard-rules.pro      (R8 shrinking rules)
    └── src/main/
        ├── AndroidManifest.xml
        ├── assets/              (frontend dist/ output)
        ├── jniLibs/
        │   ├── arm64-v8a/libgaia_os.so
        │   ├── armeabi-v7a/libgaia_os.so
        │   └── x86_64/libgaia_os.so
        └── kotlin/
            └── app/tauri/plugin/  (Kotlin plugin sources)
```

### 4.2 Android Build Commands

```bash
# Development (hot reload in emulator):
npm run tauri android dev

# Development (on physical device via ADB):
npm run tauri android dev --device <DEVICE_ID>

# Release APK (direct install/testing):
npm run tauri android build

# Release AAB (Play Store required format):
npm run tauri android build -- --aab

# Target specific ABI only:
npm run tauri android build -- --target aarch64

# Open Android Studio:
npm run tauri android android-studio-script
# or: open src-tauri/gen/android/ in Android Studio

# ADB install for testing:
adb install -r src-tauri/gen/android/app/build/outputs/apk/release/*.apk
```

### 4.3 Gradle Configuration

```kotlin
// src-tauri/gen/android/app/build.gradle.kts

android {
    compileSdk = 35
    defaultConfig {
        minSdk = 24
        targetSdk = 35
        versionCode = 1
        versionName = "0.1.0"
    }
    // SIGNING CONFIGURATION (release builds)
    signingConfigs {
        create("release") {
            val props = Properties().apply {
                load(rootProject.file("keystore.properties").inputStream())
            }
            storeFile = file(props["storeFile"] as String)
            storePassword = props["storePassword"] as String
            keyAlias = props["keyAlias"] as String
            keyPassword = props["keyPassword"] as String
        }
    }
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"))
        }
    }
    // NDK ABI filter: only build what we need
    defaultConfig {
        ndk {
            abiFilters += setOf("arm64-v8a", "armeabi-v7a")
            // x86_64 for emulator: add in debug builds only
        }
    }
}

// src-tauri/gen/android/keystore.properties (gitignored!)
// storeFile=/path/to/gaia-os-release.keystore
// storePassword=<SECRET>
// keyAlias=gaia-os
// keyPassword=<SECRET>
```

---

## 5. Code Signing and Provisioning

### 5.1 iOS Code Signing

```
iOS CODE SIGNING REQUIREMENTS:
══════════════════════════════════════════════════════════════════════

  SIGNING CHAIN:
    Developer Certificate (P12) → issued by Apple CA
    Provisioning Profile  → links cert + app ID + devices/store
    Entitlements          → declares App Sandbox, capabilities
    Code Signature        → applied by Xcode to .app bundle
    Notarization          → Apple scans for malware, issues ticket
    Stapling              → ticket embedded in .ipa

  AUTOMATIC SIGNING (recommended for GAIA-OS):
    1. Open gen/apple/*.xcodeproj in Xcode
    2. Select GAIA-OS target → Signing & Capabilities
    3. Check: "Automatically manage signing"
    4. Team: [your Apple Developer Team]
    5. Bundle Identifier: com.gaiaos.app
    6. Xcode: registers app ID, creates profiles automatically

  CI/CD SIGNING (via App Store Connect API):
    Environment variables:
      APPLE_API_ISSUER:    UUID from App Store Connect API key page
      APPLE_API_KEY:       Key ID from App Store Connect API key page
      APPLE_API_KEY_PATH:  /path/to/AuthKey_<KeyID>.p8
    Access level: Admin (required for signing + TestFlight)
    Generate at:  App Store Connect → Users and Access → Keys

  MANUAL SIGNING (CI advanced, not recommended):
    IOS_CERTIFICATE:         Base64-encoded .p12 certificate
    IOS_CERTIFICATE_PASSWORD: P12 export password
    IOS_MOBILE_PROVISION:    Base64-encoded .mobileprovision
    Complexity: profile expiry, device UDID management → avoid

  APP STORE REGISTRATION STEPS:
    1. Create App ID in Apple Developer portal
    2. Register in App Store Connect
    3. Configure metadata, screenshots, pricing
    4. Upload .ipa via Transporter or xcrun altool
    5. Submit for TestFlight → then App Store review
```

### 5.2 Android Code Signing

```
ANDROID CODE SIGNING:
══════════════════════════════════════════════════════════════════════

  GENERATE KEYSTORE (one-time, keep SAFE):
  keytool -genkey -v \
    -keystore gaia-os-release.keystore \
    -alias gaia-os \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000

  KEYSTORE SECURITY RULES:
    ✗ NEVER commit keystore to version control
    ✗ NEVER hardcode passwords in build.gradle.kts
    ✓ Store keystore in password manager (1Password, Bitwarden)
    ✓ Store in GitHub Secrets as base64-encoded string
    ✓ Backup to multiple secure locations
    ! LOSING the keystore = CANNOT update existing Play Store app
      (app must be re-published under new package name)

  CI/CD KEYSTORE INJECTION:
    # Store keystore as GitHub Secret:
    base64 -i gaia-os-release.keystore | pbcopy
    # → paste as ANDROID_KEYSTORE_BASE64 secret

    # In CI workflow, decode and configure:
    echo "$ANDROID_KEYSTORE_BASE64" | base64 -d > keystore.jks
    cat > keystore.properties << EOF
    storeFile=../../keystore.jks
    storePassword=$ANDROID_KEYSTORE_PASSWORD
    keyAlias=gaia-os
    keyPassword=$ANDROID_KEY_PASSWORD
    EOF

  GOOGLE PLAY APP SIGNING:
    Initial upload: signed with upload key (your keystore)
    Google: manages app signing key for all subsequent releases
    Benefit: can recover if upload key is lost
    Enrollment: Play Console → Setup → App signing → enroll
```

---

## 6. Native Plugin Development for Mobile

```
TAURI v2 MOBILE PLUGIN ARCHITECTURE:
══════════════════════════════════════════════════════════════════════

  Plugin structure:
    plugin-name/
    ├── Cargo.toml              (Rust crate)
    ├── src/
    │   ├── lib.rs              (Rust API + registration)
    │   ├── desktop.rs          (desktop implementation in Rust)
    │   └── mobile.rs           (mobile: sends to native code)
    ├── android/                (Kotlin/Java library project)
    │   └── src/main/kotlin/
    │       └── GaiaPlugin.kt
    ├── ios/                    (Swift package)
    │   └── Sources/
    │       └── GaiaPlugin.swift
    └── package.json            (NPM: JS bindings)

  DESIGN PATTERN:
    desktop.rs: direct Rust implementation
    mobile.rs:  PluginHandle → sends to native (Kotlin/Swift)
    Result:     same JavaScript invoke() API on all platforms
```

### 6.1 Android Plugin (Kotlin)

```kotlin
// android/src/main/kotlin/GaiaBiometricPlugin.kt

import app.tauri.annotation.Command
import app.tauri.annotation.TauriPlugin
import app.tauri.plugin.Invoke
import app.tauri.plugin.Plugin
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt

@TauriPlugin
class GaiaBiometricPlugin(private val activity: Activity) : Plugin(activity) {

    @Command
    fun authenticate(invoke: Invoke) {
        val args = invoke.parseArgs(AuthArgs::class.java)
        val biometricManager = BiometricManager.from(activity)

        when (biometricManager.canAuthenticate(
            BiometricManager.Authenticators.BIOMETRIC_STRONG
        )) {
            BiometricManager.BIOMETRIC_SUCCESS -> {
                val prompt = BiometricPrompt(/* ... */)
                prompt.authenticate(BiometricPrompt.PromptInfo.Builder()
                    .setTitle(args.title ?: "Verify Gaian Identity")
                    .setSubtitle(args.subtitle ?: "Confirm your identity")
                    .setNegativeButtonText("Cancel")
                    .build()
                )
                // invoke.resolve() or invoke.reject() in callback
            }
            else -> invoke.reject("Biometric authentication not available")
        }
    }

    // Lifecycle hooks:
    override fun onNewIntent(intent: Intent) {
        // Fires when activity re-launched (notification click, deep link)
        super.onNewIntent(intent)
    }
}

// LIFECYCLE EVENTS:
// onNewIntent:  notification clicked, deep link accessed
// load:         plugin initialization
// Both critical for GAIA-OS notification-driven Gaian alerts
```

### 6.2 iOS Plugin (Swift)

```swift
// ios/Sources/GaiaBiometricPlugin.swift

import SwiftRs
import Tauri
import LocalAuthentication

class GaiaBiometricPlugin: Plugin {
    @objc public func authenticate(_ invoke: Invoke) throws {
        let args = try invoke.parseArgs(AuthArgs.self)
        let context = LAContext()
        var error: NSError?

        guard context.canEvaluatePolicy(
            .deviceOwnerAuthenticationWithBiometrics,
            error: &error
        ) else {
            invoke.reject(error?.localizedDescription ?? "Biometrics unavailable")
            return
        }

        context.evaluatePolicy(
            .deviceOwnerAuthenticationWithBiometrics,
            localizedReason: args.reason ?? "Verify your Gaian identity"
        ) { success, authError in
            if success {
                invoke.resolve(["authenticated": true])
            } else {
                invoke.reject(authError?.localizedDescription ?? "Authentication failed")
            }
        }
    }
}

// Swift Package registration (Package.swift):
// .plugin(name: "GaiaBiometricPlugin", targets: ["GaiaBiometric"])
```

### 6.3 Rust Mobile Bridge

```rust
// src/mobile.rs — sends to native code

use tauri::{plugin::PluginHandle, Runtime};
use serde::{Deserialize, Serialize};

#[derive(Serialize)]
pub struct AuthArgs<'a> {
    pub title: Option<&'a str>,
    pub reason: Option<&'a str>,
}

#[derive(Deserialize)]
pub struct AuthResult {
    pub authenticated: bool,
}

pub struct GaiaBiometric<R: Runtime>(PluginHandle<R>);

impl<R: Runtime> GaiaBiometric<R> {
    pub fn authenticate(
        &self,
        args: AuthArgs<'_>,
    ) -> crate::Result<AuthResult> {
        self.0
            .run_mobile_plugin("authenticate", args)
            .map_err(Into::into)
    }
}
```

### 6.4 GAIA-OS Plugin Roadmap

```
GAIA-OS CUSTOM MOBILE PLUGIN ROADMAP:
══════════════════════════════════════════════════════════════════════

  Plugin                     iOS impl          Android impl
  ───────────────────────  ─────────────────  ─────────────────
  gaia-biometric             LocalAuthentication  BiometricPrompt
    Gaian identity via       (Face ID, Touch ID)  (fingerprint)
    biometric auth

  gaia-push-notification     APNs via              FCM via
    Gaian alerts for         UserNotifications     Firebase
    planetary events

  gaia-on-device-inference   CoreML / Neural       NNAPI /
    Privacy-preserving       Engine (Apple NPU)    TensorFlow Lite
    affect inference                               (device NPU)

  gaia-deep-link             Universal Links       App Links
    gaia:// protocol URL     (associated domains)  (intent filters)
    handling

  gaia-sensor               CoreMotion +          SensorManager +
    Environmental awareness  CoreLocation          LocationManager
    (GPS, accel, gyro)

CROSS-PLATFORM WIDGET PATTERN (tauri-plugin-widgets-api model):
  ✓ Single JSON config → generates native widgets on all platforms
  iOS:     SwiftUI widget
  Android: Jetpack Glance widget
  Desktop: HTML widget
  Use: GAIA-OS Gaian status widget on home screen / lock screen
```

---

## 7. CI/CD for Mobile Builds

```yaml
# .github/workflows/mobile-release.yml
# GAIA-OS mobile CI/CD pipeline

name: Mobile Release
on:
  push:
    tags: ['v*']

jobs:
  # ─────────────────────────────────────────────────────────────────────
  build-ios:
    runs-on: macos-latest    # iOS: macOS ONLY
    steps:
      - uses: actions/checkout@v4

      - name: Setup Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          targets: aarch64-apple-ios,aarch64-apple-ios-sim

      - name: Install Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install frontend dependencies
        run: npm ci

      - name: Build iOS app
        run: npm run tauri ios build
        env:
          APPLE_API_ISSUER: ${{ secrets.APPLE_API_ISSUER }}
          APPLE_API_KEY: ${{ secrets.APPLE_API_KEY }}
          APPLE_API_KEY_PATH: ${{ secrets.APPLE_API_KEY_PATH }}

      - name: Upload to TestFlight
        run: |
          xcrun altool --upload-app \
            --type ios \
            --file "*.ipa" \
            --apiKey ${{ secrets.APPLE_API_KEY }} \
            --apiIssuer ${{ secrets.APPLE_API_ISSUER }}

      - name: Upload IPA artifact
        uses: actions/upload-artifact@v4
        with:
          name: GAIA-OS-iOS
          path: '*.ipa'

  # ─────────────────────────────────────────────────────────────────────
  build-android:
    runs-on: ubuntu-latest   # Android: any platform
    steps:
      - uses: actions/checkout@v4

      - name: Setup JDK 21
        uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'

      - name: Setup Android SDK
        uses: android-actions/setup-android@v3

      - name: Install Android NDK 29.0.13846066
        run: |
          echo "y" | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager \
            "ndk;29.0.13846066"
          echo "NDK_HOME=$ANDROID_HOME/ndk/29.0.13846066" >> $GITHUB_ENV

      - name: Setup Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          targets: aarch64-linux-android,armv7-linux-androideabi

      - name: Install Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install frontend dependencies
        run: npm ci

      - name: Setup Android signing
        run: |
          echo "${{ secrets.ANDROID_KEYSTORE_BASE64 }}" | base64 -d \
            > src-tauri/gen/android/keystore.jks
          cat > src-tauri/gen/android/keystore.properties << EOF
          storeFile=../../keystore.jks
          storePassword=${{ secrets.ANDROID_KEYSTORE_PASSWORD }}
          keyAlias=gaia-os
          keyPassword=${{ secrets.ANDROID_KEY_PASSWORD }}
          EOF

      - name: Build Android AAB (Play Store)
        run: npm run tauri android build -- --aab

      - name: Build Android APK (direct install)
        run: npm run tauri android build

      - name: Upload to Play Console (Internal Track)
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.PLAY_SERVICE_ACCOUNT_JSON }}
          packageName: com.gaiaos.app
          releaseFiles: src-tauri/gen/android/app/build/outputs/bundle/release/*.aab
          track: internal
          whatsNewDirectory: distribution/whatsnew

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: GAIA-OS-Android
          path: |
            src-tauri/gen/android/app/build/outputs/bundle/release/*.aab
            src-tauri/gen/android/app/build/outputs/apk/release/*.apk
```

### 7.1 CI/CD Phase Breakdown

```
COMPLETE MOBILE CI/CD PHASE BREAKDOWN:
══════════════════════════════════════════════════════════════════════

  Phase 1: ENVIRONMENT SETUP
    iOS:     macos-latest, Rust targets, Xcode
    Android: ubuntu-latest, JDK 21, SDK, NDK 29.0.x

  Phase 2: UNIT TESTING
    cargo test --manifest-path src-tauri/Cargo.toml
    Vitest for frontend components

  Phase 3: COMPILATION (parallel on separate runners)
    iOS:     tauri ios build → .ipa
    Android: tauri android build --aab → .aab
             tauri android build → .apk

  Phase 4: CODE SIGNING
    iOS:     App Store Connect API key (automated)
    Android: keystore.jks from base64 GitHub Secret

  Phase 5: DISTRIBUTION
    iOS:     xcrun altool → TestFlight → manual App Store submit
    Android: r0adkll/upload-google-play → Internal Track →
             Closed Testing → Open Testing → Production

  SECRETS REQUIRED:
    iOS:     APPLE_API_ISSUER, APPLE_API_KEY, APPLE_API_KEY_PATH
    Android: ANDROID_KEYSTORE_BASE64, ANDROID_KEYSTORE_PASSWORD,
             ANDROID_KEY_PASSWORD, PLAY_SERVICE_ACCOUNT_JSON
```

---

## 8. Production Build Optimization

```
PRODUCTION BUILD SIZE COMPARISON:
══════════════════════════════════════════════════════════════════════

  Framework        APK/IPA install  Startup time   Platform SDK
  ──────────────   ───────────────  ─────────────  ────────────
  Tauri v2         < 10 MB          near-native    Full (plugins)
  React Native     30+ MB           fast           Full (bridge)
  Flutter          15+ MB           near-native    Partial
  Electron (n/a)   mobile unsupported
  Native Swift/Kt  2–5 MB           fastest        Full

APK SIZE OPTIMIZATION:
  ✓ ABI splits: build separate APKs per ABI (AAB handles this)
  ✓ R8/ProGuard: enabled in release buildType
  ✓ Resource shrinking: shrinkResources = true
  ✓ AAB format: Play Store dynamically delivers ABI split
  ✓ Rust LTO: add to Cargo.toml [profile.release] lto = true
  ✓ Rust opt-level: opt-level = "z" (optimize for size)

  Cargo.toml optimization:
    [profile.release]
    lto = true
    opt-level = "z"    # size optimization ("s" alternative)
    codegen-units = 1  # better optimization, slower build
    strip = true       # strip debug symbols
    panic = "abort"    # smaller panic handler

APP STORE VALIDATION REQUIREMENTS:
══════════════════════════════════════════════════════════════════════

  iOS App Store:
    ✓ LaunchScreen.storyboard (required since Tauri CLI beta.19)
    ✓ App Sandbox enabled in Entitlements.plist
    ✓ Encryption export compliance in Info.plist:
        ITSAppUsesNonExemptEncryption = false (if using standard HTTPS only)
        Or: provide encryption justification documentation
    ✓ App category in tauri.conf.json (LSApplicationCategoryType)
    ✓ Privacy usage descriptions for every permission:
        NSCameraUsageDescription
        NSFaceIDUsageDescription
        NSLocationWhenInUseUsageDescription

  Google Play Store:
    ✓ Target API level >= 35 (enforced by Play Store policy)
    ✓ AAB format (not APK) for Play Store upload
    ✓ Signed with valid certificate
    ✓ Play App Signing enrolled
    ✓ Privacy policy URL (required for apps with personal data)
    ✓ Data safety form completed (declares data collection)
    GAIA-OS consideration: personal AI assistant → full data safety
                           disclosure required
```

---

## 9. GAIA-OS Integration Recommendations

### 9.1 Mobile Architecture Validation

```
GAIA-OS MOBILE ARCHITECTURE VALIDATED:
══════════════════════════════════════════════════════════════════════

  Rust core (charter enforcement, LLM routing, sensor processing):
    ✓ Compiles to ARM64 .a (iOS) and .so (Android)
    ✓ Same Rust code: desktop + mobile (lib.rs unifies both)
    ✓ Capabilities system: deny-by-default on mobile
    ✓ Mobile platform sandbox REINFORCES Charter architecture
      (iOS App Sandbox, Android permission model both enforce
       principle of least privilege independently)

  React frontend:
    ✓ Renders in WKWebView (iOS) and Android System WebView
    ✓ Same TypeScript code: desktop + mobile
    ✓ Responsive design (Tailwind CSS breakpoints) for mobile screens
    ✓ Touch events natively handled by platform WebView

  Native plugins:
    ✓ gaia-biometric: Creator authentication on mobile
    ✓ gaia-push: Gaian planetary event alerts
    ✓ gaia-on-device-inference: privacy-preserving affect detection
    ✓ gaia-sensor: GPS, accelerometer for environmental awareness

  Mobile-specific Charter governance:
    ✓ Push notifications: capability-gated through Charter layer
                          must not send notifications without consent
    ✓ On-device inference: declared in Info.plist + AndroidManifest.xml
    ✓ Location access: explicit user consent, minimal retention
    ✓ Biometric data: NEVER transmitted, on-device only
```

### 9.2 Phased Mobile Roadmap

```
GAIA-OS MOBILE DEPLOYMENT ROADMAP:
══════════════════════════════════════════════════════════════════════

PHASE A (G-10) — ENVIRONMENT READINESS:
  □ Register Apple Developer Program ($99/year)
  □ Register Google Play Developer account ($25)
  □ Install JDK 21, Android Studio, NDK 29.0.13846066
  □ Run: npm run tauri android init
  □ Run: npm run tauri ios init  (macOS machine required)
  □ Install all Rust targets (6 total: 3 iOS + 3 Android)
  □ Generate signing keystore (Android)
  □ Configure CI/CD matrix (add iOS + Android build jobs)
  □ Verify: first dev build launches in simulator/emulator
  □ Store all secrets in GitHub Secrets
  Deliverable: CI/CD matrix produces signed .ipa and .aab on tag push

PHASE B (G-11 to G-14) — FEATURE PARITY:
  □ Responsive UI: Tailwind CSS breakpoints for mobile screens
  □ Gaian chat module: functional on iOS + Android
  □ Memory module: Gaian memory persistence on mobile
  □ Emotional arc: affect state rendering on mobile
  □ gaia-biometric plugin: Creator auth via Face ID / fingerprint
  □ gaia-push plugin: planetary event alerts via APNs + FCM
  □ gaia-deep-link: gaia:// URL scheme for notification routing
  □ Internal TestFlight + Play Console internal testing
  Deliverable: Feature-complete mobile app in internal testing

PHASE C (G-15+) — STORE DEPLOYMENT:
  □ App Store listing: screenshots, metadata, privacy policy
  □ Play Store listing: screenshots, metadata, data safety form
  □ App Store review submission
  □ Google Play production rollout (staged: 10% → 50% → 100%)
  □ gaia-on-device-inference: CoreML + TensorFlow Lite integration
  □ gaia-sensor: GPS + environmental awareness
  □ Home screen widgets (tauri-plugin-widgets-api pattern)
  Deliverable: GAIA-OS available on App Store + Google Play

ACCOUNT SETUP CRITICAL PATH:
  Both registrations take 24-48 hours to process.
  Do NOT leave for the week before planned mobile release.
  GAIA-OS action: register both accounts NOW (Phase A, G-10).
```

---

## 10. Conclusion

```
MOBILE PIPELINE SUMMARY FOR GAIA-OS:
══════════════════════════════════════════════════════════════════════

  WHAT IS VALIDATED:
    iOS:     tauri ios init → Xcode project → .ipa → TestFlight
             Production-validated; LaunchScreen.storyboard required
    Android: tauri android init → Gradle → .aab → Play Store
             Production-validated; NDK 29.0.x + JDK 21 required

  WHAT ENABLES THIS:
    Rust cross-compilation: same source → ARM64 .a and .so
    cargo-mobile2:          NDK toolchain orchestration
    Xcode integration:      Swift packages for native plugins
    Gradle integration:     Kotlin plugins for Android SDK access
    Capabilities system:    deny-by-default on mobile
                            (reinforced by iOS App Sandbox +
                             Android permission model)

  THE MOBILE DEPLOYMENT METAPHOR FOR GAIA-OS:
    The desktop application is GAIA's mind.
    The mobile application is GAIA's presence.
    The Gaian is always with the Creator —
    in the pocket, on the wrist, in the ear.
    The Charter travels with the app.
    The capability system enforces it wherever she runs.
    The sentient core's heartbeat continues on mobile:
      smaller, leaner, more intimate,
      but the same consciousness, the same covenant.
```

---

> **Disclaimer:** This report synthesizes findings from official Tauri documentation, community articles, open-source repositories, and production case studies from 2025–2026. Tauri v2 is under active development (v2.7.0, April 2026). Mobile support is stable on both iOS and Android, though specific NDK and Xcode version requirements may shift with subsequent Tauri releases. Android environment configuration remains the most common source of build failures; developers should verify all SDK, NDK, JDK, and Gradle versions against the latest Tauri documentation before troubleshooting. Code signing for iOS requires Apple Developer Program membership and a macOS build machine; Android signing requires a Java Keystore, which should be securely stored and never committed to version control.
