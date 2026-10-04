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
uv run python scripts/01_download.py   # fetch into data/raw/<release>/
uv run python scripts/02_verify.py     # re-hash and test every file
uv run python -m pytest                # parsing tests
```

The download is idempotent: a file whose local copy still matches its manifest
entry (and, on DataverseNL, the published SHA-1) is not fetched again.
Requests are sequential and at least 1.2 seconds apart.

## Layout

```
scripts/01_download.py   discovery and download
scripts/02_verify.py     checks against the manifests
tests/                   unit tests, fixtures trimmed from real responses
data/raw/<release>/      files as served, e.g. data/raw/11.0/pwt110.xlsx
data/raw/<release>/MANIFEST.json
```

Each `MANIFEST.json` has a `release` object (release page, DOI, licence link,
the release date as the page states it, and for DataverseNL the dataset version
and release time) and a `files` object keyed by file name with the URL, bytes,
sha256, sha1, Last-Modified, fetch time (UTC) and, for DataverseNL files, the
datafile id, file version, published SHA-1 and any earlier datafile of the same
name.

`data/raw/` is not committed.
