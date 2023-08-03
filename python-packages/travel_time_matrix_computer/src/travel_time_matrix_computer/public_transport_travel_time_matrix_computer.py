#!/usr/bin/env python3


"""Wrap the entire DGL travel time matrix computation (read config, prepare
data, compile output)"""


import datetime

import r5py

from .base_travel_time_matrix_computer import BaseTravelTimeMatrixComputer
from .multitemporal_travel_time_matrix_computer_mixin import (
    MultiTemporalTravelTimeMatrixComputerMixin,
)
from .walking_travel_time_matrix_computer import WalkingTravelTimeMatrixComputer


__all__ = ["PublicTransportTravelTimeMatrixComputer"]


class PublicTransportTravelTimeMatrixComputer(
    BaseTravelTimeMatrixComputer, MultiTemporalTravelTimeMatrixComputerMixin
):
    WALKING_SPEEDS = WalkingTravelTimeMatrixComputer.WALKING_SPEEDS

    def run(self):
        travel_times = None

        for timeslot_name, timeslot_time in self.DEPARTURE_TIMES.items():
            for variable_name, walking_speed in self.WALKING_SPEEDS.items():
                column_name = f"pt_{timeslot_name[0]}_{variable_name}"

                travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
                    self.transport_network,
                    origins=self.origins_destinations,
                    departure=datetime.datetime.combine(self.date, timeslot_time),
                    departure_time_window=datetime.timedelta(hours=1),
                    transport_modes=[r5py.TransportMode.TRANSIT],
                    speed_walking=walking_speed,
                    percentiles=[1],
                    max_time=self.MAX_TIME,
                )
                _travel_times = travel_time_matrix_computer.compute_travel_times()

                _travel_times = _travel_times.rename(columns={"travel_time_p1": "travel_time"})

                # Add times spent walking from the original point to the snapped points
                _travel_times = self.add_access_times(_travel_times)

                # fmt: off
                _travel_times = (
                    _travel_times.set_index(["from_id", "to_id"])
                    .rename(
                        columns={
                            "travel_time": column_name,
                            "distance": f"{column_name}_d",
                        }
                    )
                )
                # fmt: on

                if travel_times is None:
                    travel_times = _travel_times
                else:
                    travel_times = travel_times.join(_travel_times)

        return travel_times
