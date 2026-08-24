from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from voiceover_engine import (
    ProgramEntry,
    build_manifest,
    load_program,
    validate_program,
    write_manifest,
)


class PipelineTests(unittest.TestCase):
    def test_build_manifest_is_ordered_and_auditable(self) -> None:
        entries = [
            ProgramEntry(2, "Evening Show", "Northern Lights", "Studio Aurora", "en-US"),
            ProgramEntry(1, "Evening Show", "Blue Motion", "Studio Horizonte"),
        ]

        manifest = build_manifest(entries)

        self.assertEqual(2, manifest["item_count"])
        self.assertEqual("evening-show-001", manifest["items"][0]["id"])
        self.assertEqual("pt-BR-FranciscaNeural", manifest["items"][0]["voice"])
        self.assertEqual(64, len(manifest["items"][0]["text_sha256"]))

    def test_duplicate_positions_are_reported(self) -> None:
        entries = [
            ProgramEntry(1, "Session A", "First", "Group One"),
            ProgramEntry(1, "Session A", "Second", "Group Two"),
        ]

        issues = validate_program(entries)

        self.assertEqual(["duplicate_position", "duplicate_position"], [i.code for i in issues])

    def test_load_and_write_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "program.json"
            source.write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "order": 1,
                                "session": "Afternoon Showcase",
                                "choreography": "New Paths",
                                "group": "Open Stage",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            destination = Path(folder) / "out" / "manifest.json"
            written = write_manifest(build_manifest(load_program(source)), destination)

            self.assertTrue(written.exists())
            self.assertEqual(1, json.loads(written.read_text(encoding="utf-8"))["item_count"])


if __name__ == "__main__":
    unittest.main()

