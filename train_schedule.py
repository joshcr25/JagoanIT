import csv
import collections
from typing import List, Dict, Set
from data_models import Train

class TrainSchedule:
    """
    Loads and manages train schedule data from a CSV file.
    """
    def __init__(self, csv_file: str):
        """Initializes and loads the schedule."""
        self.trains: List[Train] = self._load_from_csv(csv_file)
        self.station_to_trains_map: Dict[str, List[Train]] = self._build_station_to_trains_map()

    def _load_from_csv(self, filename: str) -> List[Train]:
        """Loads train data from the specified CSV file."""
        schedule = []
        with open(filename, mode='r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            next(reader)  # Skip header row
            for row in reader:
                train_id, name, route_str, times_str = row
                
                # Split routes and times, handling potential quotes
                route = [r.strip() for r in route_str.strip('"').split(',')]
                
                departure_times = {}
                # The time format is station:HH:MM, split by ','
                time_parts = times_str.strip('"').split(',')
                for part in time_parts:
                    try:
                        station, h, m = part.split(':')
                        departure_times[station.strip()] = f"{h}:{m}"
                    except ValueError:
                        # Handle potential malformed time strings
                        continue
                        
                schedule.append(Train(train_id, name, route, departure_times))
        return schedule

    def _build_station_to_trains_map(self) -> Dict[str, List[Train]]:
        """Builds a map for efficient lookup of trains by station."""
        station_map = collections.defaultdict(list)
        for train in self.trains:
            for station in train.route:
                station_map[station].append(train)
        return station_map

    def get_trains(self) -> List[Train]:
        """Returns the list of all trains."""
        return self.trains

    def get_trains_for_station(self, station: str) -> List[Train]:
        """Gets all trains that pass through a given station."""
        return self.station_to_trains_map.get(station, [])

    def get_all_stations(self) -> Set[str]:
        """Returns a set of all unique station names."""
        return set(self.station_to_trains_map.keys())