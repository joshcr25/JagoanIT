import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Train:
    """Data class representing a single train."""
    id: str = ""
    name: str = ""
    route: List[str] = field(default_factory=list)
    departure_times: Dict[str, str] = field(default_factory=dict)

@dataclass
class RouteNode:
    """Data class for a node in the route-finding search."""
    station: str
    time: datetime.datetime
    route: List[Dict[str, Any]] = field(default_factory=list)
    transit: int = 0

    # --- TAMBAHKAN METODE INI ---
    def __lt__(self, other):
        """
        Compare two RouteNode objects. This is primarily used by the priority queue
        to break ties when arrival times are identical.
        We prioritize nodes with fewer transits.
        """
        if not isinstance(other, RouteNode):
            return NotImplemented
        return self.transit < other.transit