#!/usr/bin/env python3


"""Wrap the entire DGL travel time matrix computation (read config, prepare
data, compile output)"""


import datetime
import pathlib
import tempfile

import r5py
import car_speed_annotator

from .base_travel_time_matrix_computer import BaseTravelTimeMatrixComputer
from .multitemporal_travel_time_matrix_computer_mixin import (
    MultiTemporalTravelTimeMatrixComputerMixin,
)


__all__ = ["CarTravelTimeMatrixComputer"]


class CarTravelTimeMatrixComputer(
    BaseTravelTimeMatrixComputer, MultiTemporalTravelTimeMatrixComputerMixin
):
    def run(self):
        travel_times = None
        for timeslot_name, timeslot_time in self.DEPARTURE_TIMES.items():
            with tempfile.TemporaryDirectory() as temporary_directory:
                annotated_osm_extract_file = (
                    pathlib.Path(temporary_directory)
                    / f"{self.osm_extract_file.stem}_{timeslot_name}.osm.pbf"
                )

                car_speed_annotator.CarSpeedAnnotator(timeslot_name).annotate(
                    self.osm_extract_file,
                    annotated_osm_extract_file,
                )

            travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
                [
                    annotated_osm_extract_file,
                    self.gtfs_data_sets,
                ],
                origins=self.origins_destinations,
                departure=datetime.datetime.combine(self.date, timeslot_time),
                transport_modes=[r5py.LegMode.CAR],
            )
            _travel_times = travel_time_matrix_computer.compute_travel_times()[
                ["from_id", "to_id", "travel_time"]
            ].set_index(["from_id", "to_id"])
            _travel_times.rename(columns={"travel_time": f"car_{timeslot_name[0]}"})

            if travel_times is None:
                travel_times = _travel_times
            else:
                travel_times = travel_times.join(_travel_times)

        return travel_times
