import collections
import datetime
import tkinter as tk
from tkinter import messagebox
from typing import List, Dict, Set, Any
from PIL import Image, ImageTk

from train_schedule import TrainSchedule
from data_models import RouteNode
import occupancy_predictor as predictor

class RouteFinder:
    """
    Handles the core logic of finding train routes using a BFS algorithm.
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
            
            # Use Pillow to open and resize the image
            img = Image.open(image_path)
            img = img.resize((800, 600), Image.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            
            label = tk.Label(map_window, image=photo)
            label.image = photo  # Keep a reference!
            label.pack()

        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat gambar peta: {image_path}\nError: {e}")

    def bfs_find_routes(self, start_station: str, dest_station: str, current_time: datetime.datetime, max_transit: int) -> List[List[Dict[str, Any]]]:
        """
        Finds the best routes between two stations using an optimized BFS algorithm.
        """
        queue = collections.deque([RouteNode(start_station, current_time, [], 0)])
        results = []
        visited = set()
        best_duration = float('inf')

        while queue:
            node = queue.popleft()
            
            if node.transit > max_transit:
                continue

            last_train_id = node.route[-1]['train_id'] if node.route else "START"
            visit_key = (node.station, last_train_id, node.transit)
            if visit_key in visited:
                continue
            visited.add(visit_key)

            relevant_trains = self.schedule.get_trains_for_station(node.station)

            for train in relevant_trains:
                route = train.route
                departure_times = train.departure_times
                
                next_transit_count = node.transit
                # --- TRANSIT LOGIC ---
                if node.route:
                    previous_train_id = node.route[-1]['train_id']
                    if train.id != previous_train_id: # This is a transit
                        next_transit_count = node.transit + 1
                        if next_transit_count > max_transit:
                            continue
                        
                        norm_station = node.station.strip().lower().replace("  ", " ")
                        if norm_station not in self.INTERCHANGE_STATIONS:
                            continue
                        
                        # Check for valid line transfer
                        current_train_line = predictor.get_line(train.route)
                        # This lookup is simplified; a real app might need to fetch the full Train object
                        prev_trains = [t for t in self.schedule.get_trains() if t.id == previous_train_id]
                        if not prev_trains: continue
                        
                        previous_train_line = predictor.get_line(prev_trains[0].route)
                        allowed_lines = self.INTERCHANGE_STATIONS[norm_station]
                        
                        if current_train_line not in allowed_lines or previous_train_line not in allowed_lines:
                            continue
                # --- END TRANSIT LOGIC ---
                
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
                    
                    dep_time = datetime.datetime.combine(node.time.date(), datetime.datetime.strptime(dep_time_str, "%H:%M").time())
                    arr_time = datetime.datetime.combine(node.time.date(), datetime.datetime.strptime(arr_time_str, "%H:%M").time())

                    if dep_time < node.time:
                        continue
                    
                    first_leg_dep_time = node.route[0]['_departure_dt'] if node.route else dep_time
                    new_duration = (arr_time - first_leg_dep_time).total_seconds()

                    if new_duration > best_duration:
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

                    if next_station == dest_station:
                        results.append(new_route_so_far)
                        if new_duration < best_duration:
                            best_duration = new_duration
                    else:
                        queue.append(RouteNode(next_station, arr_time + datetime.timedelta(minutes=1), new_route_so_far, next_transit_count))

        # Sort results by transit count, then by arrival time
        results.sort(key=lambda r: (len(set(leg['train_id'] for leg in r)) - 1, r[-1]['_arrival_dt']))

        return results[:self.max_result_count]