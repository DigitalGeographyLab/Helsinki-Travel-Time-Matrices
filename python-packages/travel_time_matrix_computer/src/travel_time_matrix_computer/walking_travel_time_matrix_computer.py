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

    def run(self):
        travel_times = None
        for column_name, walking_speed in self.WALKING_SPEEDS.items():
            if self.calculate_distances:
                detailed_itineraries_computer = r5py.DetailedItinerariesComputer(
                    transport_network=self.transport_network,
                    origins=self.origins_destinations,
                    departure=datetime.datetime.combine(
                        self.date, self.DEFAULT_TIME_OF_DAY
                    ),
                    transport_modes=[r5py.TransportMode.WALK],
                    departure_time_window=datetime.timedelta(hours=1),
                    speed_walking=walking_speed,
                    max_time=self.MAX_TIME,
                )
                _travel_times = detailed_itineraries_computer.compute_travel_details()

                # Summarise the detailed itineraries:
                _travel_times = self.summarise_detailed_itineraries(_travel_times)

            else:
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
