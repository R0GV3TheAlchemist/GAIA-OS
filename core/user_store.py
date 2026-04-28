"""
core/user_store.py
GAIA User Store — SQLite-backed user registry

Provides:
  - register_user(email, username, password) -> UserRecord
  - login_user(username_or_email, password)  -> UserRecord | None
  - get_user_by_id(user_id)                  -> UserRecord | None

Storage: SQLite at GAIA_USER_DB_PATH (default: data/gaia_users.db)
Passwords: bcrypt-hashed, never stored in plaintext
Canon: C01 (Sovereignty), C15 (Consent)
"""

from __future__ import annotations

import os
import sqlite3
import uuid
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    import bcrypt
except ImportError:
    raise ImportError(
        "bcrypt is required for GAIA user auth. "
        "Add 'bcrypt>=4.0.0' to requirements.txt and run pip install."
    )

logger = logging.getLogger(__name__)

_DB_PATH = Path(os.environ.get("GAIA_USER_DB_PATH", "data/gaia_users.db"))


@dataclass
class UserRecord:
    user_id:    str
    email:      str
    username:   str
    role:       str          # "user" | "admin"
    created_at: str


def _get_conn() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_schema() -> None:
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id    TEXT PRIMARY KEY,
                email      TEXT NOT NULL UNIQUE,
                username   TEXT NOT NULL UNIQUE,
                pw_hash    TEXT NOT NULL,
                role       TEXT NOT NULL DEFAULT 'user',
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()


_ensure_schema()


class AuthError(Exception):
    """Raised for registration / login validation failures."""
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message)
        self.field = field  # which field caused the error, if applicable


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _check_password(password: str, pw_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), pw_hash.encode())


def register_user(email: str, username: str, password: str, role: str = "user") -> UserRecord:
    """
    Register a new user.
    Raises AuthError if email or username is already taken,
    or if inputs fail validation.
    """
    email    = email.strip().lower()
    username = username.strip()

    if not email or "@" not in email:
        raise AuthError("A valid email address is required.", field="email")
    if not username or len(username) < 2:
        raise AuthError("Username must be at least 2 characters.", field="username")
    if len(username) > 40:
        raise AuthError("Username must be 40 characters or fewer.", field="username")
    if not all(c.isalnum() or c in ('-', '_') for c in username):
        raise AuthError("Username may only contain letters, numbers, hyphens, and underscores.", field="username")
    if not password or len(password) < 8:
        raise AuthError("Password must be at least 8 characters.", field="password")

    user_id    = str(uuid.uuid4())
    pw_hash    = _hash_password(password)
    created_at = datetime.now(timezone.utc).isoformat()

    try:
        with _get_conn() as conn:
            conn.execute(
                "INSERT INTO users (user_id, email, username, pw_hash, role, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, email, username, pw_hash, role, created_at),
            )
            conn.commit()
    except sqlite3.IntegrityError as e:
        msg = str(e).lower()
        if "email" in msg:
            raise AuthError("That email address is already registered.", field="email")
        if "username" in msg:
            raise AuthError("That username is already taken.", field="username")
        raise AuthError("Registration failed. Please try again.")

    logger.info(f"[USER_STORE] New user registered: {username} ({email}) id={user_id}")
    return UserRecord(user_id=user_id, email=email, username=username, role=role, created_at=created_at)


def login_user(username_or_email: str, password: str) -> UserRecord:
    """
    Verify credentials. Accepts username OR email.
    Raises AuthError on invalid credentials.
    Returns UserRecord on success.
    """
    identifier = username_or_email.strip()
    if not identifier or not password:
        raise AuthError("Username/email and password are required.")

    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ? OR username = ?",
            (identifier.lower(), identifier),
        ).fetchone()

    if not row:
        raise AuthError("Invalid username or password.")
    if not _check_password(password, row["pw_hash"]):
        raise AuthError("Invalid username or password.")

    logger.info(f"[USER_STORE] Login success: {row['username']} id={row['user_id']}")
    return UserRecord(
        user_id=row["user_id"],
        email=row["email"],
        username=row["username"],
        role=row["role"],
        created_at=row["created_at"],
    )


def get_user_by_id(user_id: str) -> Optional[UserRecord]:
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if not row:
        return None
    return UserRecord(
        user_id=row["user_id"],
        email=row["email"],
        username=row["username"],
        role=row["role"],
        created_at=row["created_at"],
    )
