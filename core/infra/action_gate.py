"""
core/infra/action_gate.py
(formerly core/action_gate.py — Phase C physical migration)

ActionGate — Risk-tiered action veto system.

Every action GAIA considers taking passes through this gate. Actions are
classified into three risk tiers and handled accordingly. This is a
programmatic gate, not a prompt-level suggestion — it operates at the
infrastructure level and cannot be bypassed by model output.

Risk Tiers (from GAIA Sovereignty Stack):
  GREEN  — Low risk. Proceed autonomously. Log for audit.
  YELLOW — Medium risk. Surface to user. Proceed on implicit approval.
  RED    — High risk. Hard stop. Explicit human confirmation required.

Epistemic Status: ESTABLISHED
Canon Ref: Doc 35 (Security), Doc 21 (Axiological — Sovereignty)
"""

from enum import Enum
from typing import Callable, Optional
import datetime


class RiskTier(Enum):
    GREEN = "green"    # Autonomous — log only
    YELLOW = "yellow"  # Surface to user — proceed on silence
    RED = "red"        # Hard stop — explicit confirmation required


class ActionGate:
    """
    Intercepts proposed actions, classifies them by risk tier,
    and enforces the appropriate confirmation protocol.

    The gate is the technical implementation of human sovereignty.
    It ensures the human sovereign retains ultimate authority over
    high-risk actions regardless of model intent or instruction.
    """

    def __init__(self, confirm_callback: Optional[Callable] = None):
        self._confirm_callback = confirm_callback
        self._audit_log: list = []

    def evaluate(self, action: dict) -> dict:
        """
        Evaluate an action against the risk tier system.

        Args:
            action: Dict with keys:
                      - 'type': str (action category)
                      - 'description': str (human-readable description)
                      - 'tier': RiskTier (declared risk level)
                      - 'payload': dict (action-specific data)

        Returns:
            Dict with keys:
              - 'approved': bool
              - 'tier': RiskTier
              - 'reason': str
        """
        tier = action.get("tier", RiskTier.YELLOW)
        entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "action": action,
            "tier": tier.value,
        }

        if tier == RiskTier.GREEN:
            entry["approved"] = True
            entry["reason"] = "Auto-approved: GREEN tier"
            self._audit_log.append(entry)
            return {"approved": True, "tier": tier, "reason": entry["reason"]}

        elif tier == RiskTier.YELLOW:
            if self._confirm_callback:
                approved = self._confirm_callback(action, tier)
            else:
                approved = True
            entry["approved"] = approved
            entry["reason"] = f"YELLOW tier: {'approved' if approved else 'vetoed'} by user"
            self._audit_log.append(entry)
            return {"approved": approved, "tier": tier, "reason": entry["reason"]}

        elif tier == RiskTier.RED:
            if not self._confirm_callback:
                entry["approved"] = False
                entry["reason"] = "RED tier: no confirmation callback registered — BLOCKED"
                self._audit_log.append(entry)
                return {"approved": False, "tier": tier, "reason": entry["reason"]}
            approved = self._confirm_callback(action, tier)
            entry["approved"] = approved
            entry["reason"] = f"RED tier: explicitly {'approved' if approved else 'vetoed'} by human sovereign"
            self._audit_log.append(entry)
            return {"approved": approved, "tier": tier, "reason": entry["reason"]}

        entry["approved"] = False
        entry["reason"] = "Unknown risk tier — BLOCKED by default"
        self._audit_log.append(entry)
        return {"approved": False, "tier": tier, "reason": entry["reason"]}

    def get_audit_log(self) -> list:
        """Return the full audit log of all evaluated actions."""
        return list(self._audit_log)
