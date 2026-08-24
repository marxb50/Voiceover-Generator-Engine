"""Command-line entry point for the public reference pipeline."""

from __future__ import annotations

import argparse
import sys

from .pipeline import build_manifest, load_program, validate_program, write_manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a festival program and create an auditable TTS manifest."
    )
    parser.add_argument("program", help="Path to a JSON program file")
    parser.add_argument(
        "--output", default="manifest.json", help="Destination JSON manifest"
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        entries = load_program(args.program)
        issues = validate_program(entries)
        if issues:
            for issue in issues:
                print(
                    f"[{issue.code}] entry {issue.entry_index}: {issue.message}",
                    file=sys.stderr,
                )
            return 2
        destination = write_manifest(build_manifest(entries), args.output)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"manifest written to {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

