#!/usr/bin/env python3


"""Save the results of a travel time matrix computation in many file formats."""


import pathlib
import threading


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

        self.travel_times = travel_times
        self.origins_destinations = origins_destinations
        self.output_directory = pathlib.Path(output_directory)
        self.output_name_prefix = output_name_prefix

        self.output_directory.mkdir(parents=True, exist_ok=True)


class GiantCsvTravelTimeMatrixSaverThread(BaseTravelTimeMatrixSaverThread):
    def run(self):
        self.travel_times.to_csv(
            self.output_directory / f"{self.output_name_prefix}_travel_times.csv.zst"
        )


class CsvSplitByToIdTravelTimeMatrixSaverThread(BaseTravelTimeMatrixSaverThread):
    def run(self):
        pass


class GpkgJoinedByToIdTravelTimeMatrixSaverThread(BaseTravelTimeMatrixSaverThread):
    def run(self):
        pass


class ShapefileOfGridOnly(BaseTravelTimeMatrixSaverThread):
    def run(self):
        pass


class GpkgOfGridOnly(BaseTravelTimeMatrixSaverThread):
    def run(self):
        pass


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
