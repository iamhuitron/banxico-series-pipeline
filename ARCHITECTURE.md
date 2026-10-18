# 🏛️ Banxico Series Pipeline Architecture & Topology

Automated ETL data pipeline extracting, validating, and analyzing macroeconomic time-series from the Banco de México (Banxico) Economic Information System (SIE) API. Built with Python 3.12, Pydantic, Requests, DuckDB, and SQLite.

---

## 1. Technology Stack

| Layer | Technology | Details |
| :--- | :--- | :--- |
| **Runtime** | Python 3.12+ | Strict type annotations, asynchronous friendly structure |
| **API Client** | `requests` / `urllib3` | Authenticated HTTP client with exponential backoff and retry policies |
| **Validation** | `pydantic` v2 | Strict parsing of Banxico SIE JSON envelopes and observation arrays |
| **Data Transformation** | `pandas` / `numpy` | Time-series normalization, forward fills, rolling averages |
| **Analytical Store** | SQLite / DuckDB | Time-partitioned tables indexed by series ID and observation date |
| **CLI & Automation** | `argparse` / Cron | Parameterized daily syncs and export tasks |

---

## 2. System Topology & Component Graph

```mermaid
flowchart TD
    subgraph ExternalAPI["External Services"]
        Banxico["Banco de México SIE REST API (v1)"]
    end

    subgraph Pipeline["banxico_etl Core"]
        CLI["CLI Driver (banxico_etl/cli.py)"]
        Extract["Extractor (banxico_etl/extract.py)"]
        Models["Data Models (banxico_etl/models.py)"]
        Transform["Normalizer & Cleaner (banxico_etl/transform.py)"]
        Load["Database Loader (banxico_etl/load.py)"]
        Analytics["Time-Series Analytics (banxico_etl/analytics.py)"]
    end

    subgraph Storage["Persistence & Out"]
        DB[(DuckDB / SQLite Time-Series DB)]
        Visuals["Normalized CSVs & Financial Metrics"]
    end

    CLI --> Extract
    Extract --> Banxico
    Banxico --> Extract
    Extract --> Models
    Models --> Transform
    Transform --> Load
    Load --> DB
    DB --> Analytics
    Analytics --> Visuals
```

---

## 3. Data Processing Lifecycle

```mermaid
sequenceDiagram
    autonumber
    actor Analyst as Financial Analyst / Job
    participant CLI as banxico_etl CLI
    participant Extract as Extractor (SIE Client)
    participant Banxico as Banxico REST API
    participant Transform as Transformer
    participant Load as Storage Loader
    participant Analytics as Time-Series Analytics

    Analyst->>CLI: banxico-etl sync --series SF43718,SF60653
    CLI->>Extract: Fetch observations for date range
    Extract->>Banxico: GET /series/{idSeries}/datos/{fechaIni}/{fechaFin}
    Banxico-->>Extract: SIE JSON payload
    Extract->>Transform: Feed raw observations
    Transform->>Transform: Parse DD/MM/YYYY dates, cast numeric values, resolve gaps
    Transform->>Load: Clean observation records
    Load->>Load: Upsert records with unique (series_id, date) constraint
    Analyst->>CLI: banxico-etl analyze --metric rolling-volatility
    CLI->>Analytics: Query series history
    Analytics-->>Analyst: Compute 30-day volatility, moving averages, min/max
```

---

## 4. Directory Structure & Module Breakdown

```
banxico-series-pipeline/
├── banxico_etl/              # Core pipeline package
│   ├── extract.py            # Banxico SIE API client with authentication & retry logic
│   ├── transform.py          # Observation cleaning, date parsing, gap handling
│   ├── load.py               # SQLite/DuckDB loader and schema migrations
│   ├── models.py             # Pydantic schemas for series metadata and points
│   ├── analytics.py          # Volatility, yield curves, moving averages
│   └── cli.py                # Command-line interface for manual & scheduled runs
├── tests/                    # Pipeline validation test suite
│   └── test_etl.py           # Unit tests with mocked Banxico API responses
├── pyproject.toml            # Project packaging & dependencies
└── requirements.txt          # Runtime dependencies
```
