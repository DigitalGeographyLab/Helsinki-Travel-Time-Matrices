#!/usr/bin/env python3


"""Wrap the entire DGL travel time matrix computation (read config, prepare
data, compile output)"""


import datetime
import pathlib

import dateparser
import geopandas
import pandas
import pyaml
import shapely

from .travel_time_matrix_computer import TravelTimeMatrixComputer
from .travel_time_matrix_output_saver import TravelTimeMatrixOutputSaver


__all__ = []


PACKAGE = __package__.split(".")[0]
DATA_DIRECTORY = pathlib.Path("/data")
CONFIG_FILE = DATA_DIRECTORY / f"{PACKAGE}.yml"


def _parse_date(date):
    if isinstance(date, str):
        date = dateparser.parse(date)
    if isinstance(date, datetime.datetime):
        date = date.date()

    assert isinstance(date, datetime.date), f"Could not parse date: {date}"

    return date


def _parse_extent(extent):
    if extent is not None:
        try:
            # try to convert a string of four values into a list of floats
            box = [float(value) for value in extent.split()]
        except ValueError:
            box = extent  # maybe it’s already an iterable -> let’s try
        try:
            extent = shapely.box(*box)
        except TypeError:
            # or a WKT string (which we also support)
            try:
                extent = shapely.from_wkt(extent)
                if not isinstance(extent, (shapely.MultiPolygon, shapely.Polygon)):
                    extent = None
            except shapely.errors.ShapelyError:
                extent = None
    return extent


def _parse_gtfs_files(gtfs_files):
    gtfs_files = [_parse_path(gtfs_file) for gtfs_file in gtfs_files]
    for gtfs_file in gtfs_files:
        assert gtfs_file.exists(), f"Could not read GTFS data set {gtfs_file}"
    return gtfs_files


def _parse_origins_destinations(origins_destinations):
    origins_destinations = geopandas.read_file(origins_destinations)
    assert (
        "id" in origins_destinations.columns
    ), "origins-destinations must have an `id` column"
    assert isinstance(
        origins_destinations.geometry, geopandas.GeoSeries
    ), "origins-destinations must have a `geometry` column"

    return origins_destinations


def _parse_path(path):
    path = pathlib.Path(path)
    if not path.is_absolute():
        path = DATA_DIRECTORY / path
    path = path.resolve()
    assert path.exists(), "Cannot find f{path}"
    return path


def read_config(config_file=CONFIG_FILE):
    with open(config_file) as f:
        config = pyaml.yaml.safe_load(f.read())

    # mandatory
    config["osm_history_file"] = _parse_path(config["osm_history_file"])
    config["origins_destinations"] = _parse_origins_destinations(
        _parse_path(config["origins_destinations"])
    )
    config["date"] = _parse_date(config["date"])
    config["output_prefix"] = str(config["output_prefix"])

    # optional
    try:
        config["calculate_distances"] = bool(config["calculate_distances"])
    except KeyError:
        config["calculate_distances"] = False
    try:
        config["cycling_speeds"] = pandas.read_csv(
            _parse_path(config["cycling_speeds"])
        )
    except KeyError:
        config["cycling_speeds"] = pandas.DataFrame({"osm_id": [], "speed": []})
    try:
        config["extent"] = _parse_extent(config["extent"])
    except KeyError:
        config["extent"] = None
    try:
        config["gtfs_data_sets"] = _parse_gtfs_files(config["gtfs_data_sets"])
    except KeyError:
        config["gtfs_data_sets"] = []

    return config


def main():
    """
    Wrap the entire DGL travel time matrix computation.

    - read config
    - prepare data
    - compile output
    """

    config = read_config()

    travel_time_matrix_computer = TravelTimeMatrixComputer(**config)
    travel_times = travel_time_matrix_computer.run()

    TravelTimeMatrixOutputSaver(
        travel_times,
        config["origins_destinations"],
    ).save(
        output_directory=(DATA_DIRECTORY / "output"),
        output_name_prefix=config["output_prefix"],
    )

    travel_times.to_csv(DATA_DIRECTORY / "travel_times.csv.zst")


if __name__ == "__main__":
    main()
