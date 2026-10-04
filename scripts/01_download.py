#!/usr/bin/env python3
"""Fetch every Penn World Table release published under CC BY 4.0.

Versions are the PWT release numbers (8.0 ... 11.0), not fetch dates: each
release is a fixed publication. Files go to data/raw/<release>/.

Discovery, from the official pages only:
  1. The current release page (https://www.rug.nl/ggdc/productivity/pwt/) and
     every page linked from "Earlier Releases" are read. The release number
     comes from the page title, the DOI and the licence link from the page.
  2. A page without a link to the CC BY 4.0 licence (PWT 7.1 and earlier) is
     skipped: those releases state no licence.
  3. A release whose DOI is a DataverseNL one (10.34894/..., i.e. 11.0 and
     10.01) is listed through the public Dataverse API
     (/api/datasets/:persistentId/versions). Files of the latest released
     dataset version are taken, each checked against the SHA-1 Dataverse
     publishes. MANIFEST.json records the dataset version, the datafile id
     and file version, and any datafile of the same name in an earlier
     dataset version (in 11.0, pwt110.xlsx was replaced three days after
     release).
  4. Older releases (DOI 10.15141/...) are taken from the links under
     https://www.rug.nl/ggdc/docs/ on their page.

Taken: xlsx, dta, zip and pdf. Not taken: the ICP benchmark workbooks (.xls),
and the journal article "The Next Generation of the Penn World Table", which
is the AER paper rather than release documentation.

Each file is written to a .part file, checked against Content-Length, then
renamed. A file already in MANIFEST.json whose local copy still has the
recorded sha256 (and, for Dataverse, whose published SHA-1 has not changed)
is not fetched again.

    uv run python scripts/01_download.py
"""

import hashlib
import json
import re
import shutil
import sys
import time
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
UA = "pwt/1 (+https://github.com/yuiseki/pwt)"
SITE = "https://www.rug.nl"
CURRENT = SITE + "/ggdc/productivity/pwt/"
LISTING = SITE + "/ggdc/productivity/pwt/earlier-releases"
DATAVERSE = "https://dataverse.nl"
CC_BY = re.compile(r"https?://creativecommons\.org/licenses/by/4\.0/?")
WANTED_EXT = (".xlsx", ".dta", ".zip", ".pdf")
NOT_DOCS = ("the_next_generation_of_the_penn_world_table",)
SIZE_LIMIT = 1_000_000_000
DELAY = 1.2

_last_request = 0.0


# ---------------------------------------------------------------- parsing


def release_pages(listing_html: str) -> list[str]:
    """Absolute URLs of the release pages linked from Earlier Releases, in page order."""
    out: list[str] = []
    for href in re.findall(r'href="(/ggdc/productivity/pwt/pwt-releases/[^"#?!]+)"', listing_html):
        url = SITE + href
        if url not in out:
            out.append(url)
    return out


def version_from_title(html: str) -> str | None:
    m = re.search(r"<title>\s*PWT\s+(\d+\.\d+)\b", html)
    return m.group(1) if m else None


def wanted(name: str) -> bool:
    low = name.lower()
    return low.endswith(WANTED_EXT) and not any(low.startswith(p) for p in NOT_DOCS)


def parse_release_page(html: str) -> dict:
    lic = CC_BY.search(html)
    doi = re.search(r"\b(10\.(?:34894|15141)/[A-Z0-9]+)\b", html)
    stmt = re.search(r"\b((?:Published|released) on [A-Z][a-z]+ \d{1,2}, \d{4})", html)
    docs: list[str] = []
    for href in re.findall(r'href="(/ggdc/docs/[^"]+)"', html):
        url = SITE + unescape(href)
        if wanted(Path(urllib.parse.urlparse(url).path).name) and url not in docs:
            docs.append(url)
    return {
        "version": version_from_title(html),
        "licence": lic.group(0) if lic else None,
        "doi": doi.group(1) if doi else None,
        "release_statement": stmt.group(1) if stmt else None,
        "docs": docs,
    }


def is_dataverse(doi: str | None) -> bool:
    return bool(doi) and doi.startswith("10.34894/")


def _vlabel(v: dict) -> str:
    return f"{v['versionNumber']}.{v['versionMinorNumber']}"


def dataverse_files(versions: list[dict]) -> dict:
    """Files of the latest released version, with earlier datafiles of the same name."""
    released = [v for v in versions if v.get("versionState") == "RELEASED"]
    released.sort(key=lambda v: (v["versionNumber"], v["versionMinorNumber"]), reverse=True)
    latest, older = released[0], released[1:]
    files, skipped = [], []
    for f in latest["files"]:
        df = f["dataFile"]
        name = df["filename"]
        if f.get("restricted") or not wanted(name):
            skipped.append(name)
            continue
        earlier = []
        for v in older:
            for g in v["files"]:
                gd = g["dataFile"]
                if gd["filename"] == name and gd["id"] != df["id"]:
                    earlier.append(
                        {
                            "dataset_version": _vlabel(v),
                            "datafile_id": gd["id"],
                            "bytes": gd["filesize"],
                            "sha1": gd["checksum"]["value"],
                        }
                    )
        assert df["checksum"]["type"] == "SHA-1", df["checksum"]
        files.append(
            {
                "filename": name,
                "url": f"{DATAVERSE}/api/access/datafile/{df['id']}",
                "datafile_id": df["id"],
                "file_version": f.get("version"),
                "bytes": df["filesize"],
                "sha1": df["checksum"]["value"],
                "content_type": df.get("contentType"),
                "creation_date": df.get("creationDate"),
                "earlier_datafiles": earlier,
            }
        )
    files.sort(key=lambda x: x["filename"])
    return {
        "dataset_version": _vlabel(latest),
        "release_time": latest.get("releaseTime"),
        "publication_date": latest.get("publicationDate"),
        "licence": (latest.get("license") or {}).get("uri"),
        "files": files,
        "skipped": sorted(skipped),
    }


# ---------------------------------------------------------------- network


def _wait() -> None:
    global _last_request
    gap = time.monotonic() - _last_request
    if gap < DELAY:
        time.sleep(DELAY - gap)
    _last_request = time.monotonic()


def get_text(url: str) -> str:
    _wait()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8")


def file_hashes(path: Path) -> tuple[str, str]:
    h256, h1 = hashlib.sha256(), hashlib.sha1()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h256.update(block)
            h1.update(block)
    return h256.hexdigest(), h1.hexdigest()


def fetch(url: str, dest: Path) -> dict:
    _wait()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    tmp = dest.with_name(dest.name + ".part")
    with urllib.request.urlopen(req, timeout=600) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f, 1 << 20)
        length = r.headers.get("Content-Length")
        lm = r.headers.get("Last-Modified", "")
        final_url = r.geturl()
    got = tmp.stat().st_size
    if length is not None and got != int(length):
        tmp.unlink()
        raise SystemExit(f"{url}: got {got} bytes, the server stated {length}")
    tmp.replace(dest)
    sha256, sha1 = file_hashes(dest)
    entry = {
        "url": url,
        "bytes": got,
        "sha256": sha256,
        "sha1": sha1,
        "last_modified": lm,
        "fetched_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    if final_url != url:
        entry["served_from"] = urllib.parse.urlsplit(final_url)._replace(query="").geturl()
    return entry


def still_there(d: Path, name: str, entry: dict | None) -> bool:
    if not entry or not (d / name).exists():
        return False
    return file_hashes(d / name)[0] == entry["sha256"]


# ---------------------------------------------------------------- main


def collect() -> list[dict]:
    pages = [CURRENT] + release_pages(get_text(LISTING))
    releases, seen = [], set()
    for url in pages:
        page = parse_release_page(get_text(url))
        v = page["version"]
        if v is None or v in seen:
            continue
        seen.add(v)
        page["page"] = url
        if page["licence"] is None:
            print(f"skip {v}: no licence stated on {url}")
            continue
        releases.append(page)
    return releases


def main() -> int:
    releases = collect()
    plans = []
    for page in releases:
        if is_dataverse(page["doi"]):
            q = urllib.parse.urlencode({"persistentId": f"doi:{page['doi']}"})
            versions = json.loads(get_text(f"{DATAVERSE}/api/datasets/:persistentId/versions?{q}"))
            dv = dataverse_files(versions["data"])
            if dv["skipped"]:
                print(f"{page['version']}: not taken from Dataverse: {', '.join(dv['skipped'])}")
            files = [(f["filename"], f["url"], f) for f in dv["files"]]
            release = {
                k: page[k] for k in ("version", "page", "doi", "licence", "release_statement")
            }
            release["dataverse"] = {
                k: dv[k] for k in ("dataset_version", "release_time", "publication_date", "licence")
            }
        else:
            files = [(Path(urllib.parse.urlparse(u).path).name, u, None) for u in page["docs"]]
            release = {
                k: page[k] for k in ("version", "page", "doi", "licence", "release_statement")
            }
        plans.append((release, files))

    known = sum(f["bytes"] for _, files in plans for _, _, f in files if f)
    print(f"{len(plans)} releases, {sum(len(f) for _, f in plans)} files")

    total = 0
    for release, files in plans:
        d = RAW / release["version"]
        d.mkdir(parents=True, exist_ok=True)
        mpath = d / "MANIFEST.json"
        old = json.loads(mpath.read_text()) if mpath.exists() else {}
        manifest = {"release": release, "files": old.get("files", {})}
        for name, url, dvf in files:
            entry = manifest["files"].get(name)
            if (
                still_there(d, name, entry)
                and entry["url"] == url
                and (dvf is None or entry.get("sha1") == dvf["sha1"])
            ):
                total += entry["bytes"]
                continue
            if total + (dvf["bytes"] if dvf else 0) > SIZE_LIMIT or known > SIZE_LIMIT:
                raise SystemExit("stopping: the collection would exceed the 1GB size limit")
            entry = fetch(url, d / name)
            if dvf:
                if entry["sha1"] != dvf["sha1"] or entry["bytes"] != dvf["bytes"]:
                    (d / name).unlink()
                    raise SystemExit(f"{url}: SHA-1 or size differs from what Dataverse publishes")
                entry["dataverse"] = {
                    k: dvf[k]
                    for k in (
                        "datafile_id",
                        "file_version",
                        "creation_date",
                        "content_type",
                        "earlier_datafiles",
                    )
                }
                entry["dataverse"]["sha1"] = dvf["sha1"]
                entry["dataverse"]["sha1_matches"] = True
            manifest["files"][name] = entry
            total += entry["bytes"]
            if total > SIZE_LIMIT:
                raise SystemExit("stopping: the collection exceeded the 1GB size limit")
            print(f"{release['version']}/{name}: {entry['bytes']:,} bytes")
            mpath.write_text(json.dumps(manifest, indent=1) + "\n")
        mpath.write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"total {total:,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
