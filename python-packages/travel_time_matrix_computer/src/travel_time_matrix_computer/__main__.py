#!/usr/bin/env python3


"""Wrap the entire DGL travel time matrix computation (read config, prepare
data, compile output)"""


import argparse
import pathlib
import sys

import configargparse
import dateparser
import geopandas
import pandas
import shapely

from .travel_time_matrix_computer import TravelTimeMatrixComputer


__all__ = []


PACKAGE = __package__.split(".")[0]


def _get_argument_parser():
    try:
        argument_parser = configargparse.get_argument_parser(
            add_config_file_help=True,
            args_for_setting_config_path=["-c", "--config-file"],
            config_arg_help_message="Path to a config file, default: /data/ttm.yml",
            config_file_parser_class=configargparse.YAMLConfigFileParser,
            default_config_files=["/data/ttm.yml"],
            description=sys.modules[PACKAGE].__doc__,
            prog=PACKAGE,
        )
    except ValueError:
        argument_parser = configargparse.get_argument_parser()
    return argument_parser


def _parse_arguments():
    argument_parser = _get_argument_parser()

    argument_parser.add(
        "osm_history_file",
        help="OpenStreetMap history dump (planet or extract)",
        type=pathlib.Path,
    )

    argument_parser.add(
        "origins_destinations",
        help="Point data set of origins==destinations, in a format readable by fiona",
        type=_parse_origins_destinations,
    )

    argument_parser.add(
        "gtfs-data-set",
        help="Input GTFS data set(s), as a zipped file.",
        type=_parse_gtfs_files,
        nargs=argparse.ZERO_OR_MORE,
    )

    argument_parser.add(
        "date",
        help="For which date should the travel times be computed?",
        type=dateparser.parse,
    )

    argument_parser.add(
        "-c",
        "--cycling_speeds",
        help="A CSV data set of cycling speeds per OSM edge",
        type=pandas.read_csv,
        nargs=argparse.ZERO_OR_MORE,
    )

    argument_parser.add(
        "-e",
        "--extent",
        help=(
            "For which spatial extent should the travel time matrix be"
            "computed? \n"
            "xmin ymin xmax ymax\n"
            "Default: extent of origins/destination points"
        ),
        type=_parse_box,
    )

    return argument_parser.parse_known_args()


def _parse_box(box):
    try:
        box = [float(value) for value in box.split()]
    except ValueError:
        pass
    try:
        box = shapely.box(*box)
    except TypeError:
        box = None
    return box


def _parse_gtfs_files(gtfs_files):
    gtfs_files = [pathlib.Path(gtfs_file).resolve() for gtfs_file in gtfs_files]
    for gtfs_file in gtfs_files:
        assert gtfs_file.exists(), f"Could not read GTFS data set {gtfs_file}"
    return gtfs_files


def _parse_origins_destinations(origins_destinations):
    origins_destinations = geopandas.read_file(origins_destinations)
    assert origins_destinations.geom_type.unique() == [
        "Point"
    ], "origins_destination should be a point data set"
    return origins_destinations


def main():
    """
    Wrap the entire DGL travel time matrix computation.

    - read config
    - prepare data
    - compile output
    """

    arguments = _parse_arguments()
    print(arguments)

    travel_time_matrix_computer = TravelTimeMatrixComputer(**arguments)
    travel_time_matrix_computer.run()


if __name__ == "__main__":
    main()
