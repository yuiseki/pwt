#!/usr/bin/env python3
"""Push every release's files, its Parquet and the card to the Hugging Face Hub.

Every raw file goes up unchanged after its sha256 is checked against
data/raw/<release>/MANIFEST.json, and the card must declare every Parquet
file under data/parquet/ as a subset first: the main table of a release as
'<release>', any other table as '<release>.<table>'.

    uv run python src/publish.py             # dry run
    uv run python src/publish.py --push
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "yuiseki/pwt"
TABLES = ROOT / "scripts" / "TABLES.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def config_name(version: str, table: str) -> str:
    return version if table == "pwt" else f"{version}.{table}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()

    data = ROOT / "data"
    card = (data / "README.md").read_text(encoding="utf-8")
    tables = json.loads(TABLES.read_text())
    files = ["README.md", "LICENSE", "provenance.yaml"]

    declared = set()
    for version, specs in tables.items():
        for table in specs:
            rel = f"parquet/{version}/{table}.parquet"
            block = f"- config_name: '{config_name(version, table)}'\n  data_files: {rel}\n"
            if block not in card:
                raise SystemExit(f"the card does not declare the subset {rel}")
            if not (data / rel).exists():
                raise SystemExit(f"{rel} is missing; run scripts/03_export_parquet.py")
            declared.add(rel)
    on_disk = {p.relative_to(data).as_posix() for p in (data / "parquet").rglob("*.parquet")}
    if on_disk - declared:
        raise SystemExit(f"Parquet files the card does not declare: {sorted(on_disk - declared)}")

    for mpath in sorted((data / "raw").glob("*/MANIFEST.json")):
        d = mpath.parent
        manifest = json.loads(mpath.read_text())["files"]
        for name, m in manifest.items():
            if sha256(d / name) != m["sha256"]:
                raise SystemExit(f"raw/{d.name}/{name} is not the file in its manifest")
        files += [f"raw/{d.name}/MANIFEST.json"] + [f"raw/{d.name}/{n}" for n in sorted(manifest)]
    files += sorted(declared)

    total = sum((data / f).stat().st_size for f in files)
    for f in files:
        print(f"  {(data / f).stat().st_size:>12,}  {f}")
    print(f"{a.repo}\n  {len(files)} files, {total / 1e6:.1f} MB")
    if not a.push:
        print("\ndry run. pass --push to upload")
        return 0

    from huggingface_hub import HfApi

    api = HfApi()
    api.create_repo(a.repo, repo_type="dataset", exist_ok=True, private=False)
    api.upload_folder(
        folder_path=str(data), repo_id=a.repo, repo_type="dataset", allow_patterns=files
    )
    print(f"\npushed to https://huggingface.co/datasets/{a.repo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
