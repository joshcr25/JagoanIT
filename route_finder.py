import collections
import datetime
import heapq
import tkinter as tk
from tkinter import messagebox
from typing import List, Dict, Set, Any
from PIL import Image, ImageTk

from train_schedule import TrainSchedule
from data_models import RouteNode
import occupancy_predictor as predictor

class RouteFinder:
    """
    Handles the core logic of finding train routes using an A* algorithm.
    """
    INTERCHANGE_STATIONS: Dict[str, Set[predictor.Line]] = {
        "manggarai": {predictor.Line.BOGOR, predictor.Line.CIKARANG},
        "tanah abang": {predictor.Line.CIKARANG, predictor.Line.RANGKASBITUNG},
        "duri": {predictor.Line.CIKARANG, predictor.Line.TANGERANG},
        "kampung bandan": {predictor.Line.CIKARANG, predictor.Line.TANJUNG_PRIOK},
        "jakarta kota": {predictor.Line.BOGOR, predictor.Line.TANJUNG_PRIOK},
    }

    def __init__(self, schedule: TrainSchedule):
        self.schedule = schedule
        self.max_result_count = 1

    def get_available_stations(self) -> List[str]:
        """Returns a sorted list of all available station names."""
        return sorted(list(self.schedule.get_all_stations()))

    @staticmethod
    def show_map_image(image_path: str):
        """Displays the KRL route map in a new window."""
        try:
            map_window = tk.Toplevel()
            map_window.title("Peta Rute KRL")
            img = Image.open(image_path)
            img = img.resize((800, 600), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(map_window, image=photo)
            label.image = photo
            label.pack()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat gambar peta: {image_path}\nError: {e}")

    # --- SIGNATURE FUNGSI DIPERBARUI ---
    def astar_find_routes(self, start_station: str, dest_station: str, current_time: datetime.datetime, max_transit: int, transit_duration_minutes: int) -> List[List[Dict[str, Any]]]:
        """
        Finds the best routes between two stations using an A* algorithm based on arrival time.
        """
        queue = [(current_time, RouteNode(start_station, current_time, [], 0))]
        results = []
        visited = {}

        while queue:
            current_arrival_time, node = heapq.heappop(queue)

            visit_key = (node.station, node.transit)
            if current_arrival_time > visited.get(visit_key, datetime.datetime.max):
                continue
            
            if node.transit > max_transit:
                continue

            relevant_trains = self.schedule.get_trains_for_station(node.station)

            for train in relevant_trains:
                route = train.route
                departure_times = train.departure_times
                
                next_transit_count = node.transit
                if node.route:
                    previous_train_id = node.route[-1]['train_id']
                    if train.id != previous_train_id:
                        next_transit_count = node.transit + 1
                        if next_transit_count > max_transit:
                            continue
                        norm_station = node.station.strip().lower().replace("  ", " ")
                        if norm_station not in self.INTERCHANGE_STATIONS:
                            continue
                
                try:
                    start_idx = route.index(node.station)
                except ValueError:
                    continue

                for i in range(start_idx + 1, len(route)):
                    next_station = route[i]
                    dep_time_str = departure_times.get(node.station)
                    arr_time_str = departure_times.get(next_station)

                    if not dep_time_str or not arr_time_str:
                        continue
                    
                    current_node_time = node.time
                    dep_time = datetime.datetime.combine(
                        current_node_time.date(),
                        datetime.datetime.strptime(dep_time_str, "%H:%M").time()
                    )
                    if dep_time < current_node_time:
                        dep_time += datetime.timedelta(days=1)
                    arr_time = dep_time.replace(
                        hour=int(arr_time_str.split(':')[0]),
                        minute=int(arr_time_str.split(':')[1]),
                        second=0, microsecond=0
                    )
                    if arr_time < dep_time:
                        arr_time += datetime.timedelta(days=1)
                    
                    visit_key_next = (next_station, next_transit_count)
                    if arr_time >= visited.get(visit_key_next, datetime.datetime.max):
                         continue

                    occupancy_data = predictor.predict(train, dep_time)
                    occupancy_at_start = occupancy_data.get(node.station)

                    leg = {
                        "train_id": train.id,
                        "train_name": train.name,
                        "start_station": node.station,
                        "destination_station": next_station,
                        "departure_time": dep_time.strftime("%H:%M"),
                        "estimated_arrival": arr_time.strftime("%H:%M"),
                        "_departure_dt": dep_time,
                        "_arrival_dt": arr_time,
                        "occupancy_percentage": occupancy_at_start
                    }
                    
                    new_route_so_far = node.route + [leg]
                    visited[visit_key_next] = arr_time

                    if next_station == dest_station:
                        results.append(new_route_so_far)
                        if len(results) >= self.max_result_count:
                           pass 
                    else:
                        # --- GUNAKAN PARAMETER WAKTU TRANSIT ---
                        next_node_time = arr_time + datetime.timedelta(minutes=transit_duration_minutes)
                        # ------------------------------------
                        new_node = RouteNode(next_station, next_node_time, new_route_so_far, next_transit_count)
                        heapq.heappush(queue, (arr_time, new_node))

        results.sort(key=lambda r: (len(set(leg['train_id'] for leg in r)) - 1, r[-1]['_arrival_dt']))
        return results[:self.max_result_count]