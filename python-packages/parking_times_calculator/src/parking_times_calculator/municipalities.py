#!/usr/bin/env python3


"""Provide a `geopandas.GeoDataFrame` of the municipalities in the Helsinki
metropolitan region."""


import importlib.resources

import geopandas


__all__ = ["municipalities"]


PACKAGE = __package__.split(".")[0]


municipalities = geopandas.read_file(
    importlib.resources.files(f"{PACKAGE}.data") / "municipalities_ESPG4326.gpkg.zip"
)
