# ONC Pressure Data Access

Jupyter notebooks for accessing and processing bottom pressure recorder (BPR) data from Ocean Networks Canada's (ONC) cabled observatory at **Barkley Canyon** via the [ONC Open API](https://data.oceannetworks.ca/OpenAPI). Covers two cabled ONC instrument types: the **RBR BPR|Zero** and the **Sonardyne Fetch AZA** .

---

## Repository Structure

```
BarkleyCanyon_Cabled/
├── BPR_Zero_Cabled.ipynb            # Main BPR|Zero workflow: download, drift analysis, AZA calibration
├── BPR_Zero_Cabled_getLogFiles.ipynb # Download raw archive log files for BPR|Zero
├── SonardyneFetch.ipynb                # Download and parse Sonardyne Fetch serial data
├── ParseFetches.py                     # Reusable class for fetching and parsing Sonardyne Fetch data
└── README.md
```

---

## Prerequisites

### ONC API Token
All notebooks require an ONC API token (see here for information about ONCs OpenAPI:https://oceannetworkscanada.github.io/api-python-client/). Store it in a `.env` file in the notebook directory:

```
ONC_TOKEN=your_token_here
```

Tokens are available from your [ONC account page](https://data.oceannetworks.ca/Profile).

### Python Dependencies

```
onc          # ONC Python client library
requests
requests_cache
pandas
numpy
scipy
matplotlib
python-dotenv
```

Install with:

```bash
pip install onc requests requests-cache pandas numpy scipy matplotlib python-dotenv
```

---

## Notebooks

### 1. `BPR_Zero_Cabled_AS.ipynb` — BPR|Zero Analysis

Downloads scalar and raw data for the cabled **RBR Quartz BPR|Zero** at Barkley Canyon, characterises sensor drift, detects AZA in-situ calibration cycles, and compares against a reference BPR.

**Device:** `RBRQUARTZ3BPRZERO207223`  
**Locations:** `NCBC.P1` (BPR|Zero), `NCBC` (reference non-AZA BPR)  
**API methods:** `scalardata/getByDevice`, `scalardata/getByLocation`, `onc.getDirectRawByDevice`

**Workflow:**
1. Fetch 900-second averaged scalar pressure (`pressure1`) data via the ONC REST API
2. Plot pressure time series; filter out calibration pressure drops (outside 410–412 dbar).
3. Fit exponential + linear drift models using `scipy.optimize.curve_fit` and `numpy.polyfit`.
4. Detect AZA calibration events from `systemstatus` sensor data (step-down transitions).
5. For each calibration event, fetch a 900 s window of raw scalar data and compute the BPR|Zero − Reference pressure difference.
6. Overlay all calibration cycles and apply a 16-sample rolling mean.
7. Compare 15-min averaged pressure from `NCBC.P1` and `NCBC`; compute and plot residuals with a 25-hour rolling mean.
8. Retrieve raw archived data via `onc.getDirectRawByDevice`; split CSV-encoded lines into SF pressure, SF temperature, barometric pressure, and barometric temperature channels.

---

### 2. `BPR_Zero_Cabled_AS_getLogFiles.ipynb` — Download Archive Log Files

Downloads raw binary/ASCII log files from the ONC archive for the cabled BPR|Zero at Barkley Canyon (locationCode: **NCBC.P1**). Useful for offline or batch processing of the raw instrument data.

**Device:** `RBRQUARTZ3BPRZERO207223`  
**API methods:** `onc.getArchivefileByDevice`, `onc.downloadArchivefile`

**Workflow:**
1. Query available archive files for a given date range (`getArchivefileByDevice`).
2. Download files to a local `output/` directory, skipping files already present.

---

### 3. `SonardyneFetch.ipynb` — Sonardyne Fetch Data

Downloads, parses, and plots raw serial ASCII data from **Sonardyne Fetch AZA and non-AZA** autonomous pressure loggers at Barkley Canyon. Also documents the Sonardyne Fetch serial message format.

**Devices (three Fetch units):**
| Device Code | Unit |
|---|---|
| `SONARDYNEFETCH8306SN329744001` | Fetch AZA |
| `SONARDYNEFETCH8306SN329742001` | Fetch North |
| `SONARDYNEFETCH8306SN329742002` | Fetch East |

**API method:** `onc.getDirectRawByDevice` (via `ParseFetches`)

**Workflow:**
1. Instantiate `ParseFetches(SN, deviceCode, dateFrom, dateTo)` and call `getONCRawData()` to retrieve raw ASCII lines.
2. Call `parseData()` to decode message types and extract sensor columns (see table below).
3. Plot Digiquartz (`DQZ`) and Keller (`KLR`) pressure and temperature as 4-panel subplots.
4. Resample to 15-minute means and re-plot.
5. Optionally save/load parsed data as Parquet.

**Parsed message types and output columns:**

| Message | Columns |
|---|---|
| `DQZ` | `DQZ_Press` (dbar), `DQZ_Temp` |
| `KLR` | `KLR_PRESS` (dbar), `KLR_Temp` |
| `TMP` | `TMP_Temp` |
| `INC` | `INC_Pitch`, `INC_Roll` |
| `PIES` | `PIES_PRESS` (dbar), `PIES_TOF`, `PIES_Mag`, and others |
| `AZA` | Primary/secondary/low-port pressures and temperatures, RMS error, settling flag |
| `AZS` | AZA status summary (start/end of calibration cycle) |

> Pressure values are converted from kPa to dbar (×0.1) during parsing.

---

### 4. `ParseFetches.py` — Sonardyne Fetch Parser Module

Reusable Python class `ParseFetches` that encapsulates all ONC API calls and serial message parsing for Sonardyne Fetch instruments. Used by `SonardyneFetch.ipynb`.

```python
from ParseFetches import ParseFetches

fetcher = ParseFetches(SN, deviceCode, dateFrom, dateTo)
df_raw  = fetcher.getONCRawData()   # raw ASCII lines with timestamp index
df      = fetcher.parseData()       # parsed sensor columns
```

---

## Notes

- All API calls use `allPages=True` so the ONC client handles pagination automatically.
- HTTP requests in `BPR_Zero_Cabled_AS.ipynb` are cached with `requests_cache` to avoid redundant downloads during re-runs.
- CRC checksums in Sonardyne serial messages are stripped during parsing.

