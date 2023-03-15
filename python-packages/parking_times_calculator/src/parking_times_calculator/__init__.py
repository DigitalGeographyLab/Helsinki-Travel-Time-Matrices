#!/usr/bin/env python3

"""Calculate parking times depending on destination location within Finland"""

__version__ = "0.0.1"

from .parking_times_calculator import ParkingTimesCalculator

__all__ = [
    "ParkingTimesCalculator",
    "__version__",
]
