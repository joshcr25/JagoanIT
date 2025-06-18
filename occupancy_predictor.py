import datetime
from enum import Enum
from typing import List, Dict, Set
from data_models import Train

class Line(Enum):
    BOGOR = 1
    CIKARANG = 2
    RANGKASBITUNG = 3
    TANGERANG = 4
    TANJUNG_PRIOK = 5
    UNKNOWN = 6

class Direction(Enum):
    MENUJU_JAKARTA = 1
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
DAYTIME_START = datetime.time(9, 0)
DAYTIME_END = datetime.time(15, 0)
EVENING_PEAK_START = datetime.time(15, 30)
EVENING_PEAK_END = datetime.time(19, 0)

# Occupancy data matrix
_avg = lambda r: sum(map(int, r.replace('%', '').replace('+', '').split('-'))) // 2
OCCUPANCY_MATRIX = {
    Line.BOGOR: {
        Direction.MENUJU_JAKARTA: {
            TimePeriod.PUNCAK_PAGI: _avg("150-200%"), TimePeriod.SIANG: _avg("40-60%"),
            TimePeriod.PUNCAK_SORE: _avg("70-100%"), TimePeriod.MALAM: _avg("50-80%"),
            TimePeriod.AKHIR_PEKAN: _avg("90-120%"),
        },
        Direction.MENUJU_BOGOR: {
            TimePeriod.PUNCAK_PAGI: _avg("60-90%"), TimePeriod.SIANG: _avg("50-70%"),
            TimePeriod.PUNCAK_SORE: _avg("140-180%"), TimePeriod.MALAM: _avg("80-110%"),
            TimePeriod.AKHIR_PEKAN: _avg("70-100%"),
        },
    },
    Line.CIKARANG: {
        Direction.MENUJU_JAKARTA: {
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
         Direction.MENUJU_JAKARTA: {
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
        Direction.MENUJU_JAKARTA: {
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
MAX_OCCUPANCY = 98

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
    if route_set.intersection({"depok", "citayam", "bogor", "tebet"}):
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
    if any(term in last for term in ["jakarta", "duri", "angke", "tanah abang"]):
        return Direction.MENUJU_JAKARTA
    if any(term in last for term in ["bogor", "nambo"]):
        return Direction.MENUJU_BOGOR
    if "cikarang" in last:
        return Direction.MENUJU_CIKARANG
    if any(term in last for term in ["rangkasbitung", "parung panjang", "serpong"]):
        return Direction.MENUJU_RANGKASBITUNG
    if "tangerang" in last:
        return Direction.MENUJU_TANGERANG
    return Direction.UNKNOWN

def get_time_period(dt: datetime.datetime) -> TimePeriod:
    """Determines the time period (peak, off-peak, etc.) for a given datetime."""
    if dt.weekday() >= 5:  # Saturday or Sunday
        return TimePeriod.AKHIR_PEKAN
    
    time = dt.time()
    if MORNING_PEAK_START <= time < MORNING_PEAK_END:
        return TimePeriod.PUNCAK_PAGI
    if DAYTIME_START <= time < DAYTIME_END:
        return TimePeriod.SIANG
    if EVENING_PEAK_START <= time < EVENING_PEAK_END:
        return TimePeriod.PUNCAK_SORE
    return TimePeriod.MALAM

def predict(train: Train, current_time: datetime.datetime) -> Dict[str, int]:
    """Predicts occupancy for all stations in a train's route."""
    occupancy_map = {}
    route = train.route
    if not route:
        return occupancy_map

    line = get_line(route)
    direction = get_direction(route)
    period = get_time_period(current_time)
    
    occupancy = OCCUPANCY_MATRIX.get(line, {}).get(direction, {}).get(period, DEFAULT_OCCUPANCY)
    
    final_occupancy = max(MIN_OCCUPANCY, min(occupancy, MAX_OCCUPANCY))
    
    for station in route:
        occupancy_map[station] = final_occupancy
        
    return occupancy_map