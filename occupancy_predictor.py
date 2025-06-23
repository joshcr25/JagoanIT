import datetime
from enum import Enum
from typing import List, Dict, Set
import re
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
    DARI_BOGOR_MENUJU_JAKARTAKOTA = 1
    DARI_BOGOR_MENUJU_DEPOK = 8
    MENUJU_ANGKE = 9
    MENUJU_KAMPUNGBANDAN = 10
    MENUJU_NAMBO = 11
    DARI_DEPOK_MENUJU_MANGGARAI = 12
    MENUJU_TANAHABANG = 13
    MENUJU_BEKASI = 14
    MENUJU_DURI = 15
    DARI_BOGOR_MENUJU_MANGGARAI = 16
    DARI_TANAH_ABANG_MENUJU_MANGGARAI = 17
    DARI_MANGGARAI_MENUJU_BOGOR = 18
    DARI_NAMBO_MENUJU_JAKARTAKOTA = 19
    DARI_JAKARTAKOTA_MENUJU_NAMBO = 20
    DARI_JAKARTAKOTA_MENUJU_BOGOR = 2
    MENUJU_CIKARANG = 3
    MENUJU_RANGKASBITUNG = 4
    MENUJU_TANGERANG = 5
    DUA_ARAH = 6
    UNKNOWN = 7


class TimePeriod(Enum):
    PUNCAK_PAGI = 1
    PUNCAK_SORE = 2 # Re-numbering to keep it compact
    MALAM = 3
    AKHIR_PEKAN = 4
    AWAL_SIANG = 5 # New granular period
    MAKAN_SIANG = 6 # New granular period
    AKHIR_SIANG = 7 # New granular period



# Definisi periode waktu yang konsisten dengan enum TimePeriod
TIME_PERIOD_DEFINITIONS = {
    TimePeriod.PUNCAK_PAGI: (datetime.time(5, 30), datetime.time(8, 30)),
    TimePeriod.AWAL_SIANG: (datetime.time(8, 30), datetime.time(12, 0)),
    TimePeriod.MAKAN_SIANG: (datetime.time(12, 0), datetime.time(14,0)),
    TimePeriod.AKHIR_SIANG: (datetime.time(14, 0), datetime.time(15, 30)),
    TimePeriod.PUNCAK_SORE: (datetime.time(15, 30), datetime.time(19, 0)),
    # MALAM adalah waktu di luar periode-periode di atas
}



# metode __avg (Misalnya 100% - 120%) mereturn 110%
def _avg(percentage_range):
    match = re.match(r"(\d+)(?:\s*-\s*(\d+))?\s*%", percentage_range)
    if match:
        if match.group(2):  # Jika ada angka kedua (rentang)
            start, end = int(match.group(1)), int(match.group(2))
            return (start + end) // 2
        else:  # Jika hanya ada satu angka
            return int(match.group(1))
    else:
        raise ValueError(f"Invalid percentage range format: {percentage_range}")



# Matriks data okupansi
OCCUPANCY_MATRIX = {
    Line.BOGOR: {
        Direction.DARI_BOGOR_MENUJU_JAKARTAKOTA: {
            # Puncak okupansi berada di stasiun yg menjelang pusat kota yaitu dari
            # Pasar Minggu Baru sampai Manggarai (yaitu 100-180%) saat pagi ke arah Jakarta Kota
            TimePeriod.PUNCAK_PAGI: _avg("100-120%"), TimePeriod.SIANG: _avg("40-70%"),
            TimePeriod.PUNCAK_SORE: _avg("40-70%"), TimePeriod.MALAM: _avg("40-70%"),
            TimePeriod.AKHIR_PEKAN: _avg("70-90%"),
        },
            # Puncak okupansi berada di stasiun yg menuju pusat kota yaitu dari
            # Jakarta Kota sampai Manggarai atau dari Manggarai ke Bogor (yaitu 100%-120%) saat sore ke arah Bogor
        Direction.DARI_JAKARTAKOTA_MENUJU_BOGOR: {
            TimePeriod.PUNCAK_PAGI: _avg("40-70%"), TimePeriod.SIANG: _avg("40-70%"),
            TimePeriod.PUNCAK_SORE: _avg("100-120%"), TimePeriod.MALAM: _avg("40-70%"),
            TimePeriod.AKHIR_PEKAN: _avg("70-90%"),
        },
        
            # Puncak okupansi berada di stasiun yg menuju pusat kota yaitu dari
            # Manggarai, (yaitu 120-180%) saat pagi ke arah Manggarai
            
            # Puncak okupansi berada di stasiun yg menuju pusat kota yaitu dari
            # Bogor ke Manggarai saat siang hingga sore hari saat akhir pekan.
            # Okupansinya meningkat hingga 70-90%
        Direction.DARI_BOGOR_MENUJU_MANGGARAI: {
            TimePeriod.PUNCAK_PAGI: _avg("120-180%"), TimePeriod.SIANG: _avg("40-70%"),
            TimePeriod.PUNCAK_SORE: _avg("40-70%"), TimePeriod.MALAM: _avg("40-70%"),
            TimePeriod.AKHIR_PEKAN: _avg("70-90%"),
        },
        Direction.DARI_MANGGARAI_MENUJU_BOGOR: {
            TimePeriod.PUNCAK_PAGI: _avg("40-70%"), TimePeriod.SIANG: _avg("40-70%"),
            TimePeriod.PUNCAK_SORE: _avg("100-130%"), TimePeriod.MALAM: _avg("40-70%"),
            TimePeriod.AKHIR_PEKAN: _avg("70-90%"),
        },
        # Setelah melewati stasiun Citayam, kereta tujuan Nambo akan jauh lebih lenggang
        # dibandingkan kereta yang melanjutkan perjalanan ke Bogor
        Direction.DARI_NAMBO_MENUJU_JAKARTAKOTA: {
            TimePeriod.PUNCAK_PAGI: _avg("70-100%"), TimePeriod.SIANG: _avg("40-70%"),
            TimePeriod.PUNCAK_SORE: _avg("40-70%"), TimePeriod.MALAM: _avg("40-70%"),
            TimePeriod.AKHIR_PEKAN: _avg("70-90%"),
        },
        Direction.DARI_JAKARTAKOTA_MENUJU_NAMBO: {
            TimePeriod.PUNCAK_PAGI: _avg("40-70%"), TimePeriod.SIANG: _avg("40-70%"),
            TimePeriod.PUNCAK_SORE: _avg("70-100%"), TimePeriod.MALAM: _avg("40-70%"),
            TimePeriod.AKHIR_PEKAN: _avg("70-90%"),
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
    if route_set.intersection({"bogor", "bojong gede", "cilebut", "depok", "nambo"}):
        return Line.BOGOR
    return Line.UNKNOWN


def _direction_by_last_station(last: str) -> Direction:
    last_station_map = {
        "tanjung priok": Direction.DUA_ARAH,
        "tanah abang": Direction.MENUJU_TANAHABANG,
        "nambo": Direction.MENUJU_NAMBO,
        "angke": Direction.MENUJU_ANGKE,
        "kampung bandan": Direction.MENUJU_KAMPUNGBANDAN,
        "cikarang": Direction.MENUJU_CIKARANG,
        "tangerang": Direction.MENUJU_TANGERANG,
        "duri": Direction.MENUJU_DURI,
        "bekasi": Direction.MENUJU_BEKASI,
    }
    for key, value in last_station_map.items():
        if key in last:
            return value
    if any(term in last for term in ["rangkasbitung", "parung panjang"]):
        return Direction.MENUJU_RANGKASBITUNG
    return None

def _direction_by_first_last(first: str, last: str) -> Direction:
    if "jakarta kota" in first and "bogor" in last:
        return Direction.DARI_BOGOR_MENUJU_JAKARTAKOTA
    if "bogor" in last and "jakarta kota" in first:
        return Direction.DARI_JAKARTAKOTA_MENUJU_BOGOR
    if "depok" in last and "bogor" in first:
        return Direction.DARI_BOGOR_MENUJU_DEPOK
    if "manggarai" in last and "depok" in first:
        return Direction.DARI_DEPOK_MENUJU_MANGGARAI
    if "manggarai" in last and "bogor" in first:
        return Direction.DARI_BOGOR_MENUJU_MANGGARAI
    if "manggarai" in last and "tanah abang" in first:
        return Direction.DARI_TANAH_ABANG_MENUJU_MANGGARAI
    if "bogor" in last and "manggarai" in first:
        return Direction.DARI_MANGGARAI_MENUJU_BOGOR
    if "nambo" in last and "jakarta kota" in first:
        return Direction.DARI_JAKARTAKOTA_MENUJU_NAMBO
    if "jakarta kota" in last and "nambo" in first:
        return Direction.DARI_NAMBO_MENUJU_JAKARTAKOTA
    return None

def get_direction(route: List[str]) -> Direction:
    """Determines the direction of a train based on its route."""
    if not route or len(route) < 2:
        return Direction.UNKNOWN
    first = normalize_station(route[0])
    last = normalize_station(route[-1])

    # Check for directions based on last station only
    direction = _direction_by_last_station(last)
    if direction:
        return direction

    # Check for directions based on first and last station combinations
    direction = _direction_by_first_last(first, last)
    if direction:
        return direction

    return Direction.UNKNOWN


def get_adjacent_periods(current_time: datetime.datetime) -> List[tuple[TimePeriod, float]]:
    """
    Mengembalikan satu atau dua periode waktu beserta bobotnya, jika waktu berada di antara dua periode (transisi).
    """
    time = current_time.time()
    weekday = current_time.weekday()

    if weekday >= 5:  # Sabtu & Minggu
        return [(TimePeriod.AKHIR_PEKAN, 1.0)]
    
    puncak_pagi_start, puncak_pagi_end = TIME_PERIOD_DEFINITIONS[TimePeriod.PUNCAK_PAGI]
    awal_siang_start, awal_siang_end = TIME_PERIOD_DEFINITIONS[TimePeriod.AWAL_SIANG]
    makan_siang_start, makan_siang_end = TIME_PERIOD_DEFINITIONS[TimePeriod.MAKAN_SIANG]
    akhir_siang_start, akhir_siang_end = TIME_PERIOD_DEFINITIONS[TimePeriod.AKHIR_SIANG]
    puncak_sore_start, puncak_sore_end = TIME_PERIOD_DEFINITIONS[TimePeriod.PUNCAK_SORE]


    # Definisi transisi antar periode
    if puncak_pagi_start <= time < puncak_pagi_end:
        # Transisi 60 menit sebelum akhir puncak pagi
        transition_start = (datetime.datetime.combine(
            current_time.date(), puncak_pagi_end) - datetime.timedelta(minutes=60)).time()
        if transition_start <= time < puncak_pagi_end:
            # Interpolasi antara PUNCAK_PAGI dan SIANG
            delta = (datetime.datetime.combine(current_time.date(), puncak_pagi_end) -
                     datetime.datetime.combine(current_time.date(), time)).total_seconds() / 60
            w_pagi = delta / 60
            w_awal_siang = 1 - w_pagi
            return [(TimePeriod.PUNCAK_PAGI, w_pagi), (TimePeriod.AWAL_SIANG, w_awal_siang)]
        return [(TimePeriod.PUNCAK_PAGI, 1.0)] # No transition, fully in PUNCAK_PAGI
    if awal_siang_start <= time < awal_siang_end:
        # Transisi 60 menit sebelum akhir siang
        transition_start = (datetime.datetime.combine(current_time.date(), awal_siang_end) - datetime.timedelta(minutes=60)).time()
        if transition_start <= time < awal_siang_end:
            delta = (datetime.datetime.combine(current_time.date(), awal_siang_end) -
                     datetime.datetime.combine(current_time.date(), time)).total_seconds() / 60
            w_awal_siang = delta / 60
            w_makan_siang = 1 - w_awal_siang # Transition to MAKAN_SIANG
            return [(TimePeriod.AWAL_SIANG, w_awal_siang), (TimePeriod.MAKAN_SIANG, w_makan_siang)]
        return [(TimePeriod.AWAL_SIANG, 1.0)]
    if makan_siang_start <= time < makan_siang_end:
        # Transisi 60 menit sebelum akhir makan siang
        transition_start = (datetime.datetime.combine(current_time.date(), makan_siang_end) - datetime.timedelta(minutes=60)).time()
        if transition_start <= time < makan_siang_end:
            delta = (datetime.datetime.combine(current_time.date(), makan_siang_end) -
                     datetime.datetime.combine(current_time.date(), time)).total_seconds() / 60
            w_makan_siang = delta / 60
            w_akhir_siang = 1 - w_makan_siang # Transition to AKHIR_SIANG
            return [(TimePeriod.MAKAN_SIANG, w_makan_siang), (TimePeriod.AKHIR_SIANG, w_akhir_siang)]
        return [(TimePeriod.MAKAN_SIANG, 1.0)]
    if akhir_siang_start <= time < akhir_siang_end:
        # Transisi 60 menit sebelum akhir akhir siang
        transition_start = (datetime.datetime.combine(current_time.date(), akhir_siang_end) - datetime.timedelta(minutes=60)).time()
        if transition_start <= time < akhir_siang_end:
            delta = (datetime.datetime.combine(current_time.date(), akhir_siang_end) -
                     datetime.datetime.combine(current_time.date(), time)).total_seconds() / 60
            w_akhir_siang = delta / 60
            w_sore = 1 - w_akhir_siang # Transition to PUNCAK_SORE
            return [(TimePeriod.AKHIR_SIANG, w_akhir_siang), (TimePeriod.PUNCAK_SORE, w_sore)]
        return [(TimePeriod.AKHIR_SIANG, 1.0)]
            
    if puncak_sore_start <= time < puncak_sore_end:
        # Transisi 60 menit sebelum akhir puncak sore
        transition_start = (datetime.datetime.combine(
        current_time.date(), puncak_sore_end) - datetime.timedelta(minutes=60)).time()
        if transition_start <= time < puncak_sore_end:
            delta = (datetime.datetime.combine(current_time.date(), puncak_sore_end) -
                     datetime.datetime.combine(current_time.date(), time)).total_seconds() / 60
            w_sore = delta / 60 # Transition to MALAM
            w_malam = 1 - w_sore
            return [(TimePeriod.PUNCAK_SORE, w_sore), (TimePeriod.MALAM, w_malam)]
        return [(TimePeriod.PUNCAK_SORE, 1.0)]
    # Transisi malam ke pagi (misal 10 menit sebelum PUNCAK_PAGI_MULAI)
    transition_start = (datetime.datetime.combine(current_time.date(), puncak_pagi_start) - datetime.timedelta(minutes=10)).time()
    if transition_start <= time < puncak_pagi_start:
        delta = (datetime.datetime.combine(current_time.date(), puncak_pagi_start) -
                 datetime.datetime.combine(current_time.date(), time)).total_seconds() / 60
        w_malam = delta / 60
        w_pagi = 1 - w_malam
        return [(TimePeriod.MALAM, w_malam), (TimePeriod.PUNCAK_PAGI, w_pagi)]
    # If none of the above, it's MALAM
    return [(TimePeriod.MALAM, 1.0)]




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
    Menggunakan matriks okupansi dan profil spasial untuk prediksi yang lebih terstruktur.
    """
    occupancy_map = {}
    route = train.route
    if not route:
            return occupancy_map


    line = get_line(route)
    direction = get_direction(route)
    periods_weights = get_adjacent_periods(current_time)


    is_puncak_pagi = any(p == TimePeriod.PUNCAK_PAGI for p in periods_weights)
    is_puncak_sore = any(p == TimePeriod.PUNCAK_SORE for p in periods_weights)
    is_awal_siang = any(p == TimePeriod.AWAL_SIANG for p in periods_weights)
    is_makan_siang = any(p == TimePeriod.MAKAN_SIANG for p in periods_weights)
    is_akhir_siang = any(p == TimePeriod.AKHIR_SIANG for p in periods_weights)
    is_akhir_pekan = any(p == TimePeriod.AKHIR_PEKAN for p in periods_weights)
    # TODO
    # Jam sibuk pagi 
    # Okupansi KRL dari Bogor ke Jakarta Kota
    # Dari Bogor - Bojong Gede (0-105%)
    # Dari Citayam - Pasar Minggu (105%-115%)
    # Dari Pasar Minggu Baru - Manggarai (115% - 120%)
    # Dari Cikini - Jakarta Kota (80% menurun hingga 0%)
    
    if is_puncak_pagi and direction == Direction.DARI_BOGOR_MENUJU_JAKARTAKOTA:    
        for i, route in enumerate(route):
            occupancy_map[route] = int(-3.410605*10^-13 + 53.36605*i - 8.279928*i^2 + 0.524309 * i^3 - 0.1153014*i^4)
    
    # Jam sibuk sore
    # Okupansi KRL dari Jakarta Kota ke Bogor
    # Dari Jakarta Kota - Manggarai (0-120%)
    # Dari Manggarai - Pasar Minggu Baru (120% menurun hingga 115%)
    # Dari Pasar Minggu Baru - Citayam (115% menurun hingga 105%)
    # Dari Citayam - Bogor (105% menurun hingga 0%)
    
    if is_puncak_sore and direction == Direction.DARI_JAKARTAKOTA_MENUJU_BOGOR:
        for i, route in enumerate(route):
            occupancy_map[route] = int(6.82121*10^-13 + 56.58092 * i - 8.699259 * i^2 + 0.5364635 * i^3 - 0.01153014 * i^4)
    
    
    
    # Di luar jam sibuk yg di luar jam makan siang (08:30 - 12:00 & 14:00-15:30 & setelah jam 19:00)
    # Okupansi KRL dari Jakarta Kota ke Bogor
    # Dari Jakarta Kota - Manggarai (0% naik hingga 70%)
    # Dari Manggarai - Pasar Minggu (70% turun hingga 65%)
    # Dari Pasar Minggu - Citayam (65% turun hingga 40%)
    # Dari Bojong Gede - Bogor (40% turun hingga 0%)
    
    if is_puncak_sore and direction == Direction.DARI_JAKARTAKOTA_MENUJU_BOGOR:
        for i, route in enumerate(route):
            occupancy_map[route] = int(-1.136868*10^-13 + 25.82139 * i - 3.355988 * i^2 + 0.1825466 * i^3 - 0.003715035*i^4)
    
    # Di luar jam sibuk yg di dalam jam makan siang (12:00 - 14:00)
    # Okupansi KRL dari Jakarta Kota ke Bogor
    # Dari Jakarta Kota - Manggarai (0% naik hingga 75%)
    # Dari Manggarai - Pasar Minggu (75% turun hingga 70%)
    # Dari Pasar Minggu - Citayam (70% turun hingga 45%)
    # Dari Bojong Gede - Bogor (45% hingga 0%)
    if is_makan_siang and direction == Direction.DARI_JAKARTAKOTA_MENUJU_BOGOR:
        for i, route in enumerate(route):
            occupancy_map[route] = int(-1.136868*10^-13 + 28.11143* i - 3.723141*i^2 + 0.2066267*i^3 - 0.004256161*i^4)
    
    # Di luar jam sibuk yg di luar jam makan siang (08:30 - 12:00 & 14:00-15:30 & setelah jam 19:00)
    # Okupansi KRL dari Bogor - Jakarta Kota
    # Dari Bogor - Bojong Gede (0-40%)
    # Dari Citayam - Pasar Minggu (40-65%)
    # Dari Pasar Minggu Baru - Manggarai (65%-70%)
    # Dari Cikini - Jakarta Kota (40% menurun hingga 0%)
    if (is_awal_siang or is_akhir_siang) and direction == Direction.DARI_JAKARTAKOTA_MENUJU_BOGOR:
        for i, route in enumerate(route):
            occupancy_map[route] = int(5.684342*10^-14 + 19.65589 * i - 2.551792 * i^2 + 0.1592366* i^3 - 0.3715035*i^4)
    
    # Di luar jam sibuk yg di dalam jam makan siang (12:00 - 14:00)
    # Okupansi KRL dari Bogor - Jakarta Kota
    # Dari Bogor - Bojong Gede (0-45%)
    # Dari Citayam - Pasar Minggu (45-70%)
    # Dari Pasar Minggu Baru - Manggarai (70-75%)
    # Dari Cikini - Jakarta Kota (45% menurun hingga 0%)
    for i, route in enumerate(route):
        occupancy_map[route] = int(-5.684342*10^-14 + 22.37531 * i - 2.974952 * i^2 + 0.1849401* i^3 - 0.004256161*i^4)
    
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
