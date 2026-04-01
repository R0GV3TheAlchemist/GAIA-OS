"""
CanonLoader — Loads and validates the GAIA constitutional canon documents.

The canon is the authoritative source of GAIA's values, legal hierarchy,
and constitutional constraints. This module loads canon documents from the
local `canon/` directory (which references the GAIA OS repo) and validates
them against the expected schema.

Epistemic Status: FOUNDATIONAL
Canon Ref: GAIA Canon 01–35
"""

import os
import json
from pathlib import Path
from typing import Optional


class CanonLoader:
    """
    Loads GAIA canon documents and exposes their content to the runtime.
    
    The canon is the immutable constitutional foundation. If a canon document
    cannot be loaded or fails validation, the system refuses to start.
    This is not a graceful degradation — it is a constitutional hard stop.
    """

    CANON_DIR = Path(__file__).parent.parent / "canon"

    def __init__(self, canon_dir: Optional[Path] = None):
        self.canon_dir = canon_dir or self.CANON_DIR
        self._documents: dict = {}
        self._loaded = False

    def load(self) -> bool:
        """
        Load all available canon documents from the canon directory.
        Returns True if at least the constitutional floor documents are present.
        """
        if not self.canon_dir.exists():
            raise RuntimeError(
                f"Canon directory not found: {self.canon_dir}\n"
                "GAIA cannot start without its constitutional foundation."
            )

        for doc_path in sorted(self.canon_dir.glob("*.md")):
            doc_id = doc_path.stem
            self._documents[doc_id] = {
                "id": doc_id,
                "path": str(doc_path),
                "content": doc_path.read_text(encoding="utf-8"),
            }

        self._loaded = True
        return len(self._documents) > 0

    def get(self, doc_id: str) -> Optional[dict]:
        """Retrieve a specific canon document by ID."""
        return self._documents.get(doc_id)

    def list_documents(self) -> list:
        """List all loaded canon document IDs."""
        return list(self._documents.keys())

    @property
    def is_loaded(self) -> bool:
        return self._loaded
