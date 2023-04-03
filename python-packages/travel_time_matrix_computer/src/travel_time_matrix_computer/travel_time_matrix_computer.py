#!/usr/bin/env python3


"""Wrap the entire DGL travel time matrix computation (read config, prepare
data, compile output)"""


import datetime

from .walking_travel_time_matrix_computer import WalkingTravelTimeMatrixComputer


__all__ = ["TravelTimeMatrixComputer"]


class TravelTimeMatrixComputer:
    DEPARTURE_TIMES = {
        "rush-hour": datetime.time(hour=8),
        "midday": datetime.time(hour=12),
        "off-peak": datetime.time(hour=2),
    }

    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def run(self):
        # travel_times = []
        for time_name, time_value in self.DEPARTURE_TIMES:
            walking_travel_time_matrix_computer = WalkingTravelTimeMatrixComputer(
                **self._kwargs
            )
            travel_times = walking_travel_time_matrix_computer.run(departure=time_value)
            print(travel_times)
