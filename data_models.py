# data_models.py
import datetime
from dataclasses import dataclass, field
from enum import Enum  # Import Enum
from typing import List, Dict, Any

# --- TAMBAHKAN ENUM INI ---
class Region(Enum):
    """Merepresentasikan wilayah operasional KRL."""
    JABODETABEK = "Commuter Line Jabodetabek"
    YOGYA_SOLO = "Commuter Line Yogyakarta-Solo-Kutoarjo"
    RANGKASBITUNG_MERAK = "Commuter Line Rangkasbitung-Merak"

@dataclass
class Train:
    """Data class yang merepresentasikan satu kereta."""
    train_id: str = ""
    name: str = ""
    route: List[str] = field(default_factory=list)
    departure_times: Dict[str, str] = field(default_factory=dict)
    # --- TAMBAHKAN FIELD INI ---
    region: Region = Region.JABODETABEK  # Atribut baru untuk wilayah

@dataclass
class RouteNode:
    """Data class untuk sebuah node dalam pencarian rute."""
    station: str
    time: datetime.datetime
    route: List[Dict[str, Any]] = field(default_factory=list)
    transit: int = 0

    def __lt__(self, other):
        """
        Bandingkan dua objek RouteNode. Digunakan oleh priority queue
        untuk memecah kebuntuan jika waktu kedatangan identik.
        Kita prioritaskan node dengan transit lebih sedikit setelah waktu.
        """
        if not isinstance(other, RouteNode):
            return NotImplemented
        # Memastikan perbandingan utama adalah waktu, lalu jumlah transit
        if self.time != other.time:
            return self.time < other.time
        return self.transit < other.transit