#!/usr/bin/env python3


"""Wrap the entire DGL travel time matrix computation (read config, prepare
data, compile output)"""


import datetime
import pathlib
import tempfile

import r5py
import cycling_speed_annotator

from .base_travel_time_matrix_computer import BaseTravelTimeMatrixComputer


__all__ = ["CyclingTravelTimeMatrixComputer"]


class CyclingTravelTimeMatrixComputer(BaseTravelTimeMatrixComputer):
    # column name -> cycling (base!) speed in km/h
    # these are default values, and are adjusted in __init__()
    # according to the cycling speeds read from `self.cycling_speeds`
    CYCLING_SPEEDS = {
        "bike_fst": 18.09,
        "bike_avg": 14.92,
        "bike_slo": 11.75,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.cycling_speeds:
            c = cycling_speed_annotator.CyclingSpeedAnnotator(self.cycling_speeds)
            self.CYCLING_SPEEDS["bike_fst"] = c._mean_speed
            self.CYCLING_SPEEDS["bike_avg"] = (
                self.CYCLING_SPEEDS["bike_slo"] + self.CYCLING_SPEEDS["bike_fst"]
            ) / 2.0

    def run(self):
        travel_times = None
        for column_name, cycling_speed in self.CYCLING_SPEEDS.items():
            with tempfile.TemporaryDirectory() as temporary_directory:
                annotated_osm_extract_file = (
                    pathlib.Path(temporary_directory)
                    / f"{self.osm_extract_file.stem}_{column_name}.osm.pbf"
                )

                cycling_speed_annotator.CyclingSpeedAnnotator(
                    self.cycling_speeds,
                    base_speed=cycling_speed,
                ).annotate(
                    self.osm_extract_file,
                    annotated_osm_extract_file,
                )

            travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
                [
                    annotated_osm_extract_file,
                    self.gtfs_data_sets,
                ],
                origins=self.origins_destinations,
                departure=datetime.datetime.combine(
                    self.date, self.DEFAULT_TIME_OF_DAY
                ),
                transport_modes=[r5py.LegMode.BICYCLE],
            )
            _travel_times = travel_time_matrix_computer.compute_travel_times()[
                ["from_id", "to_id", "travel_time"]
            ].set_index(["from_id", "to_id"])
            _travel_times.rename(columns={"travel_time": column_name})

            if travel_times is None:
                travel_times = _travel_times
            else:
                travel_times = travel_times.join(_travel_times)

        return travel_times
