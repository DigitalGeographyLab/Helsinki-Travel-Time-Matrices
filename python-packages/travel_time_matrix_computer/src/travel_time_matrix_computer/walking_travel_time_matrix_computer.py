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
        "walk_avg": 4.7,
        "walk_slo": 3.43,
    }

    def estimate_walking_distance(self, travel_times):
        """
        Add a column that contains a rough estimate of walked distance.

        This adds a column `walk_d` to `travel_times` if it does not exist yet,
        and uses the `walk_avg` time and speed to derive a distance that r5 does
        not report natively
        """
        if "walk_d" not in travel_times.columns and "walk_avg" in travel_times.columns:
            meters_per_minute = self.WALKING_SPEEDS["walk_avg"] * 1000.0 / 60.0
            travel_times["walk_d"] = (
                travel_times["walk_avg"]
                .apply(lambda walking_time: walking_time * meters_per_minute)
                .round()
            )
        return travel_times

    def run(self):
        travel_times = None
        for column_name, walking_speed in self.WALKING_SPEEDS.items():
            travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
                self.transport_network,
                origins=self.origins_destinations,
                departure=datetime.datetime.combine(
                    self.date, self.DEFAULT_TIME_OF_DAY
                ),
                departure_time_window=datetime.timedelta(hours=1),
                transport_modes=[r5py.TransportMode.WALK],
                speed_walking=walking_speed,
                percentiles=[1],
                max_time=self.MAX_TIME,
            )
            _travel_times = travel_time_matrix_computer.compute_travel_times()

            _travel_times = _travel_times.rename(
                columns={"travel_time_p1": "travel_time"}
            )

            # Add times spent walking from the original point to the snapped points
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

        # Add walking distance column
        travel_times = self.estimate_walking_distance(travel_times)

        return travel_times
