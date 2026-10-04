import importlib.util
import struct
import sys
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import dta  # noqa: E402

_spec = importlib.util.spec_from_file_location("export", ROOT / "scripts" / "03_export_parquet.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


# ---------- a tiny format-115 file, built here so the reader is tested on known bytes


def dta115(variables, rows, labels=None, order="<"):
    """variables: (name, type code, value label name); rows: tuples of Python values."""
    nvar = len(variables)
    b = bytes([115, 2 if order == "<" else 1, 1, 0])
    b += struct.pack(order + "Hl", nvar, len(rows))
    b += b"test".ljust(81, b"\0") + b"01 Jan 2000 00:00".ljust(18, b"\0")
    b += bytes(t for _, t, _ in variables)
    b += b"".join(n.encode().ljust(33, b"\0") for n, _, _ in variables)
    b += b"\0" * 2 * (nvar + 1)
    b += b"".join(b"%9.0g".ljust(49, b"\0") for _ in variables)
    b += b"".join((lab or "").encode().ljust(33, b"\0") for _, _, lab in variables)
    b += b"".join(f"label of {n}".encode().ljust(81, b"\0") for n, _, _ in variables)
    b += b"\0" + struct.pack(order + "l", 0)
    codes = {251: "b", 252: "h", 253: "l", 254: "f", 255: "d"}
    for row in rows:
        for (_, t, _), x in zip(variables, row, strict=True):
            if t <= 244:
                b += x.ljust(t, b"\0") if isinstance(x, bytes) else x.encode().ljust(t, b"\0")
            else:
                b += struct.pack(order + codes[t], x)
    for name, table in (labels or {}).items():
        vals = list(table)
        txt, offs = b"", []
        for v in vals:
            offs.append(len(txt))
            txt += table[v].encode() + b"\0"
        body = struct.pack(order + "ll", len(vals), len(txt))
        body += struct.pack(order + f"{len(vals)}l", *offs)
        body += struct.pack(order + f"{len(vals)}l", *vals)
        body += txt
        b += struct.pack(order + "l", len(body)) + name.encode().ljust(33, b"\0") + b"\0" * 3 + body
    return b


VARS = [
    ("countrycode", 3, None),
    ("year", 252, None),
    ("rgdpe", 254, None),
    ("pop", 255, None),
    ("i_xr", 251, "x"),
]
LABELS = {"x": {0: "Market", 1: "Estimated"}}


@pytest.mark.parametrize("order", ["<", ">"])
def test_reader_values_missing_and_labels(order):
    rows = [
        ("JPN", 2000, 14200.9, 126.8, 0),
        ("USA", 2001, 2.0**127, 2.0**1023, 101),  # Stata's missing . for float, double, byte
    ]
    d = dta.parse(dta115(VARS, rows, LABELS, order))
    assert d.format == 115 and d.nobs == 2 and d.names == [v[0] for v in VARS]
    # a 4-byte float is widened exactly, as PWT's own xlsx files write it
    assert d.rows[0] == ("JPN", 2000, 14200.900390625, 126.8, 0)
    assert d.rows[1] == ("USA", 2001, None, None, None)
    assert d.variables[4].value_label == "x" and d.value_labels == LABELS
    assert d.variables[2].label == "label of rgdpe"


def test_reader_refuses_a_byte_it_was_not_told_how_to_decode():
    rows = [(b"C\x99te", 2000, 1.0, 1.0, 0)]
    with pytest.raises(dta.DtaError, match="not ascii"):
        dta.parse(dta115([("country", 5, None)] + VARS[1:], rows, LABELS))
    d = dta.parse(dta115([("country", 5, None)] + VARS[1:], rows, LABELS), "mac_roman")
    assert d.rows[0][0] == "Côte"


def test_reader_refuses_a_cut_file():
    b = dta115(VARS, [("JPN", 2000, 1.0, 1.0, 0)], LABELS)
    with pytest.raises(dta.DtaError):
        dta.parse(b[:-120])


def test_reader_refuses_an_unknown_format():
    with pytest.raises(dta.DtaError, match="format 113"):
        dta.parse(bytes([113]) + b"\0" * 200)


# ---------- the type rule


@pytest.mark.parametrize(
    ("name", "sql"),
    [
        ("countrycode", "VARCHAR"),
        ("country", "VARCHAR"),
        ("currency_unit", "VARCHAR"),
        ("countrycode1", "VARCHAR"),
        ("indicatorname", "VARCHAR"),
        ("year", "INTEGER"),
        ("i_mix", "INTEGER"),
        ("rgdpe", "DOUBLE"),
        ("pop", "DOUBLE"),
        ("pl_gdpe", "DOUBLE"),
        ("statcap", "DOUBLE"),
        ("cor_exp", "DOUBLE"),
        ("xr2", "DOUBLE"),
        ("v_gfcf", "DOUBLE"),
        ("q_gdp", "DOUBLE"),
        ("Ksh_TraEq", "DOUBLE"),
        ("Nc_Struc", "DOUBLE"),
        ("pl_x6", "DOUBLE"),
        ("csh_m1", "DOUBLE"),
        ("lab_sh4", "DOUBLE"),
        ("delta_k", "DOUBLE"),
        # value-labelled codes are written as their labels
        ("i_cig", "VARCHAR"),
        ("i_irr", "VARCHAR"),
        ("source", "VARCHAR"),
        ("i_lab_sh3", "VARCHAR"),
        # a name the rule does not know stays text
        ("pl_x7", "VARCHAR"),
        ("a_column_of_a_future_release", "VARCHAR"),
    ],
)
def test_column_type(name, sql):
    assert m.column_type(name) == sql


def test_every_labelled_name_is_text():
    assert all(m.column_type(n) == "VARCHAR" for n in m.LABELLED)


# ---------- values as staged and as cast


def _rel(tmp_path, header, line):
    f = tmp_path / "t.csv"
    f.write_text(header + "\n" + line + "\n", encoding="utf-8")
    con = duckdb.connect()
    return con.sql(m.select_sql(con, f, "t.dta"))


HEADER = "countrycode,year,rgdpe,i_xr"


def test_values_are_typed_and_text_stays_text(tmp_path):
    row = _rel(tmp_path, HEADER, "JPN,2000.0,14200.900390625,Estimated").fetchone()
    assert row == ("JPN", 2000, 14200.900390625, "Estimated")


def test_a_number_in_exponent_form_is_read(tmp_path):
    assert _rel(tmp_path, HEADER, "JPN,2000,3.313212077759635e-09,").fetchone()[2] == (
        3.313212077759635e-09
    )


@pytest.mark.parametrize(
    ("line", "message"),
    [
        ("JPN,2000.5,1.0,Market", "t.dta: year is not a whole number: 2000.5"),
        ("JPN,MMXX,1.0,Market", "t.dta: year is not a whole number: MMXX"),
        ("JPN,2000,1.0e,Market", "t.dta: rgdpe is not a number: 1.0e"),
        ("JPN,2000,inf,Market", "t.dta: rgdpe is not a number: inf"),
        ("JPN,2000,nan,Market", "t.dta: rgdpe is not a number: nan"),
    ],
)
def test_a_value_that_does_not_fit_stops_the_run(tmp_path, line, message):
    with pytest.raises(duckdb.Error, match=message):
        _rel(tmp_path, HEADER, line).fetchall()


def test_staged_text():
    v = dta.Variable("rgdpe", "float", 4)
    assert m.stage_value(14200.900390625, v, {}) == "14200.900390625"
    assert m.stage_value(None, v, {}) == ""
    assert m.stage_value(2000.0, dta.Variable("year", "float", 4), {}) == "2000.0"
    assert m.stage_value(2000, dta.Variable("year", "int", 2), {}) == "2000"
    assert m.stage_value("", dta.Variable("country", "str", 9), {}) == ""
    lab = dta.Variable("i_xr", "byte", 1, value_label="x")
    assert m.stage_value(1, lab, LABELS) == "Estimated"
    with pytest.raises(m.ExportError, match="i_xr has the code 7, which has no label"):
        m.stage_value(7, lab, LABELS)


def test_columns_that_clash_without_case_stop_the_run():
    with pytest.raises(m.ExportError, match="Ic_Struc and ic_struc"):
        m.check_names("t.dta", ["countrycode", "Ic_Struc", "ic_struc"])


def test_a_label_on_a_column_the_rule_does_not_expect_stops_the_run():
    d = dta.parse(dta115([("countrycode", 3, None), ("rgdpe", 251, "x")], [("JPN", 1)], LABELS))
    with pytest.raises(m.ExportError, match="rgdpe has value labels"):
        m.check_labels("t.dta", d)


def test_a_labelled_name_without_labels_stops_the_run():
    d = dta.parse(dta115([("countrycode", 3, None), ("i_xr", 251, None)], [("JPN", 1)]))
    with pytest.raises(m.ExportError, match="i_xr has no value labels"):
        m.check_labels("t.dta", d)
