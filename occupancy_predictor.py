import datetime
from enum import Enum
from typing import List, Dict
import re
import numpy as np
import mlflow
import pandas as pd
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
    # Rute Eksisting
    DARI_BOGOR_MENUJU_JAKARTAKOTA = 1
    DARI_JAKARTAKOTA_MENUJU_BOGOR = 2
    DARI_BEKASI_MENUJU_CIKARANG = 3
    MENUJU_RANGKASBITUNG = 4
    MENUJU_TANGERANG = 5
    DUA_ARAH = 6
    UNKNOWN = 7
    DARI_BOGOR_MENUJU_DEPOK = 8
    DARI_MANGGARAI_MENUJU_ANGKE = 9
    MENUJU_KAMPUNGBANDAN = 10
    MENUJU_NAMBO = 11
    DARI_DEPOK_MENUJU_MANGGARAI = 12
    MENUJU_TANAHABANG = 13
    DARI_CIKARANG_MENUJU_BEKASI = 14
    MENUJU_DURI = 15
    DARI_BOGOR_MENUJU_MANGGARAI = 16
    DARI_TANAH_ABANG_MENUJU_MANGGARAI = 17
    DARI_MANGGARAI_MENUJU_BOGOR = 18
    DARI_NAMBO_MENUJU_JAKARTAKOTA = 19
    DARI_JAKARTAKOTA_MENUJU_NAMBO = 20
    DARI_DURI_MENUJU_MANGGARAI = 21
    DARI_BEKASI_MENUJU_ANGKE = 22
    DARI_BEKASI_MENUJU_MANGGARAI = 23
    DARI_BEKASI_MENUJU_KAMPUNG_BANDAN_MELALUI_PASAR_SENEN = 24
    DARI_KAMPUNG_BANDAN_MENUJU_BEKASI_MELALUI_PASAR_SENEN = 25
    DARI_KAMPUNG_BANDAN_MENUJU_CIKARANG_MELALUI_PASAR_SENEN = 26
    DARI_CIKARANG_MENUJU_KAMPUNG_BANDAN_MELALUI_PASAR_SENEN = 27
    DARI_ANGKE_MENUJU_MANGGARAI = 28
    DARI_MANGGARAI_MENUJU_DURI = 29

    # Rute Tambahan Sesi 1
    DARI_CIKARANG_MENUJU_ANGKE_MELALUI_MANGGARAI = 30
    DARI_ANGKE_MENUJU_CIKARANG_MELALUI_MANGGARAI = 31
    DARI_BEKASI_MENUJU_ANGKE_MELALUI_MANGGARAI = 32
    DARI_ANGKE_MENUJU_BEKASI_MELALUI_MANGGARAI = 33
    DARI_CIKARANG_MENUJU_MANGGARAI = 34
    DARI_RANGKASBITUNG_MENUJU_TANAHABANG = 35
    DARI_TANAHABANG_MENUJU_RANGKASBITUNG = 36
    DARI_TANGERANG_MENUJU_DURI = 37
    DARI_DURI_MENUJU_TANGERANG = 38
    DARI_JATINEGARA_MENUJU_BOGOR = 39
    DARI_BOGOR_MENUJU_JATINEGARA = 40

    # --- PENAMBAHAN RUTE BARU (SESI 2) ---
    DARI_MANGGARAI_MENUJU_CIKARANG = 41
    DARI_CIKARANG_MENUJU_KAMPUNGBANDAN_MELALUI_MANGGARAI = 42
    DARI_KAMPUNGBANDAN_MENUJU_CIKARANG_MELALUI_MANGGARAI = 43
    DARI_BEKASI_MENUJU_KAMPUNGBANDAN_MELALUI_MANGGARAI = 44
    DARI_KAMPUNGBANDAN_MENUJU_BEKASI_MELALUI_MANGGARAI = 45
    MENUJU_ANGKE = 46
    # ------------------------------------


class TimePeriod(Enum):
    PUNCAK_PAGI = 1
    PUNCAK_SORE = 2
    MALAM = 3
    AKHIR_PEKAN = 4
    AWAL_SIANG = 5 
    MAKAN_SIANG = 6
    AKHIR_SIANG = 7



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


def normalize_station(name: str) -> str:
    """Removes parenthetical parts from station names."""
    if not name:
        return ""
    return name.split('(')[0].strip().lower() # Konversi ke lowercase untuk konsistensi


def _direction_by_last_station(last: str) -> Direction:
    last_station_map = {
        "tanjung priok": Direction.DUA_ARAH,
        "tanah abang": Direction.MENUJU_TANAHABANG,
        "nambo": Direction.MENUJU_NAMBO,
        "angke": Direction.MENUJU_ANGKE,
        "kampung bandan": Direction.MENUJU_KAMPUNGBANDAN,
        "cikarang": Direction.DARI_BEKASI_MENUJU_CIKARANG, # Perbaikan: Lebih spesifik
        "tangerang": Direction.MENUJU_TANGERANG,
        "duri": Direction.MENUJU_DURI,
        "bekasi": Direction.DARI_CIKARANG_MENUJU_BEKASI, # Perbaikan: Lebih spesifik
    }
    for key, value in last_station_map.items():
        if key in last:
            return value
    if any(term in last for term in ["rangkasbitung", "parung panjang"]):
        return Direction.MENUJU_RANGKASBITUNG
    return None

def _direction_by_first_last(first: str, last: str) -> Direction:
    # Rute Eksisting
    if "jakarta kota" in first and "bogor" in last:
        return Direction.DARI_JAKARTAKOTA_MENUJU_BOGOR
    if "bogor" in first and "jakarta kota" in last:
        return Direction.DARI_BOGOR_MENUJU_JAKARTAKOTA
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
    if "duri" in last and "manggarai" in first:
        return Direction.DARI_MANGGARAI_MENUJU_DURI
    if "manggarai" in last and "duri" in first:
        return Direction.DARI_DURI_MENUJU_MANGGARAI
    if "cikarang" in last and "bekasi" in first:
        return Direction.DARI_BEKASI_MENUJU_CIKARANG
    if "bekasi" in last and "cikarang" in first:
        return Direction.DARI_CIKARANG_MENUJU_BEKASI


    # --- LOGIKA UNTUK RUTE BARU (SESI 1 & 2) ---
    # Lin Cikarang via Manggarai
    if "cikarang" in first and "angke" in last:
        return Direction.DARI_CIKARANG_MENUJU_ANGKE_MELALUI_MANGGARAI
    if "angke" in first and "cikarang" in last:
        return Direction.DARI_ANGKE_MENUJU_CIKARANG_MELALUI_MANGGARAI
    if "bekasi" in first and "angke" in last:
        return Direction.DARI_BEKASI_MENUJU_ANGKE_MELALUI_MANGGARAI
    if "angke" in first and "bekasi" in last:
        return Direction.DARI_ANGKE_MENUJU_BEKASI_MELALUI_MANGGARAI
    if "cikarang" in first and "manggarai" in last:
        return Direction.DARI_CIKARANG_MENUJU_MANGGARAI
    if "manggarai" in first and "cikarang" in last:
        return Direction.DARI_MANGGARAI_MENUJU_CIKARANG # Baru
    if "cikarang" in first and "kampung bandan" in last:
        return Direction.DARI_CIKARANG_MENUJU_KAMPUNGBANDAN_MELALUI_MANGGARAI # Baru
    if "kampung bandan" in first and "cikarang" in last:
        return Direction.DARI_KAMPUNGBANDAN_MENUJU_CIKARANG_MELALUI_MANGGARAI # Baru
    if "bekasi" in first and "kampung bandan" in last:
        return Direction.DARI_BEKASI_MENUJU_KAMPUNGBANDAN_MELALUI_MANGGARAI # Baru
    if "kampung bandan" in first and "bekasi" in last:
        return Direction.DARI_KAMPUNGBANDAN_MENUJU_BEKASI_MELALUI_MANGGARAI # Baru

    # Lin Rangkasbitung
    if "rangkasbitung" in first and "tanah abang" in last:
        return Direction.DARI_RANGKASBITUNG_MENUJU_TANAHABANG
    if "tanah abang" in first and "rangkasbitung" in last:
        return Direction.DARI_TANAHABANG_MENUJU_RANGKASBITUNG

    # Lin Tangerang
    if "tangerang" in first and "duri" in last:
        return Direction.DARI_TANGERANG_MENUJU_DURI
    if "duri" in first and "tangerang" in last:
        return Direction.DARI_DURI_MENUJU_TANGERANG
        
    # Lin Feeder Jatinegara - Bogor
    if "jatinegara" in first and "bogor" in last:
        return Direction.DARI_JATINEGARA_MENUJU_BOGOR
    if "bogor" in first and "jatinegara" in last:
        return Direction.DARI_BOGOR_MENUJU_JATINEGARA
    # --------------------------------

    return None

def get_direction(route: List[str]) -> Direction:
    """Determines the direction of a train based on its route."""
    if not route or len(route) < 2:
        return Direction.UNKNOWN
    
    # Gunakan nama stasiun yang sudah dinormalisasi
    first = normalize_station(route[0])
    last = normalize_station(route[-1])

    # Check for directions based on first and last station combinations
    direction = _direction_by_first_last(first, last)
    if direction:
        return direction

    # Check for directions based on last station only (sebagai fallback)
    direction_fallback = _direction_by_last_station(last)
    if direction_fallback:
        return direction_fallback

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
    # Transisi malam ke pagi (misal 60 menit sebelum PUNCAK_PAGI_MULAI)
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
def calculate_fare(route: list, region, from_station=None, to_station=None) -> int:
    """
    Menghitung tarif perjalanan berdasarkan region dan rute.
    - Kutoarjo-Yogyakarta: 8000 flat
    - Yogyakarta-Palur: 8000 flat
    - Rangkasbitung-Merak: 5000 flat
    - Jabodetabek: 3000 (25km pertama) + 1000 per 10km berikutnya
    Hanya menghitung jarak dari from_station ke to_station (bukan seluruh rute kereta).
    """
    if region == Region.YOGYA_SOLO:
        return 8000
    elif region == Region.RANGKASBITUNG_MERAK:
        return 5000
    elif region == Region.JABODETABEK:
        # Cari indeks dari dan ke
        if from_station and to_station and from_station in route and to_station in route:
            idx_from = route.index(from_station)
            idx_to = route.index(to_station)
            if idx_from > idx_to:
                idx_from, idx_to = idx_to, idx_from
            sub_route = route[idx_from:idx_to+1]
        else:
            sub_route = route
        # Hitung jarak hanya pada sub_route
        distances = get_cumulative_distance(sub_route)
        distance = distances[-1] if distances else 0
        if distance <= 25:
            return 3000
        else:
            extra_km = distance - 25
            extra_blocks = int((extra_km + 9.9999) // 10)
            return 3000 + 1000 * extra_blocks
    else:
        return 0  # fallback
    
def _predict_internal(train: Train, current_time: datetime.datetime) -> Dict[str, int]:
    """
    Internal prediction logic for train occupancy.
    """
    occupancy_map = {}
    route = train.route
    if not route:
            return occupancy_map


    direction = get_direction(route)
    periods_weights = get_adjacent_periods(current_time)


    # Ekstrak flag periode waktu untuk mempermudah pembacaan
    # (Meskipun ada bobot, kita hanya cek keberadaannya untuk memilih model)
    is_puncak_pagi = any(p == TimePeriod.PUNCAK_PAGI for p, w in periods_weights)
    is_puncak_sore = any(p == TimePeriod.PUNCAK_SORE for p, w in periods_weights)
    is_awal_siang = any(p == TimePeriod.AWAL_SIANG for p, w in periods_weights)
    is_makan_siang = any(p == TimePeriod.MAKAN_SIANG for p, w in periods_weights)
    is_akhir_siang = any(p == TimePeriod.AKHIR_SIANG for p, w in periods_weights)
    is_akhir_pekan = any(p == TimePeriod.AKHIR_PEKAN for p, w in periods_weights)
    
    # KRL Lin Bogor warna Merah
    
    # Jam sibuk pagi 
    # Okupansi KRL dari Bogor ke Jakarta Kota
    # Dari Bogor - Bojong Gede (0-105%)
    # Dari Citayam - Pasar Minggu (105%-115%)
    # Dari Pasar Minggu Baru - Manggarai (115% - 120%)
    # Dari Cikini - Jakarta Kota (80% menurun hingga 0%)
    
    if (is_puncak_pagi and not is_akhir_pekan) and direction == Direction.DARI_BOGOR_MENUJU_JAKARTAKOTA:    
        for i, station_name in enumerate(route):
            occupancy_map[station_name] = int(-3.410605*10**-13 + 53.36605*i - 8.279928*i**2 + 0.524309 * i**3 - 0.1153014*i**4)
    
    # Jam sibuk sore
    # Okupansi KRL dari Jakarta Kota ke Bogor
    # Dari Jakarta Kota - Manggarai (0-120%)
    # Dari Manggarai - Pasar Minggu Baru (120% menurun hingga 115%)
    # Dari Pasar Minggu Baru - Citayam (115% menurun hingga 105%)
    # Dari Citayam - Bogor (105% menurun hingga 0%)
    
    if (is_puncak_sore and not is_akhir_pekan) and direction == Direction.DARI_JAKARTAKOTA_MENUJU_BOGOR:
        for i, station_name in enumerate(route):
            occupancy_map[station_name] = int(6.82121*10**-13 + 56.58092 * i - 8.699259 * i**2 + 0.5364635 * i**3 - 0.01153014 * i**4)
    
    
    
    # Di luar jam sibuk yg di luar jam makan siang (08:30 - 12:00 & 14:00-15:30 & setelah jam 19:00)
    # Okupansi KRL dari Jakarta Kota ke Bogor
    # Dari Jakarta Kota - Manggarai (0% naik hingga 70%)
    # Dari Manggarai - Pasar Minggu (70% turun hingga 65%)
    # Dari Pasar Minggu - Citayam (65% turun hingga 40%)
    # Dari Bojong Gede - Bogor (40% turun hingga 0%)
    
    if (not is_puncak_sore and not is_akhir_pekan) and direction == Direction.DARI_JAKARTAKOTA_MENUJU_BOGOR:
        for i, station_name in enumerate(route):
            occupancy_map[station_name] = int(-1.136868*10**-13 + 25.82139 * i - 3.355988 * i**2 + 0.1825466 * i**3 - 0.003715035*i**4)
    
    # Di luar jam sibuk yg di dalam jam makan siang (12:00 - 14:00)
    # Okupansi KRL dari Jakarta Kota ke Bogor
    # Dari Jakarta Kota - Manggarai (0% naik hingga 75%)
    # Dari Manggarai - Pasar Minggu (75% turun hingga 70%)
    # Dari Pasar Minggu - Citayam (70% turun hingga 45%)
    # Dari Bojong Gede - Bogor (45% hingga 0%)
    if (is_makan_siang and not is_akhir_pekan) and direction == Direction.DARI_JAKARTAKOTA_MENUJU_BOGOR:
        for i, station_name in enumerate(route):
            occupancy_map[station_name] = int(-1.136868*10**-13 + 28.11143* i - 3.723141*i**2 + 0.2066267*i**3 - 0.004256161*i**4)
            
    # Di luar jam sibuk yg di luar jam makan siang (08:30 - 12:00 & 14:00-15:30 & setelah jam 19:00)
    # Okupansi KRL dari Bogor - Jakarta Kota
    # Dari Bogor - Bojong Gede (0-40%)
    # Dari Citayam - Pasar Minggu (40-65%)
    # Dari Pasar Minggu Baru - Manggarai (65%-70%)
    # Dari Cikini - Jakarta Kota (40% menurun hingga 0%)
    if (is_awal_siang or is_akhir_siang) and not is_akhir_pekan and direction == Direction.DARI_BOGOR_MENUJU_JAKARTAKOTA:
        for i, station_name in enumerate(route):
            occupancy_map[station_name] = int(5.684342*10**-14 + 19.65589 * i - 2.551792 * i**2 + 0.1592366* i**3 - 0.3715035*i**4)
    
    # Di luar jam sibuk yg di dalam jam makan siang (12:00 - 14:00)
    # Okupansi KRL dari Bogor - Jakarta Kota
    # Dari Bogor - Bojong Gede (0-45%)
    # Dari Citayam - Pasar Minggu (45-70%)
    # Dari Pasar Minggu Baru - Manggarai (70-75%)
    # Dari Cikini - Jakarta Kota (45% menurun hingga 0%)
    if is_makan_siang and direction == Direction.DARI_BOGOR_MENUJU_JAKARTAKOTA and not is_akhir_pekan:
        for i, station_name in enumerate(route):
            occupancy_map[station_name] = int(-5.684342*10**-14 + 22.37531 * i - 2.974952 * i**2 + 0.1849401* i**3 - 0.004256161*i**4)
    
    # Di dalam jam sibuk pagi (05:30 - 08:30)
    # Okupansi KRL dari Bogor - Manggarai
    # Dari Bogor - Citayam (0% - 100%)
    # Dari Citayam - Pasar Minggu (100% - 130%)
    # Pasar Minggu - Tebet (130% turun hingga 120%)
    # Manggarai 0%
    if is_puncak_pagi and direction == Direction.DARI_BOGOR_MENUJU_MANGGARAI and not is_akhir_pekan:
        for i, station_name in enumerate(route):
            occupancy_map[station_name] = int(-1.023182*10**-12 + 105.331 * i - 33.7549 * i**2 + 3.610431 * i**3 - 0.1195124 * i**4)
    
    
    # Di luar jam sibuk (05:30- & 08:30 - 15:30 & 19:30+)
    # Okupansi KRL dari Manggarai - Bogor
    # Dari Manggarai - Pasar Minggu (0% - 70%)
    # Dari Pasar Minggu - Citayam (70% menurun hingga 40%)
    # Citayam - Bogor (40 % menurun hingga 0%)
    if is_puncak_sore and direction == Direction.DARI_MANGGARAI_MENUJU_BOGOR and not is_akhir_pekan:
        for i, station_name in enumerate(route):
            occupancy_map[station_name] = int(3.089 * 10**-2 * i**3 - 1.921 * i **2 + 2.283 * 10**1 * i + 7.185 * 10**-14)
    
    
    # Di akhir pekan
    # Okupansi KRL dari Manggarai - Bogor
    # Dari Manggarai - Pasar Minggu (0% - 90%)
    # Dari Pasar Minggu - Citayam (90% menurun hingga 60%)
    # Citayam - Bogor (60 % menurun hingga 0%)     
    if is_akhir_pekan and direction == Direction.DARI_MANGGARAI_MENUJU_BOGOR:
        for i, station_name in enumerate(route):
            occupancy_map[station_name] = int(1.224 * 10**-2 * i**3 - 1.893 * i**2 + 2.716 * 10**1 * i + 4.583 * 10**-14)
    

    # Di jam sibuk sore
    # Okupansi KRL dari Jakarta Kota - Nambo
    # Dari Jakarta Kota - Manggarai (0% hingga 130%)
    # Dari Manggarai - Cawang (130% menurun hingga 100%)
    # Duren Kalibata - Pondok Cina (100% menurun hingga 80%)
    # Depok Baru - Nambo (80% menurun hingga 0%)
    if is_puncak_sore and direction == Direction.DARI_JAKARTAKOTA_MENUJU_NAMBO and not is_akhir_pekan:
        for i, station_name in enumerate(route):
            occupancy_map[station_name] = int(-1.824*10**-2*i**4+8.948*10**-1*i**3-1.453*10**1*i**2+8.267*10**1*i-1.399*10**-12)
            
    # Di jam sibuk pagi
    # Okupansi KRL dari Nambo - Jakarta Kota
    # Nambo (20%)
    # Cibinong (60%)
    # Citayam - Manggarai (dari 120% - 150%)
    # Manggarai - Jakarta Kota (110% menurun hingga 0%)
    if is_puncak_pagi and direction == Direction.DARI_NAMBO_MENUJU_JAKARTAKOTA and not is_akhir_pekan:
        for i, station_name in enumerate(route):
            occupancy_map[station_name] = int(1.517*10**-3 *i**4+ 3.28*10**-2*i**3 - 4.1 * i**2 + 5.75 * 10 * i + 1.587 * 10)
            
    # Di luar jam sibuk
    # Okupansi KRL dari Nambo - Jakarta Kota
    # Nambo (10%)
    # Cibinong (30%)
    # Citayam (50%)
    # Manggarai (70%)
    # Jakarta Kota (0%)
    if (is_akhir_siang or is_awal_siang or is_makan_siang) and direction == Direction.DARI_NAMBO_MENUJU_JAKARTAKOTA and not is_akhir_pekan:
        for i, station_name in enumerate(route):
            occupancy_map[station_name] = int(1.037*10**-5*i**4+1.194*10**-2*i**3-9.251*10**-1*i**2+1.353*10**1*i+2.126*10**1)
    

    # --- BRANCH UNTUK RUTE BARU: CIKARANG/BEKASI/ANGKE/KAMPUNG BANDAN via MANGGARAI ---
    # Contoh: Cikarang–Angke via Manggarai
    if direction in [
        Direction.DARI_CIKARANG_MENUJU_ANGKE_MELALUI_MANGGARAI,
        Direction.DARI_ANGKE_MENUJU_CIKARANG_MELALUI_MANGGARAI,
        Direction.DARI_BEKASI_MENUJU_ANGKE_MELALUI_MANGGARAI,
        Direction.DARI_ANGKE_MENUJU_BEKASI_MELALUI_MANGGARAI,
        Direction.DARI_CIKARANG_MENUJU_MANGGARAI,
        Direction.DARI_MANGGARAI_MENUJU_CIKARANG,
        Direction.DARI_CIKARANG_MENUJU_KAMPUNGBANDAN_MELALUI_MANGGARAI,
        Direction.DARI_KAMPUNGBANDAN_MENUJU_CIKARANG_MELALUI_MANGGARAI,
        Direction.DARI_BEKASI_MENUJU_KAMPUNGBANDAN_MELALUI_MANGGARAI,
        Direction.DARI_KAMPUNGBANDAN_MENUJU_BEKASI_MELALUI_MANGGARAI,
    ]:
        # Jam sibuk (pagi/sore)
        if (is_puncak_pagi or is_puncak_sore) and not is_akhir_pekan:
            for i, station_name in enumerate(route):
                # Polinomial: puncak di tengah, naik ke tengah, turun ke akhir
                n = len(route) - 1 if len(route) > 1 else 1
                peak = 120
                base = 25
                if i <= n // 2:
                    occ = base + (peak - base) * (i / (n // 2 if n // 2 > 0 else 1))
                else:
                    occ = peak - (peak - base) * ((i - n // 2) / (n - n // 2 if n - n // 2 > 0 else 1))
                occupancy_map[station_name] = int(max(0, min(200, occ)))
        # Di luar jam sibuk (weekday)
        elif not is_akhir_pekan:
            for i, station_name in enumerate(route):
                n = len(route) - 1 if len(route) > 1 else 1
                peak = 70
                base = 20
                if i <= n // 2:
                    occ = base + (peak - base) * (i / (n // 2 if n // 2 > 0 else 1))
                else:
                    occ = peak - (peak - base) * ((i - n // 2) / (n - n // 2 if n - n // 2 > 0 else 1))
                occupancy_map[station_name] = int(max(0, min(200, occ)))
        # Akhir pekan
        elif is_akhir_pekan:
            for i, station_name in enumerate(route):
                n = len(route) - 1 if len(route) > 1 else 1
                peak = 90
                base = 25
                if i <= n // 2:
                    occ = base + (peak - base) * (i / (n // 2 if n // 2 > 0 else 1))
                else:
                    occ = peak - (peak - base) * ((i - n // 2) / (n - n // 2 if n - n // 2 > 0 else 1))
                occupancy_map[station_name] = int(max(0, min(200, occ)))

    # --- MEKANISME FALLBACK UNTUK RUTE BARU DAN LAINNYA ---
    # Jika tidak ada aturan spesifik yang cocok di atas (termasuk untuk rute-rute baru yang ditambahkan),
    # logika di bawah ini akan dijalankan.
    if not occupancy_map and route:
        num_stations = len(route)
        
        # Logika baru: Jadikan Manggarai sebagai puncak jika ada di rute
        peak_station_index = num_stations // 2  # Default: puncak di tengah
        try:
            # Cari indeks stasiun 'manggarai' (setelah dinormalisasi)
            normalized_route = [normalize_station(s) for s in route]
            manggarai_index = normalized_route.index('manggarai')
            peak_station_index = manggarai_index
        except ValueError:
            # Jika Manggarai tidak ada di rute, gunakan default (puncak di tengah)
            pass

        # Menggunakan waktu untuk memengaruhi puncak okupansi
        peak_occupancy = 65  # Puncak okupansi default untuk di luar jam sibuk
        if is_puncak_pagi or is_puncak_sore:
            peak_occupancy = 110 # Puncak lebih tinggi untuk jam sibuk
        elif is_akhir_pekan:
            peak_occupancy = 85 # Puncak medium untuk akhir pekan

        for i, station in enumerate(route):
            # Model segitiga sederhana: kenaikan linear ke puncak, lalu penurunan linear
            if i <= peak_station_index:
                # Fase kenaikan
                occupancy = 20 + (peak_occupancy - 20) * (i / peak_station_index) if peak_station_index > 0 else peak_occupancy
            else:
                # Fase penurunan
                denominator = num_stations - 1 - peak_station_index
                occupancy = peak_occupancy - (peak_occupancy - 20) * ((i - peak_station_index) / denominator) if denominator > 0 else 20
            
            # Memastikan nilai berada di antara 0 dan 200 persen
            occupancy_map[station] = max(0, min(200, int(occupancy)))
    # -----------------------------------------------------------

    return occupancy_map

def calculate_confidence(occupancy_map: Dict[str, int]) -> float:
    """
    Calculates a simple confidence score based on predicted occupancy values.
    This is a heuristic for demonstration purposes.
    """
    if not occupancy_map:
        return 0.0

    values = list(occupancy_map.values())
    if not values:
        return 0.0

    min_val = min(values)
    max_val = max(values)
    avg_val = np.mean(values)

    # Heuristic:
    # 1. Penalize for values outside a reasonable range (e.g., 0-150%)
    # 2. Penalize for high variance if multiple stations are predicted
    # 3. Ensure confidence is within [0, 1].

    confidence = 1.0 # Start with high confidence

    # Penalize for values outside a reasonable range (e.g., 0-150%)
    if min_val < 0:
        confidence -= 0.2
    if max_val > 150:
        confidence -= 0.1
    if max_val > 200: # More severe penalty for very high values
        confidence -= 0.2

    # Penalize for high variance if there are multiple stations
    if len(values) > 1:
        std_dev = np.std(values)
        if avg_val > 0: # Avoid division by zero
            relative_std_dev = std_dev / avg_val
            if relative_std_dev > 0.5: # High variance
                confidence -= 0.3
            elif relative_std_dev > 0.2: # Moderate variance
                confidence -= 0.1

    # Ensure confidence is within [0.0, 1.0]
    confidence = max(0.0, min(1.0, confidence))
    return confidence

class OccupancyPredictorModel(mlflow.pyfunc.PythonModel):
    """
    MLflow PythonModel wrapper for the Occupancy Predictor.
    """
    def predict(self, context, model_input: "pd.DataFrame") -> "pd.DataFrame":
        import pandas as pd
        from data_models import Train # Assuming Train is available

        results = []
        for index, row in model_input.iterrows():
            train_id = row['train_id']
            # Reconstruct route from 'route_X' columns, handling potential NaNs
            route_list = [row[col] for col in model_input.columns if col.startswith('route_') and pd.notna(row[col])]
            current_time_str = row['current_time_iso']

            # Create a Train object. This assumes Train has a constructor
            # that takes `train_id` and `route` as arguments, or that these
            # are directly assignable attributes.
            train_obj = Train(train_id=train_id, route=route_list)
            
            current_time_dt = datetime.datetime.fromisoformat(current_time_str)

            occupancy_map_single = _predict_internal(train_obj, current_time_dt)
            
            # Prepare row result for DataFrame output
            row_result = {'train_id': train_id, 'current_time_iso': current_time_str}
            for station, occupancy in occupancy_map_single.items():
                # Sanitize station names for column names
                sanitized_station = station.replace(' ', '_').replace('.', '').replace('-', '_').lower()
                row_result[f"occupancy_{sanitized_station}"] = occupancy
            results.append(row_result)
        
        return pd.DataFrame(results)


def get_cumulative_distance(route: List[str]) -> List[float]:
    # Di sini Anda akan membaca dari data `station_distances` Anda
    # dan menghitung jarak kumulatif untuk rute yang diberikan.
    # Ini adalah implementasi contoh.
    # Anda harus membangun data `station_distances_bogor_line` yang lengkap.

    # Placeholder
    # Seharusnya ini lebih cerdas dan memilih data jarak yang benar berdasarkan line
    station_distances_data = {
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
        # Normalisasi nama stasiun sebelum mencari jarak
        station1 = normalize_station(route[i]).title() # Kembalikan ke format Title Case seperti di data
        station2 = normalize_station(route[i+1]).title()
        
        station_pair = (station1, station2)
        reverse_pair = (station2, station1)
        
        # Cari jarak, jika tidak ada, gunakan default 2.0 km
        dist = station_distances_data.get(station_pair, station_distances_data.get(reverse_pair, 2.0))
        distances.append(distances[-1] + dist)

    return distances


def predict(train: Train, current_time: datetime.datetime, log_model: bool = True) -> Dict[str, int]:
    """
    Memprediksi okupansi untuk semua stasiun dalam rute kereta dengan interpolasi spasial
    yang disesuaikan dengan waktu dan arah perjalanan.
    Menggunakan matriks okupansi dan profil spasial untuk prediksi yang lebih terstruktur.
    """

    occupancy_map = {}
    route = train.route
    if not route:
            return occupancy_map


    direction = get_direction(route)
    periods_weights = get_adjacent_periods(current_time)


    is_puncak_pagi = any(p == TimePeriod.PUNCAK_PAGI for p, w in periods_weights)
    is_puncak_sore = any(p == TimePeriod.PUNCAK_SORE for p, w in periods_weights)
    is_awal_siang = any(p == TimePeriod.AWAL_SIANG for p, w in periods_weights)
    is_makan_siang = any(p == TimePeriod.MAKAN_SIANG for p, w in periods_weights)
    is_akhir_siang = any(p == TimePeriod.AKHIR_SIANG for p, w in periods_weights)
    is_akhir_pekan = any(p == TimePeriod.AKHIR_PEKAN for p, w in periods_weights)
    # KRL Lin Bogor warna Merah
    
    # Jam sibuk pagi 
    # Okupansi KRL dari Bogor ke Jakarta Kota
    # Dari Bogor - Bojong Gede (0-105%)
    # Dari Citayam - Pasar Minggu (105%-115%)
    # Dari Pasar Minggu Baru - Manggarai (115% - 120%)
    # Dari Cikini - Jakarta Kota (80% menurun hingga 0%)
    
    if is_puncak_pagi and direction == Direction.DARI_BOGOR_MENUJU_JAKARTAKOTA:    
        for i, route in enumerate(route):
            occupancy_map[route] = int(-3.410605*10**-13 + 53.36605*i - 8.279928*i**2 + 0.524309 * i**3 - 0.1153014*i**4)
    
    # Jam sibuk sore
    # Okupansi KRL dari Jakarta Kota ke Bogor
    # Dari Jakarta Kota - Manggarai (0-120%)
    # Dari Manggarai - Pasar Minggu Baru (120% menurun hingga 115%)
    # Dari Pasar Minggu Baru - Citayam (115% menurun hingga 105%)
    # Dari Citayam - Bogor (105% menurun hingga 0%)
    
    if is_puncak_sore and direction == Direction.DARI_JAKARTAKOTA_MENUJU_BOGOR:
        for i, route in enumerate(route):
            occupancy_map[route] = int(6.82121*10**-13 + 56.58092 * i - 8.699259 * i**2 + 0.5364635 * i**3 - 0.01153014 * i**4)
    
    
    
    # Di luar jam sibuk yg di luar jam makan siang (08:30 - 12:00 & 14:00-15:30 & setelah jam 19:00)
    # Okupansi KRL dari Jakarta Kota ke Bogor
    # Dari Jakarta Kota - Manggarai (0% naik hingga 70%)
    # Dari Manggarai - Pasar Minggu (70% turun hingga 65%)
    # Dari Pasar Minggu - Citayam (65% turun hingga 40%)
    # Dari Bojong Gede - Bogor (40% turun hingga 0%)
    
    if (not is_puncak_sore and not is_akhir_pekan) and direction == Direction.DARI_JAKARTAKOTA_MENUJU_BOGOR:
        for i, route in enumerate(route):
            occupancy_map[route] = int(-1.136868*10**-13 + 25.82139 * i - 3.355988 * i**2 + 0.1825466 * i**3 - 0.003715035*i**4)
    
    # Di luar jam sibuk yg di dalam jam makan siang (12:00 - 14:00)
    # Okupansi KRL dari Jakarta Kota ke Bogor
    # Dari Jakarta Kota - Manggarai (0% naik hingga 75%)
    # Dari Manggarai - Pasar Minggu (75% turun hingga 70%)
    # Dari Pasar Minggu - Citayam (70% turun hingga 45%)
    # Dari Bojong Gede - Bogor (45% hingga 0%)
    if (is_makan_siang and not is_akhir_pekan) and direction == Direction.DARI_JAKARTAKOTA_MENUJU_BOGOR:
        for i, route in enumerate(route):
            occupancy_map[route] = int(-1.136868*10**-13 + 28.11143* i - 3.723141*i**2 + 0.2066267*i**3 - 0.004256161*i**4)
    
    # Di luar jam sibuk yg di luar jam makan siang (08:30 - 12:00 & 14:00-15:30 & setelah jam 19:00)
    # Okupansi KRL dari Bogor - Jakarta Kota
    # Dari Bogor - Bojong Gede (0-40%)
    # Dari Citayam - Pasar Minggu (40-65%)
    # Dari Pasar Minggu Baru - Manggarai (65%-70%)
    # Dari Cikini - Jakarta Kota (40% menurun hingga 0%)
    if (is_awal_siang or is_akhir_siang) and not is_akhir_pekan and direction == Direction.DARI_BOGOR_MENUJU_JAKARTAKOTA:
        for i, route in enumerate(route):
            occupancy_map[route] = int(5.684342*10**-14 + 19.65589 * i - 2.551792 * i**2 + 0.1592366* i**3 - 0.3715035*i**4)
    
    # Di luar jam sibuk yg di dalam jam makan siang (12:00 - 14:00)
    # Okupansi KRL dari Bogor - Jakarta Kota
    # Dari Bogor - Bojong Gede (0-45%)
    # Dari Citayam - Pasar Minggu (45-70%)
    # Dari Pasar Minggu Baru - Manggarai (70-75%)
    # Dari Cikini - Jakarta Kota (45% menurun hingga 0%)
    if is_makan_siang and direction == Direction.DARI_BOGOR_MENUJU_JAKARTAKOTA and not is_akhir_pekan:
        for i, route in enumerate(route):
            occupancy_map[route] = int(-5.684342*10**-14 + 22.37531 * i - 2.974952 * i**2 + 0.1849401* i**3 - 0.004256161*i**4)
    
    # Di dalam jam sibuk pagi (05:30 - 08:30)
    # Okupansi KRL dari Bogor - Manggarai
    # Dari Bogor - Citayam (0% - 100%)
    # Dari Citayam - Pasar Minggu (100% - 130%)
    # Pasar Minggu - Tebet (130% turun hingga 120%)
    # Manggarai 0%
    if is_puncak_pagi and direction == Direction.DARI_BOGOR_MENUJU_MANGGARAI and not is_akhir_pekan:
        for i, route in enumerate(route):
            occupancy_map[route] = int(-1.023182*10**-12 + 105.331 * i - 33.7549 * i**2 + 3.610431 * i**3 - 0.1195124 * i**4)
    
    
    # Di luar jam sibuk (05:30- & 08:30 - 15:30 & 19:30+)
    # Okupansi KRL dari Manggarai - Bogor
    # Dari Manggarai - Pasar Minggu (0% - 70%)
    # Dari Pasar Minggu - Citayam (70% menurun hingga 40%)
    # Citayam - Bogor (40 % menurun hingga 0%)
    if is_puncak_sore and direction == Direction.DARI_MANGGARAI_MENUJU_BOGOR and not is_akhir_pekan:
        for i, route in enumerate(route):
            occupancy_map[route] = int(3.089 * 10**-2 * i**3 - 1.921 * i **2 + 2.283 * 10**1 * i + 7.185 * 10**-14)
    
    
    # Di akhir pekan
    # Okupansi KRL dari Manggarai - Bogor
    # Dari Manggarai - Pasar Minggu (0% - 90%)
    # Dari Pasar Minggu - Citayam (90% menurun hingga 60%)
    # Citayam - Bogor (60 % menurun hingga 0%)     
    if is_akhir_pekan and direction == Direction.DARI_MANGGARAI_MENUJU_BOGOR:
        for i, route in enumerate(route):
            occupancy_map[route] = int(1.224 * 10**-2 * i**3 - 1.893 * i**2 + 2.716 * 10**1 * i + 4.583 * 10**-14)
    

    # Di jam sibuk sore
    # Okupansi KRL dari Jakarta Kota - Nambo
    # Dari Jakarta Kota - Manggarai (0% hingga 130%)
    # Dari Manggarai - Cawang (130% menurun hingga 100%)
    # Duren Kalibata - Pondok Cina (100% menurun hingga 80%)
    # Depok Baru - Nambo (80% menurun hingga 0%)
    if is_puncak_sore and direction == Direction.DARI_JAKARTAKOTA_MENUJU_NAMBO and not is_akhir_pekan:
        for i, route in enumerate(route):
            occupancy_map[route] = int(-1.824*10**-2*i**4+8.948*10**-1*i**3-1.453*10**1*i**2+8.267*10**1*i-1.399*10**-12)
            
    # Di jam sibuk pagi
    # Okupansi KRL dari Nambo - Jakarta Kota
    # Nambo (20%)
    # Cibinong (60%)
    # Citayam - Manggarai (dari 120% - 150%)
    # Manggarai - Jakarta Kota (110% menurun hingga 0%)
    if is_puncak_pagi and direction == Direction.DARI_NAMBO_MENUJU_JAKARTAKOTA and not is_akhir_pekan:
        for i, route in enumerate(route):
            occupancy_map[route] = int(1.517*10**-3 *i**4+ 3.28*10**-2*i**3 - 4.1 * i**2 + 5.75 * 10 * i + 1.587 * 10)
            
    # Di luar jam sibuk
    # Okupansi KRL dari Nambo - Jakarta Kota
    # Nambo (10%)
    # Cibinong (30%)
    # Citayam (50%)
    # Manggarai (70%)
    # Jakarta Kota (0%)
    if (is_akhir_siang or is_awal_siang or is_makan_siang) and direction == Direction.DARI_NAMBO_MENUJU_JAKARTAKOTA and not is_akhir_pekan:
        for i, route in enumerate(route):
            occupancy_map[route] = int(1.037*10**-5*i**4+1.194*10**-2*i**3-9.251*10**-1*i**2+1.353*10**1*i+2.126*10**1)
    

    # --- BRANCH UNTUK RUTE BARU: CIKARANG/BEKASI/ANGKE/KAMPUNG BANDAN via MANGGARAI ---
    # Contoh: Cikarang–Angke via Manggarai
    if direction in [
        Direction.DARI_CIKARANG_MENUJU_ANGKE_MELALUI_MANGGARAI,
        Direction.DARI_ANGKE_MENUJU_CIKARANG_MELALUI_MANGGARAI,
        Direction.DARI_BEKASI_MENUJU_ANGKE_MELALUI_MANGGARAI,
        Direction.DARI_ANGKE_MENUJU_BEKASI_MELALUI_MANGGARAI,
        Direction.DARI_CIKARANG_MENUJU_MANGGARAI,
        Direction.DARI_MANGGARAI_MENUJU_CIKARANG,
        Direction.DARI_CIKARANG_MENUJU_KAMPUNGBANDAN_MELALUI_MANGGARAI,
        Direction.DARI_KAMPUNGBANDAN_MENUJU_CIKARANG_MELALUI_MANGGARAI,
        Direction.DARI_BEKASI_MENUJU_KAMPUNGBANDAN_MELALUI_MANGGARAI,
        Direction.DARI_KAMPUNGBANDAN_MENUJU_BEKASI_MELALUI_MANGGARAI,
    ]:
        # Jam sibuk (pagi/sore)
        if (is_puncak_pagi or is_puncak_sore) and not is_akhir_pekan:
            for i, station_name in enumerate(route):
                # Polinomial: puncak di tengah, naik ke tengah, turun ke akhir
                n = len(route) - 1 if len(route) > 1 else 1
                peak = 120
                base = 25
                if i <= n // 2:
                    occ = base + (peak - base) * (i / (n // 2 if n // 2 > 0 else 1))
                else:
                    occ = peak - (peak - base) * ((i - n // 2) / (n - n // 2 if n - n // 2 > 0 else 1))
                occupancy_map[station_name] = int(max(0, min(200, occ)))
        # Di luar jam sibuk (weekday)
        elif not is_akhir_pekan:
            for i, station_name in enumerate(route):
                n = len(route) - 1 if len(route) > 1 else 1
                peak = 70
                base = 20
                if i <= n // 2:
                    occ = base + (peak - base) * (i / (n // 2 if n // 2 > 0 else 1))
                else:
                    occ = peak - (peak - base) * ((i - n // 2) / (n - n // 2 if n - n // 2 > 0 else 1))
                occupancy_map[station_name] = int(max(0, min(200, occ)))
        # Akhir pekan
        elif is_akhir_pekan:
            for i, station_name in enumerate(route):
                n = len(route) - 1 if len(route) > 1 else 1
                peak = 90
                base = 25
                if i <= n // 2:
                    occ = base + (peak - base) * (i / (n // 2 if n // 2 > 0 else 1))
                else:
                    occ = peak - (peak - base) * ((i - n // 2) / (n - n // 2 if n - n // 2 > 0 else 1))
                occupancy_map[station_name] = int(max(0, min(200, occ)))

    # --- MEKANISME FALLBACK UNTUK RUTE BARU DAN LAINNYA ---
    # Jika tidak ada aturan spesifik yang cocok di atas (termasuk untuk rute-rute baru yang ditambahkan),
    # logika di bawah ini akan dijalankan.
    if not occupancy_map and route:
        num_stations = len(route)
        
        # Logika baru: Jadikan Manggarai sebagai puncak jika ada di rute
        peak_station_index = num_stations // 2  # Default: puncak di tengah
        try:
            # Cari indeks stasiun 'manggarai' (setelah dinormalisasi)
            normalized_route = [normalize_station(s) for s in route]
            manggarai_index = normalized_route.index('manggarai')
            peak_station_index = manggarai_index
        except ValueError:
            # Jika Manggarai tidak ada di rute, gunakan default (puncak di tengah)
            pass

        # Menggunakan waktu untuk memengaruhi puncak okupansi
        peak_occupancy = 65  # Puncak okupansi default untuk di luar jam sibuk
        if is_puncak_pagi or is_puncak_sore:
            peak_occupancy = 110 # Puncak lebih tinggi untuk jam sibuk
        elif is_akhir_pekan:
            peak_occupancy = 85 # Puncak medium untuk akhir pekan

        for i, station in enumerate(route):
            # Model segitiga sederhana: kenaikan linear ke puncak, lalu penurunan linear
            if i <= peak_station_index:
                # Fase kenaikan
                occupancy = 20 + (peak_occupancy - 20) * (i / peak_station_index) if peak_station_index > 0 else peak_occupancy
            else:
                # Fase penurunan
                denominator = num_stations - 1 - peak_station_index
                occupancy = peak_occupancy - (peak_occupancy - 20) * ((i - peak_station_index) / denominator) if denominator > 0 else 20
            
            # Memastikan nilai berada di antara 0 dan 200 persen
            occupancy_map[station] = max(0, min(200, int(occupancy)))
    # -----------------------------------------------------------

    return occupancy_map



def get_cumulative_distance(route: List[str]) -> List[float]:
    # Di sini Anda akan membaca dari data `station_distances` Anda
    # dan menghitung jarak kumulatif untuk rute yang diberikan.
    # Ini adalah implementasi contoh.
    # Anda harus membangun data `station_distances_bogor_line` yang lengkap.

    # Placeholder
    # Seharusnya ini lebih cerdas dan memilih data jarak yang benar berdasarkan line
    station_distances_data = {
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


# Occupancy Predictor v2
import datetime
from enum import Enum
from typing import List, Dict
import re
import numpy as np
import mlflow
import pandas as pd
from data_models import Train, Region # Pastikan Region diimpor dari data_models

class Line(Enum):
    BOGOR = 1
    CIKARANG = 2
    RANGKASBITUNG = 3
    TANGERANG = 4
    TANJUNG_PRIOK = 5
    # Penambahan Line Baru
    YOGYA_SOLO = 6
    MERAK = 7
    PRAMEKS = 8 # Line baru untuk Prambanan Ekspres
    UNKNOWN = 9


class Direction(Enum):
    # ... (Enum yang sudah ada dari 1-46 tetap sama) ...
    DARI_BOGOR_MENUJU_JAKARTAKOTA = 1
    DARI_JAKARTAKOTA_MENUJU_BOGOR = 2
    DARI_BEKASI_MENUJU_CIKARANG = 3
    MENUJU_RANGKASBITUNG = 4
    MENUJU_TANGERANG = 5
    DUA_ARAH = 6
    UNKNOWN = 7
    DARI_BOGOR_MENUJU_DEPOK = 8
    DARI_MANGGARAI_MENUJU_ANGKE = 9
    MENUJU_KAMPUNGBANDAN = 10
    MENUJU_NAMBO = 11
    DARI_DEPOK_MENUJU_MANGGARAI = 12
    MENUJU_TANAHABANG = 13
    DARI_CIKARANG_MENUJU_BEKASI = 14
    MENUJU_DURI = 15
    DARI_BOGOR_MENUJU_MANGGARAI = 16
    DARI_TANAH_ABANG_MENUJU_MANGGARAI = 17
    DARI_MANGGARAI_MENUJU_BOGOR = 18
    DARI_NAMBO_MENUJU_JAKARTAKOTA = 19
    DARI_JAKARTAKOTA_MENUJU_NAMBO = 20
    DARI_DURI_MENUJU_MANGGARAI = 21
    DARI_BEKASI_MENUJU_ANGKE = 22
    DARI_BEKASI_MENUJU_MANGGARAI = 23
    DARI_BEKASI_MENUJU_KAMPUNG_BANDAN_MELALUI_PASAR_SENEN = 24
    DARI_KAMPUNG_BANDAN_MENUJU_BEKASI_MELALUI_PASAR_SENEN = 25
    DARI_KAMPUNG_BANDAN_MENUJU_CIKARANG_MELALUI_PASAR_SENEN = 26
    DARI_CIKARANG_MENUJU_KAMPUNG_BANDAN_MELALUI_PASAR_SENEN = 27
    DARI_ANGKE_MENUJU_MANGGARAI = 28
    DARI_MANGGARAI_MENUJU_DURI = 29
    DARI_CIKARANG_MENUJU_ANGKE_MELALUI_MANGGARAI = 30
    DARI_ANGKE_MENUJU_CIKARANG_MELALUI_MANGGARAI = 31
    DARI_BEKASI_MENUJU_ANGKE_MELALUI_MANGGARAI = 32
    DARI_ANGKE_MENUJU_BEKASI_MELALUI_MANGGARAI = 33
    DARI_CIKARANG_MENUJU_MANGGARAI = 34
    DARI_RANGKASBITUNG_MENUJU_TANAHABANG = 35
    DARI_TANAHABANG_MENUJU_RANGKASBITUNG = 36
    DARI_TANGERANG_MENUJU_DURI = 37
    DARI_DURI_MENUJU_TANGERANG = 38
    DARI_JATINEGARA_MENUJU_BOGOR = 39
    DARI_BOGOR_MENUJU_JATINEGARA = 40
    DARI_MANGGARAI_MENUJU_CIKARANG = 41
    DARI_CIKARANG_MENUJU_KAMPUNGBANDAN_MELALUI_MANGGARAI = 42
    DARI_KAMPUNGBANDAN_MENUJU_CIKARANG_MELALUI_MANGGARAI = 43
    DARI_BEKASI_MENUJU_KAMPUNGBANDAN_MELALUI_MANGGARAI = 44
    DARI_KAMPUNGBANDAN_MENUJU_BEKASI_MELALUI_MANGGARAI = 45
    MENUJU_ANGKE = 46

    # --- Rute Wilayah VI & Merak ---
    # KA Prameks
    DARI_KUTOARJO_MENUJU_YOGYAKARTA = 47
    DARI_YOGYAKARTA_MENUJU_KUTOARJO = 48
    # KRL Yogya-Solo
    DARI_YOGYAKARTA_MENUJU_PALUR = 49
    DARI_PALUR_MENUJU_YOGYAKARTA = 50
    # KA Lokal Merak
    DARI_RANGKASBITUNG_MENUJU_MERAK = 51
    DARI_MERAK_MENUJU_RANGKASBITUNG = 52


class TimePeriod(Enum):
    PUNCAK_PAGI = 1
    PUNCAK_SORE = 2
    MALAM = 3
    AKHIR_PEKAN = 4
    AWAL_SIANG = 5
    MAKAN_SIANG = 6
    AKHIR_SIANG = 7


TIME_PERIOD_DEFINITIONS = {
    TimePeriod.PUNCAK_PAGI: (datetime.time(6, 0), datetime.time(9, 0)),
    TimePeriod.AWAL_SIANG: (datetime.time(9, 0), datetime.time(12, 0)),
    TimePeriod.MAKAN_SIANG: (datetime.time(12, 0), datetime.time(14, 0)),
    TimePeriod.AKHIR_SIANG: (datetime.time(14, 0), datetime.time(16, 0)),
    TimePeriod.PUNCAK_SORE: (datetime.time(16, 0), datetime.time(19, 0)),
}


def normalize_station(name: str) -> str:
    """Menghapus bagian dalam kurung dan mengubah ke huruf kecil."""
    if not name:
        return ""
    return name.split('(')[0].strip().lower()


def _direction_by_first_last(first: str, last: str) -> Direction:
    # --- Rute Wilayah VI & Merak ---
    # KA Prameks (Kutoarjo-Yogyakarta)
    if "kutoarjo" in first and "yogyakarta" in last:
        return Direction.DARI_KUTOARJO_MENUJU_YOGYAKARTA
    if "yogyakarta" in first and "kutoarjo" in last:
        return Direction.DARI_YOGYAKARTA_MENUJU_KUTOARJO
        
    # KRL (Yogyakarta-Palur/Solo)
    if "yogyakarta" in first and ("palur" in last or "solo" in last):
        return Direction.DARI_YOGYAKARTA_MENUJU_PALUR
    if ("palur" in first or "solo" in first) and "yogyakarta" in last:
        return Direction.DARI_PALUR_MENUJU_YOGYAKARTA

    # KA Lokal (Rangkasbitung-Merak)
    if "rangkasbitung" in first and "merak" in last:
        return Direction.DARI_RANGKASBITUNG_MENUJU_MERAK
    if "merak" in first and "rangkasbitung" in last:
        return Direction.DARI_MERAK_MENUJU_RANGKASBITUNG

    # --- Rute Jabodetabek (logika yang sudah ada) ---
    if "jakarta kota" in first and "bogor" in last:
        return Direction.DARI_JAKARTAKOTA_MENUJU_BOGOR
    if "bogor" in first and "jakarta kota" in last:
        return Direction.DARI_BOGOR_MENUJU_JAKARTAKOTA
    # ... (Tambahkan sisa kondisi Jabodetabek di sini) ...

    return None

def get_direction(route: List[str]) -> Direction:
    """Menentukan arah kereta berdasarkan rutenya."""
    if not route or len(route) < 2:
        return Direction.UNKNOWN

    first = normalize_station(route[0])
    last = normalize_station(route[-1])

    direction = _direction_by_first_last(first, last)
    if direction:
        return direction

    return Direction.UNKNOWN


def get_adjacent_periods(current_time: datetime.datetime) -> List[tuple[TimePeriod, float]]:
    """Mendapatkan periode waktu saat ini."""
    time = current_time.time()
    weekday = current_time.weekday()

    if weekday >= 5:  # Sabtu & Minggu
        return [(TimePeriod.AKHIR_PEKAN, 1.0)]

    for period, (start, end) in TIME_PERIOD_DEFINITIONS.items():
        if start <= time < end:
            return [(period, 1.0)]

    return [(TimePeriod.MALAM, 1.0)]


def _predict_internal(train: Train, current_time: datetime.datetime) -> Dict[str, int]:
    """Logika prediksi internal untuk okupansi kereta."""
    occupancy_map = {}
    route = train.route
    if not route:
        return occupancy_map

    direction = get_direction(route)
    periods_weights = get_adjacent_periods(current_time)
    period = periods_weights[0][0] # Ambil periode utama

    num_stations = len(route)
    if num_stations == 0:
        return {}

    # --- Logika untuk KRL YOGYAKARTA-PALUR ---
    if direction in [Direction.DARI_YOGYAKARTA_MENUJU_PALUR, Direction.DARI_PALUR_MENUJU_YOGYAKARTA]:
        peak_occupancy = 0
        base_occupancy = 0
        
        # Penumpang cenderung menuju Yogyakarta di pagi hari dan meninggalkan di sore hari
        is_menuju_yogya = direction == Direction.DARI_PALUR_MENUJU_YOGYAKARTA

        if period == TimePeriod.PUNCAK_PAGI and is_menuju_yogya:
            peak_occupancy = 95
            base_occupancy = 30
        elif period == TimePeriod.PUNCAK_SORE and not is_menuju_yogya:
             peak_occupancy = 95
             base_occupancy = 30
        elif period == TimePeriod.AKHIR_PEKAN:
            peak_occupancy = 85
            base_occupancy = 40
        else: # Di luar jam sibuk
            peak_occupancy = 65
            base_occupancy = 25
            
        for i, station_name in enumerate(route):
            # Model sederhana: Naik dari basis ke puncak di Yogyakarta, lalu turun
            # Jika dari Palur, indeksnya dibalik
            progress = (num_stations - 1 - i) if is_menuju_yogya else i
            occ = base_occupancy + (peak_occupancy - base_occupancy) * (progress / (num_stations - 1) if num_stations > 1 else 1)
            occupancy_map[station_name] = int(max(0, min(200, occ)))
        return occupancy_map

    # --- Logika untuk KA LOKAL PRAMEKS (KUTOARJO-YOGYAKARTA) ---
    if direction in [Direction.DARI_KUTOARJO_MENUJU_YOGYAKARTA, Direction.DARI_YOGYAKARTA_MENUJU_KUTOARJO]:
        start_occ, end_occ = 0, 0
        if period in [TimePeriod.PUNCAK_PAGI, TimePeriod.PUNCAK_SORE]:
            start_occ, end_occ = 35, 75
        elif period == TimePeriod.AKHIR_PEKAN:
            start_occ, end_occ = 40, 65
        else: # Di luar jam sibuk
            start_occ, end_occ = 30, 50
        
        # Logika dibalik jika arahnya dari Yogyakarta
        if direction == Direction.DARI_YOGYAKARTA_MENUJU_KUTOARJO:
            start_occ, end_occ = end_occ, start_occ

        for i, station_name in enumerate(route):
            # Interpolasi linear sederhana dari stasiun awal ke akhir
            occ = start_occ + (end_occ - start_occ) * (i / (num_stations - 1) if num_stations > 1 else 1)
            occupancy_map[station_name] = int(max(0, min(200, occ)))
        return occupancy_map

    # --- Logika untuk Kereta Lokal RANGKASBITUNG-MERAK ---
    if direction in [Direction.DARI_RANGKASBITUNG_MENUJU_MERAK, Direction.DARI_MERAK_MENUJU_RANGKASBITUNG]:
        start_occ, end_occ = 0, 0
        if period in [TimePeriod.PUNCAK_PAGI, TimePeriod.PUNCAK_SORE]:
            start_occ, end_occ = 40, 80
        elif period == TimePeriod.AKHIR_PEKAN:
            start_occ, end_occ = 35, 55
        else: # Di luar jam sibuk
            start_occ, end_occ = 30, 45
        
        if direction == Direction.DARI_MERAK_MENUJU_RANGKASBITUNG:
            start_occ, end_occ = end_occ, start_occ

        for i, station_name in enumerate(route):
            occ = start_occ + (end_occ - start_occ) * (i / (num_stations - 1) if num_stations > 1 else 1)
            occupancy_map[station_name] = int(max(0, min(200, occ)))
        return occupancy_map

    # --- (Logika yang sudah ada untuk Jabodetabek diletakkan di sini) ---
    # Fallback untuk rute Jabodetabek yang belum memiliki logika spesifik
    if not occupancy_map and route:
        peak_occupancy = 65
        if period in [TimePeriod.PUNCAK_PAGI, TimePeriod.PUNCAK_SORE]:
            peak_occupancy = 110
        elif period == TimePeriod.AKHIR_PEKAN:
            peak_occupancy = 85
        
        for i, station_name in enumerate(route):
            n = num_stations - 1 if num_stations > 1 else 1
            peak_idx = n // 2
            if i <= peak_idx:
                occ = 20 + (peak_occupancy - 20) * (i / peak_idx if peak_idx > 0 else 1)
            else:
                occ = peak_occupancy - (peak_occupancy - 20) * ((i - peak_idx) / (n - peak_idx) if n - peak_idx > 0 else 1)
            occupancy_map[station_name] = int(max(0, min(200, occ)))

    return occupancy_map

def predict(train: Train, current_time: datetime.datetime) -> Dict[str, int]:
    """Fungsi utama untuk memprediksi okupansi."""
    return _predict_internal(train, current_time)

# --- (Sisa fungsi seperti get_cumulative_distance, calculate_fare, dll. tetap sama) ---

# Contoh penggunaan (untuk testing)
if __name__ == '__main__':
    # Simulasi waktu
    waktu_puncak_pagi = datetime.datetime(2023, 10, 27, 7, 30) # Jumat pagi
    waktu_luar_sibuk = datetime.datetime(2023, 10, 27, 11, 0) # Jumat siang
    waktu_akhir_pekan = datetime.datetime(2023, 10, 28, 10, 0) # Sabtu pagi

    # --- Rute Wilayah VI ---
    rute_prameks = ["Kutoarjo", "Jenar", "Wojo", "Wates", "Yogyakarta"]
    rute_krl_yogya_solo = ["Yogyakarta", "Lempuyangan", "Maguwo", "Brambanan", "Klaten", "Purwosari", "Solo Balapan", "Solo Jebres", "Palur"]
    
    kereta_prameks = Train(train_id="PRAMEKS1", route=rute_prameks)
    kereta_krl_solo = Train(train_id="KRLSOLO1", route=rute_krl_yogya_solo)

    print("--- Prediksi KA Prameks Kutoarjo-Yogyakarta (Puncak Pagi) ---")
    okupansi_prameks = predict(kereta_prameks, waktu_puncak_pagi)
    for stasiun, persen in okupansi_prameks.items():
        print(f"{stasiun}: {persen}%")

    print("\n--- Prediksi KRL Yogyakarta-Palur (Puncak Pagi) ---")
    okupansi_krl = predict(kereta_krl_solo, waktu_puncak_pagi)
    for stasiun, persen in okupansi_krl.items():
        print(f"{stasiun}: {persen}%")

    # --- Rute Merak ---
    rute_rangkas_merak = ["Rangkasbitung", "Jambu Baru", "Catang", "Cikeusal", "Walantaka", "Serang", "Karangantu", "Tonjong Baru", "Cilegon", "Krenceng", "Merak"]
    kereta_rangkas_merak = Train(train_id="RM1", route=rute_rangkas_merak)

    print("\n--- Prediksi Kereta Lokal Rangkasbitung-Merak (Luar Jam Sibuk) ---")
    okupansi_merak = predict(kereta_rangkas_merak, waktu_luar_sibuk)
    for stasiun, persen in okupansi_merak.items():
        print(f"{stasiun}: {persen}%")
        
# Okupansi Yogyakarta-Solo v2
import datetime
from enum import Enum
from typing import List, Dict
import numpy as np

# --- DATA MODEL (DUMMY) ---
# Kelas-kelas ini diasumsikan ada di file `data_models.py`.
# Dibuat di sini agar skrip dapat berjalan mandiri untuk demonstrasi.
class Region(Enum):
    YOGYA_SOLO = 1
    RANGKASBITUNG_MERAK = 2
    JABODETABEK = 3

class Train:
    def __init__(self, train_id: str, route: List[str]):
        self.train_id = train_id
        self.route = route

# --- ENUMERATIONS ---
class Line(Enum):
    BOGOR = 1
    CIKARANG = 2
    RANGKASBITUNG = 3
    TANGERANG = 4
    TANJUNG_PRIOK = 5
    YOGYA_SOLO = 6
    MERAK = 7
    PRAMEKS = 8
    UNKNOWN = 9

class Direction(Enum):
    # Rute Jabodetabek
    DARI_BOGOR_MENUJU_JAKARTAKOTA = 1
    DARI_JAKARTAKOTA_MENUJU_BOGOR = 2
    # ... (Enum lainnya untuk Jabodetabek)
    UNKNOWN = 7
    # --- Rute Wilayah VI & Merak ---
    DARI_KUTOARJO_MENUJU_YOGYAKARTA = 47
    DARI_YOGYAKARTA_MENUJU_KUTOARJO = 48
    DARI_YOGYAKARTA_MENUJU_PALUR = 49  # Palur mewakili Solo
    DARI_PALUR_MENUJU_YOGYAKARTA = 50
    DARI_RANGKASBITUNG_MENUJU_MERAK = 51
    DARI_MERAK_MENUJU_RANGKASBITUNG = 52

class TimePeriod(Enum):
    PUNCAK_PAGI = 1
    PUNCAK_SORE = 2
    MALAM = 3
    AKHIR_PEKAN = 4
    AWAL_SIANG = 5
    MAKAN_SIANG = 6
    AKHIR_SIANG = 7

# --- DEFINISI & FUNGSI UTILITAS ---
TIME_PERIOD_DEFINITIONS = {
    TimePeriod.PUNCAK_PAGI: (datetime.time(6, 0), datetime.time(9, 0)),
    TimePeriod.AWAL_SIANG: (datetime.time(9, 0), datetime.time(12, 0)),
    TimePeriod.MAKAN_SIANG: (datetime.time(12, 0), datetime.time(14, 0)),
    TimePeriod.AKHIR_SIANG: (datetime.time(14, 0), datetime.time(16, 0)),
    TimePeriod.PUNCAK_SORE: (datetime.time(16, 0), datetime.time(19, 0)),
}

def normalize_station(name: str) -> str:
    """Menghapus bagian dalam kurung dan mengubah ke huruf kecil."""
    if not name:
        return ""
    return name.split('(')[0].strip().lower()

def _direction_by_first_last(first: str, last: str) -> Direction:
    """Menentukan arah berdasarkan stasiun pertama dan terakhir."""
    # KA Prameks (Kutoarjo-Yogyakarta)
    if "kutoarjo" in first and "yogyakarta" in last:
        return Direction.DARI_KUTOARJO_MENUJU_YOGYAKARTA
    if "yogyakarta" in first and "kutoarjo" in last:
        return Direction.DARI_YOGYAKARTA_MENUJU_KUTOARJO
        
    # KRL (Yogyakarta-Palur/Solo)
    if "yogyakarta" in first and ("palur" in last or "solo" in last):
        return Direction.DARI_YOGYAKARTA_MENUJU_PALUR
    if ("palur" in first or "solo" in first) and "yogyakarta" in last:
        return Direction.DARI_PALUR_MENUJU_YOGYAKARTA

    # KA Lokal (Rangkasbitung-Merak)
    if "rangkasbitung" in first and "merak" in last:
        return Direction.DARI_RANGKASBITUNG_MENUJU_MERAK
    if "merak" in first and "rangkasbitung" in last:
        return Direction.DARI_MERAK_MENUJU_RANGKASBITUNG

    # Jabodetabek
    if "jakarta kota" in first and "bogor" in last:
        return Direction.DARI_JAKARTAKOTA_MENUJU_BOGOR
    if "bogor" in first and "jakarta kota" in last:
        return Direction.DARI_BOGOR_MENUJU_JAKARTAKOTA
    
    return Direction.UNKNOWN

def get_direction(route: List[str]) -> Direction:
    """Mendapatkan arah perjalanan dari sebuah rute."""
    if not route or len(route) < 2:
        return Direction.UNKNOWN
    first = normalize_station(route[0])
    last = normalize_station(route[-1])
    return _direction_by_first_last(first, last)

def get_adjacent_periods(current_time: datetime.datetime) -> List[tuple[TimePeriod, float]]:
    """Mendapatkan periode waktu saat ini."""
    time = current_time.time()
    weekday = current_time.weekday()

    if weekday >= 5:  # Sabtu & Minggu
        return [(TimePeriod.AKHIR_PEKAN, 1.0)]

    for period, (start, end) in TIME_PERIOD_DEFINITIONS.items():
        if start <= time < end:
            return [(period, 1.0)]

    return [(TimePeriod.MALAM, 1.0)]


def _predict_internal(train: Train, current_time: datetime.datetime) -> Dict[str, int]:
    """Logika prediksi internal untuk okupansi kereta."""
    occupancy_map = {}
    route = train.route
    if not route:
        return occupancy_map

    direction = get_direction(route)
    periods_weights = get_adjacent_periods(current_time)
    period = periods_weights[0][0] 

    num_stations = len(route)
    if num_stations == 0:
        return {}

    # --- Logika untuk KRL YOGYAKARTA-SOLO & PRAMEKS (Kutoarjo-Yogyakarta) ---
    is_yogya_route = direction in [
        Direction.DARI_YOGYAKARTA_MENUJU_PALUR, Direction.DARI_PALUR_MENUJU_YOGYAKARTA,
        Direction.DARI_KUTOARJO_MENUJU_YOGYAKARTA, Direction.DARI_YOGYAKARTA_MENUJU_KUTOARJO
    ]
    is_merak_route = direction in [
        Direction.DARI_RANGKASBITUNG_MENUJU_MERAK, Direction.DARI_MERAK_MENUJU_RANGKASBITUNG
    ]

    if is_yogya_route or is_merak_route:
        peak_occupancy = 0
        base_occupancy = 0

        # Tentukan nilai okupansi puncak dan dasar berdasarkan rute dan waktu
        if is_yogya_route:
            is_krl_solo = direction in [Direction.DARI_YOGYAKARTA_MENUJU_PALUR, Direction.DARI_PALUR_MENUJU_YOGYAKARTA]
            if is_krl_solo:
                # KRL Yogya-Solo
                if period in [TimePeriod.PUNCAK_PAGI, TimePeriod.PUNCAK_SORE]:
                    peak_occupancy, base_occupancy = 95, 30
                elif period == TimePeriod.AKHIR_PEKAN:
                    peak_occupancy, base_occupancy = 85, 40
                else:
                    peak_occupancy, base_occupancy = 65, 25
            else:
                # Prameks Kutoarjo-Yogya
                if period in [TimePeriod.PUNCAK_PAGI, TimePeriod.PUNCAK_SORE]:
                    peak_occupancy, base_occupancy = 75, 35
                elif period == TimePeriod.AKHIR_PEKAN:
                    peak_occupancy, base_occupancy = 65, 40
                else:
                    peak_occupancy, base_occupancy = 50, 30
        elif is_merak_route:
            # KA Lokal Rangkasbitung-Merak
            if period in [TimePeriod.PUNCAK_PAGI, TimePeriod.PUNCAK_SORE]:
                peak_occupancy, base_occupancy = 80, 40
            elif period == TimePeriod.AKHIR_PEKAN:
                peak_occupancy, base_occupancy = 55, 35
            else:
                peak_occupancy, base_occupancy = 45, 30

        # === LOGIKA PARABOLA YANG DIPERBAIKI ===
        # Menghitung okupansi dengan kurva parabola.
        # Okupansi tertinggi (peak) di tengah, terendah (base) di ujung.
        n = num_stations - 1 if num_stations > 1 else 1
        for i, station_name in enumerate(route):
            x = i / n if n > 0 else 0  # Normalisasi posisi stasiun (0.0 to 1.0)
            # Rumus parabola: occ = base + (peak - base) * (1 - 4 * (x - 0.5)^2)
            parabolic_factor = 1 - 4 * (x - 0.5) ** 2
            occ = base_occupancy + (peak_occupancy - base_occupancy) * parabolic_factor
            occupancy_map[station_name] = int(max(0, min(200, occ)))
        return occupancy_map

    # Fallback untuk rute lain (misal: Jabodetabek)
    if not occupancy_map and route:
        peak_occupancy = 65
        if period in [TimePeriod.PUNCAK_PAGI, TimePeriod.PUNCAK_SORE]:
            peak_occupancy = 110
        elif period == TimePeriod.AKHIR_PEKAN:
            peak_occupancy = 85
        
        for i, station_name in enumerate(route):
            # Model segitiga sederhana untuk fallback
            n = num_stations - 1 if num_stations > 1 else 1
            peak_idx = n // 2
            if i <= peak_idx:
                occ = 20 + (peak_occupancy - 20) * (i / peak_idx if peak_idx > 0 else 1)
            else:
                occ = peak_occupancy - (peak_occupancy - 20) * ((i - peak_idx) / (n - peak_idx) if n - peak_idx > 0 else 1)
            occupancy_map[station_name] = int(max(0, min(200, occ)))

    return occupancy_map

def predict(train: Train, current_time: datetime.datetime) -> Dict[str, int]:
    """Fungsi utama untuk memprediksi okupansi."""
    return _predict_internal(train, current_time)

# --- CONTOH PENGGUNAAN ---
if __name__ == '__main__':
    # Simulasi waktu
    waktu_puncak_pagi = datetime.datetime(2023, 10, 27, 7, 30)
    waktu_luar_sibuk = datetime.datetime(2023, 10, 27, 11, 0)
    waktu_akhir_pekan = datetime.datetime(2023, 10, 28, 10, 0)

    # Rute Kutoarjo -> Yogyakarta -> Solo (diwakili Palur)
    # Untuk tujuan demonstrasi, kita gabungkan rute Prameks dan KRL
    rute_kutoarjo_solo = ["Kutoarjo", "Jenar", "Wojo", "Wates", "Yogyakarta", "Lempuyangan", "Maguwo", "Klaten", "Purwosari", "Solo Balapan", "Palur"]
    kereta_kutoarjo_solo = Train(train_id="KTSOLO1", route=rute_kutoarjo_solo)
    
    # Rute Rangkasbitung -> Merak
    rute_rangkas_merak = ["Rangkasbitung", "Jambu Baru", "Catang", "Cikeusal", "Walantaka", "Serang", "Karangantu", "Cilegon", "Krenceng", "Merak"]
    kereta_rangkas_merak = Train(train_id="RM1", route=rute_rangkas_merak)

    # Menggunakan arah Yogyakarta -> Palur untuk KRL Solo
    # karena rute gabungan ini tidak ada di enum `Direction`
    kereta_kutoarjo_solo.direction_for_logic = Direction.DARI_YOGYAKARTA_MENUJU_PALUR 

    print("--- Prediksi Rute Kutoarjo-Solo (Puncak Pagi) ---")
    print("Menggunakan logika KRL Yogya-Solo untuk okupansi.")
    okupansi_krl = predict(kereta_kutoarjo_solo, waktu_puncak_pagi)
    for stasiun, persen in okupansi_krl.items():
        print(f"{stasiun:<20}: {'#' * (persen // 4)}{' ' * (25 - persen//4)} ({persen}%)")

    print("\n--- Prediksi Rute Rangkasbitung-Merak (Akhir Pekan) ---")
    okupansi_merak = predict(kereta_rangkas_merak, waktu_akhir_pekan)
    for stasiun, persen in okupansi_merak.items():
        print(f"{stasiun:<20}: {'#' * (persen // 4)}{' ' * (25 - persen//4)} ({persen}%)")

