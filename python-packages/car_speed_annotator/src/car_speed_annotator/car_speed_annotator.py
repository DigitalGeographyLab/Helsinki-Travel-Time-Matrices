#!/usr/bin/env python3


"""Add custom tags to OSM extracts for DGL’s travel time matrices"""


__all__ = ["CarSpeedAnnotator"]


import pathlib

import osmium


# Actually driven speeds as a fraction of the speed limit

# These data are the results of Eero Perola’s MSc thesis,
# in which he used TomTom floating car data to compare speed
# limit and measured speeds
# TODO: Add link to helda, once the thesis is published

# Times of the day, as used below, refer to floating car
# data averaged over the following time windows:
#   - average:      5:00-6:00, 9:00-10:00, 15:00-16:00,
#                   17:00-18:00, 21:00-22:00
#   - midday:       10:00-15:00
#   - nighttime:     0:00-05:00
#   - rush-hour:    7:00-9:00

# The speed limits are in km/h, and the road classes refer
# to the Digiroad classification for Finland

# The first group are by time of day and by speed limit
SPEED_COEFFICIENTS_BY_TIME_OF_DAY_AND_SPEED_LIMIT = {
    "average": {
        20: 0.7125,
        30: 0.82,
        40: 0.85,
        50: 0.831,
        60: 0.94,
        70: 0.97,
        80: 0.98625,
        100: 0.967,
        120: 0.856666667,
    },
    "midday": {
        20: 0.665,
        30: 0.813333333,
        40: 0.8575,
        50: 0.836,
        60: 0.948333333,
        70: 0.978571429,
        80: 0.993125,
        100: 0.971,
        120: 0.865833333,
    },
    "nighttime": {
        20: 0.885,
        30: 0.893333333,
        40: 0.93,
        50: 0.894,
        60: 0.963333333,
        70: 0.985714286,
        80: 0.99875,
        100: 0.969,
        120: 0.856666667,
    },
    "rush-hour": {
        20: 0.835,
        30: 0.81,
        40: 0.845,
        50: 0.822,
        60: 0.938333333,
        70: 0.974285714,
        80: 0.9875,
        100: 0.965,
        120: 0.850416667,
    },
}

# The second group are speed coefficients by time of day and road class
SPEED_COEFFICIENTS_BY_TIME_OF_DAY_AND_ROAD_CLASS = {
    "average": {1: 0.927, 2: 0.965714286, 3: 0.878, 4: 0.853, 5: 0.7},
    "midday": {1: 0.937, 2: 0.975, 3: 0.886, 4: 0.857, 5: 0.692},
    "nighttime": {1: 0.97, 2: 0.985, 3: 0.93375, 4: 0.913, 5: 0.753},
    "rush-hour": {1: 0.93, 2: 0.97, 3: 0.873, 4: 0.845, 5: 0.712},
}


class CarSpeedAnnotator(osmium.SimpleHandler):
    def __init__(
        self,
        time_of_day: str,
        by: str = "speed_limit",
        # https://github.com/conveyal/r5/blob/5dd418710df6f22d5a96e604f8ace9072e730cf8/src/main/java/com/conveyal/r5/labeling/SpeedLabeler.java#L67
        tag_name: str = "maxspeed:motorcar",
    ) -> None:
        """
        Create a CarSpeedAnnotator

        Arguments
        ---------
        time_of_day : str
            one of `average`, `midday`, `nighttime`, or `rush-hour`
        by : str
            use values categorised by the Digiroad road class, or the speed limit,
            one of `road_class` or `speed_limit` (default)
        tag_name : str
            which tag to write into OSM ways, default: `maxspeed:motorcar`
        """
        super().__init__()

        if time_of_day not in ("average", "midday", "nighttime", "rush-hour"):
            raise ValueError(
                "`time_of_day` must be one of `average`, `midday`, `nighttime`, or `rush-hour`"
            )
        self._time_of_day = time_of_day

        if by not in ("road_class", "speed_limit"):
            raise ValueError("`by` must be one of `road_class` or `speed_limit`")
        self._by = by

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
        self.apply_file(str(input_file))
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

        speed_limit = self._get_speed_limit(tags)

        if self._by == "road_class":
            road_class = self._get_road_class(tags)
            car_speed = (
                speed_limit
                * SPEED_COEFFICIENTS_BY_TIME_OF_DAY_AND_ROAD_CLASS[self._time_of_day][
                    road_class
                ]
            )
        else:
            # clamp it to known values
            _speed_limit = min(
                SPEED_COEFFICIENTS_BY_TIME_OF_DAY_AND_SPEED_LIMIT["average"].keys(),
                key=lambda x: abs(x - speed_limit),
            )
            car_speed = (
                speed_limit
                * SPEED_COEFFICIENTS_BY_TIME_OF_DAY_AND_SPEED_LIMIT[self._time_of_day][
                    _speed_limit
                ]
            )

        tags[self._tag_name] = f"{car_speed:0.2f}"
        way.tags = tags

        self._writer.add_way(way)

    def _get_road_class(self, tags: dict) -> int:
        # modelled after com.conveyal.r5.labeling.StreetClass
        # and https://github.com/DigitalGeographyLab/r5/blob/
        # fbb1ccaf61294633b100c8a141dc91a253fe6643/src/main/
        # java/com/conveyal/r5/streets/JaakkonenStreetClass.java

        road_class = 5  # default = lowest
        try:
            highway = tags["highway"]

            if highway == "motorway":
                road_class = 1
            if highway == "primary":
                road_class = 2
            elif highway == "secondary":
                road_class = 3
            elif highway == "tertiary":
                road_class = 4
        except KeyError:
            pass
        return road_class

    def _get_speed_limit(self, tags: dict) -> int:
        # modelled after com.conveyal.r5.labeling.SpeedLabeler.getSpeedMS
        speed_limit = 40  # default value

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
            speed_limit = int(tags["maxspeed"])

        return speed_limit
