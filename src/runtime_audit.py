"""Minimal runtime audit record for formal discovery-v1."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_runtime_audit(audit: dict[str, Any], path: Path) -> None:
    path.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
