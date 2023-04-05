#!/usr/bin/env python3


"""Wrap the entire DGL travel time matrix computation (read config, prepare
data, compile output)"""


import datetime
import functools

import r5py
import car_speed_annotator
import parking_times_calculator

from .base_travel_time_matrix_computer import BaseTravelTimeMatrixComputer
from .multitemporal_travel_time_matrix_computer_mixin import (
    MultiTemporalTravelTimeMatrixComputerMixin,
)


__all__ = ["CarTravelTimeMatrixComputer"]


class CarTravelTimeMatrixComputer(
    BaseTravelTimeMatrixComputer, MultiTemporalTravelTimeMatrixComputerMixin
):
    @functools.cached_property
    def parking_times(self):
        _parking_times_calculator = parking_times_calculator.ParkingTimesCalculator()
        parking_times = self.origins_destinations.copy()
        parking_times["parking_time"] = parking_times.geometry.apply(
            _parking_times_calculator.parking_time
        )
        parking_times = parking_times[["id", "parking_time"]].copy()
        return parking_times

    def run(self):
        travel_times = None
        original_osm_extract_file = self.osm_extract_file

        for timeslot_name, timeslot_time in self.DEPARTURE_TIMES.items():
            column_name = f"car_{timeslot_name[0]}"

            annotated_osm_extract_file = (
                original_osm_extract_file.parent
                / f"{self.osm_extract_file.stem}_{timeslot_name}.osm.pbf"
            )

            car_speed_annotator.CarSpeedAnnotator(timeslot_name).annotate(
                self.osm_extract_file,
                annotated_osm_extract_file,
            )
            self.osm_extract_file = annotated_osm_extract_file

            travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
                transport_network=self.transport_network,
                origins=self.origins_destinations,
                departure=datetime.datetime.combine(self.date, timeslot_time),
                transport_modes=[r5py.LegMode.CAR],
            )

            _travel_times = travel_time_matrix_computer.compute_travel_times()

            # fmt: off
            _travel_times = _travel_times.set_index("from_id")
            _travel_times["travel_time"] = _travel_times["travel_time"] + _travel_times.join(self.access_walking_times)["walking_time"]
            _travel_times = _travel_times.set_index("to_id")
            _travel_times["travel_time"] = _travel_times["travel_time"] + _travel_times.join(self.access_walking_times)["walking_time"]
            _travel_times["travel_time"] = _travel_times["travel_time"] + _travel_times.join(self.parking_times)["parking_time"]

            _travel_times = (
                _travel_times.set_index(["from_id", "to_id"])
                [["from_id", "to_id", "travel_time"]]
                .rename(columns={"travel_time": column_name})
            )
            # fmt: on

            if travel_times is None:
                travel_times = _travel_times
            else:
                travel_times = travel_times.join(_travel_times)

            annotated_osm_extract_file.unlink()
            self.osm_extract_file = original_osm_extract_file

        return travel_times
