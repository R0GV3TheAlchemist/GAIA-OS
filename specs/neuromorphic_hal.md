# Neuromorphic Hardware Abstraction Layer (HAL)

**Status:** Research / Planned 
**Source:** `GAIA_Neuromorphic_Hardware_Integration_Spec_v1.0.md` 
**Canon Ref:** GAIA Neuromorphic Integration Specification v1.0

---

## Purpose

The Neuromorphic HAL is the adapter layer that allows GAIA's core reasoning engine to run on
both conventional CPU/GPU hardware and specialized neuromorphic chips (e.g., Intel Loihi 2,
IBM TrueNorth, BrainScaleS) without changing the constitutional logic above it.

## Design Principle

> "If specialized neuromorphic hardware is present, use it.
> If not, degrade gracefully to conventional inference.
> The constitutional core is hardware-agnostic."

## Target Platforms

| Platform | Type | Status |
|---|---|---|
| Intel Loihi 2 | Neuromorphic (SNN) | Research |
| IBM TrueNorth | Neuromorphic (SNN) | Research |
| BrainScaleS 2 | Neuromorphic (analog) | Research |
| NVIDIA GPU | Conventional | Planned |
| Apple Silicon (Neural Engine) | Conventional + NPU | Planned |
| Standard CPU (x86/ARM) | Conventional | Baseline |

## HAL Interface (Draft)

```python
class NeuromorphicHAL:
    """
    Hardware Abstraction Layer for GAIA inference.
    Detects available hardware and routes inference accordingly.
    """

    def detect(self) -> str:
        """Returns hardware target: 'loihi2', 'truenorth', 'gpu', 'cpu'"""
        ...

    def load_model(self, model_path: str) -> bool:
        """Load a GAIA inference model onto the detected hardware."""
        ...

    def infer(self, inputs: dict) -> dict:
        """Run inference. Returns constitutional-layer outputs."""
        ...

    def fallback(self) -> str:
        """Return the fallback hardware target if primary is unavailable."""
        return 'cpu'
```

## Research Links

- [Intel Loihi 2](https://www.intel.com/content/www/us/en/research/neuromorphic-computing.html)
- [Norse (SNN framework)](https://github.com/norse/norse)
- [BindsNET](https://github.com/BindsNET/bindsnet)
- [GAIA Neuromorphic Spec (source doc)](../GAIA_Neuromorphic_Hardware_Integration_Spec_v1.0.md)
