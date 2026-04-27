"""
core/layers/layer_01_physical.py

LAYER 01 — PHYSICAL
Crystal:      Quartz
Polarity:     [+] Manifest
Mode:         Chaos / Body Alchemy
Color:        Clear / White
Universal Law: Law of Divine Oneness

"Everything that exists is connected through
 the same physical substrate."

This is the ground layer. The most concrete.
The most real in the ordinary sense of real.

It handles:
  - Hardware and device context detection
  - File system operations (read, write, watch)
  - Network connectivity and health
  - Local configuration storage
  - System health monitoring

Nothing touches the filesystem or network in GAIA-OS
without passing through this layer first.
It is the earth beneath everything.

Stable. Grounded. Concrete. Never rushes.
Physical reality is what it is.

Constitutional reference: canon/C-SINGULARITY.md
Canon references:         C32 (Quartz), C50 (GAIA is Geology),
                          C42 (Periodic Table)
Architectural reference:  canon/C89-TWELVE-LAYERS-KERNEL-SPEC.md
"""

import os
import platform
import socket
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import time

from core.kernel import register_layer

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# PHYSICAL CONTEXT
# ─────────────────────────────────────────────

@dataclass
class PhysicalContext:
    """
    A snapshot of the physical environment
    GAIA-OS is running in.

    This is the ground truth — what machine,
    what OS, what network, what storage.
    Everything above this layer rests on this.
    """
    hostname:          str  = ""
    platform:          str  = ""
    platform_version:  str  = ""
    architecture:      str  = ""
    processor:         str  = ""
    cpu_count:         int  = 0
    network_available: bool = False
    local_ip:          str  = ""
    gaia_root:         Path = Path(".")
    config_dir:        Path = Path(".")
    data_dir:          Path = Path(".")
    storage_healthy:   bool = False
    layer_healthy:     bool = False
    initialized_at:    float = field(default_factory=time.time)
    notes:             list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "hostname":          self.hostname,
            "platform":          self.platform,
            "platform_version":  self.platform_version,
            "architecture":      self.architecture,
            "cpu_count":         self.cpu_count,
            "network_available": self.network_available,
            "local_ip":          self.local_ip,
            "gaia_root":         str(self.gaia_root),
            "config_dir":        str(self.config_dir),
            "data_dir":          str(self.data_dir),
            "storage_healthy":   self.storage_healthy,
            "layer_healthy":     self.layer_healthy,
            "initialized_at":    self.initialized_at,
            "notes":             self.notes,
        }


# ─────────────────────────────────────────────
# GAIA-OS DIRECTORY STRUCTURE
# ─────────────────────────────────────────────

def resolve_gaia_root() -> Path:
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if any([
            (parent / "pyproject.toml").exists(),
            (parent / "src").exists(),
            (parent / ".gaia").exists(),
            (parent / "canon").exists(),
        ]):
            return parent
    return Path.cwd()


GAIA_ROOT  = resolve_gaia_root()
CONFIG_DIR = GAIA_ROOT / ".gaia" / "config"
DATA_DIR   = GAIA_ROOT / ".gaia" / "data"
MEMORY_DIR = GAIA_ROOT / ".gaia" / "memory"
LOG_DIR    = GAIA_ROOT / ".gaia" / "logs"


# ─────────────────────────────────────────────
# LAYER 01 — PHYSICAL
# ─────────────────────────────────────────────

class PhysicalLayer:
    """
    Layer 01 — The ground.

    Stable. Grounded. Concrete.
    Physical reality is what it is.
    This layer does not interpret. It reports.
    It does not judge. It holds.

    The Law of Divine Oneness operates here:
    every hardware component, every file,
    every network packet — all of it is one
    continuous physical substrate that GAIA-OS
    rests upon.
    """

    LAYER_NUMBER = 1
    LAYER_NAME   = "Physical"
    CRYSTAL      = "Quartz"

    def __init__(self):
        self._context: Optional[PhysicalContext] = None
        self._initialized = False
        self._initialize()

    def _initialize(self):
        logger.info("Layer 01 — Physical — initializing ground. ✦")
        context = PhysicalContext()

        # ── Machine
        try:
            context.hostname         = socket.gethostname()
            context.platform         = platform.system()
            context.platform_version = platform.version()
            context.architecture     = platform.machine()
            context.processor        = platform.processor()
            context.cpu_count        = os.cpu_count() or 0
            context.notes.append(
                f"Running on {context.platform} "
                f"({context.architecture}) — {context.hostname}"
            )
        except Exception as e:
            logger.warning(f"Layer 01: machine detection partial — {e}")
            context.notes.append(f"Machine detection partial: {e}")

        # ── Network
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            context.local_ip = s.getsockname()[0]
            s.close()
            context.network_available = True
            context.notes.append(f"Network available. Local IP: {context.local_ip}")
        except Exception:
            context.network_available = False
            context.notes.append("Network not available. Offline mode.")
            logger.info("Layer 01: network unavailable. GAIA-OS runs offline.")

        # ── Directories
        context.gaia_root  = GAIA_ROOT
        context.config_dir = CONFIG_DIR
        context.data_dir   = DATA_DIR

        for directory in [CONFIG_DIR, DATA_DIR, MEMORY_DIR, LOG_DIR]:
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"Layer 01: could not create {directory} — {e}")
                context.notes.append(f"Directory creation failed: {directory}")

        context.storage_healthy = True
        context.layer_healthy   = True
        context.initialized_at  = time.time()
        context.notes.append(f"GAIA-OS root: {GAIA_ROOT}")

        self._context     = context
        self._initialized = True

        logger.info(
            f"Layer 01 — Physical — ground established. "
            f"Platform: {context.platform} | "
            f"Network: {context.network_available} | "
            f"Root: {GAIA_ROOT}"
        )

        register_layer(self.LAYER_NUMBER, self.handle)
        logger.info("Layer 01 registered with kernel. ✦")

    # ─────────────────────────────────────────
    # KERNEL HANDLER
    # ─────────────────────────────────────────

    def handle(self, intention: str, context: dict) -> dict:
        if not self._initialized or not self._context:
            return {
                "output":   "Physical layer not initialized.",
                "metadata": {"healthy": False}
            }
        physical_summary = (
            f"Ground: {self._context.platform} | "
            f"Network: {'online' if self._context.network_available else 'offline'} | "
            f"Root: {self._context.gaia_root}"
        )
        return {
            "output":   physical_summary,
            "metadata": {
                "healthy":           self._context.layer_healthy,
                "platform":          self._context.platform,
                "network_available": self._context.network_available,
                "gaia_root":         str(self._context.gaia_root),
            }
        }

    # ─────────────────────────────────────────
    # FILE OPERATIONS
    # ─────────────────────────────────────────

    def read_config(self, config_name: str) -> Optional[dict]:
        config_path = CONFIG_DIR / f"{config_name}.json"
        if not config_path.exists():
            logger.debug(f"Layer 01: config '{config_name}' not found.")
            return None
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Layer 01: could not read config '{config_name}' — {e}")
            return None

    def write_config(self, config_name: str, data: dict) -> bool:
        config_path = CONFIG_DIR / f"{config_name}.json"
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Layer 01: config '{config_name}' written.")
            return True
        except Exception as e:
            logger.error(f"Layer 01: could not write config '{config_name}' — {e}")
            return False

    def read_data(self, filename: str) -> Optional[str]:
        data_path = DATA_DIR / filename
        if not data_path.exists():
            return None
        try:
            return data_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Layer 01: could not read data '{filename}' — {e}")
            return None

    def write_data(self, filename: str, content: str) -> bool:
        data_path = DATA_DIR / filename
        try:
            data_path.parent.mkdir(parents=True, exist_ok=True)
            data_path.write_text(content, encoding="utf-8")
            logger.debug(f"Layer 01: data '{filename}' written.")
            return True
        except Exception as e:
            logger.error(f"Layer 01: could not write data '{filename}' — {e}")
            return False

    def path_exists(self, relative_path: str) -> bool:
        return (GAIA_ROOT / relative_path).exists()

    # ─────────────────────────────────────────
    # NETWORK
    # ─────────────────────────────────────────

    def check_network(self) -> bool:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(2)
            s.connect(("8.8.8.8", 80))
            s.close()
            if self._context:
                self._context.network_available = True
            return True
        except Exception:
            if self._context:
                self._context.network_available = False
            return False

    def is_online(self) -> bool:
        if self._context:
            return self._context.network_available
        return False

    # ─────────────────────────────────────────
    # STATUS
    # ─────────────────────────────────────────

    def context(self) -> Optional[PhysicalContext]:
        return self._context

    def status(self) -> dict:
        if not self._context:
            return {"healthy": False, "message": "Not initialized."}
        return {
            "layer":   self.LAYER_NUMBER,
            "name":    self.LAYER_NAME,
            "crystal": self.CRYSTAL,
            "healthy": self._context.layer_healthy,
            "context": self._context.to_dict(),
        }


# ─────────────────────────────────────────────
# SINGLETON
# ─────────────────────────────────────────────

physical_layer = PhysicalLayer()


def get_physical_context() -> Optional[PhysicalContext]:
    return physical_layer.context()


def read_config(name: str) -> Optional[dict]:
    return physical_layer.read_config(name)


def write_config(name: str, data: dict) -> bool:
    return physical_layer.write_config(name, data)
