# 📈 Banxico Series Pipeline: Macroeconomic Time-Series ETL & Econometric Engine

<p align="left">
  <strong>Automated Data Pipeline for Banco de México (Banxico SIE) Series into Parquet & DuckDB</strong><br>
  Designed and engineered by <a href="https://github.com/iamhuitron"><strong>Miguel Delgado Huitrón</strong></a> (<code>@iamhuitron</code>) · Informatics, UNAM
</p>

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/DuckDB-In--Process_SQL-FFF000?style=flat-square&logo=duckdb&logoColor=black" alt="DuckDB" />
  <img src="https://img.shields.io/badge/Apache_Arrow-Parquet-D22128?style=flat-square&logo=apachearrow&logoColor=white" alt="PyArrow" />
  <img src="https://img.shields.io/badge/Tests-Pytest_Passing-success?style=flat-square&logo=pytest&logoColor=white" alt="Pytest" />
  <img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square" alt="MIT" />
</p>

---

## 📌 Problem & Motivation

Quantitative financial analysts, corporate treasuries, and FinTech applications in Mexico require constant access to core macroeconomic benchmark time series:
1. **Tipo de Cambio FIX (USD/MXN)** (`SF43718`): Published daily by Banco de México on business days.
2. **Tasa TIIE 28 Días** (`SF43783`): Official benchmark interbank interest rate.
3. **Unidades de Inversión (UDIS)** (`SP68257`): Inflation-adjusted financial unit published daily.
4. **Índice Nacional de Precios al Consumidor (INPC)** (`SP1`): Monthly consumer price index measuring inflation.

Working directly with raw data streams poses practical data engineering challenges:
- **Disparate Observation Frequencies:** Daily vs. business days vs. monthly data points create misaligned timestamps.
- **Calendar Gaps:** Banking holidays and weekends require robust forward-fill or interpolation strategies to avoid data breaks in downstream econometric models.
- **Derived Metrics Overhead:** Calculating real interest rates (Fisher equation) and annualized inflation requires repetitive cross-series transformations.

**Banxico Series Pipeline** automates the entire Extraction, Harmonization, and Loading (ETL) lifecycle, materializing cleaned chronological datasets into **Apache Parquet** and an embedded **DuckDB** analytics database.

---

## 🏗️ Data Architecture

```
┌────────────────────────────────────────────────────────┐
│                   Banxico SIE Ingestion                │
│       (REST API Endpoint / Reproducible Offline Data)  │
└───────────────────────────┬────────────────────────────┘
                            │
               Extractor & Observation Parser
                            │
┌───────────────────────────▼────────────────────────────┐
│         Harmonization & Transformation Pipeline        │
│   ├── Calendar alignment (Business days / Holidays)   │
│   ├── Forward-fill imputation                          │
│   ├── Year-over-Year (YoY) Inflation Computation       │
│   └── Real Interest Rate: TIIE 28d - Inflación Anual   │
└───────────────────────────┬────────────────────────────┘
                            │
            Zero-Copy PyArrow Batch Ingestion
                            │
┌───────────────────────────▼────────────────────────────┐
│              Storage & Econometric Engine              │
│   ├── Columnar Dataset: macro_indicators.parquet       │
│   ├── Embedded DuckDB: macro_series.duckdb             │
│   └── Statistical Queries: Correlación, Volatilidad    │
└────────────────────────────────────────────────────────┘
```

---

## 🧮 Mathematical Formulations

### 1. Annualized Year-over-Year (YoY) Inflation
$$\pi_t = \left( \frac{\text{INPC}_t - \text{INPC}_{t-12}}{\text{INPC}_{t-12}} \right) \times 100$$

### 2. Real Interest Rate (Fisher Approximation)
$$r_t \approx i_t - \pi_t$$
Where $i_t$ is the 28-day TIIE and $\pi_t$ is the annualized headline inflation rate.

### 3. Cross-Series Pearson Correlation
$$\rho_{X, Y} = \frac{\sum_{i=1}^n (X_i - \bar{X})(Y_i - \bar{Y})}{\sqrt{\sum_{i=1}^n (X_i - \bar{X})^2 \sum_{i=1}^n (Y_i - \bar{Y})^2}}$$

---

## 🚀 Quick Start & CLI Usage

### 1. Installation

```bash
git clone https://github.com/iamhuitron/banxico-series-pipeline.git
cd banxico-series-pipeline

python3 -m venv .venv
source .venv/bin/activate

pip install -e .[dev]
```

### 2. Run the Automated ETL Pipeline

```bash
python3 -m banxico_etl.cli run-etl --lake-dir ./data/macro_lake
```

Output:
```text
Iniciando extracción de series Banxico SIE...
✓ Extraídas 2022 observaciones en 4 series clave.
Transformando y armonizando frecuencias temporales...
✓ Generados 821 registros temporales diarios armonizados.
✓ Persistidos 821 días en DuckDB y particionados en Apache Parquet.
```

### 3. Display Latest Macroeconomic Snapshot

```bash
python3 -m banxico_etl.cli snapshot --lake-dir ./data/macro_lake
```

Output:
```text
======================= SNAPSHOT MACROECONÓMICO =======================
Fecha de Referencia : 2026-03-31
Tipo de Cambio FIX  : $17.9170 MXN/USD
Tasa TIIE (28 días) : 10.47%
Valor UDIS          : $8.758900 MXN
Índice INPC         : 146.38 pts
Inflación Anual     : 4.28%
Tasa de Interés Real: 6.19% (TIIE - Inflación)
========================================================================
```

### 4. Compute Descriptive Statistics & Correlations

```bash
python3 -m banxico_etl.cli stats --lake-dir ./data/macro_lake
```

---

## 🐍 Python SDK Integration

```python
from banxico_etl import BanxicoExtractor, MacroTransformer, MacroStorage, MacroAnalytics

# 1. Extract raw series
extractor = BanxicoExtractor()
raw_data = extractor.get_sample_historical_dataset()

# 2. Transform and compute derived metrics
indicators = MacroTransformer.align_and_harmonize_series(raw_data)

# 3. Store in DuckDB & Parquet
storage = MacroStorage(base_dir="./data/macro_lake")
storage.save_indicators(indicators)

# 4. Perform statistical analysis
analytics = MacroAnalytics(storage.con)
latest = analytics.get_latest_indicators()
print(f"Tipo de Cambio: ${latest['usd_mxn_fix']} MXN/USD")
print(f"Tasa Real: {latest['tasa_real']}%")

storage.close()
```

---

## 🧪 Automated Unit Testing

Run the test suite:

```bash
pytest --verbose
```

All test suites pass:
```text
tests/test_etl.py::test_extract_sample_data PASSED
tests/test_etl.py::test_transform_and_align PASSED
tests/test_etl.py::test_load_and_analytics PASSED

============================== 3 passed in 4.64s ===============================
```

---

## 📄 License

This project is licensed under the **MIT License**. Created by [Miguel Delgado Huitrón](https://github.com/iamhuitron).
