"""
Data Extraction Module for Banco de México (Banxico SIE) series.
Supports both direct REST API extraction and offline benchmark datasets.
"""

import os
import json
import urllib.request
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .models import Observation


BANXICO_SERIES_CATALOG = {
    "SF43718": "Tipo de cambio FIX (USD/MXN)",
    "SF43783": "Tasa de Interés Interbancaria de Equilibrio (TIIE 28 días)",
    "SP68257": "Valor de Unidades de Inversión (UDIS)",
    "SP1": "Índice Nacional de Precios al Consumidor (INPC General)"
}


class BanxicoExtractor:
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.environ.get("BANXICO_TOKEN")

    def fetch_series_api(self, series_id: str, start_date: str, end_date: str) -> List[Observation]:
        """
        Fetches observations from official Banxico SIE REST API.
        """
        if not self.api_token:
            raise ValueError("Banxico API token required for live extraction. Set BANXICO_TOKEN environment variable.")

        url = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{series_id}/datos/{start_date}/{end_date}"
        req = urllib.request.Request(url, headers={"Bmx-Token": self.api_token, "Accept": "application/json"})
        
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

        observations = []
        series_data = data.get("bmx", {}).get("series", [])
        if series_data:
            datos = series_data[0].get("datos", [])
            for item in datos:
                # Format: DD/MM/YYYY -> YYYY-MM-DD
                raw_date = item.get("fecha")
                raw_val = item.get("dato", "").replace(",", "")
                try:
                    dt = datetime.strptime(raw_date, "%d/%m/%Y")
                    val = float(raw_val)
                    observations.append(Observation(fecha=dt.strftime("%Y-%m-%d"), serie_id=series_id, dato=val))
                except (ValueError, TypeError):
                    continue

        return observations

    def get_sample_historical_dataset(self) -> Dict[str, List[Observation]]:
        """
        Generates realistic Mexican macroeconomic series covering 2024 to 2026
        for offline, zero-cost, fully reproducible testing and demonstration.
        """
        dataset = {s_id: [] for s_id in BANXICO_SERIES_CATALOG}
        start = datetime(2024, 1, 1)
        end = datetime(2026, 3, 31)
        curr = start

        # Initial baseline values (realistic Mexican economic indicators)
        usd = 17.10
        tiie = 11.25
        udis = 8.02
        inpc = 133.20

        day_count = 0
        while curr <= end:
            dt_str = curr.strftime("%Y-%m-%d")
            # Only business days have FIX and TIIE
            if curr.weekday() < 5:
                # Macro trend: USD gradual oscillation between 16.80 and 20.20
                if curr.year == 2024 and curr.month < 6:
                    usd += 0.005 if day_count % 3 == 0 else -0.004
                elif curr.year >= 2024 and curr.month >= 6:
                    # Electoral / market adjustment in late 2024
                    usd += 0.012 if day_count % 2 == 0 else -0.006
                    usd = min(max(usd, 16.50), 20.50)

                # TIIE gradual easing from 11.25% towards 8.50%
                if curr.year >= 2025:
                    tiie = max(tiie - 0.002, 8.50)
                else:
                    tiie = max(tiie - 0.0005, 10.75)

                dataset["SF43718"].append(Observation(fecha=dt_str, serie_id="SF43718", dato=round(usd, 4)))
                dataset["SF43783"].append(Observation(fecha=dt_str, serie_id="SF43783", dato=round(tiie, 4)))

            # UDIS published daily
            udis += 0.0009
            dataset["SP68257"].append(Observation(fecha=dt_str, serie_id="SP68257", dato=round(udis, 6)))

            # INPC published monthly (10th of each month)
            if curr.day == 10:
                inpc *= 1.0035  # ~4.2% annualized inflation
                dataset["SP1"].append(Observation(fecha=dt_str, serie_id="SP1", dato=round(inpc, 4)))

            curr += timedelta(days=1)
            day_count += 1

        return dataset
