#!/usr/bin/env python3


"""Define the urban zones of Syke’s YKR."""


import enum
import importlib.resources

import geopandas


__all__ = ["YkrVyöhyke", "ykr_vyöhykkeet"]


class YkrVyöhyke(enum.Enum):
    """Enumerate the YKR urban zone categories."""

    # compare: https://paikkatieto.ymparisto.fi/arcgis/rest/services/Liiteri/
    # Liiteri_YhdyskuntarakenteenVyohykkeet/MapServer/6
    KESKUSTAN_JALANKULKUVYÖHYKE = (1, "Keskustan jalankulkuvyöhyke")
    KESKUSTAN_REUNAVYÖHYKE = (2, "Keskustan reunavyöhyke")
    INTENSIIVINEN_JOUKKOLIIKENNEVYÖHYKE = (3, "Intensiivinen joukkoliikennevyöhyke")
    JOUKKOLIIKENNEVYÖHYKE = (4, "Joukkoliikennevyöhyke")
    AUTOVYÖHYKE = (5, "Autovyöhyke")
    ALAKESKUKSEN_JALANKULKUVYÖHYKE = (10, "Alakeskuksen jalankulkuvyöhyke")
    ALAKESKUKSEN_JALANKULKUVYÖHYKE_JOUKKOLIIKENNE = (
        11,
        "Alakeskuksen jalankulkuvyöhyke/ joukkoliikenne",
    )
    ALAKESKUKSEN_JALANKULKUVYÖHYKE_INTENSIIVINEN_JOUKKOLIIKENNE = (
        12,
        "Alakeskuksen jalankulkuvyöhyke/ intensiivinen joukkoliikenne",
    )
    KESKUSTAN_REUNAVYÖHYKE_JOUKKOLIIKENNE = (
        40,
        "Keskustan reunavyöhyke/ joukkoliikenne",
    )
    KESKUSTAN_REUNAVYÖHYKE_INTENSIIVINEN_JOUKKOLIIKENNE = (
        41,
        "Keskustan reunavyöhyke/ intensiivinen joukkoliikenne",
    )

    def __init__(self, value, name):
        self._value_ = value
        self._name_ = name

    @classmethod
    def _missing_(cls, value):
        for name in dir(cls):
            if cls[name].name == value or cls[name].value == value:
                return cls[name]
        return None


PACKAGE = __package__.split(".")[0]


ykr_vyöhykkeet = geopandas.read_file(
    importlib.resources.files(f"{PACKAGE}.data")
    / "yhdyskuntarakenteen_vyohykkeet_2021_EPSG3857.gpkg.zip"
)
