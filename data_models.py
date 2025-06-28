# Beberapa instans (tapi gk semua) yang dibantu Github Copilot dan Google Gemini
# -- Awal Kutipan
import datetime
from dataclasses import dataclass, field
from enum import Enum  # Import Enum
from typing import List, Dict, Any

# Merepresentasikan wilayah operasional KRL
class Region(Enum):
    JABODETABEK = "Commuter Line Jabodetabek"
    YOGYA_SOLO = "Commuter Line Yogyakarta-Solo-Kutoarjo"
    RANGKASBITUNG_MERAK = "Commuter Line Rangkasbitung-Merak"

# Data class yg merepresentasikan satu kereta.
@dataclass
class Train:
    train_id: str = ""
    name: str = ""
    route: List[str] = field(default_factory=list)
    departure_times: Dict[str, str] = field(default_factory=dict)
    # --- TAMBAHKAN FIELD INI ---
    region: Region = Region.JABODETABEK  # Atribut baru untuk wilayah
    
    def __init__(self, train_id: str, name: str = "", route: List[str] = None, departure_times: Dict[str, str] = None, region: Region = Region.JABODETABEK):
        self.train_id = train_id
        self.name = name
        self.route = route if route is not None else []
        self.departure_times = departure_times if departure_times is not None else {}
        self.region = region
    


# Data class untuk sebuah node dalam pencarian rute.
@dataclass
class RouteNode:
    station: str
    time: datetime.datetime
    route: List[Dict[str, Any]] = field(default_factory=list)
    transit: int = 0

    
    def __lt__(self, other):
        # Bandingkan dua objek RouteNode. Digunakan oleh priority queue
        # untuk memecah kebuntuan jika waktu kedatangan identik.
        # Kita prioritaskan node dengan transit lebih sedikit setelah waktu.
        if not isinstance(other, RouteNode):
            return NotImplemented
        # Memastikan perbandingan utama adalah waktu, lalu jumlah transit
        if self.time != other.time:
            return self.time < other.time
        return self.transit < other.transit
    
# -- Akhir kutipan