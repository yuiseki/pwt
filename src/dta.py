"""A small reader for Stata .dta files, formats 114, 115, 117 and 118, standard library only.

PWT ships its tables as Stata files in two layouts: the binary layout of
Stata 10 to 12 (format 114 and 115; PWT 8.0 and the national accounts
vintages) and the tagged layout of Stata 13 and 14 (format 117 and 118;
everything from 8.1 on). Only what PWT uses is read: fixed-width strings,
the five numeric types, missing values and value labels. A strL column, a
format this reader does not know, or a file that does not end where its
header says it should, raises DtaError instead of returning a guess.

Values come back as Python values: str, int, float, or None for a missing
value (Stata's . and .a to .z alike). A 4-byte float is widened to a double
exactly, as Stata itself does and as PWT's own xlsx files write it (14200.9
stored as a float is 14200.900390625).

Formats 114 to 117 do not say how their strings are encoded; Stata wrote
them in the encoding of the machine it ran on. They are decoded as ASCII
unless the caller names an encoding, so a byte above 127 stops the read
instead of turning into a wrong letter. Format 118 is UTF-8.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path


class DtaError(ValueError):
    pass


# numeric type codes: (old layout, new layout) -> (struct code, size, kind)
_OLD_NUMERIC = {251: ("b", 1, "byte"), 252: ("h", 2, "int"), 253: ("l", 4, "long"),
                254: ("f", 4, "float"), 255: ("d", 8, "double")}  # fmt: skip
_NEW_NUMERIC = {65530: ("b", 1, "byte"), 65529: ("h", 2, "int"), 65528: ("l", 4, "long"),
                65527: ("f", 4, "float"), 65526: ("d", 8, "double")}  # fmt: skip
# the largest non-missing value of each integer type; above it is . or .a to .z
_INT_MAX = {"byte": 100, "int": 32740, "long": 2147483620}
_FLOAT_MISSING = 2.0**127  # 0x7f000000
_DOUBLE_MISSING = 2.0**1023  # 0x7fe0000000000000


@dataclass
class Variable:
    name: str
    kind: str  # "str", "byte", "int", "long", "float", "double"
    width: int  # bytes per value
    label: str = ""
    format: str = ""
    value_label: str = ""  # the name of the value label set, "" for none


@dataclass
class Dta:
    format: int
    nobs: int
    variables: list[Variable]
    rows: list[tuple]
    value_labels: dict[str, dict[int, str]] = field(default_factory=dict)
    data_label: str = ""

    @property
    def names(self) -> list[str]:
        return [v.name for v in self.variables]


def _cstr(b: bytes, encoding: str) -> str:
    return b.split(b"\0", 1)[0].decode(encoding)


def _decoder(variables: list[Variable], order: str, encoding: str):
    parts, kinds = [], []
    for v in variables:
        if v.kind == "str":
            parts.append(f"{v.width}s")
        else:
            parts.append(
                {"byte": "b", "int": "h", "long": "l", "float": "f", "double": "d"}[v.kind]
            )
        kinds.append(v.kind)
    st = struct.Struct(order + "".join(parts))

    def convert(raw: tuple) -> tuple:
        out = []
        for k, x in zip(kinds, raw, strict=True):
            if k == "str":
                out.append(_cstr(x, encoding))
            elif k in _INT_MAX:
                out.append(None if x > _INT_MAX[k] else x)
            elif k == "float":
                out.append(None if x >= _FLOAT_MISSING else x)
            else:
                out.append(None if x >= _DOUBLE_MISSING else x)
        return tuple(out)

    return st, convert


def _value_label_table(b: bytes, order: str, encoding: str) -> dict[int, str]:
    n, txtlen = struct.unpack_from(order + "ll", b, 0)
    offs = struct.unpack_from(order + f"{n}l", b, 8)
    vals = struct.unpack_from(order + f"{n}l", b, 8 + 4 * n)
    txt = b[8 + 8 * n : 8 + 8 * n + txtlen]
    if len(txt) != txtlen:
        raise DtaError("value label table is cut short")
    return {v: _cstr(txt[o:], encoding) for v, o in zip(vals, offs, strict=True)}


def _read_old(b: bytes, encoding: str) -> Dta:
    fmt = b[0]
    if fmt not in (114, 115):
        raise DtaError(f"dta format {fmt} is not read here")
    order = {1: ">", 2: "<"}.get(b[1])
    if order is None:
        raise DtaError(f"unknown byte order {b[1]}")
    enc = encoding
    nvar, nobs = struct.unpack_from(order + "Hl", b, 4)
    data_label = _cstr(b[10:91], enc)
    pos = 10 + 81 + 18
    types = list(b[pos : pos + nvar])
    pos += nvar
    names = [_cstr(b[pos + 33 * i : pos + 33 * (i + 1)], enc) for i in range(nvar)]
    pos += 33 * nvar + 2 * (nvar + 1)
    fmts = [_cstr(b[pos + 49 * i : pos + 49 * (i + 1)], enc) for i in range(nvar)]
    pos += 49 * nvar
    lbls = [_cstr(b[pos + 33 * i : pos + 33 * (i + 1)], enc) for i in range(nvar)]
    pos += 33 * nvar
    vlabs = [_cstr(b[pos + 81 * i : pos + 81 * (i + 1)], enc) for i in range(nvar)]
    pos += 81 * nvar
    while True:  # expansion fields
        t = b[pos]
        (n,) = struct.unpack_from(order + "l", b, pos + 1)
        pos += 5 + n
        if t == 0 and n == 0:
            break
    variables = []
    for i, t in enumerate(types):
        if 1 <= t <= 244:
            kind, width = "str", t
        elif t in _OLD_NUMERIC:
            kind, width = _OLD_NUMERIC[t][2], _OLD_NUMERIC[t][1]
        else:
            raise DtaError(f"variable {names[i]} has unknown type {t}")
        variables.append(Variable(names[i], kind, width, vlabs[i], fmts[i], lbls[i]))
    st, convert = _decoder(variables, order, enc)
    end = pos + st.size * nobs
    if end > len(b):
        raise DtaError(f"{nobs} rows do not fit in the file")
    rows = [convert(r) for r in st.iter_unpack(b[pos:end])]
    labels: dict[str, dict[int, str]] = {}
    pos = end
    while pos < len(b):
        (n,) = struct.unpack_from(order + "l", b, pos)
        name = _cstr(b[pos + 4 : pos + 37], enc)
        labels[name] = _value_label_table(b[pos + 40 : pos + 40 + n], order, enc)
        pos += 40 + n
    if pos != len(b):
        raise DtaError("value labels run past the end of the file")
    return Dta(fmt, nobs, variables, rows, labels, data_label)


def _tag(b: bytes, name: str, pos: int) -> int:
    t = f"<{name}>".encode()
    if b[pos : pos + len(t)] != t:
        raise DtaError(f"expected {t!r} at byte {pos}")
    return pos + len(t)


def _read_new(b: bytes, encoding: str) -> Dta:
    pos = _tag(b, "stata_dta", 0)
    pos = _tag(b, "header", pos)
    pos = _tag(b, "release", pos)
    fmt = int(b[pos : pos + 3])
    if fmt not in (117, 118):
        raise DtaError(f"dta format {fmt} is not read here")
    pos = _tag(b, "/release", pos + 3)
    pos = _tag(b, "byteorder", pos)
    order = {b"LSF": "<", b"MSF": ">"}[b[pos : pos + 3]]
    pos = _tag(b, "/byteorder", pos + 3)
    pos = _tag(b, "K", pos)
    (nvar,) = struct.unpack_from(order + "H", b, pos)
    pos = _tag(b, "/K", pos + 2)
    pos = _tag(b, "N", pos)
    if fmt == 117:
        (nobs,) = struct.unpack_from(order + "L", b, pos)
        pos = _tag(b, "/N", pos + 4)
    else:
        (nobs,) = struct.unpack_from(order + "Q", b, pos)
        pos = _tag(b, "/N", pos + 8)
    enc = encoding if fmt == 117 else "utf-8"
    pos = _tag(b, "label", pos)
    if fmt == 117:
        n = b[pos]
        pos += 1
    else:
        (n,) = struct.unpack_from(order + "H", b, pos)
        pos += 2
    data_label = b[pos : pos + n].decode(enc)
    pos = _tag(b, "/label", pos + n)
    pos = _tag(b, "timestamp", pos)
    pos += 1 + b[pos]
    pos = _tag(b, "/timestamp", pos)
    pos = _tag(b, "/header", pos)
    pos = _tag(b, "map", pos)
    offsets = struct.unpack_from(order + "14Q", b, pos)
    if offsets[13] != len(b):
        raise DtaError(f"the map says the file has {offsets[13]} bytes, it has {len(b)}")

    nlen = 33 if fmt == 117 else 129
    flen = 49 if fmt == 117 else 57
    llen = 81 if fmt == 117 else 321
    pos = _tag(b, "variable_types", offsets[2])
    types = struct.unpack_from(order + f"{nvar}H", b, pos)
    pos = _tag(b, "varnames", offsets[3])
    names = [_cstr(b[pos + nlen * i : pos + nlen * (i + 1)], enc) for i in range(nvar)]
    pos = _tag(b, "formats", offsets[5])
    fmts = [_cstr(b[pos + flen * i : pos + flen * (i + 1)], enc) for i in range(nvar)]
    pos = _tag(b, "value_label_names", offsets[6])
    lbls = [_cstr(b[pos + nlen * i : pos + nlen * (i + 1)], enc) for i in range(nvar)]
    pos = _tag(b, "variable_labels", offsets[7])
    vlabs = [_cstr(b[pos + llen * i : pos + llen * (i + 1)], enc) for i in range(nvar)]

    variables = []
    for i, t in enumerate(types):
        if 1 <= t <= 2045:
            kind, width = "str", t
        elif t in _NEW_NUMERIC:
            kind, width = _NEW_NUMERIC[t][2], _NEW_NUMERIC[t][1]
        elif t == 32768:
            raise DtaError(f"variable {names[i]} is a strL, which is not read here")
        else:
            raise DtaError(f"variable {names[i]} has unknown type {t}")
        variables.append(Variable(names[i], kind, width, vlabs[i], fmts[i], lbls[i]))

    st, convert = _decoder(variables, order, enc)
    pos = _tag(b, "data", offsets[9])
    end = pos + st.size * nobs
    if b[end : end + 7] != b"</data>":
        raise DtaError(f"{nobs} rows of {st.size} bytes do not end at </data>")
    rows = [convert(r) for r in st.iter_unpack(b[pos:end])]

    labels: dict[str, dict[int, str]] = {}
    pos = _tag(b, "value_labels", offsets[11])
    while b[pos : pos + 5] == b"<lbl>":
        pos += 5
        (n,) = struct.unpack_from(order + "l", b, pos)
        name = _cstr(b[pos + 4 : pos + 4 + nlen], enc)
        start = pos + 4 + nlen + 3
        labels[name] = _value_label_table(b[start : start + n], order, enc)
        pos = _tag(b, "/lbl", start + n)
    _tag(b, "/value_labels", pos)
    return Dta(fmt, nobs, variables, rows, labels, data_label)


def parse(b: bytes, encoding: str = "ascii") -> Dta:
    """encoding applies to formats 114 to 117 only; 118 is UTF-8."""
    try:
        if b[:11] == b"<stata_dta>":
            return _read_new(b, encoding)
        return _read_old(b, encoding)
    except UnicodeDecodeError as e:
        raise DtaError(
            f"a string is not {encoding}: {e.object[max(0, e.start - 20) : e.end + 20]!r}"
        ) from e
    except (struct.error, IndexError) as e:
        raise DtaError(f"the file is cut short: {e}") from e


def read(path: str | Path, encoding: str = "ascii") -> Dta:
    return parse(Path(path).read_bytes(), encoding)
