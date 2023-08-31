#!/usr/bin/env python3


"""Add custom tags to OSM extracts for DGL’s travel time matrices"""


__all__ = ["CarSpeedAnnotator"]


import pathlib

import osmium
import pyproj
import shapely

from .speed_coefficients import SPEED_COEFFICIENTS
from .ykr_vyohykkeet import YkrVyöhyke, ykr_vyöhykkeet


# used for `maxspeed=walk`, cf. https://wiki.openstreetmap.org/wiki/Key:maxspeed#Values
WALKING_SPEED = 10

# Speed people drive on German motorways where there is no speed limit
# This is the 75th percentile reported in:
# Holthaus, T., Goebels, C. and Leerkamp, B. (2020) Evaluation of driven
# speed on German motorways without speed limits – a new approach. Wupperal:
# Bergische Universität Wuppertal: Lehr- und Forschungsgebiet für
# Güterverkehrsplanung und Transportlogistik. Available at:
# https://www.gut.uni-wuppertal.de/fileadmin/bauing/leerkamp/Homepage_alt/Downloads/202003_Tempolimit/20200305-Evaluation_speed_FCD.pdf.
SPEED_DRIVEN_WHEN_NO_LIMIT = 130

# Used only if the `maxspeed` tag cannot be read:
DEFAULT_SPEED_LIMIT = 50
DEFAULT_TIME_OF_DAY = "average"
DEFAULT_URBAN_ZONE = YkrVyöhyke.AUTOVYÖHYKE

# To transform lat/lon geometries into a (kinda) area-true reference system
CRS_TRANSFORMER = pyproj.Transformer.from_crs(
    "EPSG:4326",
    "EPSG:3857",
    always_xy=True,
).transform


class CarSpeedAnnotator(osmium.SimpleHandler):
    def __init__(
        self,
        time_of_day: str,
        # https://github.com/conveyal/r5/blob/5dd418710df6f22d5a96e604f8ace9072e730cf8/src/main/java/com/conveyal/r5/labeling/SpeedLabeler.java#L67
        tag_name: str = "maxspeed:motorcar",
    ) -> None:
        """
        Create a CarSpeedAnnotator

        Arguments
        ---------
        time_of_day : str
            one of `average`, `midday`, `nighttime`, or `rush-hour`
        tag_name : str
            which tag to write into OSM ways, default: `maxspeed:motorcar`
        """
        super().__init__()

        if time_of_day not in ("average", "midday", "nighttime", "rush-hour"):
            raise ValueError(
                "`time_of_day` must be one of `average`, `midday`, `nighttime`, or `rush-hour`"
            )
        self._time_of_day = time_of_day

        self._tag_name = tag_name

    def annotate(
        self,
        input_file: pathlib.Path | str,
        output_file: pathlib.Path | str,
    ):
        """
        Add car speed tags to an OSM.pbf extract.

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
        self.apply_file(str(input_file), locations=True)
        del self._writer

    def node(self, node: osmium.osm.Node) -> None:
        """Process a node: always save to output file, verbatim."""
        self._writer.add_node(node)

    def relation(self, relation: osmium.osm.Relation) -> None:
        """Process a relation: always save to output file, verbatim."""
        self._writer.add_relation(relation)

    def way(self, way: osmium.osm.Way) -> None:
        """Process a way: set car speed, then save to output."""
        way = osmium.osm.mutable.Way(way)
        tags = dict(way.tags)

        if "highway" in tags:
            geometry = shapely.LineString(
                [(node.location.lon, node.location.lat) for node in way.nodes]
            )

            try:
                urban_zone = YkrVyöhyke(
                    self._largest_intersection(ykr_vyöhykkeet, geometry).vyoh
                )
            except AttributeError:
                urban_zone = DEFAULT_URBAN_ZONE

            speed_limit = self._get_speed_limit(tags)
            # clamp to known values:
            _speed_limit = min(
                SPEED_COEFFICIENTS[DEFAULT_URBAN_ZONE][DEFAULT_TIME_OF_DAY].keys(),
                key=lambda x: abs(x - speed_limit),
            )

            try:
                car_speed = (
                    speed_limit
                    * SPEED_COEFFICIENTS[urban_zone][self._time_of_day][_speed_limit]
                )
            except (
                KeyError
            ):  # always (?) speed_limit, others are clamped to known values
                car_speed = (
                    speed_limit
                    * SPEED_COEFFICIENTS[urban_zone][self._time_of_day][
                        DEFAULT_SPEED_LIMIT
                    ]
                )

            tags[self._tag_name] = f"{car_speed:0.2f}"
            way.tags = tags

        self._writer.add_way(way)

    def _get_speed_limit(self, tags: dict) -> int:
        # modelled after com.conveyal.r5.labeling.SpeedLabeler.getSpeedMS
        speed_limit = DEFAULT_SPEED_LIMIT

        if "maxspeed:motorcar" in tags:
            speed_limit = int(tags["maxspeed:motorcar"])
        elif "maxspeed:forward" in tags and "maxspeed:reverse" in tags:
            speed_limit = int(
                (int(tags["maxspeed:forward"]) + int(tags["maxspeed:reverse"])) / 2.0
            )
        elif "maxspeed:forward" in tags:
            speed_limit = int(tags["maxspeed:forward"])
        elif "maxspeed:reverse" in tags:
            speed_limit = int(tags["maxspeed:reverse"])
        elif "maxspeed:lanes" in tags:
            _speed_limits = [
                int(_speed_limit) for _speed_limit in tags["maxspeed:lanes"].split("|")
            ]
            speed_limit = int(sum(_speed_limits) / len(_speed_limits))
        elif "maxspeed" in tags:
            try:
                speed_limit = int(tags["maxspeed"])
            except ValueError:
                if tags["maxspeed"] == "walk":
                    speed_limit = WALKING_SPEED
                elif tags["maxspeed"] == "none":
                    speed_limit = SPEED_DRIVEN_WHEN_NO_LIMIT
                else:
                    pass  # use default value

        return speed_limit

    @staticmethod
    def _largest_intersection(zones, geometry):
        """
        Find the zone with which `geometry` has the largest intersection.

        Arguments
        =========
        zones : geopandas.GeoDataFrame
            zones to search for an intersection with geometry
        geometry : shapely.Geometry
            the geometry for which to search for a zone

        Returns
        =======
        geopandas.GeoSeries
            the row of zones that matched best
        """
        intersecting_zone = None
        geometry = shapely.ops.transform(CRS_TRANSFORMER, geometry).buffer(1)

        if len(intersecting_zones := zones[zones.geometry.intersects(geometry)]) == 1:
            intersecting_zone = intersecting_zones.squeeze()
        elif len(intersecting_zones) > 1:  # not zero
            intersecting_areas = intersecting_zones.geometry.intersection(geometry).area
            intersecting_zone = zones.loc[intersecting_areas.idxmax()]

        return intersecting_zone
