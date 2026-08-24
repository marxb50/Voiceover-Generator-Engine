"""Domain objects shared by validation and manifest generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


SUPPORTED_LANGUAGES = frozenset({"pt-BR", "en-US"})


def _required_text(record: Mapping[str, Any], field: str) -> str:
    value = str(record.get(field, "")).strip()
    if not value:
        raise ValueError(f"{field} is required")
    return " ".join(value.split())


@dataclass(frozen=True, slots=True)
class ProgramEntry:
    """One choreography scheduled in a festival session."""

    order: int
    session: str
    choreography: str
    group: str
    language: str = "pt-BR"

    @classmethod
    def from_mapping(cls, record: Mapping[str, Any]) -> "ProgramEntry":
        try:
            order = int(record.get("order", 0))
        except (TypeError, ValueError) as exc:
            raise ValueError("order must be an integer") from exc

        language = str(record.get("language", "pt-BR")).strip() or "pt-BR"
        return cls(
            order=order,
            session=_required_text(record, "session"),
            choreography=_required_text(record, "choreography"),
            group=_required_text(record, "group"),
            language=language,
        )


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """A deterministic problem found before audio generation starts."""

    code: str
    message: str
    entry_index: int

    def as_dict(self) -> dict[str, str | int]:
        return {
            "code": self.code,
            "message": self.message,
            "entry_index": self.entry_index,
        }

