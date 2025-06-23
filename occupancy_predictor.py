import datetime
from enum import Enum
from typing import List, Dict, Set
import mlflow
import numpy as np
from data_models import Train
# Tambahkan import Region jika perlu
from data_models import Region


class Line(Enum):
    BOGOR = 1
    CIKARANG = 2
    RANGKASBITUNG = 3
    TANGERANG = 4
    TANJUNG_PRIOK = 5
    UNKNOWN = 6


class Direction(Enum):
    MENUJU_JAKARTAKOTA = 1
    MENUJU_DEPOK = 8
    MENUJU_ANGKE = 9
    MENUJU_KAMPUNGBANDAN = 10
    MENUJU_NAMBO = 11
    DARI_DEPOK_MENUJU_MANGGARAI = 12
    MENUJU_TANAHABANG = 13
    MENUJU_BEKASI = 14
    MENUJU_DURI = 15
    DARI_BOGOR_MENUJU_MANGGARAI = 16
    MENUJU_BOGOR = 2
    MENUJU_CIKARANG = 3
    MENUJU_RANGKASBITUNG = 4
    MENUJU_TANGERANG = 5
    DUA_ARAH = 6
    UNKNOWN = 7


class TimePeriod(Enum):
    PUNCAK_PAGI = 1
    SIANG = 2
    PUNCAK_SORE = 3
    MALAM = 4
    AKHIR_PEKAN = 5


# Time definitions
MORNING_PEAK_START = datetime.time(5, 30)
MORNING_PEAK_END = datetime.time(8, 30)
DAYTIME_START = datetime.time(8, 31)
DAYTIME_END = datetime.time(15, 29)
EVENING_PEAK_START = datetime.time(15, 30)
EVENING_PEAK_END = datetime.time(19, 0)



# metode __avg (Misalnya 100% - 120%) mereturn 110%
def _avg(r): return sum(
    map(int, r.replace('%', '').replace('+', '').split('-'))) // len(list(map(int, r.replace('%', '').replace('+', '').split('-'))))

# Matriks data okupansi
OCCUPANCY_MATRIX = {
    Line.BOGOR: {
        Direction.MENUJU_JAKARTAKOTA: {
            # Puncak okupansi berada di stasiun yg menjelang pusat kota yaitu dari
            # Pasar Minggu Baru sampai Manggarai (yaitu 100-120%) saat pagi ke arah Jakarta Kota
            TimePeriod.PUNCAK_PAGI: _avg("100-120%"), TimePeriod.SIANG: _avg("40-70%"),
            TimePeriod.PUNCAK_SORE: _avg("40-70%"), TimePeriod.MALAM: _avg("40-70%"),
            TimePeriod.AKHIR_PEKAN: _avg("70-90%"),
        },
            # Puncak okupansi berada di stasiun yg menuju pusat kota yaitu dari
            # Jakarta Kota sampai Manggarai atau dari Manggarai ke Bogor (yaitu 100%-120%) saat sore ke arah Bogor
        Direction.MENUJU_BOGOR: {
            TimePeriod.PUNCAK_PAGI: _avg("40-70%"), TimePeriod.SIANG: _avg("40-70%"),
            TimePeriod.PUNCAK_SORE: _avg("100-120%"), TimePeriod.MALAM: _avg("40-70%"),
            TimePeriod.AKHIR_PEKAN: _avg("70-90%"),
        },
        
            # Puncak okupansi berada di stasiun yg menuju pusat kota yaitu dari
            # Pasar Minggu sampai Tebet (yaitu 120-180%) saat sore ke arah Bogor
        Direction.MENUJU_MANGGARAI: {
            TimePeriod.PUNCAK_PAGI: _avg("120-180%"), TimePeriod.SIANG: _avg("40-70%"),
            TimePeriod.PUNCAK_SORE: _avg("40-70%"), TimePeriod.MALAM: _avg("40-70%"),
            TimePeriod.AKHIR_PEKAN: _avg("40-70%"),
        },
    },
    Line.CIKARANG: {
        Direction.MENUJU_KAMPUNGBANDAN: {
            TimePeriod.PUNCAK_PAGI: _avg("130-170%"), TimePeriod.SIANG: _avg("35-55%"),
            TimePeriod.PUNCAK_SORE: _avg("60-80%"), TimePeriod.MALAM: _avg("40-60%"),
            TimePeriod.AKHIR_PEKAN: _avg("60-90%"),
        },
        Direction.MENUJU_CIKARANG: {
            TimePeriod.PUNCAK_PAGI: _avg("50-70%"), TimePeriod.SIANG: _avg("40-60%"),
            TimePeriod.PUNCAK_SORE: _avg("120-160%"), TimePeriod.MALAM: _avg("70-100%"),
            TimePeriod.AKHIR_PEKAN: _avg("60-90%"),
        },
    },
    Line.RANGKASBITUNG: {
        Direction.MENUJU_TANAHABANG: {
            TimePeriod.PUNCAK_PAGI: _avg("160-220%"), TimePeriod.SIANG: _avg("50-70%"),
            TimePeriod.PUNCAK_SORE: _avg("80-110%"), TimePeriod.MALAM: _avg("60-90%"),
            TimePeriod.AKHIR_PEKAN: _avg("80-110%"),
        },
        Direction.MENUJU_RANGKASBITUNG: {
            TimePeriod.PUNCAK_PAGI: _avg("60-80%"), TimePeriod.SIANG: _avg("60-80%"),
            TimePeriod.PUNCAK_SORE: _avg("150-200%"), TimePeriod.MALAM: _avg("90-120%"),
            TimePeriod.AKHIR_PEKAN: _avg("80-110%"),
        },
    },
    Line.TANGERANG: {
        Direction.MENUJU_DURI: {
            TimePeriod.PUNCAK_PAGI: _avg("120-160%"), TimePeriod.SIANG: _avg("40-60%"),
            TimePeriod.PUNCAK_SORE: _avg("60-80%"), TimePeriod.MALAM: _avg("45-65%"),
            TimePeriod.AKHIR_PEKAN: _avg("50-75%"),
        },
        Direction.MENUJU_TANGERANG: {
            TimePeriod.PUNCAK_PAGI: _avg("50-70%"), TimePeriod.SIANG: _avg("45-65%"),
            TimePeriod.PUNCAK_SORE: _avg("110-150%"), TimePeriod.MALAM: _avg("70-90%"),
            TimePeriod.AKHIR_PEKAN: _avg("50-75%"),
        },
    },
    Line.TANJUNG_PRIOK: {
        Direction.DUA_ARAH: {
            TimePeriod.PUNCAK_PAGI: _avg("20-40%"), TimePeriod.SIANG: _avg("15-30%"),
            TimePeriod.PUNCAK_SORE: _avg("25-40%"), TimePeriod.MALAM: _avg("15-30%"),
            TimePeriod.AKHIR_PEKAN: _avg("20-35%"),
        },
    }
}
DEFAULT_OCCUPANCY = 30
MIN_OCCUPANCY = 5
MAX_OCCUPANCY = 200


def normalize_station(name: str) -> str:
    """Removes parenthetical parts from station names."""
    if not name:
        return ""
    return name.split('(')[0].strip()


def get_line(route: List[str]) -> Line:
    """Determines the line based on the stations in a route."""
    route_set = {normalize_station(s) for s in route}
    if route_set.intersection({"bekasi", "cikarang", "tambun"}):
        return Line.CIKARANG
    if route_set.intersection({"parung panjang", "serpong", "rangkasbitung", "kebayoran"}):
        return Line.RANGKASBITUNG
    if route_set.intersection({"rawa buaya", "batu ceper", "tangerang"}):
        return Line.TANGERANG
    if route_set.intersection({"ancol", "tanjung priok"}):
        return Line.TANJUNG_PRIOK
    if route_set.intersection({"bogor", "bojong gede", "cilebut", "nambo", "depok", "nambo"}):
        return Line.BOGOR
    return Line.UNKNOWN


def get_direction(route: List[str]) -> Direction:
    """Determines the direction of a train based on its route."""
    if not route or len(route) < 2:
        return Direction.UNKNOWN
    first = normalize_station(route[0])
    last = normalize_station(route[-1])

    if "tanjung priok" in first or "tanjung priok" in last:
        return Direction.DUA_ARAH
    if "tanah abang" in last:
        return Direction.MENUJU_TANAHABANG
    if "jakarta kota" in last:
        return Direction.MENUJU_JAKARTAKOTA
    if "bogor" in last:
        return Direction.MENUJU_BOGOR
    if "nambo" in last:
        return Direction.MENUJU_NAMBO
    if "depok" in last:
        return Direction.MENUJU_DEPOK
    if "manggarai" in last and any(term in first for term in ["bogor", "depok"]):
        return Direction.MENUJU_MANGGARAI
    if "cikarang" in last:
        return Direction.MENUJU_CIKARANG
    if any(term in last for term in ["rangkasbitung", "parung panjang"]):
        return Direction.MENUJU_RANGKASBITUNG
    if "tangerang" in last:
        return Direction.MENUJU_TANGERANG
    if "duri" in last:
        return Direction.MENUJU_DURI
    if "bekasi" in last:
        return Direction.MENUJU_BEKASI
    return Direction.UNKNOWN


def get_adjacent_periods(current_time: datetime.datetime) -> List[tuple[TimePeriod, float]]:
    """
    Mengembalikan satu atau dua periode waktu beserta bobotnya, jika waktu berada di antara dua periode (transisi).
    """
    time = current_time.time()
    weekday = current_time.weekday()

    if weekday >= 5:  # Sabtu & Minggu
        return [(TimePeriod.AKHIR_PEKAN, 1.0)]

    # Definisi transisi antar periode
    if MORNING_PEAK_START <= time < MORNING_PEAK_END:
        # Transisi 10 menit sebelum akhir puncak pagi
        transition_start = (datetime.datetime.combine(
            current_time.date(), MORNING_PEAK_END) - datetime.timedelta(minutes=10)).time()
        if transition_start <= time < MORNING_PEAK_END:
            # Interpolasi antara PUNCAK_PAGI dan SIANG
            delta = (datetime.datetime.combine(current_time.date(), MORNING_PEAK_END) -
                     datetime.datetime.combine(current_time.date(), time)).total_seconds() / 60
            w_pagi = delta / 10
            w_siang = 1 - w_pagi
            return [(TimePeriod.PUNCAK_PAGI, w_pagi), (TimePeriod.SIANG, w_siang)]
        return [(TimePeriod.PUNCAK_PAGI, 1.0)]
    if DAYTIME_START <= time < DAYTIME_END:
        # Transisi 10 menit sebelum akhir siang
        transition_start = (datetime.datetime.combine(
            current_time.date(), DAYTIME_END) - datetime.timedelta(minutes=10)).time()
        if transition_start <= time < DAYTIME_END:
            delta = (datetime.datetime.combine(current_time.date(), DAYTIME_END) -
                     datetime.datetime.combine(current_time.date(), time)).total_seconds() / 60
            w_siang = delta / 10
            w_sore = 1 - w_siang
            return [(TimePeriod.SIANG, w_siang), (TimePeriod.PUNCAK_SORE, w_sore)]
        return [(TimePeriod.SIANG, 1.0)]
    if EVENING_PEAK_START <= time < EVENING_PEAK_END:
        # Transisi 10 menit sebelum akhir puncak sore
        transition_start = (datetime.datetime.combine(
            current_time.date(), EVENING_PEAK_END) - datetime.timedelta(minutes=10)).time()
        if transition_start <= time < EVENING_PEAK_END:
            delta = (datetime.datetime.combine(current_time.date(), EVENING_PEAK_END) -
                     datetime.datetime.combine(current_time.date(), time)).total_seconds() / 60
            w_sore = delta / 10
            w_malam = 1 - w_sore
            return [(TimePeriod.PUNCAK_SORE, w_sore), (TimePeriod.MALAM, w_malam)]
        return [(TimePeriod.PUNCAK_SORE, 1.0)]
    # Transisi malam ke pagi (misal 10 menit sebelum MORNING_PEAK_START)
    transition_start = (datetime.datetime.combine(current_time.date(
    ), MORNING_PEAK_START) - datetime.timedelta(minutes=10)).time()
    if transition_start <= time < MORNING_PEAK_START:
        delta = (datetime.datetime.combine(current_time.date(), MORNING_PEAK_START) -
                 datetime.datetime.combine(current_time.date(), time)).total_seconds() / 60
        w_malam = delta / 10
        w_pagi = 1 - w_malam
        return [(TimePeriod.MALAM, w_malam), (TimePeriod.PUNCAK_PAGI, w_pagi)]
    # Default malam
    return [(TimePeriod.MALAM, 1.0)]


def interpolate_occupancy(line: Line, direction: Direction, periods_weights: List[tuple[TimePeriod, float]]) -> int:
    """
    Mengambil data dari OCCUPANCY_MATRIX dan meratakannya berdasarkan bobot periods_weights.
    Jika data tidak ada, fallback ke DEFAULT_OCCUPANCY.
    """
    occ_sum = 0.0
    occ_matrix = OCCUPANCY_MATRIX.get(line)
    if not occ_matrix:
        return DEFAULT_OCCUPANCY
    # Cek direction, fallback ke DUA_ARAH jika tidak ada
    if direction not in occ_matrix:
        if Direction.DUA_ARAH in occ_matrix:
            occ_dir = occ_matrix[Direction.DUA_ARAH]
        else:
            return DEFAULT_OCCUPANCY
    else:
        occ_dir = occ_matrix[direction]
    for period, weight in periods_weights:
        occ = occ_dir.get(period, DEFAULT_OCCUPANCY)
        occ_sum += occ * weight
    occ_sum = max(MIN_OCCUPANCY, min(MAX_OCCUPANCY, occ_sum))
    return int(round(occ_sum))


# --- FUNGSI HITUNG TARIF UNTUK RUTE ---
def calculate_fare(route: list, region) -> int:
    """
    Menghitung tarif perjalanan berdasarkan region dan rute.
    - Kutoarjo-Yogyakarta: 8000 flat
    - Yogyakarta-Palur: 8000 flat
    - Rangkasbitung-Merak: 5000 flat
    - Jabodetabek: 3000 (25km pertama) + 1000 per 10km berikutnya
    """
    if region == Region.YOGYA_SOLO:
        return 8000
    elif region == Region.RANGKASBITUNG_MERAK:
        return 5000
    elif region == Region.JABODETABEK:
        distance = get_cumulative_distance(route)
        if distance <= 25:
            return 3000
        else:
            extra_km = distance - 25
            # pembulatan ke atas per 10km
            extra_blocks = int((extra_km + 9.9999) // 10)
            return 3000 + 1000 * extra_blocks
    else:
        return 0  # fallback


def predict(train: Train, current_time: datetime.datetime) -> Dict[str, int]:
    """
    Memprediksi okupansi untuk semua stasiun dalam rute kereta dengan interpolasi spasial
    yang disesuaikan dengan waktu dan arah perjalanan.
    """
    occupancy_map = {}
    route = train.route
    if not route:
            return occupancy_map


    line = get_line(route)
    direction = get_direction(route)
    periods_weights = get_adjacent_periods(current_time)
    base_occupancy = interpolate_occupancy(line, direction, periods_weights)

    n = len(route)
    if n == 1:
            occupancy_map[route[0]] = int(base_occupancy)
            return occupancy_map

    positions = np.linspace(0, 1, n)
    is_puncak_pagi = any(p == TimePeriod.PUNCAK_PAGI for p, w in periods_weights)
    is_puncak_sore = any(p == TimePeriod.PUNCAK_SORE for p, w in periods_weights)
    is_menuju_jakarta = direction == Direction.MENUJU_JAKARTA
    is_meninggalkan_jakarta = direction in [
            Direction.MENUJU_BOGOR,
            Direction.MENUJU_CIKARANG,
            Direction.MENUJU_RANGKASBITUNG,
            Direction.MENUJU_TANGERANG,
        ]

    if is_puncak_sore and is_meninggalkan_jakarta:
            k_decay = 2.0
            station_factors = np.exp(-k_decay * positions) * 0.9 + 0.15
    elif is_puncak_pagi and is_menuju_jakarta:
            k_growth = 3.0
            station_factors = np.exp(-k_growth * (1 - positions)) * 0.9 + 0.1
    else:
            station_factors = 0.7 + 0.3 * np.sin(np.pi * positions)

    for i, station in enumerate(route):
            predicted_occ = min(100, base_occupancy * station_factors[i])
            occupancy_map[station] = int(predicted_occ)
            
    return occupancy_map



def get_cumulative_distance(route: List[str]) -> List[float]:
    # Di sini Anda akan membaca dari data `station_distances` Anda
    # dan menghitung jarak kumulatif untuk rute yang diberikan.
    # Ini adalah implementasi contoh.
    # Anda harus membangun data `station_distances_bogor_line` yang lengkap.

    # Placeholder
    # Seharusnya ini lebih cerdas dan memilih data jarak yang benar berdasarkan line
    station_distances_data = {
        # ... (copy seluruh pasangan stasiun dan jaraknya, satu arah saja) ...
        ("Bogor", "Cilebut"): 7.518,
        ("Cilebut", "Bojong Gede"): 4.331,
        ("Bojong Gede", "Citayam"): 5.197,
        ("Citayam", "Depok"): 5.084,
        ("Depok", "Depok Baru"): 1.741,
        ("Depok Baru", "Pondok Cina"): 2.57,
        ("Pondok Cina", "Universitas Indonesia"): 1.109,
        ("Universitas Indonesia", "Universitas Pancasila"): 2.264,
        ("Universitas Pancasila", "Lenteng Agung"): 1.029,
        ("Lenteng Agung", "Tanjung Barat"): 2.460,
        ("Tanjung Barat", "Pasar Minggu"): 3.031,
        ("Pasar Minggu", "Pasar Minggu Baru"): 1.695,
        ("Pasar Minggu Baru", "Duren Kalibata"): 1.509,
        ("Duren Kalibata", "Cawang"): 1.475,
        ("Cawang", "Tebet"): 1.301,
        ("Tebet", "Manggarai"): 2.601,

        # B. Rangkasbitung - Tanah abang
        ("Rangkasbitung", "Citeras"): 9.847,
        ("Citeras", "Maja"): 7.293,
        ("Maja", "Cikoya"): 1.835,
        ("Cikoya", "Tigaraksa"): 2.651,
        ("Tigaraksa", "Tenjo"): 2.974,
        ("Tenjo", "Daru"): 3.902,
        ("Daru", "Cilejit"): 2.675,
        ("Cilejit", "Parung Panjang"): 7.025,
        ("Parung Panjang", "Cicayur"): 5.968,
        ("Cicayur", "Cisauk"): 2.519,
        ("Cisauk", "Serpong"): 1.784,
        ("Serpong", "Rawa Buntu"): 2.413,
        ("Rawa Buntu", "Sudimara"): 4.566,
        ("Sudimara", "Jurang Mangu"): 1.974,
        ("Jurang Mangu", "Pondok Ranji"): 2.179,
        ("Pondok Ranji", "Kebayoran"): 6.218,
        ("Kebayoran", "Palmerah"): 3.373,
        ("Palmerah", "Tanah Abang"): 3.191,

        # C. TANAH ABANG - JATINEGARA
        ("Tanah Abang", "Duri"): 3.632,
        ("Duri", "Angke"): 1.230,
        ("Angke", "Kampung Badan"): 4.102,
        ("Kampung Badan", "Rajawali"): 1.444,
        ("Rajawali", "Kemayoran"): 1.901,
        ("Kemayoran", "Pasar Senen"): 1.436,
        ("Pasar Senen", "Gang Sentiong"): 1.567,
        ("Gang Sentiong", "Kramat"): 0.973,
        ("Kramat", "Pondok Jati"): 1.829,
        ("Pondok Jati", "Jatinegara"): 1.236,

        # D. JATINEGARA - CIKARANG
        ("Jatinegara", "Klender"): 3.395,
        ("Klender", "Buaran"): 3.1,
        ("Buaran", "Klender Baru"): 1.305,
        ("Klender Baru", "Cakung"): 1.385,
        ("Cakung", "Kranji"): 3.097,
        ("Kranji", "Bekasi"): 2.520,
        ("Bekasi", "Bekasi Timur"): 3.298,
        ("Bekasi Timur", "Tambun"): 3.43,
        ("Tambun", "Cibitung"): 3.42,
        ("Cibitung", "Cikarang"): 6.489,

        # E. TANAH ABANG - MANGGARAI
        ("Tanah Abang", "Karet"): 2.029,
        ("Karet", "BNI City"): 0.377,
        ("BNI City", "Sudirman"): 0.434,
        ("Sudirman", "Manggarai"): 3.186,

        # F. (Route between Manggarai and Jakarta Kota)
        ("Manggarai", "Cikini"): 1.606,
        ("Cikini", "Gondangdia"): 1.699,
        ("Gondangdia", "Juanda"): 2.198,
        ("Juanda", "Sawah Besar"): 0.707,
        ("Sawah Besar", "Mangga Besar"): 1.121,
        ("Mangga Besar", "Jayakarta"): 1.02,
        ("Jayakarta", "Jakarta Kota"): 1.467,

        # G. TANGERANG - DURI
        ("Tangerang", "Tanah Tinggi"): 1.609,
        ("Tanah Tinggi", "Batu Ceper"): 2.0,
        ("Batu Ceper", "Poris"): 1.8,
        ("Poris", "Kalideres"): 2.548,
        ("Kalideres", "Rawa Buaya"): 2.504,
        ("Rawa Buaya", "Bojong Indah"): 1.152,
        ("Bojong Indah", "Taman Kota"): 2.434,
        ("Taman Kota", "Pesing"): 1.514,
        ("Pesing", "Grogol"): 2.036,
        ("Grogol", "Duri"): 1.7,

        # H. Jakarta Kota - Tanjung Priok
        ("Jakarta Kota", "Kampung Bandan"): 1.364,
        ("Kampung Bandan", "Ancol"): 6.5,
        ("Ancol", "Tanjung Priok"): 4.566
    }

    distances = [0.0]
    for i in range(len(route) - 1):
        station_pair = (route[i], route[i+1])
        reverse_pair = (route[i+1], route[i])
        dist = station_distances_data.get(station_pair, station_distances_data.get(reverse_pair, 2.0))
        distances.append(distances[-1] + dist)

    return distances
