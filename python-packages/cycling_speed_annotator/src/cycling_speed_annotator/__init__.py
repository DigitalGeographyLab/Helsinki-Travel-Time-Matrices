#!/usr/bin/env python3

"""Add custom tags to OSM extracts for DGL’s travel time matrices"""

__version__ = "0.0.1"

from .cycling_speed_annotator import CyclingSpeedAnnotator

__all__ = [
    "CyclingSpeedAnnotator",
    "__version__",
]
