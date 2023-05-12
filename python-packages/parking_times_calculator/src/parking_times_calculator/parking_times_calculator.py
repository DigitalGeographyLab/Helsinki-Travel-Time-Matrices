#!/usr/bin/env python3


"""Calculate parking times depending on destination location within Finland"""


__all__ = ["ParkingTimesCalculator"]


import sys

import shapely

from .municipalities import municipalities
from .ykr_vyohykkeet import YkrVyöhyke, ykr_vyöhykkeet


# Median parking times PLUS median walking times,
# by municipality and YKR zone, in minutes,
#
# according to
#
# Vesanen, S. (2020) Parking private cars and spatial accessibility in Helsinki
#   capital region – Parking time as a part of the total travel time. MSc thesis.
#   University of Helsinki. http://urn.fi/URN:NBN:fi:hulib-202010304366

PARKING_TIMES = {
    "Espoo": {
        YkrVyöhyke.ALAKESKUKSEN_JALANKULKUVYÖHYKE: 3 + 3,
        YkrVyöhyke.INTENSIIVINEN_JOUKKOLIIKENNEVYÖHYKE: 2 + 3,
        YkrVyöhyke.JOUKKOLIIKENNEVYÖHYKE: 1 + 2,
        YkrVyöhyke.AUTOVYÖHYKE: 1 + 2,
        None: 2 + 3,
    },
    "Helsinki": {
        YkrVyöhyke.KESKUSTAN_JALANKULKUVYÖHYKE: 5 + 5,
        YkrVyöhyke.KESKUSTAN_REUNAVYÖHYKE: 4 + 4,
        YkrVyöhyke.ALAKESKUKSEN_JALANKULKUVYÖHYKE: 3 + 3,
        YkrVyöhyke.INTENSIIVINEN_JOUKKOLIIKENNEVYÖHYKE: 2 + 2,
        YkrVyöhyke.JOUKKOLIIKENNEVYÖHYKE: 1 + 2,
        YkrVyöhyke.AUTOVYÖHYKE: 1 + 1,
        None: 2 + 3,
    },
    "Kauniainen": {
        YkrVyöhyke.JOUKKOLIIKENNEVYÖHYKE: 2 + 2,
    },
    "Vantaa": {
        YkrVyöhyke.ALAKESKUKSEN_JALANKULKUVYÖHYKE: 3 + 3,
        YkrVyöhyke.INTENSIIVINEN_JOUKKOLIIKENNEVYÖHYKE: 2 + 2,
        YkrVyöhyke.JOUKKOLIIKENNEVYÖHYKE: 2 + 2,
        YkrVyöhyke.AUTOVYÖHYKE: 1 + 2,
        None: 2 + 3,
    },
}

_parking_times = [
    parking_time
    for parking_times_per_city in PARKING_TIMES.values()
    for parking_time in parking_times_per_city.values()
]

MEAN_PARKING_TIME = int(sum(_parking_times) / len(_parking_times))

del _parking_times


class ParkingTimesCalculator:
    @staticmethod
    def parking_time(destination: shapely.Point, verbose: bool = False) -> int:
        """
        Find the time needed for finding a parking spot.

        Arguments
        ---------
        destination : shapely.Point
            Around where to find a parking spot. Currently, data covers the
            Helsinki metropolitan area (Helsinki, Espoo, Kauniainen, Vantaa).
        verbose : bool
            Print some reasoning for the resulting parking time (which
            municipality, which urban zone)
        """
        try:
            municipality = municipalities[
                municipalities.geometry.contains(destination)
            ].name.values[0]
        except IndexError:
            municipality = None

        try:
            urban_zone = YkrVyöhyke(
                ykr_vyöhykkeet[
                    ykr_vyöhykkeet.geometry.contains(destination)
                ].vyoh.values[0]
            )
        except (IndexError, KeyError):
            urban_zone = None

        try:
            parking_time = PARKING_TIMES[municipality][urban_zone]
        except KeyError:
            parking_time = MEAN_PARKING_TIME

        if verbose:
            print(
                f"municipality: {municipality}, "
                f"urban zone: {urban_zone} "
                f"-> parking time: {parking_time}",
                file=sys.stderr,
            )

        return parking_time
