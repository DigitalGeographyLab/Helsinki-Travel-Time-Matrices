#!/usr/bin/env python3


"""Wrap the entire DGL travel time matrix computation (read config, prepare
data, compile output)"""


from .car_travel_time_matrix_computer import CarTravelTimeMatrixComputer
from .cycling_travel_time_matrix_computer import CyclingTravelTimeMatrixComputer
from .public_transport_travel_time_matrix_computer import (
    PublicTransportTravelTimeMatrixComputer,
)
from .walking_travel_time_matrix_computer import WalkingTravelTimeMatrixComputer


__all__ = ["TravelTimeMatrixComputer"]


class TravelTimeMatrixComputer:
    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def run(self):
        print("now computing walking times")
        walking_travel_time_matrix_computer = WalkingTravelTimeMatrixComputer(
            **self._kwargs
        )
        travel_times = walking_travel_time_matrix_computer.run()
        del walking_travel_time_matrix_computer

        print("now computing cycling times")
        cycling_travel_time_matrix_computer = CyclingTravelTimeMatrixComputer(
            **self._kwargs
        )
        travel_times = travel_times.join(cycling_travel_time_matrix_computer.run())
        del cycling_travel_time_matrix_computer

        print("now computing driving times")
        car_travel_time_matrix_computer = CarTravelTimeMatrixComputer(**self._kwargs)
        travel_times = travel_times.join(car_travel_time_matrix_computer.run())
        del car_travel_time_matrix_computer

        print("now computing public transport times")
        public_transport_travel_time_matrix_computer = (
            PublicTransportTravelTimeMatrixComputer(**self._kwargs)
        )
        travel_times = travel_times.join(
            public_transport_travel_time_matrix_computer.run()
        )
        del public_transport_travel_time_matrix_computer

        return travel_times
