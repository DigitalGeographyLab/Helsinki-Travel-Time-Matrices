#!/usr/bin/env python3

"""Add custom tags to OSM extracts for DGL’s travel time matrices"""

__version__ = "0.0.1"

from .car_speed_annotator import CarSpeedAnnotator

__all__ = [
    "CarSpeedAnnotator",
    "__version__",
]
