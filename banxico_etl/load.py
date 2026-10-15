"""
Loading and persistence engine: writes to Apache Parquet and DuckDB database.
"""

import os
from typing import List, Optional
import pyarrow as pa
import pyarrow.parquet as pq
import duckdb
from .models import MacroEconomicIndicator


class MacroStorage:
    def __init__(self, base_dir: str = "./data/macro_lake", db_path: Optional[str] = None):
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)
        
        self.db_path = db_path or os.path.join(self.base_dir, "macro_series.duckdb")
        self.con = duckdb.connect(self.db_path)
        self._init_duckdb()

    def _init_duckdb(self):
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS macro_indicators (
                fecha VARCHAR PRIMARY KEY,
                año INTEGER,
                mes INTEGER,
                usd_mxn_fix DOUBLE,
                tiie_28d DOUBLE,
                udis DOUBLE,
                inpc DOUBLE,
                inflacion_anual DOUBLE,
                tasa_real DOUBLE
            );
        """)

    def save_indicators(self, indicators: List[MacroEconomicIndicator]) -> int:
        if not indicators:
            return 0

        # High-performance zero-copy Arrow ingestion into DuckDB
        dicts = [ind.to_dict() for ind in indicators]
        table = pa.Table.from_pylist(dicts)
        
        self.con.register("_arrow_batch", table)
        self.con.execute("INSERT OR REPLACE INTO macro_indicators SELECT * FROM _arrow_batch;")
        self.con.unregister("_arrow_batch")

        # Materialize Parquet
        parquet_path = os.path.join(self.base_dir, "macro_indicators.parquet")
        pq.write_table(table, parquet_path)

        return len(indicators)

    def close(self):
        self.con.close()
