#!/usr/bin/env python3
"""Turn each release's Stata tables into typed Parquet, one file per table.

The source of every table is its Stata file (.dta), listed in
scripts/TABLES.json: PWT ships each table as Stata and, for some, as Excel
too, and the Stata file is the exact one (11.0's xlsx rounds to 15
significant digits, the national accounts xlsx of 8.1 and 9.0 to about 8).
For 8.0 and 8.1 the Stata file is inside a zip and is read from there.
src/dta.py reads it with the standard library.

The type of a column comes from its name, never from inference:

  - the identifiers countrycode, country, currency_unit, countrycode1,
    countrycode2, countryname, indicatorname, seriescode are text
  - columns whose codes carry Stata value labels (LABELLED: i_cig, i_xr,
    source, ...) are written as their labels, the text PWT's own xlsx shows
  - year and i_mix are INTEGER and must be whole numbers
  - the measures (NUMERIC and NUMERIC_PATTERNS) are DOUBLE; a 4-byte float
    is widened exactly
  - any other name stays text

Each value goes through a staging CSV in data/work/ and is checked with a
regular expression before the cast; a value that does not fit stops the run
with the file, the column and the value. Rows keep the order of the Stata
file. An empty Stata string is Stata's missing string and becomes NULL.

    uv run python scripts/03_export_parquet.py
"""

from __future__ import annotations

import csv
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import dta  # noqa: E402

RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "parquet"
WORK = ROOT / "data" / "work"
TABLES = ROOT / "scripts" / "TABLES.json"

TEXT = {
    "countrycode", "country", "currency_unit", "countrycode1", "countrycode2",
    "countryname", "indicatorname", "seriescode",
}  # fmt: skip
LABELLED = {
    "i_cig", "i_xm", "i_xr", "i_outlier", "i_irr",
    "i_emp", "source", "i_labsh", "i_labsh2", "i_comp_sh",
    "i_lab_sh1", "i_lab_sh2", "i_lab_sh3", "i_lab_sh4",
}  # fmt: skip
INTEGERS = {"year", "i_mix"}
NUMERIC = {
    # main table
    "rgdpe", "rgdpo", "pop", "emp", "avh", "hc", "ccon", "cda", "cgdpe", "cgdpo",
    "cn", "ck", "ctfp", "cwtfp", "rgdpna", "rconna", "rdana", "rnna", "rkna",
    "rtfpna", "rwtfpna", "labsh", "irr", "delta", "xr", "pl_con", "pl_da",
    "pl_gdpo", "pl_gdpe", "cor_exp", "statcap",
    "csh_c", "csh_i", "csh_g", "csh_x", "csh_m", "csh_r",
    "pl_c", "pl_i", "pl_g", "pl_x", "pl_m", "pl_n", "pl_k",
    # national accounts
    "xr2",
    # labour detail
    "yr_sch", "comp_sh",
    # depreciation rates (8.0)
    "delta_k",
}  # fmt: skip
NUMERIC_PATTERNS = (
    r"[vq]_(c|i|g|x|m|gdp|gfcf)",  # national accounts, current and constant prices
    r"(Ic|Ip|Nc|Np|Dc|Kc|Kp|Ksh)_(Struc|Mach|TraEq|Other)",  # capital detail
    r"(pl|csh)_[xm][1-6]",  # trade detail, by BEC category
    r"lab_sh[1-4]",  # labour detail
)

NUMBER = r"-?[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?"
WHOLE = r"-?[0-9]+(\.0)?"


class ExportError(ValueError):
    pass


def column_type(name: str) -> str:
    if name in TEXT or name in LABELLED:
        return "VARCHAR"
    if name in INTEGERS:
        return "INTEGER"
    if name in NUMERIC or any(re.fullmatch(p, name) for p in NUMERIC_PATTERNS):
        return "DOUBLE"
    return "VARCHAR"


def check_names(source: str, names: list[str]) -> None:
    """DuckDB matches column names without case; PWT has no such pair, so one stops the run."""
    seen: dict[str, str] = {}
    for n in names:
        if n.lower() in seen:
            raise ExportError(f"{source}: {seen[n.lower()]} and {n} clash in DuckDB")
        seen[n.lower()] = n


def check_labels(source: str, d: dta.Dta) -> None:
    for v in d.variables:
        if v.value_label and v.name not in LABELLED:
            raise ExportError(f"{source}: {v.name} has value labels the type rule does not expect")
        if v.name in LABELLED and not v.value_label:
            raise ExportError(f"{source}: {v.name} has no value labels")
        if v.value_label and v.value_label not in d.value_labels:
            raise ExportError(f"{source}: {v.name} names the missing label set {v.value_label}")


def stage_value(x, v: dta.Variable, labels: dict[str, dict[int, str]]) -> str:
    """The text of one value in the staging CSV; '' is NULL."""
    if x is None:
        return ""
    if v.value_label:
        table = labels[v.value_label]
        if x not in table:
            raise ExportError(f"{v.name} has the code {x!r}, which has no label")
        return table[x]
    if v.kind == "str":
        return x
    return repr(x) if isinstance(x, float) else str(x)


def expected_rows(d: dta.Dta) -> list[tuple]:
    """The rows as the Parquet must hold them: labels applied, empty strings NULL."""
    out = []
    for r in d.rows:
        row = []
        for v, x in zip(d.variables, r, strict=True):
            if x is None or (v.kind == "str" and x == ""):
                row.append(None)
            elif v.value_label:
                row.append(d.value_labels[v.value_label][x])
            else:
                row.append(x)
        out.append(tuple(row))
    return out


def _expr(source: str, name: str) -> str:
    c, t = f'"{name}"', column_type(name)
    if t == "VARCHAR":
        return f"{c} as {c}"
    if t == "INTEGER":
        ok, what, cast = (
            f"regexp_full_match({c}, '{WHOLE}')",
            "a whole number",
            (f"cast(cast({c} as double) as integer)"),
        )
    else:
        ok, what, cast = f"regexp_full_match({c}, '{NUMBER}')", "a number", f"cast({c} as double)"
    return (
        f"case when {c} is null then null when {ok} then {cast} "
        f"else error('{source}: {name} is not {what}: ' || {c}) end as {c}"
    )


def select_sql(con, path: Path, source: str) -> str:
    src = (
        f"read_csv('{path}', header = true, all_varchar = true, strict_mode = true, "
        "quote = '\"', escape = '\"')"
    )
    names = con.sql(f"select * from {src} limit 0").columns
    return f"select {', '.join(_expr(source, n) for n in names)} from {src}"


def load(version: str, spec: dict) -> tuple[str, dta.Dta]:
    path = RAW / version / spec["file"]
    if "member" in spec:
        with zipfile.ZipFile(path) as z:
            data = z.read(spec["member"])  # CRC checked by zipfile
        source = f"{spec['file']}/{spec['member']}"
    else:
        data = path.read_bytes()
        source = spec["file"]
    return source, dta.parse(data, spec.get("encoding", "ascii"))


def stage(d: dta.Dta, path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(d.names)
        for r in d.rows:
            w.writerow(
                [stage_value(x, v, d.value_labels) for v, x in zip(d.variables, r, strict=True)]
            )


def main() -> int:
    import duckdb

    con = duckdb.connect()
    con.execute("set memory_limit = '8GB'")
    tables = json.loads(TABLES.read_text())
    for version, specs in tables.items():
        for table, spec in specs.items():
            source, d = load(version, spec)
            check_names(source, d.names)
            check_labels(source, d)
            work = WORK / version
            work.mkdir(parents=True, exist_ok=True)
            csv_path = work / f"{table}.csv"
            stage(d, csv_path)
            out = OUT / version
            out.mkdir(parents=True, exist_ok=True)
            p = out / f"{table}.parquet"
            con.execute(
                f"copy ({select_sql(con, csv_path, source)}) to '{p}' "
                "(format parquet, compression zstd, write_bloom_filter false)"
            )
            got = con.sql(f"select count(*) from '{p}'").fetchone()[0]
            if got != d.nobs:
                raise SystemExit(f"{version}/{table}: {got} rows written, {source} has {d.nobs}")
            csv_path.unlink()
            text = [n for n in d.names if column_type(n) == "VARCHAR" and n not in TEXT | LABELLED]
            note = f", kept as text by default: {text}" if text else ""
            print(
                f"{version}/{table}: {got:,} rows, {len(d.names)} columns, "
                f"{p.stat().st_size:,} bytes{note}",
                flush=True,
            )
        if (WORK / version).exists() and not any((WORK / version).iterdir()):
            (WORK / version).rmdir()
    if WORK.exists() and not any(WORK.iterdir()):
        WORK.rmdir()
    return 0


if __name__ == "__main__":
    sys.exit(main())
