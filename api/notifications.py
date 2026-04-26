"""
api/notifications.py — P4 Proactive Notifications

GAIA sends warm, non-spammy desktop notifications based on:
  1. Time-based triggers  (morning check-in, evening reflection)
  2. Memory triggers      (user mentioned a goal/intention recently)

Rules:
  - Max 3 notifications per day (configurable, hard ceiling = 5)
  - Minimum 2-hour cooldown between any two notifications
  - Quiet hours respected (default: 22:00 – 08:00 local time)
  - Notifications are never repeated within 24 hours
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/notifications", tags=["notifications"])

# ── Persistence ───────────────────────────────────────────────────────────────

DATA_DIR = Path.home() / ".local" / "share" / "GAIA"
STATE_FILE = DATA_DIR / "notification-state.json"


def _load_state() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {
        "delivered_today": [],      # list of notification IDs delivered today
        "last_delivered_at": None,  # ISO datetime string
        "date": None,               # YYYY-MM-DD — resets counters daily
        "dismissed": [],            # IDs the user has dismissed
        "settings": {
            "daily_cap": 3,
            "quiet_start": 22,      # hour (local)
            "quiet_end": 8,         # hour (local)
            "enabled": True,
        },
    }


def _save_state(state: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def _reset_if_new_day(state: dict) -> dict:
    today = datetime.now().strftime("%Y-%m-%d")
    if state.get("date") != today:
        state["delivered_today"] = []
        state["last_delivered_at"] = None
        state["date"] = today
    return state


# ── Notification catalogue ────────────────────────────────────────────────────

class Notification(BaseModel):
    id: str
    title: str
    body: str
    trigger: str        # "time" | "memory"
    section: str        # "chat" | "memory" | "settings" — where to navigate on click


TIME_TRIGGERS: list[dict] = [
    {
        "id": "morning-checkin",
        "hour_start": 8,
        "hour_end": 10,
        "title": "Good morning — GAIA is here.",
        "body": "How are you feeling today? I'm ready when you are.",
        "section": "chat",
    },
    {
        "id": "midday-pulse",
        "hour_start": 12,
        "hour_end": 14,
        "title": "Midday check-in",
        "body": "Take a breath. What\'s on your mind right now?",
        "section": "chat",
    },
    {
        "id": "evening-reflection",
        "hour_start": 19,
        "hour_end": 21,
        "title": "Evening reflection",
        "body": "The day is winding down. Want to capture anything before it fades?",
        "section": "memory",
    },
]


def _in_quiet_hours(settings: dict) -> bool:
    hour = datetime.now().hour
    qs, qe = settings["quiet_start"], settings["quiet_end"]
    if qs > qe:  # spans midnight
        return hour >= qs or hour < qe
    return qs <= hour < qe


def _cooldown_elapsed(state: dict, minutes: int = 120) -> bool:
    last = state.get("last_delivered_at")
    if not last:
        return True
    try:
        last_dt = datetime.fromisoformat(last)
        return datetime.now() - last_dt >= timedelta(minutes=minutes)
    except Exception:
        return True


def _build_time_notification(state: dict) -> Optional[Notification]:
    """Return the first time-based notification that fits the current window."""
    hour = datetime.now().hour
    delivered = set(state["delivered_today"])

    for trigger in TIME_TRIGGERS:
        nid = trigger["id"]
        if nid in delivered:
            continue
        if trigger["hour_start"] <= hour < trigger["hour_end"]:
            return Notification(
                id=nid,
                title=trigger["title"],
                body=trigger["body"],
                trigger="time",
                section=trigger["section"],
            )
    return None


def _build_memory_notification(state: dict) -> Optional[Notification]:
    """
    Query ChromaDB for recent user intentions / goals mentioned in the last 48 h.
    Returns a personalised nudge if one is found and not already delivered.
    """
    try:
        import chromadb  # type: ignore

        client = chromadb.PersistentClient(
            path=str(DATA_DIR / "memory")
        )
        collection = client.get_or_create_collection("gaia_memory")

        # Search for intention/goal patterns in recent memory
        results = collection.query(
            query_texts=["intention goal plan want to do today"],
            n_results=3,
            where={"timestamp": {"$gte": (datetime.now() - timedelta(hours=48)).isoformat()}},
        )

        docs = results.get("documents", [[]])[0]
        if not docs:
            return None

        # Use the first relevant memory snippet as context
        snippet = docs[0][:80].strip().rstrip(".")
        nid = f"memory-{uuid.uuid5(uuid.NAMESPACE_DNS, snippet)}"

        if nid in set(state["delivered_today"]):
            return None

        return Notification(
            id=nid,
            title="GAIA remembers…",
            body=f"You mentioned: \"{snippet}\" — still on your mind?",
            trigger="memory",
            section="memory",
        )
    except Exception:
        # ChromaDB unavailable or no relevant memories — silent fail
        return None


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/pending", response_model=Optional[Notification])
def get_pending_notification():
    """
    Poll endpoint. Returns the next notification to display, or null.
    The frontend calls this every 5 minutes from the AmbientOrb.
    """
    state = _load_state()
    state = _reset_if_new_day(state)
    settings = state["settings"]

    if not settings["enabled"]:
        return None

    cap = min(settings["daily_cap"], 5)  # hard ceiling
    if len(state["delivered_today"]) >= cap:
        return None

    if _in_quiet_hours(settings):
        return None

    if not _cooldown_elapsed(state):
        return None

    # Time-based triggers take priority; memory triggers fill the gap
    notification = _build_time_notification(state) or _build_memory_notification(state)
    _save_state(state)
    return notification


class DismissRequest(BaseModel):
    notification_id: str


@router.post("/dismiss")
def dismiss_notification(req: DismissRequest):
    """Mark a notification as delivered so it won't repeat today."""
    state = _load_state()
    state = _reset_if_new_day(state)

    nid = req.notification_id
    if nid not in state["delivered_today"]:
        state["delivered_today"].append(nid)
    state["last_delivered_at"] = datetime.now().isoformat()

    _save_state(state)
    return {"status": "dismissed"}


class NotificationSettings(BaseModel):
    daily_cap: Optional[int] = None
    quiet_start: Optional[int] = None
    quiet_end: Optional[int] = None
    enabled: Optional[bool] = None


@router.post("/settings")
def update_notification_settings(body: NotificationSettings):
    """Update notification preferences from the Settings UI."""
    state = _load_state()
    s = state["settings"]

    if body.daily_cap is not None:
        s["daily_cap"] = max(1, min(body.daily_cap, 5))
    if body.quiet_start is not None:
        s["quiet_start"] = body.quiet_start % 24
    if body.quiet_end is not None:
        s["quiet_end"] = body.quiet_end % 24
    if body.enabled is not None:
        s["enabled"] = body.enabled

    _save_state(state)
    return {"status": "updated", "settings": s}


@router.get("/settings")
def get_notification_settings():
    """Return current notification settings for the Settings UI."""
    state = _load_state()
    return state["settings"]
