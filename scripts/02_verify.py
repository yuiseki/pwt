#!/usr/bin/env python3
"""Check every file under data/raw/<release>/ against its MANIFEST.json.

Re-hashes each file (sha256, and the SHA-1 DataverseNL publishes where there
is one), tests every zip container (zip, and xlsx, which is a zip) with
zipfile.testzip, reads every gzip to the end and counts CSV rows. Files in a
release directory that are not in its manifest are reported too. Prints one
ok/FAIL line per file and exits non-zero on any failure.

    uv run python scripts/02_verify.py
"""

import csv
import gzip
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"


def hashes(path: Path) -> tuple[str, str]:
    h256, h1 = hashlib.sha256(), hashlib.sha1()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h256.update(block)
            h1.update(block)
    return h256.hexdigest(), h1.hexdigest()


def count_csv_rows(f: io.TextIOBase) -> int:
    return sum(1 for _ in csv.reader(f))


def check(path: Path, entry: dict) -> list[str]:
    problems = []
    if not path.exists():
        return ["missing"]
    if path.stat().st_size != entry["bytes"]:
        problems.append(f"size {path.stat().st_size} != {entry['bytes']}")
    sha256, sha1 = hashes(path)
    if sha256 != entry["sha256"]:
        problems.append("sha256 differs")
    published = entry.get("dataverse", {}).get("sha1")
    if published and sha1 != published:
        problems.append("SHA-1 differs from DataverseNL")
    low = path.name.lower()
    if low.endswith((".zip", ".xlsx")):
        try:
            with zipfile.ZipFile(path) as z:
                bad = z.testzip()
            if bad:
                problems.append(f"bad zip member {bad}")
        except zipfile.BadZipFile as e:
            problems.append(f"bad zip: {e}")
    elif low.endswith(".gz"):
        try:
            with gzip.open(path, "rb") as g:
                while g.read(1 << 20):
                    pass
        except (OSError, EOFError) as e:
            problems.append(f"bad gzip: {e}")
    elif low.endswith(".csv"):
        with open(path, newline="", encoding="utf-8", errors="replace") as f:
            entry["_rows"] = count_csv_rows(f)
    return problems


def main() -> int:
    failures = 0
    n = 0
    for mpath in sorted(RAW.glob("*/MANIFEST.json")):
        d = mpath.parent
        manifest = json.loads(mpath.read_text())
        files = manifest.get("files", {})
        for name, entry in sorted(files.items()):
            n += 1
            problems = check(d / name, entry)
            extra = f", {entry['_rows']:,} rows" if "_rows" in entry else ""
            if problems:
                failures += 1
                print(f"FAIL {d.name}/{name}: {'; '.join(problems)}")
            else:
                print(f"ok   {d.name}/{name}: {entry['bytes']:,} bytes{extra}")
        for p in sorted(d.iterdir()):
            if p.name != "MANIFEST.json" and p.name not in files:
                failures += 1
                print(f"FAIL {d.name}/{p.name}: not in MANIFEST.json")
    if n == 0:
        print("FAIL no manifests under data/raw/")
        return 1
    print(f"{n} files checked, {failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
