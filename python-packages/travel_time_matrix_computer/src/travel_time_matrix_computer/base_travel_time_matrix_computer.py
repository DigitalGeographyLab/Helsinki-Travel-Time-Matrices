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

        self.osm_history_file = osm_history_file
        self.origins_destinations = origins_destinations
        self.gtfs_data_sets = gtfs_data_sets
        self.cycling_speeds = cycling_speeds

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
        value = value.to_crs("EPSG:4326")

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
        self._origins_destinations = value.copy()
        if self._origins_destinations.geom_type.unique().tolist() != ["Point"]:
            original_crs = self._origins_destinations.crs
            equidistant_crs = self._good_enough_crs
            # fmt: off
            self._origins_destinations.geometry = (
                self._origins_destinations.geometry
                .to_crs(equidistant_crs)
                .centroid
                .to_crs(original_crs)
            )
            # fmt: on

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
                pathlib.Path(temporary_directory)
                / f"{osm_history_file.stem}_{osm_snapshot_datetime}.osm.pbf"
            )
            osm_extract_filename = (
                osm_history_file.parent
                / f"{osm_history_file.stem}_{osm_snapshot_datetime}_cut-to-extent.osm.pbf"
            )

            extent_polygon = pathlib.Path(temporary_directory) / "extent.geojson"
            # with open(extent_polygon, "w") as f:
            #     f.write(shapely.to_geojson(self.extent))
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
                ]
            )
            # fmt: on

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
