"""
Banxico Series Pipeline: Automated ETL and econometric engine for Mexican macro indicators.
"""

__version__ = "1.0.0"
__author__ = "Miguel Delgado Huitron (@iamhuitron)"

from .models import Observation, MacroEconomicIndicator
from .extract import BanxicoExtractor, BANXICO_SERIES_CATALOG
from .transform import MacroTransformer
from .load import MacroStorage
from .analytics import MacroAnalytics

__all__ = [
    "Observation",
    "MacroEconomicIndicator",
    "BanxicoExtractor",
    "BANXICO_SERIES_CATALOG",
    "MacroTransformer",
    "MacroStorage",
    "MacroAnalytics",
]
