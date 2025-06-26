# Beberapa instans (tapi gk semua) yang dibantu Github Copilot dan Google Gemini
# -- Awal Kutipan
import csv
import collections
from typing import List, Dict, Set
import math
# --- UBAH IMPORT ---
from data_models import Train, Region

# Daftar ini digunakan untuk mengidentifikasi rute kereta
YOGYA_SOLO_STATIONS = {
    "palur", "solo jebres", "solo balapan", "purwosari", "gawok",
    "delanggu", "ceper", "klaten", "srowot", "brambanan",
    "maguwo", "lempuyangan", "yogyakarta", "wates", "wojo", "jenar", "kutoarjo"
}
RANGKASBITUNG_MERAK_STATIONS = {
    "merak", "krenceng", "cilegon", "tonjong baru", "karangantu", "serang", "walantaka", "cikeusal", "catang", "jambu baru", "rangkasbitung"
}

def _determine_region(route: List[str]) -> Region:
    """Menentukan wilayah operasional kereta berdasarkan rutenya."""
    # Jika ada stasiun dari rute yang ada di dalam set stasiun Yogya-Solo
    if any(station.lower() in YOGYA_SOLO_STATIONS for station in route):
        return Region.YOGYA_SOLO
    elif any(station.lower() in RANGKASBITUNG_MERAK_STATIONS for station in route):
        return Region.RANGKASBITUNG_MERAK
    return Region.JABODETABEK

# --- JARAK UNTUK JABODETABEK (SAMA DENGAN occupancy_predictor.py) ---
JABODETABEK_DISTANCES = {
    # A. Bogor - Manggarai
        ("Bogor", "Cilebut"): 7.518, ("Cilebut", "Bogor"): 7.518,
        ("Cilebut", "Bojong Gede"): 4.331, ("Bojong Gede", "Cilebut"): 4.331,
        ("Bojong Gede", "Citayam"): 5.197, ("Citayam", "Bojong Gede"): 5.197,
        ("Citayam", "Depok"): 5.084, ("Depok", "Citayam"): 5.084,
        ("Depok", "Depok Baru"): 1.741, ("Depok Baru", "Depok"): 1.741,
        ("Depok Baru", "Pondok Cina"): 2.57, ("Pondok Cina", "Depok Baru"): 2.57,
        ("Pondok Cina", "Universitas Indonesia"): 1.109, ("Universitas Indonesia", "Pondok Cina"): 1.109,
        ("Universitas Indonesia", "Universitas Pancasila"): 2.264, ("Universitas Pancasila", "Universitas Indonesia"): 2.264,
        ("Universitas Pancasila", "Lenteng Agung"): 1.029, ("Lenteng Agung", "Universitas Pancasila"): 1.029,
        ("Lenteng Agung", "Tanjung Barat"): 2.460, ("Tanjung Barat", "Lenteng Agung"): 2.460,
        ("Tanjung Barat", "Pasar Minggu"): 3.031, ("Pasar Minggu", "Tanjung Barat"): 3.031,
        ("Pasar Minggu", "Pasar Minggu Baru"): 1.695, ("Pasar Minggu Baru", "Pasar Minggu"): 1.695,
        ("Pasar Minggu Baru", "Kalibata"): 1.509, ("Kalibata", "Pasar Minggu Baru"): 1.509,
        ("Kalibata", "Cawang"): 1.475, ("Cawang", "Kalibata"): 1.475,
        ("Cawang", "Tebet"): 1.301, ("Tebet", "Cawang"): 1.301,
        ("Tebet", "Manggarai"): 2.601, ("Manggarai", "Tebet"): 2.601,

        # B. Rangkas bitung - Tanah abang
        ("Rangkas bitung", "Citeras"): 9.847, ("Citeras", "Rangkas bitung"): 9.847,
        ("Citeras", "Maja"): 7.293, ("Maja", "Citeras"): 7.293,
        ("Maja", "Cikoya"): 1.835, ("Cikoya", "Maja"): 1.835,
        ("Cikoya", "Tigaraksa"): 2.651, ("Tigaraksa", "Cikoya"): 2.651,
        ("Tigaraksa", "Tenjo"): 2.974, ("Tenjo", "Tigaraksa"): 2.974,
        ("Tenjo", "Daru"): 3.902, ("Daru", "Tenjo"): 3.902,
        ("Daru", "Cilejit"): 2.675, ("Cilejit", "Daru"): 2.675,
        ("Cilejit", "Parung Panjang"): 7.025, ("Parung Panjang", "Cilejit"): 7.025,
        ("Parung Panjang", "Cicayur"): 5.968, ("Cicayur", "Parung Panjang"): 5.968,
        ("Cicayur", "Cisauk"): 2.519, ("Cisauk", "Cicayur"): 2.519,
        ("Cisauk", "Serpong"): 1.784, ("Serpong", "Cisauk"): 1.784,
        ("Serpong", "Rawa Buntu"): 2.413, ("Rawa Buntu", "Serpong"): 2.413,
        ("Rawa Buntu", "Sudimara"): 4.566, ("Sudimara", "Rawa Buntu"): 4.566,
        ("Sudimara", "Jurang Mangu"): 1.974, ("Jurang Mangu", "Sudimara"): 1.974,
        ("Jurang Mangu", "Pondok Ranji"): 2.179, ("Pondok Ranji", "Jurang Mangu"): 2.179,
        ("Pondok Ranji", "Kebayoran"): 6.218, ("Kebayoran", "Pondok Ranji"): 6.218,
        ("Kebayoran", "Palmerah"): 3.373, ("Palmerah", "Kebayoran"): 3.373,
        ("Palmerah", "Tanah Abang"): 3.191, ("Tanah Abang", "Palmerah"): 3.191,

        # C. TANAH ABANG - JATINEGARA
        ("Tanah Abang", "Duri"): 3.632, ("Duri", "Tanah Abang"): 3.632,
        ("Duri", "Angke"): 1.230, ("Angke", "Duri"): 1.230,
        ("Angke", "Kampung Badan"): 4.102, ("Kampung Badan", "Angke"): 4.102,
        ("Kampung Badan", "Rajawali"): 1.444, ("Rajawali", "Kampung Badan"): 1.444,
        ("Rajawali", "Kemayoran"): 1.901, ("Kemayoran", "Rajawali"): 1.901,
        ("Kemayoran", "Pasar Senen"): 1.436, ("Pasar Senen", "Kemayoran"): 1.436,
        ("Pasar Senen", "Gang Sentiong"): 1.567, ("Gang Sentiong", "Pasar Senen"): 1.567,
        ("Gang Sentiong", "Kramat"): 0.973, ("Kramat", "Gang Sentiong"): 0.973,
        ("Kramat", "Pondok Jati"): 1.829, ("Pondok Jati", "Kramat"): 1.829,
        ("Pondok Jati", "Jatinegara"): 1.236, ("Jatinegara", "Pondok Jati"): 1.236,

        # D. JATINEGARA - CIKARANG
        ("Jatinegara", "Klender"): 3.395, ("Klender", "Jatinegara"): 3.395,
        ("Klender", "Buaran"): 3.1, ("Buaran", "Klender"): 3.1,
        ("Buaran", "Klender Baru"): 1.305, ("Klender Baru", "Buaran"): 1.305,
        ("Klender Baru", "Cakung"): 1.385, ("Cakung", "Klender Baru"): 1.385,
        ("Cakung", "Kranji"): 3.097, ("Kranji", "Cakung"): 3.097,
        ("Kranji", "Bekasi"): 2.520, ("Bekasi", "Kranji"): 2.520,
        ("Bekasi", "Bekasi Timur"): 3.298, ("Bekasi Timur", "Bekasi"): 3.298,
        ("Bekasi Timur", "Tambun"): 3.43, ("Tambun", "Bekasi Timur"): 3.43,
        ("Tambun", "Cibitung"): 3.42, ("Cibitung", "Tambun"): 3.42,
        ("Cibitung", "Cikarang"): 6.489, ("Cikarang", "Cibitung"): 6.489,

        # E. TANAH ABANG - MANGGARAI
        ("Tanah Abang", "Karet"): 2.029, ("Karet", "Tanah Abang"): 2.029,
        ("Karet", "BNI City"): 0.377, ("BNI City", "Karet"): 0.377,
        ("BNI City", "Sudirman"): 0.434, ("Sudirman", "BNI City"): 0.434,
        ("Sudirman", "Manggarai"): 3.186, ("Manggarai", "Sudirman"): 3.186,

        # F. (Route between Manggarai and Jakarta Kota)
        ("Manggarai", "Cikini"): 1.606, ("Cikini", "Manggarai"): 1.606,
        ("Cikini", "Gondangdia"): 1.699, ("Gondangdia", "Cikini"): 1.699,
        ("Gondangdia", "Juanda"): 2.198, ("Juanda", "Gondangdia"): 2.198,
        ("Juanda", "Sawah Besar"): 0.707, ("Sawah Besar", "Juanda"): 0.707,
        ("Sawah Besar", "Mangga Besar"): 1.121, ("Mangga Besar", "Sawah Besar"): 1.121,
        ("Mangga Besar", "Jayakarta"): 1.02, ("Jayakarta", "Mangga Besar"): 1.02,
        ("Jayakarta", "Jakarta Kota"): 1.467, ("Jakarta Kota", "Jayakarta"): 1.467,

        # G. TANGERANG - DURI
        ("Tangerang", "Tanah Tinggi"): 1.609, ("Tanah Tinggi", "Tangerang"): 1.609,
        ("Tanah Tinggi", "Batu Ceper"): 2.0, ("Batu Ceper", "Tanah Tinggi"): 2.0,
        ("Batu Ceper", "Poris"): 1.8, ("Poris", "Batu Ceper"): 1.8,
        ("Poris", "Kalideres"): 2.548, ("Kalideres", "Poris"): 2.548,
        ("Kalideres", "Rawa Buaya"): 2.504, ("Rawa Buaya", "Kalideres"): 2.504,
        ("Rawa Buaya", "Bojong Indah"): 1.152, ("Bojong Indah", "Rawa Buaya"): 1.152,
        ("Bojong Indah", "Taman Kota"): 2.434, ("Taman Kota", "Bojong Indah"): 2.434,
        ("Taman Kota", "Pesing"): 1.514, ("Pesing", "Taman Kota"): 1.514,
        ("Pesing", "Grogol"): 2.036, ("Grogol", "Pesing"): 2.036,
        ("Grogol", "Duri"): 1.7, ("Duri", "Grogol"): 1.7,

        # H. Jakarta Kota - Tanjung Priok
        ("Jakarta Kota", "Kampung Bandan"): 1.364, ("Kampung Bandan", "Jakarta Kota"): 1.364,
        ("Kampung Bandan", "Ancol"): 6.5, ("Ancol", "Kampung Bandan"): 6.5,
        ("Ancol", "Tanjung Priok"):4.566, ("Tanjung Priok", "Ancol"):4.566
}

# --- FUNGSI HITUNG JARAK UNTUK JABODETABEK ---
def get_jabodetabek_distance(station_a: str, station_b: str) -> float:
    """Mengembalikan jarak (km) antara dua stasiun Jabodetabek, default 2.0 km jika tidak ditemukan."""
    return JABODETABEK_DISTANCES.get(
        (station_a, station_b),
        JABODETABEK_DISTANCES.get((station_b, station_a), 2.0)
    )

# --- FUNGSI HITUNG JARAK TOTAL UNTUK RUTE JABODETABEK ---
def get_total_jabodetabek_distance(route: list) -> float:
    total = 0.0
    for i in range(len(route) - 1):
        total += get_jabodetabek_distance(route[i], route[i+1])
    return total

def _get_simple_path(route: list) -> list:
    """
    Mengembalikan lintasan dari stasiun awal ke akhir tanpa stasiun berulang.
    Jika ada stasiun yang sama lebih dari sekali, hanya ambil sampai kemunculan pertama stasiun akhir.
    """
    seen = set()
    simple_path = []
    for st in route:
        if st in seen:
            break
        simple_path.append(st)
        seen.add(st)
    # Pastikan stasiun akhir tetap masuk
    if route and route[-1] not in seen:
        simple_path.append(route[-1])
    return simple_path

# --- FUNGSI HITUNG TARIF ---
def calculate_fare(route: list, region) -> int:
    """
    Menghitung tarif perjalanan berdasarkan region dan rute.
    - Kutoarjo-Yogyakarta: 8000 flat
    - Yogyakarta-Palur: 8000 flat
    - Rangkasbitung-Merak: 5000 flat
    - Jabodetabek: 3000 (25km pertama) + 1000 per 10km berikutnya (pembulatan ke atas)
    """
    # Ambil lintasan tanpa stasiun berulang
    route = _get_simple_path(route)
    if region == Region.YOGYA_SOLO:
        return 8000
    elif region == Region.RANGKASBITUNG_MERAK:
        return 5000
    elif region == Region.JABODETABEK:
        distance = get_total_jabodetabek_distance(route)
        if distance <= 25:
            return 3000
        else:
            extra_km = distance - 25
            extra_blocks = math.ceil(extra_km / 10)
            return 3000 + 1000 * extra_blocks
    else:
        return 0  # fallback

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

    def get_fare_for_train(self, train: Train) -> int:
        """Mengembalikan tarif untuk kereta tertentu."""
        return calculate_fare(train.route, train.region)
    
# -- Akhir Kutipan