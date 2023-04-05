#!/usr/bin/env python3


"""Wrap the entire DGL travel time matrix computation (read config, prepare
data, compile output)"""


import datetime
import pathlib
import subprocess
import tempfile
import warnings

import geopandas
import pyproj
import r5py


__all__ = ["BaseTravelTimeMatrixComputer"]


class BaseTravelTimeMatrixComputer:
    DEFAULT_TIME_OF_DAY = datetime.time(hour=12)

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

        self.cycling_speeds = cycling_speeds
        self.gtfs_data_sets = gtfs_data_sets
        self.osm_history_file = osm_history_file
        self.origins_destinations = origins_destinations

    def add_access_times(self, travel_times):
        """Add the times to walk from/to origin/destination to/from a snapped point."""
        travel_times = travel_times.copy()
        for which_end in ("from_id", "to_id"):
            # fmt: off
            travel_times = (
                travel_times
                .set_index(which_end)
                .join(self.access_walking_times)
                .reset_index(names=which_end)
            )
            travel_times.loc[
                travel_times["travel_time"] != 0,  # origin == destination
                "travel_time",
            ] += travel_times["walking_time"]
            # fmt: on
            travel_times = travel_times[["from_id", "to_id", "travel_time"]]
        return travel_times

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
        self._extent = value

    @property
    def _good_enough_crs(self):
        """
        Find the most appropriate UTM reference system for the current extent.

        (We need this to be able to calculate lengths in meters.
        Results don’t have to be perfect, so also the neighbouring UTM grid will do.)

        Returns
        -------
        pyproj.CRS
            Best-fitting UTM reference system.
        """
        try:
            crsinfo = pyproj.database.query_utm_crs_info(
                datum_name="WGS 84",
                area_of_interest=pyproj.aoi.AreaOfInterest(*self.extent.bounds),
            )[0]
            crs = pyproj.CRS.from_authority(crsinfo.auth_name, crsinfo.code)
        except IndexError:
            # no UTM grid found for the location?! are we on the moon?
            crs = pyproj.CRS.from_epsg(3857)  # well, web mercator will have to do
        return crs

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
        WORKING_CRS = "EPSG:4326"
        EQUIDISTANT_CRS = self._good_enough_crs

        value = value.to_crs(WORKING_CRS)

        # cut to extent (if applicable):
        if self.extent is None:
            self.extent = value.geometry.unary_union
            warnings.warn(
                "No extent specified, using the extent of `origins_destinations`",
                RuntimeWarning,
            )
        else:
            value = value[value.geometry.within(self.extent)]

        # remember original for joining output back
        self.__origins_destinations = value.copy()

        # use centroid if not already points
        origins_destinations = value.copy()
        if origins_destinations.geom_type.unique().tolist() != ["Point"]:
            # fmt: off
            origins_destinations.geometry = (
                origins_destinations.geometry
                .to_crs(EQUIDISTANT_CRS)
                .centroid
                .to_crs(WORKING_CRS)
            )
            # fmt: on

        # snap to network, remember walking time (constant speed)
        # from original point to snapped point
        WALKING_SPEED = 3.6  # km/h
        # fmt: off
        origins_destinations["snapped_geometry"] = (
            self.transport_network.snap_to_network(origins_destinations["geometry"])
        )
        origins_destinations["snapped_distance"] = (  # meters
            origins_destinations.geometry.to_crs(EQUIDISTANT_CRS)
            .distance(
                origins_destinations.snapped_geometry.to_crs(EQUIDISTANT_CRS)
            )
        )
        origins_destinations["walking_time"] = (  # minutes
            origins_destinations["snapped_distance"]
            / (WALKING_SPEED * 1000 / 60.0)
        ).round(2)

        self.access_walking_times = (
            origins_destinations
            [["id", "walking_time"]]
            .copy()
            .set_index("id")
        )
        self._origins_destinations = (
            origins_destinations
            [["id", "geometry"]]
            .copy()
        )
        # fmt: on

    @property
    def osm_history_file(self):
        return self._osm_history_file

    @osm_history_file.setter
    def osm_history_file(self, osm_history_file):
        with tempfile.TemporaryDirectory() as temporary_directory:
            osm_snapshot_datetime = f"{self.date:%Y-%m-%dT00:00:00Z}"
            osm_snapshot_filename = (
                pathlib.Path(temporary_directory)
                / f"{osm_history_file.stem}_{osm_snapshot_datetime}.osm.pbf"
            )
            osm_extract_filename = (
                osm_history_file.parent
                / f"{osm_history_file.stem}_{osm_snapshot_datetime}_cut-to-extent.osm.pbf"
            )

            extent_polygon = pathlib.Path(temporary_directory) / "extent.geojson"
            geopandas.GeoDataFrame({"geometry": [self.extent]}).to_file(extent_polygon)

            # fmt: off
            subprocess.run(
                [
                    "/usr/bin/osmium",
                    "time-filter",
                    f"{osm_history_file}",
                    f"{osm_snapshot_datetime}",
                    "--output", f"{osm_snapshot_filename}",
                    "--output-format", "osm.pbf",
                    "--overwrite",
                    "--no-progress",
                ]
            )
            subprocess.run(
                [
                    "/usr/bin/osmium",
                    "extract",
                    "--strategy", "complete_ways",
                    "--polygon", f"{extent_polygon}",
                    f"{osm_snapshot_filename}",
                    "--output", f"{osm_extract_filename}",
                    "--output-format", "osm.pbf",
                    "--overwrite",
                    "--no-progress",
                ]
            )
            # fmt: on

        self.osm_extract_file = osm_extract_filename

    @property
    def transport_network(self):
        transport_network = r5py.TransportNetwork(
            self.osm_extract_file,
            self.gtfs_data_sets,
        )
        return transport_network

    def run(self):
        raise NotImplementedError
