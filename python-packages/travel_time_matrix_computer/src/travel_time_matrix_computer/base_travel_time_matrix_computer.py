#!/usr/bin/env python3


"""Wrap the entire DGL travel time matrix computation (read config, prepare
data, compile output)"""


import pathlib
import subprocess
import tempfile
import warnings

import r5py


__all__ = ["BaseTravelTimeMatrixComputer"]


class BaseTravelTimeMatrixComputer:
    def __init__(
        self,
        osm_history_file,
        origins_destinations,
        date,
        gtfs_data_sets=[],
        cycling_speeds=None,
        extent=None,
    ):
        # constraints for other layers
        self.extent = extent
        self.date = date

        self.osm_history_file = osm_history_file
        pass

    @property
    def cycling_speeds(self):
        return self._cycling_speeds

    @cycling_speeds.setter
    def cycling_speeds(self, value):
        self._cycling_speeds = value

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        self._date = value

    @property
    def extent(self):
        return self._extent

    @extent.setter
    def extent(self, value):
        self._extent = value.to_crs("EPSG:4326")

    @property
    def gtfs_data_sets(self):
        return self._gtfs_data_sets

    @gtfs_data_sets.setter
    def gtfs_data_sets(self, value):
        self._gtfs_data_sets = value

    @property
    def origins_destinations(self):
        return self._origins_destinations

    @origins_destinations.setter
    def origins_destinations(self, value):
        value = value.to_crs("EPSG:4326")

        # cut to extent (if applicable):
        if self.extent is None:
            self.extent = value.geometry.unary_union
            warnings.warn(
                "No extent specified, using the extent of `origins_destinations`",
                RuntimeWarning,
            )
        else:
            value = value[value.geometry.within(self.extent.geometry)]

        # remember original for joining output back
        self.__origins_destinations = value.copy()

        # use centroid if not already points
        self._origins_destinations = value.copy()
        if self._origins_destinations.geom_type.unique().tolist() != ["Point"]:
            self._origins_destinations.geometry = (
                self._origins_destinations.geometry.centroid
            )

    @property
    def osm_extract_file(self):
        return self._osm_extract_file

    @property
    def osm_history_file(self):
        return self._osm_history_file

    @osm_history_file.setter
    def osm_history_file(self, osm_history_file):
        with tempfile.TemporaryDirectory() as temporary_directory:
            osm_snapshot_datetime = f"{self.date:%Y-%m-%dT00:00:00Z}"
            osm_snapshot_filename = (
                pathlib.Path(temporary_directory.name)
                / f"{osm_history_file.stem}_{osm_snapshot_datetime}.osm.pbf"
            )
            osm_extract_filename = (
                osm_history_file.parent
                / f"{osm_history_file.stem}_{osm_snapshot_datetime}_cut-to-extent.osm.pbf"
            )

            extent_polygon = pathlib.Path(temporary_directory.name) / "extent.geojson"
            self.extent.to_file(extent_polygon)

            subprocess.run(
                [
                    "/usr/bin/osmium",
                    "time-filter" f"{osm_history_file}",
                    f"{osm_snapshot_datetime}",
                    "--output",
                    f"{osm_snapshot_filename}",
                    "--output-format",
                    "osm.pbf",
                ]
            )
            subprocess.run(
                [
                    "/usr/bin/osmium",
                    "extract",
                    "--strategy",
                    "complete_ways",
                    "--polygon",
                    f"{extent_polygon}",
                    f"{osm_snapshot_filename}",
                    "--output",
                    f"{osm_extract_filename}",
                    "--output-format",
                    "osm.pbf",
                ]
            )

        self._osm_extract_file = osm_extract_filename

    @property
    def transport_network(self):
        transport_network = r5py.TransportNetwork(
            self.osm_extract_file,
            self.gtfs_data_sets,
        )
        return transport_network

    def run(self):
        raise NotImplementedError
