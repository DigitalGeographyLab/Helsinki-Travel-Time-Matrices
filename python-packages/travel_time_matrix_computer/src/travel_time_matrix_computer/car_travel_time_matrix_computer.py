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
    def add_parking_times(self, travel_times):
        """Add the time it takes to park the car at the destination."""
        COLUMNS = travel_times.columns
        # fmt: off
        travel_times = (
            travel_times
            .set_index("to_id")
            .join(self.parking_times)
            .reset_index(names="to_id")
        )
        travel_times.loc[
            travel_times.from_id != travel_times.to_id,
            "travel_time"
        ] += travel_times["parking_time"]
        # fmt: on
        travel_times = travel_times[COLUMNS]
        return travel_times

    @functools.cached_property
    def parking_times(self):
        _parking_times_calculator = parking_times_calculator.ParkingTimesCalculator()
        parking_times = self.origins_destinations.copy()
        parking_times["parking_time"] = parking_times.geometry.apply(
            _parking_times_calculator.parking_time
        )
        parking_times = parking_times.set_index("id")[["parking_time"]]
        return parking_times

    def run(self):
        travel_times = None
        # original_osm_extract_file = self.osm_extract_file

        for timeslot_name, timeslot_time in self.DEPARTURE_TIMES.items():
            column_suffix = timeslot_name[0]

            # annotated_osm_extract_file = (
            #     original_osm_extract_file.parent
            #     / f"{self.osm_extract_file.stem}_{timeslot_name}.osm.pbf"
            # )

            # car_speed_annotator.CarSpeedAnnotator(timeslot_name).annotate(
            #     self.osm_extract_file,
            #     annotated_osm_extract_file,
            # )
            # self.osm_extract_file = annotated_osm_extract_file

            if self.calculate_distances:
                detailed_itineraries_computer = r5py.DetailedItinerariesComputer(
                    transport_network=self.transport_network,
                    origins=self.origins_destinations,
                    departure=datetime.datetime.combine(self.date, timeslot_time),
                    departure_time_window=datetime.timedelta(hours=1),
                    transport_modes=[r5py.TransportMode.CAR],
                    max_time=self.MAX_TIME,
                )
                _travel_times = detailed_itineraries_computer.compute_travel_details()

                # Summarise the detailed itineraries:
                _travel_times = self.summarise_detailed_itineraries(_travel_times)

            else:
                travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
                    transport_network=self.transport_network,
                    origins=self.origins_destinations,
                    departure=datetime.datetime.combine(self.date, timeslot_time),
                    transport_modes=[r5py.TransportMode.CAR],
                    percentiles=[1],
                    max_time=self.MAX_TIME,
                )
                _travel_times = travel_time_matrix_computer.compute_travel_times()

                _travel_times = _travel_times.rename(columns={"travel_time_p1": "travel_time"})

            # Add times spent walking from the original point to the snapped points,
            # and for finding a parking spot
            _travel_times = self.add_access_times(_travel_times)
            _travel_times = self.add_parking_times(_travel_times)

            # fmt: off
            _travel_times = (
                _travel_times.set_index(["from_id", "to_id"])
                .rename(
                    columns={
                        "travel_time": f"car_{column_suffix}",
                        "distance": f"car_{column_suffix}_d",
                    }
                )
            )
            # fmt: on

            if travel_times is None:
                travel_times = _travel_times
            else:
                travel_times = travel_times.join(_travel_times)

            # annotated_osm_extract_file.unlink()
            # self.osm_extract_file = original_osm_extract_file

        return travel_times
