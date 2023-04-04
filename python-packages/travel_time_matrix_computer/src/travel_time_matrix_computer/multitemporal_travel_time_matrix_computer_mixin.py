#!/usr/bin/env python3


"""Wrap the entire DGL travel time matrix computation (read config, prepare
data, compile output)"""


import datetime


__all__ = ["MultiTemporalTravelTimeMatrixComputerMixin"]


class MultiTemporalTravelTimeMatrixComputerMixin:
    DEPARTURE_TIMES = {
        "rush-hour": datetime.time(hour=8),
        "midday": datetime.time(hour=12),
        "nighttime": datetime.time(hour=2),
    }
