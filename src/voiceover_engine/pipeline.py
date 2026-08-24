"""Validation and manifest generation for a privacy-safe festival program."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .domain import SUPPORTED_LANGUAGES, ProgramEntry, ValidationIssue


DEFAULT_VOICES = {
    "pt-BR": "pt-BR-FranciscaNeural",
    "en-US": "en-US-JennyNeural",
}

ANNOUNCEMENT_TEMPLATES = {
    "pt-BR": "Coreografia número {order}: {choreography}, do grupo {group}.",
    "en-US": "Choreography number {order}: {choreography}, by {group}.",
}


def load_program(path: str | Path) -> list[ProgramEntry]:
    """Load either a JSON list or an object containing an ``entries`` list."""

    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    records = payload.get("entries") if isinstance(payload, dict) else payload
    if not isinstance(records, list):
        raise ValueError("program JSON must be a list or contain an entries list")
    return [ProgramEntry.from_mapping(record) for record in records]


def validate_program(entries: Sequence[ProgramEntry]) -> list[ValidationIssue]:
    """Find invalid orders, languages and duplicate positions by session."""

    issues: list[ValidationIssue] = []
    positions = Counter((entry.session.casefold(), entry.order) for entry in entries)

    for index, entry in enumerate(entries):
        if entry.order <= 0:
            issues.append(
                ValidationIssue("invalid_order", "order must be greater than zero", index)
            )
        if entry.language not in SUPPORTED_LANGUAGES:
            issues.append(
                ValidationIssue(
                    "unsupported_language",
                    f"language must be one of {sorted(SUPPORTED_LANGUAGES)}",
                    index,
                )
            )
        if positions[(entry.session.casefold(), entry.order)] > 1:
            issues.append(
                ValidationIssue(
                    "duplicate_position",
                    f"order {entry.order} is duplicated in session {entry.session}",
                    index,
                )
            )

    return issues


def _slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_value.casefold()).strip("-")


def _announcement(entry: ProgramEntry) -> str:
    template = ANNOUNCEMENT_TEMPLATES.get(
        entry.language, ANNOUNCEMENT_TEMPLATES["pt-BR"]
    )
    return template.format(
        order=entry.order,
        choreography=entry.choreography,
        group=entry.group,
    )


def build_manifest(
    entries: Iterable[ProgramEntry],
    voices: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Create stable work items that an asynchronous TTS adapter can consume."""

    materialized = list(entries)
    issues = validate_program(materialized)
    if issues:
        details = "; ".join(f"#{issue.entry_index}: {issue.code}" for issue in issues)
        raise ValueError(f"program validation failed: {details}")

    selected_voices = {**DEFAULT_VOICES, **(voices or {})}
    work_items: list[dict[str, Any]] = []

    for entry in sorted(materialized, key=lambda item: (item.session, item.order)):
        text = _announcement(entry)
        identifier = f"{_slug(entry.session)}-{entry.order:03d}"
        work_items.append(
            {
                "id": identifier,
                "session": entry.session,
                "order": entry.order,
                "language": entry.language,
                "voice": selected_voices[entry.language],
                "text": text,
                "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "output_file": f"audio/{_slug(entry.session)}/{identifier}.mp3",
                "status": "pending",
            }
        )

    return {
        "schema_version": 1,
        "item_count": len(work_items),
        "items": work_items,
    }


def write_manifest(manifest: Mapping[str, Any], path: str | Path) -> Path:
    """Write a UTF-8 JSON manifest and return its resolved path."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return destination.resolve()

