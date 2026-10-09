"""On-demand SQLite backups taken with the sqlite3 command-line shell."""

import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from app.repository import DB_PATH

BACKUP_DIR: Final[Path] = DB_PATH.with_name("backups")
_LABEL_PATTERN: Final[re.Pattern[str]] = re.compile(r"[a-z0-9-]{1,32}")


class InvalidLabelError(ValueError):
    """Raised when a backup label is outside ``[a-z0-9-]{1,32}``."""


def backup_path(label: str) -> Path:
    """Return the timestamped file a backup with ``label`` is written to."""
    if not _LABEL_PATTERN.fullmatch(label):
        raise InvalidLabelError(f"invalid backup label: {label!r}")
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return BACKUP_DIR / f"{timestamp}-{label}.db"


def create_backup(label: str) -> Path:
    """Copy the live database to a new backup file and return its path."""
    target = backup_path(label)
    BACKUP_DIR.mkdir(exist_ok=True)
    subprocess.run(
        ["sqlite3", str(DB_PATH), f".backup {target}"],
        check=True,
        capture_output=True,
        timeout=60,
    )
    return target
