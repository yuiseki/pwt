---
license: cc-by-4.0
language:
- en
pretty_name: Penn World Table
task_categories:
- tabular-regression
- time-series-forecasting
tags:
- economics
- macroeconomics
- national-accounts
- productivity
- purchasing-power-parity
- penn-world-table
- ggdc
size_categories:
- 100K<n<1M
configs:
- config_name: '11.0'
  data_files: parquet/11.0/pwt.parquet
  default: true
- config_name: '11.0.na_data'
  data_files: parquet/11.0/na_data.parquet
- config_name: '11.0.capital_detail'
  data_files: parquet/11.0/capital_detail.parquet
- config_name: '11.0.labor_detail'
  data_files: parquet/11.0/labor_detail.parquet
- config_name: '11.0.trade_detail'
  data_files: parquet/11.0/trade_detail.parquet
- config_name: '11.0.esh_bilateral_cor'
  data_files: parquet/11.0/esh_bilateral_cor.parquet
- config_name: '10.01'
  data_files: parquet/10.01/pwt.parquet
- config_name: '10.01.na_data'
  data_files: parquet/10.01/na_data.parquet
- config_name: '10.01.capital_detail'
  data_files: parquet/10.01/capital_detail.parquet
- config_name: '10.01.labor_detail'
  data_files: parquet/10.01/labor_detail.parquet
- config_name: '10.01.trade_detail'
  data_files: parquet/10.01/trade_detail.parquet
- config_name: '10.01.esh_bilateral_cor'
  data_files: parquet/10.01/esh_bilateral_cor.parquet
- config_name: '10.0'
  data_files: parquet/10.0/pwt.parquet
- config_name: '10.0.na_data'
  data_files: parquet/10.0/na_data.parquet
- config_name: '10.0.capital_detail'
  data_files: parquet/10.0/capital_detail.parquet
- config_name: '10.0.labor_detail'
  data_files: parquet/10.0/labor_detail.parquet
- config_name: '10.0.trade_detail'
  data_files: parquet/10.0/trade_detail.parquet
- config_name: '10.0.esh_bilateral_cor'
  data_files: parquet/10.0/esh_bilateral_cor.parquet
- config_name: '9.1'
  data_files: parquet/9.1/pwt.parquet
- config_name: '9.1.na_data'
  data_files: parquet/9.1/na_data.parquet
- config_name: '9.1.capital_detail'
  data_files: parquet/9.1/capital_detail.parquet
- config_name: '9.1.labor_detail'
  data_files: parquet/9.1/labor_detail.parquet
- config_name: '9.1.trade_detail'
  data_files: parquet/9.1/trade_detail.parquet
- config_name: '9.1.esh_bilateral_cor'
  data_files: parquet/9.1/esh_bilateral_cor.parquet
- config_name: '9.0'
  data_files: parquet/9.0/pwt.parquet
- config_name: '9.0.na_data'
  data_files: parquet/9.0/na_data.parquet
- config_name: '9.0.capital_detail'
  data_files: parquet/9.0/capital_detail.parquet
- config_name: '9.0.labor_detail'
  data_files: parquet/9.0/labor_detail.parquet
- config_name: '9.0.trade_detail'
  data_files: parquet/9.0/trade_detail.parquet
- config_name: '9.0.esh_bilateral_cor'
  data_files: parquet/9.0/esh_bilateral_cor.parquet
- config_name: '8.1'
  data_files: parquet/8.1/pwt.parquet
- config_name: '8.1.na_data'
  data_files: parquet/8.1/na_data.parquet
- config_name: '8.1.trade_detail'
  data_files: parquet/8.1/trade_detail.parquet
- config_name: '8.1.esh_bilateral_cor'
  data_files: parquet/8.1/esh_bilateral_cor.parquet
- config_name: '8.0'
  data_files: parquet/8.0/pwt.parquet
- config_name: '8.0.na_data'
  data_files: parquet/8.0/na_data.parquet
- config_name: '8.0.trade_detail'
  data_files: parquet/8.0/trade_detail.parquet
- config_name: '8.0.esh_bilateral_cor'
  data_files: parquet/8.0/esh_bilateral_cor.parquet
- config_name: '8.0.depreciation_rates'
  data_files: parquet/8.0/depreciation_rates.parquet
- config_name: '8.0.na_data_v2009'
  data_files: parquet/8.0/na_data_v2009.parquet
- config_name: '8.0.na_data_v2010'
  data_files: parquet/8.0/na_data_v2010.parquet
---

# pwt

The Penn World Table (PWT), releases 8.0 to 11.0, as the Groningen Growth
and Development Centre (GGDC) of the University of Groningen published them.
PWT gives relative levels of income, output, inputs and productivity by
country and year: real GDP at chained PPPs, population, employment, hours
worked, human capital, capital stock, TFP, exchange rates, price levels and
expenditure shares. PWT 11.0 covers 185 countries from 1950 to 2023.

Each release is kept whole. Its main table is the subset named by the
release (`'11.0'`), and its other tables are subsets named
`'<release>.<table>'` (`'11.0.na_data'`). Beside the Parquet are all the
files the release pages link, byte for byte, under `raw/<release>/`.

CC BY 4.0. Cite Feenstra, Inklaar and Timmer (2015) whenever the data are
used (see Licence).

## Releases

PWT revises the whole history in every release, and the base year of its
prices moves, so a value from one release does not continue a series from
another: Japan's 2019 `rgdpe` is 5,028,348 (million 2017 US$) in 10.0 and
5,515,624 (million 2021 US$) in 11.0. State the release you use.

| release | released | DOI | main table rows | countries | years | price base |
|---|---|---|---:|---:|---|---|
| `11.0` | October 7, 2025 | [10.34894/FABVLR](https://doi.org/10.34894/FABVLR) | 13,690 | 185 | 1950 to 2023 | 2021 US$ |
| `10.01` | January 23, 2023 | [10.34894/QT5BCC](https://doi.org/10.34894/QT5BCC) | 12,810 | 183 | 1950 to 2019 | 2017 US$ |
| `10.0` | not stated on its page | [10.15141/S5Q94M](https://doi.org/10.15141/S5Q94M) | 12,810 | 183 | 1950 to 2019 | 2017 US$ |
| `9.1` | not stated on its page | [10.15141/S50T0R](https://doi.org/10.15141/S50T0R) | 12,376 | 182 | 1950 to 2017 | 2011 US$ |
| `9.0` | not stated on its page | [10.15141/S5J01T](https://doi.org/10.15141/S5J01T) | 11,830 | 182 | 1950 to 2014 | 2011 US$ |
| `8.1` | April 13, 2015 | [10.15141/S5NP4S](https://doi.org/10.15141/S5NP4S) | 10,354 | 167 | 1950 to 2011 | 2005 US$ |
| `8.0` | July 2, 2013 | [10.15141/S5159X](https://doi.org/10.15141/S5159X) | 10,354 | 167 | 1950 to 2011 | 2005 US$ |

The release dates are those the release pages state. The price base is the
one the main table's variable labels name (for `rgdpe`, "in mil. 2021US$"
in 11.0). Releases 7.1 and earlier are not here: their pages state no
licence.

The main table has one row for every country and year in its range, with or
without values: in 11.0, 11,201 of the 13,690 rows have `rgdpe`.

## Subsets

| subset | rows | columns | years | countries | made from |
|---|---:|---:|---|---:|---|
| `11.0` | 13,690 | 51 | 1950 to 2023 | 185 | `raw/11.0/pwt110.dta` |
| `11.0.na_data` | 13,114 | 21 | 1950 to 2025 | 217 | `raw/11.0/pwt110_na_data.dta` |
| `11.0.capital_detail` | 13,320 | 34 | 1950 to 2023 | 180 | `raw/11.0/pwt110_capital_detail.dta` |
| `11.0.labor_detail` | 13,114 | 24 | 1950 to 2025 | 217 | `raw/11.0/pwt110_labor_detail.dta` |
| `11.0.trade_detail` | 13,690 | 30 | 1950 to 2023 | 185 | `raw/11.0/pwt110_trade_detail.dta` |
| `11.0.esh_bilateral_cor` | 393,970 | 4 | 1970 to 2021 | 187 | `raw/11.0/pwt110_sh_bilateral_cor_data.dta` |
| `10.01` | 12,810 | 52 | 1950 to 2019 | 183 | `raw/10.01/pwt1001.dta` |
| `10.01.na_data` | 12,588 | 21 | 1950 to 2019 | 217 | `raw/10.01/pwt1001_na_data.dta` |
| `10.01.capital_detail` | 12,600 | 34 | 1950 to 2019 | 180 | `raw/10.01/pwt1001_capital_detail.dta` |
| `10.01.labor_detail` | 12,588 | 20 | 1950 to 2019 | 217 | `raw/10.01/pwt1001-labor-detail.dta` |
| `10.01.trade_detail` | 12,810 | 30 | 1950 to 2019 | 183 | `raw/10.01/pwt1001-trade-detail.dta` |
| `10.01.esh_bilateral_cor` | 256,410 | 4 | 1970 to 2017 | 184 | `raw/10.01/pwt1001-esh_bilateral_cor_data.dta` |
| `10.0` | 12,810 | 52 | 1950 to 2019 | 183 | `raw/10.0/pwt100.dta` |
| `10.0.na_data` | 12,588 | 21 | 1950 to 2019 | 217 | `raw/10.0/pwt100-na-data.dta` |
| `10.0.capital_detail` | 12,600 | 34 | 1950 to 2019 | 180 | `raw/10.0/pwt100-capital-detail.dta` |
| `10.0.labor_detail` | 12,588 | 20 | 1950 to 2019 | 217 | `raw/10.0/pwt100-labor-detail.dta` |
| `10.0.trade_detail` | 12,810 | 30 | 1950 to 2019 | 183 | `raw/10.0/pwt100-trade-detail.dta` |
| `10.0.esh_bilateral_cor` | 256,410 | 4 | 1970 to 2017 | 184 | `raw/10.0/pwt100-esh-bilateral-cor-data.dta` |
| `9.1` | 12,376 | 52 | 1950 to 2017 | 182 | `raw/9.1/pwt91.dta` |
| `9.1.na_data` | 12,088 | 21 | 1950 to 2017 | 216 | `raw/9.1/pwt91_na_data.dta` |
| `9.1.capital_detail` | 12,240 | 34 | 1950 to 2017 | 180 | `raw/9.1/pwt91_capital_detail.dta` |
| `9.1.labor_detail` | 12,376 | 20 | 1950 to 2017 | 182 | `raw/9.1/pwt91_labor_detail.dta` |
| `9.1.trade_detail` | 12,376 | 30 | 1950 to 2017 | 182 | `raw/9.1/pwt91_trade_detail.dta` |
| `9.1.esh_bilateral_cor` | 76,170 | 4 | 1970 to 2011 | 186 | `raw/9.1/esh_bilateral_cor_data.dta` |
| `9.0` | 11,830 | 47 | 1950 to 2014 | 182 | `raw/9.0/pwt90.dta` |
| `9.0.na_data` | 11,386 | 21 | 1950 to 2014 | 212 | `raw/9.0/pwt90-na-data.dta` |
| `9.0.capital_detail` | 11,830 | 22 | 1950 to 2014 | 182 | `raw/9.0/pwt90_capital_detail.dta` |
| `9.0.labor_detail` | 11,830 | 20 | 1950 to 2014 | 182 | `raw/9.0/pwt90_labor_detail.dta` |
| `9.0.trade_detail` | 11,830 | 30 | 1950 to 2014 | 182 | `raw/9.0/pwt90_trade_detail.dta` |
| `9.0.esh_bilateral_cor` | 76,170 | 4 | 1970 to 2011 | 186 | `raw/9.0/esh_bilateral_cor_data.dta` |
| `8.1` | 10,354 | 47 | 1950 to 2011 | 167 | `pwt81.dta` in `raw/8.1/pwt81.zip` |
| `8.1.na_data` | 10,624 | 19 | 1950 to 2011 | 209 | `na_data.dta` in `raw/8.1/na_data8.1.zip` |
| `8.1.trade_detail` | 10,354 | 30 | 1950 to 2011 | 167 | `pwt81_trade_detail.dta` in `raw/8.1/pwt81_trade_detail.zip` |
| `8.1.esh_bilateral_cor` | 43,770 | 4 | 1970 to 2005 | 168 | `esh_bilateral_cor_data.dta` in `raw/8.1/esh_bilateral_cor_data.zip` |
| `8.0` | 10,354 | 39 | 1950 to 2011 | 167 | `pwt80.dta` in `raw/8.0/pwt80.zip` |
| `8.0.na_data` | 10,624 | 19 | 1950 to 2011 | 209 | `na_data.dta` in `raw/8.0/na_data-pwt8.0.zip` |
| `8.0.trade_detail` | 10,354 | 30 | 1950 to 2011 | 167 | `pwt80_trade_detail.dta` in `raw/8.0/pwt80_trade_detail.zip` |
| `8.0.esh_bilateral_cor` | 43,770 | 4 | 1970 to 2005 | 168 | `esh_bilateral_cor_data.dta` in `raw/8.0/esh_bilateral_cor_data.zip` |
| `8.0.depreciation_rates` | 8,059 | 3 | 1951 to 2011 | 167 | `depreciation_rates.dta` in `raw/8.0/depreciation_rates.zip` |
| `8.0.na_data_v2009` | 10,278 | 18 | 1950 to 2009 | 211 | `na_data_v2009.dta` in `raw/8.0/na_data_v2009.zip` |
| `8.0.na_data_v2010` | 10,497 | 18 | 1950 to 2010 | 211 | `na_data_v2010.dta` in `raw/8.0/na_data_v2010.zip` |

Countries are distinct `countrycode` values (`countrycode1` for
`esh_bilateral_cor`). The tables, as the release pages describe them:

- the release subset (`'11.0'`): the main table, the `Data` sheet of
  `pwt110.xlsx` and `pwt110.dta`
- `na_data`: the national accounts PWT starts from, in national currency
- `capital_detail`: investment, capital stock, capital services and
  depreciation by asset (structures, machinery, transport equipment, other)
- `labor_detail`: employment and hours, years of schooling and its source,
  and the labour share under four ways of treating mixed income
- `trade_detail`: price levels and shares of exports and imports by Broad
  Economic Category
- `esh_bilateral_cor`: the correlation of expenditure shares between two
  countries in a benchmark year (11.0 names its file `sh_bilateral_cor_data`)
- `depreciation_rates` (8.0 only): the depreciation rate of the total
  capital stock
- `na_data_v2009`, `na_data_v2010`: the national accounts vintages that the
  8.0 page links as "NA vintages"

Some subsets are the same table, because the release pages link the same
file: `10.0` and `10.01` share `na_data`, `labor_detail`, `trade_detail`
and `esh_bilateral_cor` (their main tables and `capital_detail` differ);
`8.0` and `8.1` share `esh_bilateral_cor`, as do `9.0` and `9.1`.

### Files kept raw only

Every file under `raw/<release>/` is listed in that release's
`MANIFEST.json` with its URL, size, sha256 and Last-Modified. These have no
subset of their own:

- the Excel copies of tables made from Stata (`pwt110.xlsx` and so on); the
  Stata file is the more exact one (see Things to know)
- documentation (`*.pdf`)
- the program packages (`program_package_pwt_110.zip`, `programs8.zip` and
  so on): Stata do files and the input data PWT is computed from
- `pwt80_mat.zip`: PWT 8.0 as a MATLAB file
- national accounts vintages that later pages link again, which are
  already subsets: `na_data_v2011.dta` (9.0 to 10.01) is byte for byte
  `8.0.na_data`; `pwt90-na-data.dta` and `pwt91_na_data.dta` in 10.0 and
  10.01 are `9.0.na_data` and `9.1.na_data`; `na_data_v2009` and
  `na_data_v2010` in 8.1 to 10.01 hold the same Stata file as the 8.0
  subsets

## Columns and types

The Parquet is made from the Stata file of each table, read with a small
reader of the Stata format written for this dataset. The type of a column
comes from its name, never from inference, and is the same in every
release:

| columns | type |
|---|---|
| `countrycode`, `country`, `currency_unit`, `countrycode1`, `countrycode2`, `countryname`, `indicatorname`, `seriescode` | VARCHAR, as in the file |
| `i_cig`, `i_xm`, `i_xr`, `i_outlier`, `i_irr`, `i_emp`, `source`, `i_labsh`, `i_labsh2`, `i_comp_sh`, `i_lab_sh1` to `i_lab_sh4` | VARCHAR, the Stata value label of the code (see below) |
| `year`, `i_mix` | INTEGER |
| every other column of the tables here (the measures) | DOUBLE |

A measure is DOUBLE whether the Stata file stores it as a 4-byte float, a
double or an integer. A 4-byte float is widened exactly, as PWT's own xlsx
writes it: 14200.9 stored as a float is 14200.900390625. Missing values
(Stata's `.` and `.a` to `.z`) and empty strings are NULL. Column names
are those of the Stata file, case included (`Ic_Struc`).

### Main table

Descriptions are shortened from the Legend sheet of `pwt110.xlsx` and the
Stata variable labels of 11.0; the price base differs by release (see
Releases). The last column says which releases have it.

| column | type | description | releases |
|---|---|---|---|
| `countrycode` | VARCHAR | 3-letter ISO country code | all |
| `country` | VARCHAR | Country name | all |
| `currency_unit` | VARCHAR | Currency unit | all |
| `year` | INTEGER | Year | all |
| `rgdpe` | DOUBLE | Expenditure-side real GDP at chained PPPs (in mil. 2021US$) | all |
| `rgdpo` | DOUBLE | Output-side real GDP at chained PPPs (in mil. 2021US$) | all |
| `pop` | DOUBLE | Population (in millions) | all |
| `emp` | DOUBLE | Number of persons engaged (in millions) | all |
| `avh` | DOUBLE | Average annual hours worked by persons engaged | all |
| `hc` | DOUBLE | Human capital index, based on years of schooling and returns to education | all |
| `ccon` | DOUBLE | Real consumption of households and government, at current PPPs | 8.1 to 11.0 |
| `cda` | DOUBLE | Real domestic absorption (real consumption plus investment) at current PPPs | 8.1 to 11.0 |
| `cgdpe` | DOUBLE | Expenditure-side real GDP at current PPPs | all |
| `cgdpo` | DOUBLE | Output-side real GDP at current PPPs | all |
| `cn` | DOUBLE | Capital stock at current PPPs | 9.1 to 11.0 |
| `ck` | DOUBLE | Capital services levels at current PPPs (USA=1) | all |
| `ctfp` | DOUBLE | TFP level at current PPPs (USA=1) | all |
| `cwtfp` | DOUBLE | Welfare-relevant TFP levels at current PPPs (USA=1) | 8.1 to 11.0 |
| `rgdpna` | DOUBLE | Real GDP at constant national prices | all |
| `rconna` | DOUBLE | Real consumption at constant national prices | 8.1 to 11.0 |
| `rdana` | DOUBLE | Real domestic absorption at constant national prices | 8.1 to 11.0 |
| `rnna` | DOUBLE | Capital stock at constant national prices | 9.1 to 11.0 |
| `rkna` | DOUBLE | Capital services at constant national prices | all |
| `rtfpna` | DOUBLE | TFP at constant national prices | all |
| `rwtfpna` | DOUBLE | Welfare-relevant TFP at constant national prices | 8.1 to 11.0 |
| `labsh` | DOUBLE | Share of labour compensation in GDP at current national prices | all |
| `irr` | DOUBLE | Real internal rate of return | 9.1 to 11.0 |
| `delta` | DOUBLE | Average depreciation rate of the capital stock | 8.1 to 11.0 |
| `xr` | DOUBLE | Exchange rate, national currency/USD (market+estimated) | all |
| `pl_con` | DOUBLE | Price level of CCON (PPP/XR) | 8.1 to 11.0 |
| `pl_da` | DOUBLE | Price level of CDA (PPP/XR) | 8.1 to 11.0 |
| `pl_gdpe` | DOUBLE | Price level of CGDPe (PPP/XR) | 8.0 |
| `pl_gdpo` | DOUBLE | Price level of CGDPo (PPP/XR) | all |
| `i_cig` | VARCHAR | Whether relative price data for consumption, investment and government is extrapolated, benchmark or interpolated | all |
| `i_xm` | VARCHAR | The same for exports and imports | all |
| `i_xr` | VARCHAR | Whether the exchange rate is market-based or estimated | all |
| `i_outlier` | VARCHAR | Whether the observation on `pl_gdpe` or `pl_gdpo` is an outlier | all |
| `i_irr` | VARCHAR | Whether `irr` is regular, may be biased by a low capital share, hit the lower bound of 1 percent, or is an outlier | 9.1 to 11.0 |
| `cor_exp` | DOUBLE | Correlation between expenditure shares of the country and the US (benchmark observations only) | all |
| `statcap` | DOUBLE | Statistical capacity indicator (World Bank, developing countries only) | 8.0 to 10.01 |
| `csh_c`, `csh_i`, `csh_g`, `csh_x`, `csh_m`, `csh_r` | DOUBLE | Shares in CGDPo of household consumption, capital formation, government consumption, merchandise exports and imports, and the residual | all |
| `pl_c`, `pl_i`, `pl_g`, `pl_x`, `pl_m`, `pl_k` | DOUBLE | Price levels of household consumption, capital formation, government consumption, exports, imports, capital services | all |
| `pl_n` | DOUBLE | Price level of the capital stock | 9.1 to 11.0 |

Columns by release: 8.0 has 39, 8.1 and 9.0 have 47, 9.1, 10.0 and 10.01
have 52, 11.0 has 51 (it drops `statcap`).

The coded columns hold the label PWT gives each code, as the xlsx shows
them. The labels changed between releases:

| column | labels | releases |
|---|---|---|
| `i_cig`, `i_xm` | Extrapolated, Benchmark, Interpolated | all |
| `i_cig` | also ICP PPP timeseries: benchmark or interpolated, ICP PPP timeseries: extrapolated | 10.0 to 11.0 |
| `i_xr` | Market, Estimated | 8.0 to 9.0 |
| `i_xr` | Market-based, Estimated | 9.1 to 11.0 |
| `i_outlier` | Regular, Outlier | all |
| `i_irr` | Regular, Low capital share, Lower bound, Outlier | 9.1 to 11.0 |

### Other tables

| table | columns | type | releases |
|---|---|---|---|
| `na_data` | `countrycode`; `year`; `v_c`, `v_i`, `v_g`, `v_x`, `v_m`, `v_gdp`, `v_gfcf` (current national prices); `q_c`, `q_i`, `q_g`, `q_x`, `q_m`, `q_gdp`, `q_gfcf` (constant national prices); `pop`, `xr` (market), `xr2` (market+estimated) | VARCHAR; INTEGER; DOUBLE | all |
| `na_data` | `emp`, `avh` | DOUBLE | 9.0 to 11.0 |
| `na_data_v2009`, `na_data_v2010` | as `na_data`, without `xr2`, `emp`, `avh`; `q_*` at constant national 2005 prices | | 8.0 |
| `capital_detail` | `countrycode`; `year`; `Ic_*` investment at current prices, `Ip_*` investment price index, `Kc_*` current-cost capital services, `Kp_*` capital services price index, `Dc_*` capital consumption, each for `Struc`, `Mach`, `TraEq`, `Other` | VARCHAR; INTEGER; DOUBLE | 9.0 to 11.0 |
| `capital_detail` | `Nc_*` current-cost net capital stock, `Np_*` capital stock price index, `Ksh_*` share in capital services, for the same four assets | DOUBLE | 9.1 to 11.0 |
| `labor_detail` | `countrycode`; `year`; `emp`, `avh`, `yr_sch`, `labsh`, `comp_sh`, `lab_sh1` to `lab_sh4`; `i_emp`, `source`, `i_labsh`, `i_labsh2`, `i_comp_sh`, `i_lab_sh1` to `i_lab_sh4` (labels) | VARCHAR; INTEGER; DOUBLE; VARCHAR | 9.0 to 11.0 |
| `labor_detail` | `i_mix` (0 or 1, no labels); `countryname`, `indicatorname`, `seriescode` | INTEGER; VARCHAR | 11.0 |
| `trade_detail` | `countrycode`; `year`; `pl_x1` to `pl_x6`, `pl_m1` to `pl_m6`, `pl_x`, `pl_m`, `csh_x1` to `csh_x6`, `csh_m1` to `csh_m6`, `csh_x`, `csh_m` | VARCHAR; INTEGER; DOUBLE | all |
| `esh_bilateral_cor` | `countrycode1`, `countrycode2`; `year`; `cor_exp` | VARCHAR; INTEGER; DOUBLE | all |
| `depreciation_rates` | `countrycode`; `year`; `delta_k` | VARCHAR; INTEGER; DOUBLE | 8.0 |

The numbers 1 to 6 in `trade_detail` are the Broad Economic Categories:
food and beverages, industrial supplies, fuels and lubricants, capital
goods, transport equipment, consumer goods. The labels of the coded
columns of `labor_detail` are in its Stata file and are written out as
text here, as in the main table.

```sql
-- DuckDB, straight off the Hub: Japan in PWT 11.0
SELECT year, rgdpo, pop, emp, hc, ctfp, xr, i_xr
FROM 'hf://datasets/yuiseki/pwt/parquet/11.0/pwt.parquet'
WHERE countrycode = 'JPN' AND year >= 2015
ORDER BY year;
```

```sql
-- the same country and year in every release; the price base moves
SELECT split_part(filename, '/', -2) AS release, rgdpe, pop
FROM read_parquet('hf://datasets/yuiseki/pwt/parquet/*/pwt.parquet', filename = true)
WHERE countrycode = 'JPN' AND year = 2010
ORDER BY try_cast(release AS DOUBLE);
```

## Things to know

- The Stata file is the exact source. PWT's xlsx files hold the same
  tables but round some of them: the xlsx of 11.0 writes 15 significant
  digits, and the national accounts xlsx of 8.1 and 9.0 round many values
  to 4 significant digits (`124200000` where the Stata file has
  `124151822.432507`). The other xlsx files agree with the Stata files to
  the last digit.
- `pwt81.xlsx` has 10,357 rows and `pwt81.dta` 10,354. The xlsx holds
  Zimbabwe 2009 to 2011 twice: once with `currency_unit` "US Dollar" and
  the values of the Stata file, and once with "Zimbabwe Dollar" and other
  values. The subset `8.1` follows the Stata file.
- `pwt81.dta` writes Côte d'Ivoire with the byte 0x99, which is ô in the
  Mac Roman encoding; the string is decoded as Mac Roman, and the result
  equals the country name in `pwt81.xlsx`. The other Stata files of 8.0
  and 8.1 read here are plain ASCII; those of 9.0 and later are in the
  Stata 14 format, which is UTF-8.
- Country names change between releases: Turkey in 8.0 to 10.01 is Türkiye
  in 11.0.
- `year` is stored as a float or a double in some Stata files
  (`trade_detail`, `labor_detail`, `esh_bilateral_cor`); every value is a
  whole number and is INTEGER here.
- `labor_detail` of 11.0 adds `countryname`, `indicatorname` and
  `seriescode`, filled on 6,886 rows with one World Bank series
  ("Total natural resources rents (% of GDP)", `NY.GDP.TOTL.RT.ZS`), and
  `i_mix`, a 0 or 1 without labels. The user guide of 11.0 is the place to
  read what they mean.
- The variable labels inside the Stata files are not always updated: the
  11.0 `trade_detail` labels still say "USA GDPo in 2011=1".
- In 11.0, `pwt110.xlsx` was replaced on DataverseNL three days after the
  release (dataset version 1.0 to 2.0). The files here are those of
  version 2.0; `raw/11.0/MANIFEST.json` records the file it replaced.
- `na_data_v2009.zip` holds, besides `na_data_v2009.dta`, a zip of the
  same name with the same Stata file inside.
- The program packages contain input data from other sources (Barro-Lee
  schooling, ICP benchmark workbooks and others) as PWT distributes them.
  Their own terms were not checked.

## Checked before upload

`scripts/02_verify.py` in the source repository checks, with DuckDB:

- every raw file has the size and sha256 in its `MANIFEST.json`, and the
  SHA-1 DataverseNL publishes where it publishes one; every zip and xlsx
  passes a CRC test
- every subset has the number of rows its Stata file states
- every value of every subset equals the value read from the Stata file
  (codes as their labels, empty strings as NULL), compared one by one
- where PWT ships the same table as xlsx (the main tables, `na_data`,
  `capital_detail` of 10.0 to 11.0, `depreciation_rates`), the xlsx has the
  same number of rows (8.1's main table excepted, as above), and every
  value agrees with it, read by DuckDB's excel extension, within a relative
  1e-6 (5e-4 for the national accounts of 8.1 and 9.0); the
  (`countrycode`, `country`) pairs of each main table equal those of its
  xlsx
- every column has the type its name gives
- a DuckDB without extensions opens every file; no row group has a bloom
  filter

## Licence

Each release page says, for its release (11.0 at
https://www.rug.nl/ggdc/productivity/pwt/, the others under
https://www.rug.nl/ggdc/productivity/pwt/pwt-releases/, read on
2026-10-05):

> Penn World Table 11.0 by Robert C. Feenstra, Robert Inklaar and Marcel P.
> Timmer is licensed under a Creative Commons Attribution 4.0 International
> License.

The pages of 8.0, 8.1, 9.0, 9.1, 10.0 and 10.01 say the same with their own
version number. Under "Attribution requirement" the pages say:

> When using these data (for whatever purpose), please make the following
> reference: Feenstra, Robert C., Robert Inklaar and Marcel P. Timmer
> (2015), "The Next Generation of the Penn World Table" American Economic
> Review, 105(10), 3150-3182, available for download at www.ggdc.net/pwt

The DataverseNL records of 11.0 and 10.01 state CC BY 4.0 as well.

The files under `raw/` are GGDC's, unchanged. The Parquet is made from the
Stata files; `LICENSE` beside this file says what was done.

## Citation

Feenstra, Robert C., Robert Inklaar and Marcel P. Timmer (2015), "The Next
Generation of the Penn World Table", American Economic Review, 105(10),
3150-3182. https://doi.org/10.1257/aer.20130954

and the release used, by its DOI, for example:

Feenstra, Robert C., Robert Inklaar and Marcel P. Timmer, Penn World Table
version 11.0, Groningen Growth and Development Centre, University of
Groningen. https://doi.org/10.34894/FABVLR

The DOIs of the other releases are in the table under Releases.

```bibtex
@article{feenstra2015next,
  author  = {Feenstra, Robert C. and Inklaar, Robert and Timmer, Marcel P.},
  title   = {The Next Generation of the Penn World Table},
  journal = {American Economic Review},
  volume  = {105},
  number  = {10},
  pages   = {3150--3182},
  year    = {2015},
  doi     = {10.1257/aer.20130954}
}
```
