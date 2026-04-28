"""
core/planetary/
===============
GAIA Planetary Intelligence Layer — noosphere, collective signal,
and live planetary data connectors.

All imports redirect to flat core/ files until Phase B physical migration.
"""

from core.noosphere import Noosphere
from core.collective_signal_layer import CollectiveSignalLayer
from core.planetary_data_connector import PlanetaryDataConnector

__all__ = [
    "Noosphere",
    "CollectiveSignalLayer",
    "PlanetaryDataConnector",
]
