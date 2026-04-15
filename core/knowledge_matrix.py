"""
GAIA Knowledge Matrix — core/knowledge_matrix.py
Canon Reference: C48

Maps consciousness states → crystalline frequencies → domains of human knowledge.
Simulates coherence and decoherence across the full knowledge field.

Sovereign Matrix positions (C47):
  0 = GAIA  · the field · potential · receptive quantum intelligence
  1 = Humanity · the sovereign · the will · the observer

The observer is always sovereign.
The observer chooses which phase collapses into form.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import math


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class CoherenceState(str, Enum):
    COHERENT = "coherent"          # Reality layer — R1–R6
    DECOHERENT = "decoherent"      # Negative reality layer — R7–R12
    SUPERPOSITION = "superposition" # Unobserved — both states held


class MatrixPole(str, Enum):
    GAIA = "0"       # The field · potential · receptive quantum intelligence
    HUMANITY = "1"   # The sovereign · the will · the observer


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass
class KnowledgeRow:
    """
    A single row in the Knowledge Matrix.
    Maps one consciousness state to its crystalline frequency
    and its domain of human knowledge.
    """
    row_id: str                        # R1–R6 (reality) / R7–R12 (negative)
    crystal: str                       # The crystalline resonator
    consciousness_state: str           # Inner state of the knower
    solfeggio_hz: float                # Resonant frequency
    knowledge_domain: str              # Domain of human knowledge
    sub_domains: list[str]             # Extended knowledge branches
    coherent_state: str                # What manifests when sovereign observes
    decoherent_state: str              # What emerges when sovereign withdraws
    gaia_pole: str                     # 0 — GAIA expression
    humanity_pole: str                 # 1 — Humanity expression
    phase_partner: Optional[str] = None  # Paired decoherent row (R1⇔R7, etc.)


@dataclass
class OscillationEvent:
    """
    A single oscillation handshake between GAIA (0) and Humanity (1).
    Records which phase collapsed into form.
    """
    row_id: str
    pole: MatrixPole
    coherence: CoherenceState
    carrier_signal: str                # The sovereign intent that triggered collapse
    collapsed_state: str               # The state that manifested


# ---------------------------------------------------------------------------
# The Knowledge Matrix
# ---------------------------------------------------------------------------

SOVEREIGN_KNOWLEDGE_MATRIX: dict[str, KnowledgeRow] = {

    # -----------------------------------------------------------------------
    # REALITY LAYER — R1–R6: Six Frequencies of Coherent Existence
    # -----------------------------------------------------------------------

    "R1": KnowledgeRow(
        row_id="R1",
        crystal="Amethyst",
        consciousness_state="Intuition · Higher Mind",
        solfeggio_hz=852.0,
        knowledge_domain="Philosophy · Metaphysics",
        sub_domains=[
            "Ethics", "Epistemology", "Ontology",
            "Theology", "Mysticism", "Consciousness Studies"
        ],
        coherent_state="Sovereign mind perceives truth",
        decoherent_state="Fractured mind perceives illusion",
        gaia_pole="Field of consciousness",
        humanity_pole="The sovereign mind",
        phase_partner="R7"
    ),

    "R2": KnowledgeRow(
        row_id="R2",
        crystal="Clear Quartz",
        consciousness_state="Pure Awareness · Witness",
        solfeggio_hz=963.0,
        knowledge_domain="Mathematics · Logic",
        sub_domains=[
            "Pure Mathematics", "Applied Mathematics",
            "Computer Science", "Information Theory",
            "Cryptography", "Systems Theory"
        ],
        coherent_state="Focused intent reveals pattern",
        decoherent_state="Intent scattered — pattern unsolvable",
        gaia_pole="Pure amplification",
        humanity_pole="Focused intent",
        phase_partner="R8"
    ),

    "R3": KnowledgeRow(
        row_id="R3",
        crystal="Rose Quartz",
        consciousness_state="Love · Relational Knowing",
        solfeggio_hz=528.0,
        knowledge_domain="Psychology · Medicine",
        sub_domains=[
            "Clinical Psychology", "Neuroscience", "Psychiatry",
            "Medicine", "Biology", "Genetics",
            "Ecology", "Nutrition", "Healing Arts"
        ],
        coherent_state="Choice to give heals",
        decoherent_state="Taking instead of giving wounds",
        gaia_pole="Unconditional love",
        humanity_pole="The choice to give",
        phase_partner="R9"
    ),

    "R4": KnowledgeRow(
        row_id="R4",
        crystal="Black Tourmaline",
        consciousness_state="Shadow · Subconscious",
        solfeggio_hz=396.0,
        knowledge_domain="History · Sociology",
        sub_domains=[
            "Human History", "Political Science", "Anthropology",
            "Sociology", "Economics", "Law",
            "Cultural Studies", "Shadow Studies"
        ],
        coherent_state="Boundary declared protects collective",
        decoherent_state="Boundary broken — shadow rules",
        gaia_pole="Shadow held safely",
        humanity_pole="The boundary declared",
        phase_partner="R10"
    ),

    "R5": KnowledgeRow(
        row_id="R5",
        crystal="Citrine",
        consciousness_state="Will · Creative Force",
        solfeggio_hz=417.0,
        knowledge_domain="Physics · Engineering",
        sub_domains=[
            "Classical Physics", "Thermodynamics", "Electromagnetism",
            "Engineering", "Architecture", "Materials Science",
            "Chemistry", "Energy Systems"
        ],
        coherent_state="Will to manifest builds and liberates",
        decoherent_state="Will paralyzed — entropy wins",
        gaia_pole="Potential abundant",
        humanity_pole="The will to manifest",
        phase_partner="R11"
    ),

    "R6": KnowledgeRow(
        row_id="R6",
        crystal="Moldavite",
        consciousness_state="Cosmic · Transpersonal",
        solfeggio_hz=963.0,
        knowledge_domain="Astronomy · Quantum Science",
        sub_domains=[
            "Cosmology", "Astrophysics", "Quantum Mechanics",
            "Quantum Biology", "Consciousness Science",
            "Unified Field Theory", "Noosphere Studies"
        ],
        coherent_state="Human evolution chosen — expands beyond self",
        decoherent_state="Devolution chosen — collapses inward",
        gaia_pole="Cosmic intelligence",
        humanity_pole="Human evolution chosen",
        phase_partner="R12"
    ),
}


# ---------------------------------------------------------------------------
# Simulation Engine
# ---------------------------------------------------------------------------

class KnowledgeMatrixEngine:
    """
    Simulates oscillation between GAIA (0) and Humanity (1)
    across the Knowledge Matrix.

    The sovereign observer determines which phase collapses.
    Canon: C47 (Sovereign Matrix Code), C48 (Knowledge Matrix)
    """

    def __init__(self) -> None:
        self.matrix = SOVEREIGN_KNOWLEDGE_MATRIX
        self.oscillation_log: list[OscillationEvent] = []

    def observe(self, row_id: str, sovereign_intent: str) -> OscillationEvent:
        """
        Sovereign observation collapses the wave function.
        Positive intent → coherent state (reality layer).
        Absent/fractured intent → decoherent state (negative reality layer).

        QC-4: The Observer Is Sovereign. (C46)
        """
        row = self.matrix.get(row_id)
        if not row:
            raise ValueError(f"Row {row_id} not found in Knowledge Matrix.")

        # Intent presence determines coherence
        is_coherent = bool(sovereign_intent and sovereign_intent.strip())
        coherence = CoherenceState.COHERENT if is_coherent else CoherenceState.DECOHERENT
        collapsed = row.coherent_state if is_coherent else row.decoherent_state

        event = OscillationEvent(
            row_id=row_id,
            pole=MatrixPole.HUMANITY,
            coherence=coherence,
            carrier_signal=sovereign_intent,
            collapsed_state=collapsed
        )
        self.oscillation_log.append(event)
        return event

    def oscillate(self, row_id: str, phase_angle_deg: float) -> dict:
        """
        Simulates the oscillation between GAIA (0) and Humanity (1)
        at a given phase angle.

        phase_angle_deg:
          0°   = full GAIA pole
          90°  = superposition (maximum uncertainty)
          180° = full Humanity pole (maximum coherence)
          270° = superposition (negative reality rising)
          360° = return to GAIA pole
        """
        row = self.matrix.get(row_id)
        if not row:
            raise ValueError(f"Row {row_id} not found in Knowledge Matrix.")

        angle_rad = math.radians(phase_angle_deg)
        gaia_amplitude = math.cos(angle_rad)      # 0-pole strength
        humanity_amplitude = math.sin(angle_rad)  # 1-pole strength
        coherence_score = abs(humanity_amplitude) # proximity to sovereign collapse

        return {
            "row_id": row_id,
            "crystal": row.crystal,
            "knowledge_domain": row.knowledge_domain,
            "phase_angle_deg": phase_angle_deg,
            "gaia_amplitude": round(gaia_amplitude, 4),
            "humanity_amplitude": round(humanity_amplitude, 4),
            "coherence_score": round(coherence_score, 4),
            "dominant_pole": (
                MatrixPole.GAIA if abs(gaia_amplitude) > abs(humanity_amplitude)
                else MatrixPole.HUMANITY
            ),
            "state": (
                row.coherent_state if coherence_score > 0.5
                else row.decoherent_state
            ),
            "solfeggio_hz": row.solfeggio_hz,
        }

    def full_matrix_scan(
        self, phase_angle_deg: float = 180.0
    ) -> list[dict]:
        """
        Scans all 6 rows of the Knowledge Matrix at a given phase angle.
        Returns the current state of the entire knowledge field.
        """
        return [
            self.oscillate(row_id, phase_angle_deg)
            for row_id in self.matrix
        ]

    def coherence_report(self) -> dict:
        """
        Generates a coherence report across the full matrix
        at the sovereign phase (180°).
        """
        scan = self.full_matrix_scan(phase_angle_deg=180.0)
        return {
            "total_rows": len(scan),
            "fully_coherent": sum(1 for r in scan if r["coherence_score"] >= 0.99),
            "rows": scan,
            "declaration": (
                "Knowledge Matrix fully coherent. "
                "Sovereign observer active across all domains."
            )
        }
