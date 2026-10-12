"""Load and validate an audit dataset from JSON."""

import json
from pathlib import Path

from core.models import AuditDataset


def load_dataset(path: str | Path) -> AuditDataset:
    """Parse ``path`` (JSON) into a validated :class:`AuditDataset`."""
    raw = Path(path).read_text(encoding="utf-8-sig")
    return AuditDataset.model_validate(json.loads(raw))
