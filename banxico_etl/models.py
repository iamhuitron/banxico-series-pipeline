"""
Data models and typed schemas for macroeconomic time-series.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from datetime import date


@dataclass
class Observation:
    fecha: str  # YYYY-MM-DD
    serie_id: str
    dato: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MacroEconomicIndicator:
    fecha: str
    año: int
    mes: int
    usd_mxn_fix: Optional[float]
    tiie_28d: Optional[float]
    udis: Optional[float]
    inpc: Optional[float]
    inflacion_anual: Optional[float]  # YoY %
    tasa_real: Optional[float]  # TIIE - Inflación

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
