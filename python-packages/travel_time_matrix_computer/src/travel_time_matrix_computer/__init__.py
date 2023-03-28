#!/usr/bin/env python3

"""Wrap the entire DGL travel time matrix computation (read config, prepare
data, compile output)"""

__version__ = "0.0.1"

from .travel_time_matrix_computer import TravelTimeMatrixComputer

__all__ = [
    "TravelTimeMatrixComputer",
    "__version__",
]
