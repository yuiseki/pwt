#!/usr/bin/env python3
"""Check every file under data/raw/<release>/ against its MANIFEST.json.

Re-hashes each file (sha256, and the SHA-1 DataverseNL publishes where there
is one), tests every zip container (zip, and xlsx, which is a zip) with
zipfile.testzip, reads every gzip to the end and counts CSV rows. Files in a
release directory that are not in its manifest are reported too.

Then checks every Parquet table listed in scripts/TABLES.json:
  - its row count equals the Stata file's own count (the N of its header),
    and, where PWT ships the same table as xlsx, the rows of the xlsx
    (8.1's main table excepted: its xlsx has 3 more rows, see KNOWN_XLSX_EXTRA)
  - every value equals the value read from the Stata file with src/dta.py
    (labels applied, empty strings as NULL), compared one by one, with a
    sha256 over all of them printed for the record
  - every column has the type 03_export_parquet.column_type gives its name
  - where there is an xlsx, every value agrees with it, read by DuckDB's
    excel extension, a reader independent of src/dta.py: text equal, numbers
    within a relative 1e-6 (the xlsx of 11.0 rounds to 15 significant
    digits), or 5e-4 for the national accounts of 8.1 and 9.0, whose xlsx
    rounds many values to 4 significant digits (XLSX_TOLERANCE); rows are
    matched on countrycode and year (and currency_unit in the main table)
  - for the main tables, the (countrycode, country) pairs equal the xlsx's,
    which checks how the Stata strings were decoded
  - a plain DuckDB without extensions opens the file
  - no row group carries a bloom filter

Prints one ok/FAIL line per check and exits non-zero on any failure.

    uv run python scripts/02_verify.py
"""

import csv
import gzip
import hashlib
import importlib.util
import io
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PQ = ROOT / "data" / "parquet"
TABLES = ROOT / "scripts" / "TABLES.json"
# 8.1's pwt81.xlsx holds Zimbabwe 2009 to 2011 twice, once with currency_unit
# "US Dollar" (as in pwt81.dta) and once with "Zimbabwe Dollar" and other values.
KNOWN_XLSX_EXTRA = {("8.1", "pwt"): 3}
# The national accounts xlsx of 8.1 and 9.0 hold many values rounded to 4
# significant digits (124200000 for 124151822.432507); the dta has them whole.
XLSX_TOLERANCE = {("8.1", "na_data"): 5e-4, ("9.0", "na_data"): 5e-4}

_spec = importlib.util.spec_from_file_location("export", ROOT / "scripts" / "03_export_parquet.py")
export = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(export)


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


def digest(rows) -> str:
    h = hashlib.sha256()
    for r in rows:
        h.update(repr(r).encode())
    return h.hexdigest()


def xlsx_disagreements(
    con, p: Path, xl: str, names: list[str], table: str, tol: float = 1e-6
) -> dict:
    """Columns whose values differ between the Parquet and the xlsx, with counts."""
    xcols = con.sql(f"select * from {xl} limit 0").columns
    keys = ["countrycode", "year"] + (["currency_unit"] if table == "pwt" else [])
    on = " and ".join(
        f"p.{k} = cast(cast(x.{k} as double) as integer)" if k == "year" else f"p.{k} = x.{k}"
        for k in keys
    )
    tests = []
    for c in names:
        if c not in xcols or c in keys:
            continue
        pc, xc = f'p."{c}"', f"nullif(x.\"{c}\", '')"
        if export.column_type(c) == "VARCHAR":
            bad = f"{pc} is distinct from {xc}"
        else:
            xv = f"cast({xc} as double)"
            bad = (
                f"({pc} is null) <> ({xc} is null) or "
                f"abs({pc} - {xv}) > {tol} * greatest(abs({pc}), abs({xv}))"
            )
        tests.append(f'count(*) filter (where {bad}) as "{c}"')
    missing = con.sql(f"select count(*) from '{p}' p anti join {xl} x on {on}").fetchone()[0]
    r = con.sql(f"select {', '.join(tests)} from '{p}' p join {xl} x on {on}")
    out = {c: n for c, n in zip(r.columns, r.fetchone(), strict=True) if n}
    if missing:
        out["rows not in the xlsx"] = missing
    return out


def check_parquet() -> int:
    import duckdb

    failures = []

    def ok(good: bool, what: str) -> None:
        print(("ok   " if good else "FAIL ") + what)
        if not good:
            failures.append(what)

    con = duckdb.connect()
    con.execute("set memory_limit = '8GB'; load excel")
    plain = duckdb.connect()
    plain.execute("set memory_limit = '8GB'")
    for version, specs in json.loads(TABLES.read_text()).items():
        for table, spec in specs.items():
            name = f"{version}/{table}"
            p = PQ / version / f"{table}.parquet"
            if not p.exists():
                ok(False, f"{name}: {p.name} missing")
                continue
            source, d = export.load(version, spec)
            want = export.expected_rows(d)
            got = con.sql(f"select * from '{p}'").fetchall()
            ok(
                len(got) == d.nobs == len(want),
                f"{name}: {len(got):,} rows, {source} says {d.nobs:,}",
            )

            if "xlsx" in spec:
                x = RAW / version / spec["xlsx"]
                sheet = spec.get("sheet", "Data")
                xl = f"read_xlsx('{x}', sheet = '{sheet}', all_varchar = true)"
                n = con.sql(f"select count(*) from {xl}").fetchone()[0]
                extra = KNOWN_XLSX_EXTRA.get((version, table), 0)
                ok(
                    n == d.nobs + extra,
                    f"{name}: {spec['xlsx']} has {n:,} rows"
                    + (f" ({extra} more than the dta, known)" if extra else ", as the dta"),
                )
                tol = XLSX_TOLERANCE.get((version, table), 1e-6)
                agree = xlsx_disagreements(con, p, xl, d.names, table, tol)
                ok(not agree, f"{name}: every value agrees with the xlsx to {tol} {agree or ''}")
                if table == "pwt":
                    xs = set(con.sql(f"select distinct countrycode, country from {xl}").fetchall())
                    ps = set(con.sql(f"select distinct countrycode, country from '{p}'").fetchall())
                    ok(xs == ps, f"{name}: {len(ps)} country names as in the xlsx")

            same = got == want
            if not same:
                bad = next(i for i, (a, b) in enumerate(zip(got, want, strict=False)) if a != b)
                print(f"     first difference at row {bad}: {got[bad]} != {want[bad]}")
            ok(same, f"{name}: every value as in the dta, sha256 {digest(want)[:16]}")

            types = dict(
                con.sql(
                    f"select column_name, column_type from (describe select * from '{p}')"
                ).fetchall()
            )
            wrong = {c: t for c, t in types.items() if t != export.column_type(c)}
            ok(
                not wrong and list(types) == d.names,
                f"{name}: {len(types)} columns, names as in the dta, types by name {wrong or ''}",
            )

            n = plain.sql(f"select count(*) from '{p}'").fetchone()[0]
            ok(n == d.nobs, f"{name}: a DuckDB without extensions opens it")

            bloom = con.sql(
                "select count(*) filter (where bloom_filter_offset is not null) "
                f"from parquet_metadata('{p}')"
            ).fetchone()[0]
            ok(bloom == 0, f"{name}: no bloom filters")
    print(f"Parquet: {len(failures)} failures")
    return len(failures)


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
    failures += check_parquet()
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
