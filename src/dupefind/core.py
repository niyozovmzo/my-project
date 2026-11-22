"""Core engine for finding duplicate files."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from typing import Iterable, Iterator

CHUNK = 1024 * 1024  # 1 MiB


@dataclass
class Group:
    """A group of files that are byte-for-byte duplicates."""

    files: list[str]
    size: int
    sha256: str


def _walk(paths: Iterable[str]) -> Iterator[str]:
    """Yield regular files under the given paths (files pass through)."""
    for path in paths:
        path = os.path.abspath(path)
        if os.path.isfile(path):
            yield path
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                dirs.sort()
                for name in sorted(files):
                    yield os.path.join(root, name)


def _hash_file(path: str, full: bool) -> str:
    """SHA-256 of a file; when not full, hash only head+tail (2 MiB total)."""
    digest = hashlib.sha256()
    size = os.path.getsize(path)
    with open(path, "rb") as fh:
        if not full and size > 2 * CHUNK:
            digest.update(fh.read(CHUNK))
            fh.seek(-CHUNK, os.SEEK_END)
            digest.update(fh.read(CHUNK))
        else:
            while True:
                block = fh.read(CHUNK)
                if not block:
                    break
                digest.update(block)
    return digest.hexdigest()


def find_duplicates(paths: Iterable[str], min_size: int = 1) -> list[Group]:
    """Find duplicate groups. Uses a size -> partial hash -> full hash funnel."""
    # 1) Group by size.
    by_size: dict[int, list[str]] = {}
    for file in _walk(paths):
        try:
            size = os.path.getsize(file)
        except OSError:
            continue
        if size >= min_size:
            by_size.setdefault(size, []).append(file)

    # 2) Group by head+tail hash.
    by_partial: dict[tuple[int, str], list[str]] = {}
    for size, files in by_size.items():
        if len(files) < 2:
            continue
        for file in files:
            try:
                digest = _hash_file(file, full=False)
            except OSError:
                continue
            by_partial.setdefault((size, digest), []).append(file)

    # 3) Confirm with a full hash.
    groups: list[Group] = []
    for (size, _), files in by_partial.items():
        if len(files) < 2:
            continue
        by_full: dict[str, list[str]] = {}
        for file in files:
            try:
                digest = _hash_file(file, full=True)
            except OSError:
                continue
            by_full.setdefault(digest, []).append(file)
        for digest, dupes in by_full.items():
            if len(dupes) >= 2:
                groups.append(Group(files=sorted(dupes), size=size, sha256=digest))

    # Most wasteful first.
    groups.sort(key=lambda g: -(g.size * (len(g.files) - 1)))
    return groups


def wasted_bytes(groups: Iterable[Group]) -> int:
    """Bytes that could be reclaimed by keeping one copy per group."""
    return sum(group.size * (len(group.files) - 1) for group in groups)
