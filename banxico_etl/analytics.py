"""
Econometric and statistical analytics over macro time-series.
"""

from typing import Dict, Any, List
import duckdb


class MacroAnalytics:
    def __init__(self, duckdb_conn: duckdb.DuckDBPyConnection):
        self.con = duckdb_conn

    def get_latest_indicators(self) -> Dict[str, Any]:
        """Returns the most recent macroeconomic snapshot."""
        row = self.con.execute("""
            SELECT fecha, usd_mxn_fix, tiie_28d, udis, inpc, inflacion_anual, tasa_real
            FROM macro_indicators
            ORDER BY fecha DESC
            LIMIT 1
        """).fetchone()

        if not row:
            return {}

        return {
            "fecha": row[0],
            "usd_mxn_fix": round(row[1], 4) if row[1] is not None else None,
            "tiie_28d": round(row[2], 2) if row[2] is not None else None,
            "udis": round(row[3], 4) if row[3] is not None else None,
            "inpc": round(row[4], 2) if row[4] is not None else None,
            "inflacion_anual": round(row[5], 2) if row[5] is not None else None,
            "tasa_real": round(row[6], 2) if row[6] is not None else None,
        }

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Calculates historical min, max, avg and stddev across series."""
        res = self.con.execute("""
            SELECT 
                COUNT(*) as n_obs,
                ROUND(MIN(usd_mxn_fix), 4) as min_usd,
                ROUND(AVG(usd_mxn_fix), 4) as avg_usd,
                ROUND(MAX(usd_mxn_fix), 4) as max_usd,
                ROUND(STDDEV(usd_mxn_fix), 4) as std_usd,
                ROUND(MIN(tiie_28d), 2) as min_tiie,
                ROUND(AVG(tiie_28d), 2) as avg_tiie,
                ROUND(MAX(tiie_28d), 2) as max_tiie,
                ROUND(AVG(tasa_real), 2) as avg_tasa_real
            FROM macro_indicators
            WHERE usd_mxn_fix IS NOT NULL
        """).fetchone()

        return {
            "num_observaciones": res[0],
            "usd_min": res[1],
            "usd_avg": res[2],
            "usd_max": res[3],
            "usd_stddev": res[4],
            "tiie_min": res[5],
            "tiie_avg": res[6],
            "tiie_max": res[7],
            "tasa_real_promedio": res[8],
        }

    def get_correlation_matrix(self) -> Dict[str, float]:
        """Calculates Pearson correlation between key financial series."""
        res = self.con.execute("""
            SELECT 
                ROUND(corr(usd_mxn_fix, tiie_28d), 4) as corr_usd_tiie,
                ROUND(corr(usd_mxn_fix, inflacion_anual), 4) as corr_usd_inf,
                ROUND(corr(tiie_28d, inflacion_anual), 4) as corr_tiie_inf
            FROM macro_indicators
            WHERE usd_mxn_fix IS NOT NULL AND tiie_28d IS NOT NULL AND inflacion_anual IS NOT NULL
        """).fetchone()

        return {
            "corr_usd_tiie": res[0] or 0.0,
            "corr_usd_inflacion": res[1] or 0.0,
            "corr_tiie_inflacion": res[2] or 0.0,
        }

    def get_monthly_aggregates(self) -> List[Dict[str, Any]]:
        """Groups time series into monthly averages and volatilities."""
        query = """
            SELECT 
                año,
                mes,
                ROUND(AVG(usd_mxn_fix), 4) as usd_promedio,
                ROUND(STDDEV(usd_mxn_fix), 4) as usd_volatilidad,
                ROUND(AVG(tiie_28d), 2) as tiie_promedio,
                ROUND(AVG(inflacion_anual), 2) as inflacion_promedio,
                ROUND(AVG(tasa_real), 2) as tasa_real_promedio
            FROM macro_indicators
            WHERE usd_mxn_fix IS NOT NULL
            GROUP BY año, mes
            ORDER BY año ASC, mes ASC
        """
        return self.con.execute(query).df().to_dict(orient="records")
