# route_finder.py
import collections
import datetime
import heapq
import tkinter as tk
from typing import List, Dict, Any, Set
from PIL import Image, ImageTk

from train_schedule import TrainSchedule
# --- UBAH IMPORT ---
from data_models import RouteNode, Region
import occupancy_predictor as predictor


class RouteFinder:
    """
    Menangani logika inti untuk menemukan rute kereta.
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
        self.max_result_count = 3  # Menaikkan agar bisa menampilkan beberapa alternatif

    @staticmethod
    def show_map_image(image_path: str):
        # ... (Tidak ada perubahan di sini)
        pass

    # --- UBAH SIGNATURE find_routes ---
    def find_routes(
        self,
        start_station: str,
        dest_station: str,
        start_time: datetime.datetime,
        region: Region
    ) -> List[List[Dict[str, Any]]]:
        """
        Menemukan rute antara dua stasiun pada waktu tertentu di wilayah spesifik.
        """
        if not all([start_station, dest_station, start_time, region]):
            return []

        queue = [(start_time, RouteNode(start_station, start_time, [], 0))]
        visited = {(start_station, 0): start_time}
        results = []
        max_transits = 2 if region == Region.JABODETABEK else 1

        while queue and len(results) < self.max_result_count:
            __, node = heapq.heappop(queue)
            trains_at_station = self.schedule.get_trains_for_station(node.station, region)
            self._process_trains(trains_at_station, node, dest_station, max_transits, visited, queue, results)
        
        results = self._sort_and_filter_results(results)
        return results[:self.max_result_count]

    def _process_trains(self, trains_at_station, node, dest_station, max_transits, visited, queue, results):
        for train in trains_at_station:
            try:
                current_idx = train.route.index(node.station)
            except ValueError:
                continue

            predicted_occupancies = predictor.predict(train, node.time)
            self._process_train_legs(train, current_idx, node, dest_station, max_transits, visited, queue, results, predicted_occupancies)

            if len(results) >= self.max_result_count:
                break
        

    def _process_train_legs(self, train, current_idx, node, dest_station, max_transits, visited, queue, results, predicted_occupancies):
        for i in range(current_idx + 1, len(train.route)):
            if self._should_skip_leg(train, node, i):
                continue

            next_station = train.route[i]
            dep_time_str = train.departure_times.get(node.station)
            arr_time_str = train.departure_times.get(next_station)
            dep_time, arr_time = self._get_departure_arrival_times(node.time, dep_time_str, arr_time_str)
            if not self._is_leg_time_and_transit_valid(node, dep_time, arr_time, train, max_transits):
                continue

            is_different_train = not node.route or train.id != node.route[-1]['train_id']
            next_transit_count = node.transit + 1 if is_different_train and node.route else node.transit
            visit_key = (next_station, next_transit_count)
            if self._should_skip_visit(visit_key, visited, arr_time):
                continue

            __, new_route_so_far = self._create_leg_and_route(train, node, next_station, dep_time, arr_time, predicted_occupancies)
            visited[visit_key] = arr_time

            if self._handle_leg_result(next_station, dest_station, results, new_route_so_far, queue, arr_time, is_different_train, next_transit_count):
                break

    def _is_leg_time_and_transit_valid(self, node, dep_time, arr_time, train, max_transits):
        if not self._is_time_valid(node.time, dep_time, arr_time):
            return False
        is_different_train = not node.route or train.id != node.route[-1]['train_id']
        next_transit_count = node.transit + 1 if is_different_train and node.route else node.transit
        if next_transit_count > max_transits:
            return False
        return True

    def _handle_leg_result(self, next_station, dest_station, results, new_route_so_far, queue, arr_time, is_different_train, next_transit_count):
        if next_station == dest_station:
            results.append(new_route_so_far)
            if len(results) >= self.max_result_count:
                return True
        else:
            self._enqueue_next_node(next_station, arr_time, is_different_train, new_route_so_far, next_transit_count, queue)
        return False

    def _should_skip_leg(self, train, node, i):
        next_station = train.route[i]
        dep_time_str = train.departure_times.get(node.station)
        arr_time_str = train.departure_times.get(next_station)
        if not dep_time_str or not arr_time_str:
            return True
        return False

    def _should_skip_visit(self, visit_key, visited, arr_time):
        return visit_key in visited and visited[visit_key] <= arr_time

    def _create_leg_and_route(self, train, node, next_station, dep_time, arr_time, predicted_occupancies):
        leg = self._create_leg(train, node, next_station, dep_time, arr_time, predicted_occupancies)
        new_route_so_far = node.route + [leg]
        return leg, new_route_so_far

    def _handle_destination(self, next_station, dest_station, results, new_route_so_far):
        if next_station == dest_station:
            results.append(new_route_so_far)
            return True
        return False

    def _get_departure_arrival_times(self, node_time, dep_time_str, arr_time_str):
        dep_h, dep_m = map(int, dep_time_str.split(':'))
        arr_h, arr_m = map(int, arr_time_str.split(':'))
        dep_time = node_time.replace(hour=dep_h, minute=dep_m, second=0, microsecond=0)
        if dep_time < node_time:
            dep_time += datetime.timedelta(days=1)
        arr_time = dep_time.replace(hour=arr_h, minute=arr_m)
        if arr_time < dep_time:
            arr_time += datetime.timedelta(days=1)
        return dep_time, arr_time

    def _is_time_valid(self, node_time, dep_time, arr_time):
        return dep_time > node_time and arr_time > dep_time

    def _create_leg(self, train, node, next_station, dep_time, arr_time, predicted_occupancies):
        return {
            "train_id": train.id, "train_name": train.name,
            "start_station": node.station, "destination_station": next_station,
            "departure_time": dep_time.strftime("%H:%M"),
            "estimated_arrival": arr_time.strftime("%H:%M"),
            "_departure_dt": dep_time, "_arrival_dt": arr_time,
            "occupancy_percentage": predicted_occupancies.get(node.station, -1)
        }

    def _enqueue_next_node(self, next_station, arr_time, is_different_train, new_route_so_far, next_transit_count, queue):
        transit_wait_minutes = 15 if is_different_train else 2
        next_node_time = arr_time + datetime.timedelta(minutes=transit_wait_minutes)
        if next_node_time <= arr_time:
            return
        new_node = RouteNode(next_station, next_node_time, new_route_so_far, next_transit_count)
        heapq.heappush(queue, (arr_time, new_node))

    def _sort_and_filter_results(self, results):
        results.sort(key=lambda r: (r[-1]['_arrival_dt'], len(r)))
        if not results:
            return results
        min_duration = (results[0][-1]['_arrival_dt'] - results[0][0]['_departure_dt']).total_seconds()
        max_tolerated = min_duration + 30 * 60
        filtered = []
        for r in results:
            dur = (r[-1]['_arrival_dt'] - r[0]['_departure_dt']).total_seconds()
            if dur <= max_tolerated:
                filtered.append(r)
            if len(filtered) >= self.max_result_count:
                break
        return filtered
