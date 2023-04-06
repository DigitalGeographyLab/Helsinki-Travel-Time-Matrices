#!/usr/bin/env python3


"""Wrap the entire DGL travel time matrix computation (read config, prepare
data, compile output)"""


import datetime

import r5py

from .base_travel_time_matrix_computer import BaseTravelTimeMatrixComputer


__all__ = ["WalkingTravelTimeMatrixComputer"]


class WalkingTravelTimeMatrixComputer(BaseTravelTimeMatrixComputer):
    # column name -> walking speed in km/h
    WALKING_SPEEDS = {
        "walk_avg": 5.15,
        "walk_slo": 3.43,
    }

    def run(self):
        travel_times = None
        for column_name, walking_speed in self.WALKING_SPEEDS.items():
            travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
                self.transport_network,
                origins=self.origins_destinations,
                departure=datetime.datetime.combine(
                    self.date, self.DEFAULT_TIME_OF_DAY
                ),
                transport_modes=[r5py.LegMode.WALK],
                speed_walking=walking_speed,
                max_time=self.MAX_TIME,
            )

            _travel_times = travel_time_matrix_computer.compute_travel_times()
            _travel_times = self.add_access_times(_travel_times)

            # fmt: off
            _travel_times = (
                _travel_times.set_index(["from_id", "to_id"])
                .rename(columns={"travel_time": column_name})
            )
            # fmt: on

            if travel_times is None:
                travel_times = _travel_times
            else:
                travel_times = travel_times.join(_travel_times)

        return travel_times
