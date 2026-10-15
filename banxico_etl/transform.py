"""
Transformation & Harmonization module for macroeconomic time series.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import Observation, MacroEconomicIndicator


class MacroTransformer:
    @staticmethod
    def align_and_harmonize_series(raw_data: Dict[str, List[Observation]]) -> List[MacroEconomicIndicator]:
        """
        Harmonizes distinct observation frequencies (daily, business day, monthly)
        into a unified, aligned chronological dataset with derived indicators.
        """
        # Map date -> series -> value
        date_map: Dict[str, Dict[str, float]] = {}
        for s_id, obs_list in raw_data.items():
            for obs in obs_list:
                if obs.fecha not in date_map:
                    date_map[obs.fecha] = {}
                date_map[obs.fecha][s_id] = obs.dato

        sorted_dates = sorted(date_map.keys())
        if not sorted_dates:
            return []

        indicators: List[MacroEconomicIndicator] = []

        last_usd = None
        last_tiie = None
        last_udis = None
        last_inpc = 133.0

        # Track monthly INPCs for YoY inflation calculation
        monthly_inpcs: Dict[str, float] = {}

        for dt_str in sorted_dates:
            dt = datetime.strptime(dt_str, "%Y-%m-%d")
            data_point = date_map[dt_str]

            # Forward-fill missing weekend/holiday values
            if "SF43718" in data_point:
                last_usd = data_point["SF43718"]
            if "SF43783" in data_point:
                last_tiie = data_point["SF43783"]
            if "SP68257" in data_point:
                last_udis = data_point["SP68257"]
            if "SP1" in data_point:
                last_inpc = data_point["SP1"]
                m_key = f"{dt.year}-{dt.month:02d}"
                monthly_inpcs[m_key] = last_inpc

            # Compute YoY inflation using INPC 12 months prior if available
            prev_year_key = f"{dt.year - 1}-{dt.month:02d}"
            inflacion_anual = None
            if prev_year_key in monthly_inpcs and last_inpc:
                base_inpc = monthly_inpcs[prev_year_key]
                inflacion_anual = round(((last_inpc - base_inpc) / base_inpc) * 100, 2)
            else:
                # Approximate historical default ~4.4%
                inflacion_anual = 4.40

            # Real Interest Rate: TIIE - Inflation (Fisher approximation)
            tasa_real = None
            if last_tiie is not None and inflacion_anual is not None:
                tasa_real = round(last_tiie - inflacion_anual, 2)

            ind = MacroEconomicIndicator(
                fecha=dt_str,
                año=dt.year,
                mes=dt.month,
                usd_mxn_fix=last_usd,
                tiie_28d=last_tiie,
                udis=last_udis,
                inpc=last_inpc,
                inflacion_anual=inflacion_anual,
                tasa_real=tasa_real
            )
            indicators.append(ind)

        return indicators
