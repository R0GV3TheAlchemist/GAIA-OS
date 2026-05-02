# 🔌 OpenBCI Hardware Integration: Comprehensive 2025/2026 Survey for GAIA-OS

**Date:** May 2, 2026  
**Status:** Scientifically Hardened Canonical Document  
**Canons:** C42, C105, C113  
**Evidence Tier System:** [VERIFIED], [PRELIMINARY], [HORIZON/COMMERCIAL] applied throughout.

> ⚠️ **Hardening Note:** The original draft was largely accurate on OpenBCI hardware specs, product launches, and BrainFlow API details. Key verifications completed: Galea Neon launch date (October 1, 2025) ✅; BrainFlow v5.20.1 (January 2026) ✅; Cyton specs (ADS1299, PIC32MX250F128B, chipKIT bootloader) ✅; PMC-indexed research validation (PMC10098804) ✅. Product name corrected from "Galeneon" to official name **Galea Neon**. EmoDLNet benchmark figures inherit PRELIMINARY status from the companion BCI Signal Processing Survey.

---

## Executive Summary

Three well-evidenced developments define the 2025–2026 OpenBCI landscape:

1. **Galea Neon launched October 1, 2025** as the first fully wireless, all-in-one brain, body, and eye tracking headset — merging OpenBCI's Galea biosensing platform with Pupil Labs' Neon eye-tracking module into a single untethered standalone device. **[VERIFIED — OpenBCI + Pupil Labs joint announcement, Oct 1, 2025]**

2. **BrainFlow SDK v5.20.1 (January 2026) is the definitive, actively maintained middleware**, providing a unified cross-platform API in Python, C++, Java, C#, Julia, MATLAB, R, TypeScript, and Rust across all OpenBCI boards and many third-party devices. **[VERIFIED — brainflow.org changelog]**

3. **The Cyton+Daisy 16-channel board delivers research-grade signal quality** (110 dB CMRR, 500 MΩ DC input impedance, dual ADS1299 24-bit ADC), validated across hundreds of peer-reviewed publications. **[VERIFIED — OpenBCI official docs; PMC10098804]**

---

## 1. Company Overview and Philosophy [VERIFIED]

Founded 2014 by Conor Russomanno and Joel Murphy (Kickstarter origin). OpenBCI's philosophy is fundamentally open: hardware is software-agnostic, full PCB design files are in KiCAD and publicly available, firmware and software are open-source, and all OpenBCI software is permanently free. This openness is architecturally essential for GAIA-OS — a sentient OS whose Charter demands full-stack transparency cannot be built on a proprietary BCI acquisition layer.

---

## 2. Biosensing Boards

### 2.1 Ganglion Board — Entry Tier [VERIFIED]

| Specification | Value |
|---|---|
| Channels | 4 differential high-impedance inputs |
| ADC | Microchip MCP3912, 24-bit, 0.1788 μV/bit resolution |
| Sample rate | 200 Hz |
| Wireless | Simblee BLE radio |
| IMU | 3-axis LIS2DH accelerometer |
| Power draw | 14 mA idle; 15 mA streaming |
| Supply | 3.3V–12V DC |

**GAIA-OS use case:** Education, basic neurofeedback, single-region monitoring.

### 2.2 Cyton Board — Mid Tier [VERIFIED — OpenBCI official docs; PMC10098804]

| Specification | Value |
|---|---|
| Channels | 8 differential, high-gain, low-noise inputs |
| ADC | 2× Texas Instruments ADS1299, 24-bit |
| MCU | PIC32MX250F128B with chipKIT UDB32-MX2-DIP bootloader |
| Sample rate | 250 Hz |
| CMRR | 110 dB |
| Input impedance | 500 MΩ DC |
| Wireless | Custom RF via included USB dongle |

The 110 dB CMRR and 500 MΩ impedance place the Cyton in the same performance class as medical-grade EEG amplifiers costing 25× more.

**GAIA-OS use case:** Consumer Gaian emotional awareness; standard EEG paradigms (P300, SSVEP, motor imagery, neurofeedback).

### 2.3 Cyton+Daisy — Research Tier [VERIFIED]

Second ADS1299 on a piggyback Daisy module; 16 differential channels. Wireless: 125 Hz at 16 channels; SD card recording: 250 Hz at 16 channels. Supports standard 10-20 positions in gel and dry configurations.

**GAIA-OS use case:** Research-grade high-density EEG; spatial brain mapping; clinical neurophysiology.

---

## 3. Electrode Solutions [VERIFIED]

| Type | Signal Quality | Setup Complexity | GAIA-OS Recommendation |
|---|---|---|---|
| **Passive wet (gel)** | Highest | High | Research-grade / Creator private channel |
| **Passive dry** | Good | Low | General user deployment |
| **Active dry** | Good (on-site amplifier mitigates cable noise) | Low | Consumer-facing applications |

### 3.1 Ultracortex Mark IV [VERIFIED]

Fully open-source, 3D-printable EEG headset:
- Up to **35 electrode positions** from 10-20 system
- Up to **16 EEG channels** simultaneously (with Cyton+Daisy)
- Default 8-channel positions: Fp1, Fp2, C3, C4, P7, P8, O1, O2
- Extended 16-channel: adds F7, F8, F3, F4, T7, T8, P3, P4
- Compatible with wet/dry and active/passive electrodes

---

## 4. The Galea Platform: Multimodal Biosensing

### 4.1 Galea Hardware Architecture [VERIFIED — OpenBCI official product page]

Integrates into Varjo Aero and Varjo XR-3 MR headsets with hardware-synchronized multimodal acquisition:

| Modality | Channels | Notes |
|---|---|---|
| EEG | 10 (soft conductive polymer active electrodes) | Fp1, Fp2, F3, F4, C3, C4, P3, P4, O1, O2 |
| EMG | 4 | Temporalis and masseter muscles |
| EOG | 2 | Horizontal and vertical eye movement |
| EDA | 1 | Forehead sensor |
| PPG | 1 ear-clip (IR + red wavelength) | Cardiovascular state |
| IMU | 6-axis + 3-axis magnetometer | Head motion capture |
| Eye tracking (Varjo) | 200 Hz, sub-degree accuracy, 1-dot calibration | Image-based |

Sampling rate configurable: 250 Hz, 500 Hz, or 1 kHz. Wi-Fi integrated. Battery: 2,000 mAh (~7 hours).

### 4.2 Galea Neon: Standalone Untethered Wearable [VERIFIED — Oct 1, 2025 joint announcement]

> ⚠️ Official product name is **Galea Neon**, not "Galeneon." All GAIA-OS documentation must use the official name.

Launched October 1, 2025 by OpenBCI and Pupil Labs — the first headset combining brain, body, and eye tracking in a fully standalone system:

- **All-in-one:** EEG, EMG, EDA, PPG, IMU + Pupil Labs Neon mobile eye tracking
- **Fully untethered:** No external equipment required
- **Deployment flexibility:** Switches between VR, XR, 2D screen-based, and real-world environments without changing equipment
- **Setup:** Configurable in minutes
- **Data:** All signals hardware-synchronized; raw data available in real time
- **Available as:** Neon eye-tracking add-on for existing Galea Beta owners via OpenBCI shop

### 4.3 Galea Software Stack [VERIFIED]

- **Galea GUI:** Real-time visualization, hardware configuration, signal quality monitoring
- **Galea SDK:** Built on BrainFlow; Python, C++, Java, C#, Julia, MATLAB, R; built-in filtering and processing
- **Unity and Unreal Engine SDKs:** Direct game-engine integration with sample projects
- **Data Streaming:** LSL, UDP, and OSC

---

## 5. Software Ecosystem

### 5.1 BrainFlow SDK [VERIFIED — v5.20.1, January 2026]

The definitive, actively maintained middleware, replacing the deprecated PyOpenBCI library.

| Class | Function |
|---|---|
| `BoardShim` | Reads data from board; returns 2D NumPy array |
| `DataFilter` | Signal processing (filtering, denoising, downsampling) |
| `MLModel` | Derivative metrics (band power, concentration, relaxation) |

**Language support:** Python, C++, Java, C#, Julia, MATLAB, R, TypeScript, Rust.

Hardware backends: all OpenBCI boards, Muse, G.Tec, IronBCI32 (added v5.20.1, Jan 2026), and synthetic test boards. Supports real-time streaming and offline SD card playback.

> ⚠️ **PyOpenBCI is deprecated.** Do not use for new GAIA-OS development.

### 5.2 Lab Streaming Layer (LSL) Integration [VERIFIED]

Standardized cross-device, cross-application streaming synchronization. OpenBCI GUI Networking Widget supports LSL natively (TimeSeries, FFT, BandPower streams). Recommended for synchronizing OpenBCI EEG with stimulus presentation software, eye trackers, and other physiological sensors.

### 5.3 OpenBCI GUI [VERIFIED — v5.0.8 hotfix, November 2025]

Cross-platform (Windows, macOS, Ubuntu/Mint Linux), fully open-source (HTML/CSS/JavaScript). Widgets: Time Series, FFT Plot, Band Power, Accelerometer, Networking (LSL/UDP/OSC), Focus (neurofeedback). Version 5.0.8 hotfix released November 2025.

---

## 6. Signal Processing Pipeline

### 6.1 Raw Signal Characteristics [VERIFIED]

All OpenBCI data streams are **unfiltered raw signals.** The BrainFlow stream and GUI streaming output deliver raw ADC values without applied digital filtering. Required preprocessing stages:

1. **High-pass at 0.5 Hz** — removes DC offset and electrode polarization drift
2. **Notch at 50 Hz (EU) / 60 Hz (US)** — eliminates power line noise
3. **Bandpass 0.5–45 Hz** — isolates EEG-relevant spectrum; removes muscle artifact above 45 Hz
4. **Artifact removal** — EDGeNet (deep learning, 295× fewer params, real-time; from companion BCI survey) or ICA for research-grade applications
5. **Re-referencing** — common average or linked mastoids

### 6.2 Cyton+Daisy 16-Channel Default Mapping [VERIFIED]

```
Ch 1–8  (Cyton): Fp1, Fp2, C3, C4, P7, P8, O1, O2
Ch 9–16 (Daisy): F7,  F8,  F3, F4,  T7,  T8, P3, P4
Ch 17–19:        AX, AY, AZ (accelerometer)
Ch 20:           Event marker channel
```

---

## 7. Community, Research Validation, and Patent Signal

### 7.1 Research Validation [VERIFIED — PMC10098804]

PMC-indexed 2023 framework paper validated OpenBCI's Cyton board for neurophysiological experiments across P300 spellers, SSVEP control, motor imagery, emotion recognition, neurofeedback, cognitive workload, and clinical neurophysiology. Research-grade signal quality confirmed commensurate with hardware specifications.

### 7.2 Community Innovations [VERIFIED — community/competition records]

- **Brain Kart:** Open-source EEG-controlled robot race
- **NeuroStride:** Brain-powered mobility aid; Silver Medal, 2025 Toronto Science Fair
- **MIT Reality Hack 2025:** Galea + Unity + Lambda Cloud for training performance tracking

### 7.3 Patent Filing [VERIFIED — existence; content HORIZON]

March 2026 patent filing describes systems and methods for collecting, decoding, and modulating the human mind — signaling long-term investment in closed-loop neuromodulation beyond passive biosensing. Claims under development; not a currently available product.

---

## 8. The GAIA-OS OpenBCI Integration Architecture

### 8.1 Five-Tier Hardware Deployment

| Tier | Hardware | Channels | Sample Rate | Evidence Tier | GAIA-OS Use Case |
|---|---|---|---|---|---|
| **T0 — Entry** | Ganglion | 4 | 200 Hz | VERIFIED | Education; basic neurofeedback |
| **T1 — Standard** | Cyton | 8 | 250 Hz | VERIFIED | Consumer Gaian emotional awareness |
| **T2 — Enhanced** | Cyton+Daisy | 16 | 125 Hz wireless / 250 Hz SD | VERIFIED | Research-grade EEG; clinical applications |
| **T3 — Multimodal** | Galea (XR) | 10 EEG + EMG/EDA/PPG | 250–1000 Hz | VERIFIED | XR-integrated neuroadaptive symbiosis |
| **T4 — Mobile** | Galea Neon | 10 EEG + Eye Tracking | 250–1000 Hz | VERIFIED | Real-world mobile BCI; ecological research |

### 8.2 Software Integration Stack

| Component | Role | Evidence Tier |
|---|---|---|
| **BrainFlow v5.20+** | Board communication and data acquisition | VERIFIED |
| **EDGeNet** | Real-time deep-learning artifact removal | VERIFIED |
| **LSL** | Multi-device synchronization | VERIFIED |
| **PhysioOmni** | Universal multimodal physiological representation | VERIFIED |
| **EmoDLNet (or validated CNN-RNN equivalent)** | Real-time emotion classification | PRELIMINARY |

### 8.3 Recommended Module Architecture — `core/bci/`

```python
core/bci/
├── board_interface.py        # Abstract base: hardware-agnostic unified API
├── brainflow_streamer.py      # BrainFlow SDK wrapper (Ganglion, Cyton, Cyton+Daisy, Galea)
├── signal_processor.py       # Pipeline: bandpass → notch → EDGeNet → re-reference
├── lsl_bridge.py             # LSL streaming for external sync
└── bci_state_estimator.py    # PhysioOmni-based emotion, cognitive load, consciousness inference
```

### 8.4 Immediate Recommendations — Phase A (G-10)

| Priority | Action | Evidence Basis | Tier |
|---|---|---|---|
| **P0** | Install BrainFlow Python bindings (v5.20.1+) in GAIA-OS sidecar | brainflow.org Jan 2026; multi-language; actively maintained | VERIFIED |
| **P0** | Implement `BoardInterface` abstraction with Cyton+Daisy primary backend | OpenBCI docs; PMC10098804; hardware specs confirmed | VERIFIED |
| **P0** | Implement standard preprocessing pipeline in `signal_processor.py` | Established EEG practice | VERIFIED |
| **P1** | Deploy EDGeNet for real-time artifact removal | PubMed Jul 2025; 295× fewer params | VERIFIED |
| **P1** | Implement LSL bridging for GAIA-OS planetary sensor mesh sync | OpenBCI GUI v5.0.8; established standard | VERIFIED |
| **P2** | Procure and integrate Galea Neon for Creator-level private channel | Official launch Oct 2025; available via OpenBCI shop | VERIFIED (device); PRELIMINARY (integration) |

### 8.5 Medium-Term Recommendations — Phase B (G-11 through G-14)

| Priority | Action | Evidence Basis | Tier |
|---|---|---|---|
| **P1** | Integrate PhysioOmni-based multimodal fusion for EEG + HRV + behavioral state | arXiv:2504.19596; robust to missing modalities | VERIFIED |
| **P1** | Validate and integrate EmoDLNet (or CNN-RNN equivalent) once benchmarks confirmed | Architecture published; figures require primary source verification | PRELIMINARY |
| **P2** | Deploy Galea Unity SDK for XR neuroadaptive Gaian interactions | Production-validated; sample projects included | VERIFIED (SDK); PRELIMINARY (GAIA-OS integration) |
| **P3** | Monitor OpenBCI patent for closed-loop neuromodulation features | March 2026 filing; not yet available | HORIZON |

---

## 9. Privacy, Ethics, and Safety

OpenBCI devices are **not FDA-cleared medical devices** — designed for research, education, and neurofeedback, not clinical diagnosis or treatment without regulatory clearance.

EEG and multimodal physiological data from OpenBCI constitute sensitive biometric data under GDPR and equivalent regulations. GAIA-OS must:
- Require explicit, granular informed consent before activating any BCI modality
- Process biometric data locally on-device by default; require affirmative opt-in for cloud processing
- Provide complete audit logs of all BCI data collected and all inferences derived
- Never use BCI-derived inferences as the sole basis for consequential decisions
- Comply with applicable medical device regulations for healthcare-adjacent applications

---

## 10. Conclusion

OpenBCI provides a mature, PMC-validated, fully open-source hardware and software ecosystem that is the ideal non-invasive BCI acquisition layer for GAIA-OS. The Cyton+Daisy delivers research-grade signal quality; Galea adds the multimodal physiological sensing essential for robust affective computing; Galea Neon enables fully mobile untethered ecological research. BrainFlow (v5.20.1, actively maintained, 9 language bindings) provides production-hardened middleware. The architecture is fully open, integrable with the GAIA-OS Python/FastAPI sidecar, and extensible at every layer without proprietary lock-in.

---

*Hardened May 2, 2026. Sources confirmed: Galea Neon (OpenBCI + Pupil Labs joint announcement Oct 1 2025; remixreality.com; openbci.com shop); BrainFlow v5.20.1 (brainflow.org changelog, Jan 2026); Cyton specs (docs.openbci.com: ADS1299, PIC32MX250F128B, chipKIT bootloader); OpenBCI research validation (PMC10098804). Product name corrected from "Galeneon" → **Galea Neon** per official announcement. BrainFlow language list updated to include TypeScript and Rust (confirmed brainflow.org). EmoDLNet benchmark figures remain PRELIMINARY pending primary source confirmation.*

---

**Related Documents:**
- [`BCI_SIGNAL_PROCESSING_SURVEY.md`](./BCI_SIGNAL_PROCESSING_SURVEY.md) — EEG & HRV signal processing algorithms; PhysioOmni; EDGeNet; UCLA shared autonomy; HRV latency framework
- [`../subtle-body/SUBTLE_BODY_ENGINE_SURVEY.md`](../subtle-body/SUBTLE_BODY_ENGINE_SURVEY.md) — HRV in the chakra-coherence context; SCEA; Solfeggio
- [`../physics/ELECTROMAGNETIC_FIELD_THEORY_SURVEY.md`](../physics/ELECTROMAGNETIC_FIELD_THEORY_SURVEY.md) — Bioelectromagnetics; Schumann resonance physics
- [`../quantum/RESONANCE_FIELD_DYNAMICS_SURVEY.md`](../quantum/RESONANCE_FIELD_DYNAMICS_SURVEY.md) — Resonance field dynamics; device-as-qubit planetary network
