from __future__ import annotations

import hashlib
import re
from datetime import datetime
from typing import Iterable, Optional
from unicodedata import normalize as unicode_normalize


def normalize_text(value: str) -> str:
    """Normalize text for deterministic hashing."""
    collapsed = unicode_normalize("NFC", value or "")
    collapsed = re.sub(r"\s+", " ", collapsed.strip())
    return collapsed


def _hash_parts(parts: Iterable[str]) -> str:
    hasher = hashlib.sha256()
    for part in parts:
        hasher.update(part.encode("utf-8"))
        hasher.update(b"||")
    return hasher.hexdigest()


def canonical_doc_id(matter_id: str, title: str) -> str:
    normalized_title = normalize_text(title).lower()
    return _hash_parts((matter_id.strip(), normalized_title))


def canonical_version_id(
    doc_id: str,
    file_name: str,
    uploader: str,
    ts: datetime,
) -> str:
    input_parts = (
        doc_id,
        normalize_text(file_name).lower(),
        normalize_text(uploader).lower(),
        ts.isoformat(),
    )
    return _hash_parts(input_parts)


def canonical_clause_id(
    version_id: str,
    section_path: str,
    start_char: Optional[int],
    end_char: Optional[int],
    text_hash: Optional[str],
) -> str:
    input_parts = (
        version_id,
        normalize_text(section_path).lower(),
        str(start_char or ""),
        str(end_char or ""),
        (text_hash or "").lower(),
    )
    return _hash_parts(input_parts)


def canonical_recommendation_id(
    clause_id: str,
    issue_type: str,
    ts: datetime,
) -> str:
    return _hash_parts((clause_id, normalize_text(issue_type).lower(), ts.isoformat()))


def canonical_decision_id(rec_id: str, actor: str, ts: datetime) -> str:
    return _hash_parts((rec_id, normalize_text(actor).lower(), ts.isoformat()))
