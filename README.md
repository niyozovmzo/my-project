# dupefind

**Fast, dependency-free duplicate file finder for the command line.**

Scans folders, finds byte-for-byte identical files, and tells you exactly how much
disk space they waste — using a three-stage funnel (size → head+tail hash → full
SHA-256) so even huge files are handled quickly.

```
$ dupefind ~/Downloads ~/Documents
[1] 3 files, 1.2 GB each (sha256 9f2c7a1b34e5…)
    /home/you/Downloads/movie.mkv
    /home/you/Documents/backup/movie.mkv
    /home/you/Documents/backup/movie (1).mkv
[2] 2 files, 84.0 MB each (sha256 0a11e8d9c2f4…)
    ...

Found 2 duplicate group(s), wasting 2.5 GB.
```

## Features

- :zap: **Zero dependencies** — standard library only, runs on any Python ≥ 3.9
- :mag: **Exact results** — duplicates confirmed with full SHA-256, no false positives
- :rocket: **Fast on big files** — first/last-MiB pre-filter avoids full reads of distinct files
- :bar_chart: **JSON output** — easy to script (`--json`)
- :earth_americas: **Cross-platform** — Windows, Linux, macOS

## Install

```bash
pip install .
```

Or run without installing:

```bash
PYTHONPATH=src python -m dupefind ~/Downloads
```

## Usage

```bash
# scan one or more directories (recursively)
dupefind /path/to/folder /another/folder

# ignore small files (< 10 MB)
dupefind ~/Downloads --min-size 10485760

# machine-readable output
dupefind ~/Downloads --json > dupes.json
```

The tool only **reports** duplicates — it never deletes anything by itself.
You decide what to keep.

## How it works

1. **Size pass** — files are grouped by size; unique sizes are skipped.
2. **Partial hash pass** — the first and last MiB of each candidate is hashed,
   which rejects most non-duplicates without reading the whole file.
3. **Full hash pass** — survivors are fully hashed with SHA-256 to guarantee
   byte-for-byte equality.

Complexity is O(n) in file count, with I/O only where it matters.

## Development

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## License

MIT — see [LICENSE](LICENSE).
