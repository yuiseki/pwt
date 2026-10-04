import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / "tests" / "fixtures"


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dl = load("download", "01_download.py")


def test_release_pages_from_listing():
    pages = dl.release_pages((FIX / "earlier_releases.html").read_text())
    assert pages[0] == "https://www.rug.nl/ggdc/productivity/pwt/pwt-releases/pwt1001"
    assert "https://www.rug.nl/ggdc/productivity/pwt/pwt-releases/pwt8.0" in pages
    assert "https://www.rug.nl/ggdc/productivity/pwt/pwt-releases/pwt-5.6" in pages
    assert len(pages) == len(set(pages)) == 12


def test_version_from_title():
    assert (
        dl.version_from_title("<title>PWT 10.01 | PWT earlier releases | GGDC</title>") == "10.01"
    )
    assert dl.version_from_title("<title>PWT 11.0 | Penn World Table</title>") == "11.0"
    assert dl.version_from_title("<title>Earlier Releases | Penn World Table</title>") is None


def test_parse_rug_release_page():
    page = dl.parse_release_page((FIX / "release_pwt80.html").read_text())
    assert page["version"] == "8.0"
    assert page["licence"] == "http://creativecommons.org/licenses/by/4.0/"
    assert page["doi"] == "10.15141/S5159X"
    assert page["release_statement"] == "released on July 2, 2013"
    docs = page["docs"]
    assert docs[0] == "https://www.rug.nl/ggdc/docs/pwt80.xlsx"
    assert "https://www.rug.nl/ggdc/docs/pwt80.zip" in docs
    assert "https://www.rug.nl/ggdc/docs/pwt_80_user_guide.pdf" in docs
    assert "https://www.rug.nl/ggdc/docs/na_data_v2009.zip" in docs
    # the journal article, the ICP .xls workbooks and pages outside /ggdc/docs/ are not taken
    assert not any("next_generation" in u for u in docs)
    assert not any(u.endswith(".xls") for u in docs)
    assert len(docs) == len(set(docs))


def test_parse_dataverse_release_page():
    page = dl.parse_release_page((FIX / "release_pwt110.html").read_text())
    assert page["version"] == "11.0"
    assert page["doi"] == "10.34894/FABVLR"
    assert page["release_statement"] == "Published on October 7, 2025"
    assert dl.is_dataverse(page["doi"])
    assert not dl.is_dataverse("10.15141/S5159X")


def test_page_without_licence():
    html = "<title>PWT 7.1 | PWT earlier releases</title><a href='/ggdc/docs/pwt71.zip'>x</a>"
    page = dl.parse_release_page(html)
    assert page["version"] == "7.1"
    assert page["licence"] is None


def test_wanted_doc():
    assert dl.wanted("pwt100-na-data.dta")
    assert dl.wanted("pwt80.XLSX")
    assert dl.wanted("pwt100-whatsnew.pdf")
    assert not dl.wanted("icp1970.xls")
    assert not dl.wanted("the_next_generation_of_the_penn_world_table.pdf")
    assert not dl.wanted("readme.txt")


def test_dataverse_latest_files_and_replacement():
    versions = json.loads((FIX / "dataverse_versions_pwt110.json").read_text())["data"]
    info = dl.dataverse_files(versions)
    assert info["dataset_version"] == "2.0"
    assert info["release_time"] == "2025-10-10T11:49:22Z"
    assert info["licence"] == "http://creativecommons.org/licenses/by/4.0"
    files = {f["filename"]: f for f in info["files"]}
    assert set(files) == {"pwt110.xlsx", "pwt110.dta", "pwt110_user_guide_to_data_files.pdf"}
    x = files["pwt110.xlsx"]
    assert x["url"] == "https://dataverse.nl/api/access/datafile/554105"
    assert x["datafile_id"] == 554105
    assert x["file_version"] == 1
    assert x["bytes"] == 5839841
    assert x["sha1"] == "f6045409aae2b7e468ba7e97952cbd7cd530a9eb"
    assert x["creation_date"] == "2025-10-10"
    assert x["earlier_datafiles"] == [
        {
            "dataset_version": "1.0",
            "datafile_id": 554027,
            "bytes": 5841216,
            "sha1": "cd05909f3a7688c94cfd3a9324611ad29d757d3b",
        }
    ]
    assert files["pwt110.dta"]["earlier_datafiles"] == []


def test_dataverse_skips_xls():
    versions = json.loads((FIX / "dataverse_versions_pwt1001_xls.json").read_text())["data"]
    info = dl.dataverse_files(versions)
    assert info["dataset_version"] == "1.1"
    assert info["files"] == []
    assert info["skipped"] == ["icp1970.xls"]


vf = load("verify", "02_verify.py")


def test_verify_detects_bad_hash_and_zip(tmp_path):
    import zipfile

    good = tmp_path / "a.zip"
    with zipfile.ZipFile(good, "w") as z:
        z.writestr("x.csv", "a,b\n1,2\n")
    sha256, sha1 = vf.hashes(good)
    entry = {"bytes": good.stat().st_size, "sha256": sha256, "dataverse": {"sha1": sha1}}
    assert vf.check(good, entry) == []
    assert vf.check(good, {**entry, "sha256": "0" * 64}) == ["sha256 differs"]
    bad = tmp_path / "b.xlsx"
    bad.write_bytes(b"not a zip")
    s, _ = vf.hashes(bad)
    assert vf.check(bad, {"bytes": 9, "sha256": s})[0].startswith("bad zip")
    assert vf.check(tmp_path / "missing.dta", entry) == ["missing"]
