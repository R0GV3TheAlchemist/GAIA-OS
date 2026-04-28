"""
core/planetary/
===============
GAIA Planetary Intelligence Layer — noosphere, collective signal,
and live planetary data connectors.

Submodules
----------
noosphere                — planetary noosphere coherence layer (C43)
collective_signal_layer  — collective signal aggregation
planetary_data_connector — live planetary data feeds (Schumann, GCP, etc.)
"""

from core.planetary.noosphere import Noosphere
from core.planetary.collective_signal_layer import CollectiveSignalLayer
from core.planetary.planetary_data_connector import PlanetaryDataConnector

__all__ = [
    "Noosphere",
    "CollectiveSignalLayer",
    "PlanetaryDataConnector",
]
