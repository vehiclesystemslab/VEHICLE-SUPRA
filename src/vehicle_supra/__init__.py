"""
VEHICLE-SUPRA
-------------
Coherence-Governed Architecture for Autonomous AI Agents

Alpha research prototype by Roberto Borda Milan / VEHICLE Systems Lab.

Web    : https://vehiclesystemslab.com
Framework DOI: 10.5281/zenodo.19981738
License: MIT
"""

from .node import (
    SupraNode,
    SupraNodeConfig,
    REGIME_A0,
    REGIME_A1,
    REGIME_A2,
    REGIME_A3,
    REGIME_A4,
    REGIME_A5,
    REGIME_A6,
)
from .network import SupraNetwork

__version__ = "0.2.1"
__author__ = "Roberto Borda Milan"
__doi__ = "10.5281/zenodo.19981738"

__all__ = [
    "SupraNode",
    "SupraNodeConfig",
    "SupraNetwork",
    "REGIME_A0",
    "REGIME_A1",
    "REGIME_A2",
    "REGIME_A3",
    "REGIME_A4",
    "REGIME_A5",
    "REGIME_A6",
]
