# pwt

A reproducible collection of the Penn World Table (PWT), releases 8.0 to 11.0,
kept as published by the Groningen Growth and Development Centre (GGDC),
University of Groningen.

PWT is a database of relative levels of income, output, inputs and
productivity by country and year (PWT 11.0: 185 countries, 1950 to 2023):
real GDP at chained PPPs, population, employment, hours worked, human
capital, capital stock, TFP, exchange rates, price levels and expenditure
shares, plus supplementary tables (national accounts, capital, labour and
trade detail, expenditure share correlations, program packages).

## Source

- Current release: <https://www.rug.nl/ggdc/productivity/pwt/>
- Earlier releases: <https://www.rug.nl/ggdc/productivity/pwt/earlier-releases>
- 11.0 and 10.01 are hosted on DataverseNL
  (<https://doi.org/10.34894/FABVLR>, <https://doi.org/10.34894/QT5BCC>); their
  file lists and SHA-1 checksums come from the public Dataverse API.
  10.0 and earlier are files under `https://www.rug.nl/ggdc/docs/`, as linked
  from each release page.

Taken: the xlsx, dta and zip data files and the documentation PDFs linked from
each release page. Not taken: the ICP benchmark workbooks (`icp19xx.xls`), the
journal article "The Next Generation of the Penn World Table" (a paper, not
release documentation), and releases 7.1 and earlier, whose pages state no
licence. Files linked from more than one release page (for example the national
accounts vintages `na_data_v2009.zip`) are kept in each release that links them.

In 11.0, `pwt110.xlsx` was replaced on DataverseNL three days after release
(dataset version 1.0 to 2.0). The latest dataset version is taken, and the
manifest records the dataset version, the datafile id and file version, and the
earlier datafile it replaced.

## Licence

PWT 8.0 and later are licensed by Robert C. Feenstra, Robert Inklaar and
Marcel P. Timmer under the Creative Commons Attribution 4.0 International
License (<https://creativecommons.org/licenses/by/4.0/>), as stated on each
release page and in the DataverseNL metadata. When using the data, cite:

> Feenstra, Robert C., Robert Inklaar and Marcel P. Timmer (2015), "The Next
> Generation of the Penn World Table", American Economic Review, 105(10),
> 3150-3182, available for download at www.ggdc.net/pwt

## Run

```sh
uv run python scripts/01_download.py        # fetch into data/raw/<release>/
uv run python scripts/03_export_parquet.py  # Stata tables -> data/parquet/<release>/<table>.parquet
uv run python scripts/02_verify.py          # re-hash every raw file, check every Parquet
uv run python -m pytest                     # tests
uv run python src/publish.py                # dry run: list what would go to the Hub
uv run python src/publish.py --push         # upload to huggingface.co/datasets/yuiseki/pwt
```

The export reads each table from its Stata file (inside the zip for 8.0
and 8.1) with `src/dta.py`, a standard-library reader of Stata formats 114
to 118, and writes one Parquet file per table, as listed in
`scripts/TABLES.json`. The main table of a release becomes the subset
`'<release>'`, every other table `'<release>.<table>'`. Column types come
from column names (`column_type` in the export script); a value that does
not fit its type stops the export. `02_verify.py` then compares every value
with the Stata file, row counts and values with the xlsx where PWT ships
one, and the types with the rule.

`publish.py` refuses to upload if the card (`data/README.md`) does not
declare every Parquet file as a subset, or if a raw file's sha256 differs
from its manifest. It uploads `data/README.md`, `data/LICENSE`,
`data/provenance.yaml`, the Parquet and every raw file unchanged.

The download is idempotent: a file whose local copy still matches its manifest
entry (and, on DataverseNL, the published SHA-1) is not fetched again.
Requests are sequential and at least 1.2 seconds apart.

## Layout

```
scripts/01_download.py        discovery and download
scripts/03_export_parquet.py  Stata tables to typed Parquet
scripts/TABLES.json           which file of which release is which table
scripts/02_verify.py          checks against the manifests, the Stata files and the xlsx
src/dta.py                    Stata .dta reader (formats 114, 115, 117, 118)
src/publish.py                upload to the Hugging Face Hub (dry run by default)
tests/                        unit tests, fixtures trimmed from real responses
data/raw/<release>/           files as served, e.g. data/raw/11.0/pwt110.xlsx
data/raw/<release>/MANIFEST.json
data/parquet/<release>/       one Parquet file per table, e.g. data/parquet/11.0/pwt.parquet
data/README.md                the dataset card; data/LICENSE; data/provenance.yaml
```

Each `MANIFEST.json` has a `release` object (release page, DOI, licence link,
the release date as the page states it, and for DataverseNL the dataset version
and release time) and a `files` object keyed by file name with the URL, bytes,
sha256, sha1, Last-Modified, fetch time (UTC) and, for DataverseNL files, the
datafile id, file version, published SHA-1 and any earlier datafile of the same
name.

`data/raw/` and `data/parquet/` are not committed; the card, LICENSE and
provenance.yaml under `data/` are.
