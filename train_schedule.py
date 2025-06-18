# train_schedule.py
import csv
import collections
from typing import List, Dict, Set
# --- UBAH IMPORT ---
from data_models import Train, Region

# --- TAMBAHKAN SET STASIUN UNTUK WILAYAH YOGYA-SOLO ---
# Daftar ini digunakan untuk mengidentifikasi rute kereta
YOGYA_SOLO_STATIONS = {
    "palur", "solo jebres", "solo balapan", "purwosari", "gawok",
    "delanggu", "ceper", "klaten", "srowot", "brambanan",
    "maguwo", "lempuyangan", "yogyakarta", "kutoarjo"
}

def _determine_region(route: List[str]) -> Region:
    """Menentukan wilayah operasional kereta berdasarkan rutenya."""
    # Jika ada stasiun dari rute yang ada di dalam set stasiun Yogya-Solo
    if any(station.lower() in YOGYA_SOLO_STATIONS for station in route):
        return Region.YOGYA_SOLO
    return Region.JABODETABEK

class TrainSchedule:
    """
    Memuat dan mengelola data jadwal kereta dari file CSV.
    """
    def __init__(self, csv_file: str):
        """Menginisialisasi dan memuat jadwal."""
        self.trains: List[Train] = self._load_from_csv(csv_file)
        self.station_to_trains_map: Dict[str, List[Train]] = self._build_station_to_trains_map()
        # --- TAMBAHKAN DATA TERSTRUKTUR BERDASARKAN WILAYAH ---
        self.trains_by_region: Dict[Region, List[Train]] = self._group_trains_by_region()
        self.stations_by_region: Dict[Region, Set[str]] = self._get_stations_by_region()

    def _load_from_csv(self, filename: str) -> List[Train]:
        """Memuat data kereta dari file CSV yang ditentukan."""
        schedule = []
        with open(filename, mode='r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            next(reader)  # Lewati baris header
            for row in reader:
                train_id, name, route_str, times_str = row
                route = [r.strip() for r in route_str.strip('\"').split(',')]
                
                departure_times = {}
                time_parts = times_str.strip('\"').split(',')
                for part in time_parts:
                    try:
                        station, h, m = part.split(':')
                        departure_times[station.strip()] = f"{h}:{m}"
                    except ValueError:
                        continue
                
                # --- TAMBAHKAN LOGIKA PENENTUAN WILAYAH ---
                region = _determine_region(route)
                schedule.append(Train(train_id, name, route, departure_times, region))
        return schedule

    def _build_station_to_trains_map(self) -> Dict[str, List[Train]]:
        """Membangun map untuk pencarian kereta berdasarkan stasiun yang efisien."""
        station_map = collections.defaultdict(list)
        for train in self.trains:
            for station in train.route:
                station_map[station].append(train)
        return station_map

    # --- TAMBAHKAN METODE-METODE BARU INI ---
    def _group_trains_by_region(self) -> Dict[Region, List[Train]]:
        """Mengelompokkan semua kereta berdasarkan wilayah operasionalnya."""
        grouped = collections.defaultdict(list)
        for train in self.trains:
            grouped[train.region].append(train)
        return grouped

    def _get_stations_by_region(self) -> Dict[Region, Set[str]]:
        """Mendapatkan semua nama stasiun unik untuk setiap wilayah."""
        regional_stations = collections.defaultdict(set)
        for region, trains in self.trains_by_region.items():
            for train in trains:
                for station in train.route:
                    regional_stations[region].add(station)
        return regional_stations

    def get_trains_for_station(self, station: str, region: Region) -> List[Train]:
        """Mendapatkan semua kereta untuk stasiun tertentu dalam wilayah spesifik."""
        all_trains = self.station_to_trains_map.get(station, [])
        return [train for train in all_trains if train.region == region]

    def get_available_stations_by_region(self, region: Region) -> List[str]:
        """Mengembalikan daftar nama stasiun yang tersedia untuk suatu wilayah, diurutkan."""
        return sorted(list(self.stations_by_region.get(region, set())))

    def get_all_stations(self) -> Set[str]:
        """Mengembalikan satu set semua nama stasiun unik."""
        return set(self.station_to_trains_map.keys())