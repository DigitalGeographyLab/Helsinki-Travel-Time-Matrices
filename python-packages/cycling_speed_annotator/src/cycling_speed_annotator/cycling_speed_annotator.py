#!/usr/bin/env python3


"""Add custom tags to OSM extracts for DGL’s travel time matrices"""


__all__ = ["CyclingSpeedAnnotator"]


import collections.abc
import functools
import pathlib

import osmium
import pandas


class CyclingSpeedAnnotator(osmium.SimpleHandler):
    def __init__(
        self,
        cycling_speeds: pandas.DataFrame,
        cycling_speeds_column_names: collections.abc.Iterable[str] = (
            "osm_id",
            "speed",
        ),
        base_speed: float | None = None,
        tag_name: str = "DGL:bicyclespeed",
    ) -> None:
        """
        Add the values

        """
        super().__init__()

        self._cycling_speeds = cycling_speeds.rename(
            columns={
                cycling_speeds_column_names[0]: "osm_id",
                cycling_speeds_column_names[1]: "speed",
            }
        )

        # input from Vuokko is m/s, we want to write km/h
        self._cycling_speeds.speed = self._cycling_speeds.speed * 3.6

        self._tag_name = tag_name

        if base_speed is not None:
            self._base_speed = base_speed
        else:
            self._base_speed = self._mean_speed

    def annotate(
        self,
        input_file: pathlib.Path | str,
        output_file: pathlib.Path | str,
    ):
        """
        Add cycling speed tags to an OSM.pbf extract.

        Arguments
        ---------
        input_file : pathlib.Path | str
            Which file to read from
        output_file : pathlib.Path | str
            To which file to write annotated data. Will be overwritten if exists.
        """
        input_file = pathlib.Path(input_file)
        output_file = pathlib.Path(output_file)
        try:
            output_file.unlink()
        except FileNotFoundError:
            pass

        self._writer = osmium.SimpleWriter(str(output_file))
        self.apply_file(str(input_file))
        del self._writer

    @functools.cached_property
    def _mean_speed(self) -> float:
        return float(self._cycling_speeds.speed.mean())

    def node(self, node: osmium.osm.Node) -> None:
        """Process a node: always save to output file, verbatim."""
        self._writer.add_node(node)

    def relation(self, relation: osmium.osm.Relation) -> None:
        """Process a relation: always save to output file, verbatim."""
        self._writer.add_relation(relation)

    def way(self, way: osmium.osm.Way) -> None:
        """Process a way: attach bicycle speed, then save to output."""
        way = osmium.osm.mutable.Way(way)
        tags = dict(way.tags)

        if way.id in self._cycling_speeds.osm_id.values:
            cycling_speed = (
                float(
                    self._cycling_speeds[
                        self._cycling_speeds.osm_id == way.id
                    ].speed.mean()
                )
                / self._mean_speed
                * self._base_speed
            )
        else:
            cycling_speed = self._base_speed

        tags[self._tag_name] = f"{cycling_speed:0.2f}"
        way.tags = tags

        self._writer.add_way(way)
