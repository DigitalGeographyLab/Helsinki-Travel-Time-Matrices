#!/usr/bin/env python3


"""Save the results of a travel time matrix computation in many file formats."""


import geopandas
import pathlib
import tempfile
import threading
import zipfile


class BaseTravelTimeMatrixSaverThread(threading.Thread):
    def __init__(
        self,
        travel_times,
        origins_destinations,
        output_directory,
        output_name_prefix,
    ):
        """Save the results of a travel time matrix computation."""
        super().__init__()

        self.travel_times = travel_times.reset_index(names=["from_id", "to_id"])
        self.origins_destinations = origins_destinations.set_index("id")
        self.output_directory = pathlib.Path(output_directory)
        self.output_name_prefix = output_name_prefix

        self.output_directory.mkdir(parents=True, exist_ok=True)


class GiantCsvTravelTimeMatrixSaverThread(BaseTravelTimeMatrixSaverThread):
    def run(self):
        self.travel_times.to_csv(
            self.output_directory / "Helsinki_TravelTimeMatrix_2023.csv.zst",
            compression={
                "method": "zstd",
                "threads": -1,
                "level": 12,
                "write_checksum": True,
            },
            index=False,
        )


class CsvSplitByToIdTravelTimeMatrixSaverThread(BaseTravelTimeMatrixSaverThread):
    def run(self):
        with tempfile.TemporaryDirectory(dir=self.output_directory) as temp_directory:
            output_directory = (
                pathlib.Path(temp_directory) / f"{self.output_name_prefix}"
            )
            output_directory.mkdir()
            for to_id, group in self.travel_times.groupby("to_id"):
                group.to_csv(
                    output_directory
                    / f"{self.output_name_prefix}_travel_times_to_{to_id}.csv",
                    index=False,
                )

            ARCHIVE_NAME = (
                self.output_directory
                / f"{self.output_name_prefix}_travel_times.csv.zip"
            )
            try:
                ARCHIVE_NAME.unlink()
            except FileNotFoundError:
                pass

            archive = zipfile.ZipFile(
                ARCHIVE_NAME,
                mode="a",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )

            # archive.mkdir(f"{self.output_name_prefix}")  # Python>=3.11
            for csv_file in output_directory.glob("*.csv"):
                archive.write(
                    csv_file,
                    csv_file.relative_to(temp_directory),
                )
                csv_file.unlink()


class GpkgJoinedByToIdTravelTimeMatrixSaverThread(BaseTravelTimeMatrixSaverThread):
    def run(self):
        with tempfile.TemporaryDirectory(dir=self.output_directory) as output_directory:
            output_directory = pathlib.Path(output_directory)
            GPKG_FILE = (
                output_directory / f"{self.output_name_prefix}_travel_times.gpkg"
            )

            # fmt: off
            travel_times_with_to_geom = geopandas.GeoDataFrame(
                self.travel_times.set_index("to_id")
                .join(self.origins_destinations)
                .reset_index(names="to_id")
            ).rename({"geometry": "to_geometry"})
            # fmt: on
            travel_times_with_to_geom.to_file(GPKG_FILE)
            del travel_times_with_to_geom

            ARCHIVE_NAME = (
                self.output_directory
                / f"{self.output_name_prefix}_travel_times.gpkg.zip"
            )
            try:
                ARCHIVE_NAME.unlink()
            except FileNotFoundError:
                pass

            archive = zipfile.ZipFile(
                ARCHIVE_NAME,
                mode="a",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )

            archive.write(GPKG_FILE, GPKG_FILE.name)
            GPKG_FILE.unlink()


class ShapefileOfGridOnly(BaseTravelTimeMatrixSaverThread):
    def run(self):
        with tempfile.TemporaryDirectory(dir=self.output_directory) as output_directory:
            output_directory = pathlib.Path(output_directory)
            self.origins_destinations.to_file(
                output_directory / f"{self.output_name_prefix}_grid.shp"
            )

            ARCHIVE_NAME = (
                self.output_directory / f"{self.output_name_prefix}_grid.shp.zip"
            )
            try:
                ARCHIVE_NAME.unlink()
            except FileNotFoundError:
                pass

            archive = zipfile.ZipFile(
                ARCHIVE_NAME,
                mode="a",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )

            for shp_part_file in output_directory.glob("*"):
                archive.write(shp_part_file, shp_part_file.name)
                shp_part_file.unlink()


class GpkgOfGridOnly(BaseTravelTimeMatrixSaverThread):
    def run(self):
        with tempfile.TemporaryDirectory(dir=self.output_directory) as output_directory:
            output_directory = pathlib.Path(output_directory)
            GPKG_FILE = output_directory / f"{self.output_name_prefix}_grid.gpkg"
            self.origins_destinations.to_file(GPKG_FILE)

            ARCHIVE_NAME = (
                self.output_directory / f"{self.output_name_prefix}_grid.gpkg.zip"
            )
            try:
                ARCHIVE_NAME.unlink()
            except FileNotFoundError:
                pass

            archive = zipfile.ZipFile(
                ARCHIVE_NAME,
                mode="a",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )

            archive.write(GPKG_FILE, GPKG_FILE.name)
            GPKG_FILE.unlink()


class GiantParquetTravelTimeMatrixSaverThread(BaseTravelTimeMatrixSaverThread):
    def run(self):
        pass


class AspatialParquetTravelTimeMatrixSaverThread(BaseTravelTimeMatrixSaverThread):
    def run(self):
        pass


class TravelTimeMatrixOutputSaver:
    TTM_SAVER_THREADS = [
        GiantCsvTravelTimeMatrixSaverThread,
        CsvSplitByToIdTravelTimeMatrixSaverThread,
        GpkgJoinedByToIdTravelTimeMatrixSaverThread,
        ShapefileOfGridOnly,
        GpkgOfGridOnly,
        GiantParquetTravelTimeMatrixSaverThread,
        AspatialParquetTravelTimeMatrixSaverThread,
    ]

    def __init__(self, travel_time_data, origins_destinations):
        """Save data."""
        self.travel_time_data = travel_time_data
        self.origins_destinations = origins_destinations

    def save(self, output_directory, output_name_prefix):
        """Save data."""
        threads = []
        for ttm_saver_thread in self.TTM_SAVER_THREADS:
            t = ttm_saver_thread(
                self.travel_time_data,
                self.origins_destinations,
                output_directory,
                output_name_prefix,
            )
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
