"""Command line interface for dupefind."""

from __future__ import annotations

import argparse
import json
import sys

from .core import find_duplicates, wasted_bytes


def _human(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size} B" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dupefind",
        description="Find duplicate files and show how much space they waste.",
    )
    parser.add_argument(
        "paths", nargs="+", help="files or directories to scan"
    )
    parser.add_argument(
        "--min-size",
        type=int,
        default=1,
        help="ignore files smaller than N bytes (default: 1)",
    )
    parser.add_argument(
        "--json", action="store_true", help="print results as JSON"
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s 1.0.0"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    groups = find_duplicates(args.paths, min_size=args.min_size)

    if args.json:
        print(
            json.dumps(
                {
                    "duplicate_groups": [
                        {"size": g.size, "sha256": g.sha256, "files": g.files}
                        for g in groups
                    ],
                    "wasted_bytes": wasted_bytes(groups),
                },
                indent=2,
            )
        )
        return 0

    if not groups:
        print("No duplicates found.")
        return 0

    for index, group in enumerate(groups, 1):
        print(
            f"[{index}] {len(group.files)} files, "
            f"{_human(group.size)} each (sha256 {group.sha256[:12]}…)"
        )
        for file in group.files:
            print(f"    {file}")

    print()
    print(
        f"Found {len(groups)} duplicate group(s), "
        f"wasting {_human(wasted_bytes(groups))}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
